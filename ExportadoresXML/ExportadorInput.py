from azure.storage.blob import ContainerClient
from azure.core.exceptions import ResourceNotFoundError
from lxml import etree
import io
import time
import os

class ExportadorInput():
    def __init__(self, container_name:str, feeder:str, data:str):
        self.container_name = container_name
        self.filename = feeder
        self.data = data

        
    
    def exporta_blob(self, conteudo, filename_extension=".xml"):
        blobname = "_".join([
                    self.data,
                    self.filename
                    ]) + filename_extension
        try: conteudo = conteudo.getvalue()
        except AttributeError: pass

        try:
            name = "/".join([self.filename, blobname])
            #exportando o conteedo gerado para o Blob
            conn_str = os.environ["InputDataLake"]
            blob_block = ContainerClient.from_connection_string(conn_str=conn_str, container_name=self.container_name)
            blob_block.upload_blob(name, conteudo, overwrite=True, encoding='utf-8')
            #verificando se o arquivo foi criado
            blob_block.download_blob(name)
            return "Ok"
        except ResourceNotFoundError as e:
            return str(e)