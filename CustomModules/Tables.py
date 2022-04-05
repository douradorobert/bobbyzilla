from datetime import datetime
import os

from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableServiceClient

class ConectaTableControle():
    """Modulo de conexão com as table de controle de download"""
    def __init__(self, table_name):
        self._table_name = table_name
        self.__conecta_table()

    @property
    def table_name(self):
        return self._table_name

    def __conecta_table(self):
        #conectando à table de controle de download das funções
        conn_str = os.environ["InputDataLake"]
        table_service_client = TableServiceClient.from_connection_string(conn_str=conn_str)
        self._table_client = table_service_client.get_table_client(table_name=self.table_name)
        
    def verifica_entidade(self, partition_key, row_key):
        try:
            entity = self._table_client.get_entity(partition_key, row_key)
        #caso não exista para o dia, o mesmo é criado
        except ResourceNotFoundError:
            entity = {
                'PartitionKey': partition_key,
                'RowKey' : row_key,
                'Timestamp': datetime.today(),
                'Status' : 'pending'
                }
            self._table_client.create_entity(entity=entity)
            entity = self._table_client.get_entity(partition_key, row_key)
        
        return entity

    def atualiza_entidade(self, entity):
        self._table_client.update_entity(entity)