from datetime import datetime
from io import BytesIO
import pandas as pd
import polars as pl
from google.cloud import storage,bigquery
import pytz
from environment import DATASET, GIA_PROJECT, TABLE, GIA_TEXT_BUCKET, GIA_AUDIO_METADATA, BUCKET_STRUCTURE_CATEGORIZED, FILE_STRUCTURE_CATEGORIZED, TIME_ZONE
import os

class DataReader(object):
    """
    A class to read and process data from various sources including metadata and audio files.
    
    Attributes:
        id_table (str): The identifier for the table/audio file
        project_id (str): Google Cloud project ID
        audio_bucket (str): GCS bucket for audio files
        audio_metadata (str): GCS bucket for metadata
        table_used (str): Reference table name
        storage_client: Google Cloud Storage client instance
    """

    def __init__(self, id_table: str) -> None:

        self.id_table = id_table
        self.project_id = GIA_PROJECT
        self.text_bucket = GIA_TEXT_BUCKET
        self.text_var = os.environ['GIA_TEXT_VAR']
        self.audio_metadata = GIA_AUDIO_METADATA
        self.meta_project = os.environ['META_PROJECT']
        self.meta_dataset = os.environ['META_DATASET']
        self.meta_table = os.environ['META_TABLE']  
        self.meta_key = os.environ['META_KEY']
        self.table_used = TABLE
        self.dataset_used = DATASET
        self.storage_client = storage.Client(project=GIA_PROJECT)
        self.bigquery_client = bigquery.Client(project=GIA_PROJECT)

    def extract_metadata_storage(self) -> pd.DataFrame:
        """
        Extracts metadata from Excel files stored in Google Cloud Storage.
        
        Returns:
            pd.DataFrame: DataFrame containing metadata filtered by audio name.
                         Returns empty DataFrame if no matching files found.
        """
        # Initialize storage client
        bucket = self.storage_client.bucket(self.audio_metadata)

        # List all blobs in bucket
        blobs = bucket.list_blobs()

        # Initialize empty list to store dataframes
        dfs = []

        # Iterate through blobs and process those starting with 'metadata'
        for blob in blobs:
            if blob.name.lower().startswith('metadata'):
                # Construct the full path to the file in GCS
                gcs_path = f"gs://{self.audio_metadata}/{blob.name}"

                # Read the CSV file directly from GCS

                df = pd.read_excel(gcs_path)
                dfs.append(df)

        # Concatenate all dataframes if any were found
        if dfs:
            final_df = pd.concat(dfs, ignore_index=True)
            # Filtrar el DataFrame para que solo incluya filas donde 'id_tabla' es igual a self.id_table
            final_df = final_df[final_df['Audioname'] == self.id_table.split("/")[-1]]
            final_df.reset_index(drop=True, inplace=True)
            return final_df
        else:
            return pd.DataFrame()  # Return empty dataframe if no matching files found


    def extract_metadata(self) -> pd.DataFrame:
        
        key_audio = str(self.id_table.split('/')[-1].split('.')[0])
        
        query = f"""
            SELECT 
                *
            FROM `{self.meta_project}.{self.meta_dataset}.{self.meta_table}`
            WHERE CAST({self.meta_key} AS STRING) = '{key_audio}'
            LIMIT 1
        """
        df = self.bigquery_client.query(query).to_dataframe()
        df = df.astype(str)

        return df

    @staticmethod
    def get_item(x) -> str:
        """
        Retrieves the first item's 'item' value from a nested dictionary structure.

        Args:
            x (dict): A dictionary that contains a 'list' key, which maps to a list of dictionaries.

        Returns:
            str: The 'item' value of the first dictionary in the 'list' if it exists, otherwise returns the input dictionary.

        Example:
            >>> get_item({'list': [{'item': 'value1'}, {'item': 'value2'}]})
            'value1'
            >>> get_item({'list': []})
            {'list': []}
            >>> get_item({})
            {}
        """
        return x['list'][0]['item'] if x and 'list' in x and x['list'] else x
    
    def validate_existence_structure_file(self, bucket_name: str, file_name: str) -> tuple[bool,pl.DataFrame | None]:
        """
        Validates the existence of a file in a specified bucket and reads its content into a Polars DataFrame if it exists.

        Args:
            bucket_name (str): The name of the bucket where the file is stored.
            file_name (str): The name of the file to check for existence.

        Returns:
            tuple[bool, pl.DataFrame | None]: A tuple containing a boolean indicating the existence of the file and a Polars DataFrame with the file's content if it exists, otherwise None.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        if blob.exists():
            data = blob.download_as_bytes()
            # Leer los bytes en Polars como un CSV usando BytesIO
            df = pl.read_csv(BytesIO(data))
            return True, df
        return False, None
    
    @staticmethod
    def extract_date_hour() -> str:
        """
        Extracts the current date and hour in a specified time zone.

        This function retrieves the current date and time based on the specified
        time zone and returns it as a string. It also prints the current date and
        time to the console.

        Returns:
            str: The current date and time in the specified time zone, formatted
            as a string without microseconds.
        """
        # Obtener la zona horaria
        time_data = pytz.timezone(TIME_ZONE)
        # Obtener la fecha y hora actual
        new_date = datetime.now(time_data)
        return str(new_date).split('.')[0]
    
    def create_table_with_metadata(self, df_result: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
        """
        Creates a new table with metadata by filtering, joining, and renaming columns.
        
        Args:
            df_result (pl.DataFrame): The main DataFrame containing the results
            
        Returns:
            tuple[pl.DataFrame, dict]: A tuple containing:
                - Transformed DataFrame with renamed columns and additional metadata
                - Dictionary mapping new column names to original names
                
        Process:
            1. Validates and handles existing structure file
            2. Saves schema to CSV in Google Cloud Storage
            3. Renames columns with custom naming convention
            4. Converts all columns to string type
            5. Adds duration, silence, and timestamp columns
            6. Adds creation date flag
        """
        is_existence, df_old = self.validate_existence_structure_file(
            BUCKET_STRUCTURE_CATEGORIZED, FILE_STRUCTURE_CATEGORIZED)
        if is_existence:
            old_columns = df_old.columns
            missing_columns = list(set(old_columns) - set(df_result.columns))
            if len(missing_columns) > 0:
                df_missing = pl.DataFrame({col: [None] * len(df_result) for col in missing_columns})
                df_result = df_result.hstack(df_missing)
                all_columns_ordered = old_columns + [col for col in df_result.columns if col not in old_columns]
                df_result = df_result.select(all_columns_ordered)

        
        pl.DataFrame(schema=df_result.schema).to_pandas().to_csv(f'gs://{BUCKET_STRUCTURE_CATEGORIZED}/{FILE_STRUCTURE_CATEGORIZED}', index=False)
        new_column_names = [
            f"custom_data_{str(i+2).zfill(2)}" for i in range(len(df_result.columns))]

        # Renombrar las columnas
        column_mapping = dict(zip(new_column_names, df_result.columns))

        # Renombrar las columnas
        df_renamed = df_result.rename(
            dict(zip(df_result.columns, new_column_names)))
        # pasar columnas a sting
        df_renamed = df_renamed.with_columns([
            pl.col(col).cast(pl.Utf8) for col in df_renamed.columns
        ])
        df_renamed = df_renamed.with_columns(
            df_result["Marca_temporal"].cast(
                pl.Utf8).alias("date_interaction")
        )

        df_renamed = df_renamed.with_columns(
            pl.lit(self.extract_date_hour()).alias("flag_creation_date")
        )

        return df_renamed,column_mapping

    def read_data(self) -> tuple[pd.DataFrame, bool]:
        """
        Main method to read and combine all necessary data.
        
        Returns:
            tuple[pd.DataFrame, bool, dict]: A tuple containing:
                - Combined and processed DataFrame
                - Boolean indicating if process was successful
                - Column mapping dictionary
                
        Process:
            1. Extracts metadata
            2. Extracts distribution data
            3. Gets non-phonetic metrics
            4. Combines all DataFrames
            5. Processes and transforms the combined data
        """
        # validate_existence = self.bigquery_client.query(f"""
        #     SELECT COUNT(*) as count
        #     FROM `{self.project_id}.{self.dataset_used}.{self.table_used}`
        #     WHERE custom_data_01     = "{self.id_table.split("/")[-1]}"
        # """).to_dataframe()
        # if validate_existence['count'][0] > 0:
        #     return pd.DataFrame(), True,{},"Interaction duplicated, skipping..."
        
        # Leer el archivo a procesar - Texto
        df_txt = pd.read_csv(f"gs://{self.text_bucket}/{self.id_table}", sep="|", encoding='utf-8-sig')
        
        # Leer metadata
        df_metadata = self.extract_metadata()

        if df_metadata.empty:

            # Ubicacion del texto
            df_txt['ubicacion_texto'] = [f'{self.text_bucket} {self.id_table}']
            df_txt['Marca_temporal'] =datetime.now()

            return df_txt
        
        df_metadata = df_metadata.astype(str)

        # Guardar la información de la columna self.text_var en un DataFrame independiente
        df_text_var = df_txt[[self.text_var]].copy()

        # Excluir la columna self.text_var de df_metadata
        df_txt_filtered = df_txt.drop(columns=[self.text_var], errors='ignore')

        # Concatenar los DataFrames
        df_txt = pd.concat([df_txt_filtered, df_metadata], axis=1)

        # Ubicacion del texto
        df_txt['ubicacion_texto'] = [f'{self.text_bucket} {self.id_table}']
        df_txt['Marca_temporal'] =datetime.now()

        # Convertir el DataFrame combinado a un DataFrame de Polars
        pl_df = pl.from_pandas(df_txt)
        pl_df_custom,column_mapping = self.create_table_with_metadata(pl_df)

        pd_df_custom = pl_df_custom.to_pandas()
        pd_df_custom = pd.concat([df_text_var, pd_df_custom], axis=1)
        pd_df_custom = pd_df_custom.astype(str)

        return pd_df_custom
