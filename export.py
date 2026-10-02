import pandas as pd

class ExportLocal(object):

    def __init__(self, df):
        self.df = df

    def export(self):

        # Obtener la fecha y hora actual
        today = pd.Timestamp.now()

        # Formatear la fecha y hora en el formato deseado
        fecha_str = today.strftime('%d_%m_%Y_%H_%M_%S')

        self.df.to_excel(f'test_{fecha_str}.xlsx', index=False)