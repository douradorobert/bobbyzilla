from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceNotFoundError
import pandas as pd
import os

def get_feriados(calendario:str):
    """Obtem uma lista de feriados com base no calendario especificado

    Args:
        calendario (str): CalendarioBrazilOTC or CalendarioBrazilBMF 

    Returns:
        list: lista contendo os feriados de acordo com o calendário solicitado
    """
    if not calendario in ["CalendarioBrazilOTC", "CalendarioBrazilBMF"]:
        raise ResourceNotFoundError(
            "Os calendários de feriados disponíveis são "+
            "CalendarioBrazilOTC e CalendarioBrazilBMF."
                )
    #conexão com o banco
    conn_str = os.environ["InputDataLake"]

    #conexão com a table de feriados
    table_service_client = TableServiceClient.from_connection_string(conn_str=conn_str)
    table_client = table_service_client.get_table_client(table_name=calendario)

    #limpeza dos valores e geração da lista de feriados
    df = pd.DataFrame(table_client.list_entities())
    feriados = list(df["RowKey"])

    return feriados