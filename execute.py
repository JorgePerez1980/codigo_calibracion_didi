from read import DataReader
from GAI_txt import TextAnalytics
from export import ExportLocal
import pandas as pd

class WorkFlow(object):
  """
  Class that coordinates the workflow to process call transcript texts.

  Attributes:
    file_name (str): Name of the file containing call transcripts.

  Methods:
    run(): Executes the complete workflow for reading, analyzing, and loading data.
  """
  
  def __init__(self, request:dict) -> None:
    """
    Initializes the WorkFlow class.

    Args:
      file_name (str): Name of the file containing call transcripts.
    """
    
    self.request = request
    self.dfs = []

  def run(self) -> None:
    """
    Executes the complete workflow:
    1. Reads call transcripts from a file.
    2. Processes the transcripts using the text analysis model.
    3. Loads the analysis results into a data store.
    """
    for key, value in self.request.items():
      print(f"Clave: {key}, Valor: {value}")
      file_name = value
      print(f"Procesing file: {file_name}.")
      df = DataReader(file_name).read_data()      
      df = TextAnalytics(df).processing()
      # Agregar el ID de la interacción.
      df['custom_data_01'] = [file_name.split("/")[-1]] 
      self.dfs.append(df)

    df = pd.concat(self.dfs, axis=0)
    df = df.reset_index(drop=True)
    print(df.head())
    ExportLocal(df).export()
    return "finish process"     