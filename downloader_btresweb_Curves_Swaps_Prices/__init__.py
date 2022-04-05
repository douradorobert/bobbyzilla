import io
import logging
import os
from datetime import datetime, timezone

import logging
import azure.functions as func
from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableServiceClient

from CustomModules.Scrappers import get_taxa_referencial
from CustomModules.TimeFunctions import get_last_busday
from ExportadoresXML.ExportadorInput import ExportadorInput
from opencensus.ext.azure.log_exporter import AzureEventHandler

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.utcnow().replace(
        tzinfo= timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Python timer trigger function ran at %s', utc_timestamp)


    arquivos = [
                'DI x IPCA',
                'DI x IGP-M',
                'Cupom limpo',
                'DI x dólar',
                'DI x euro',
                'Real x euro',
                'Real x iene',
                'DI x pré',
                'Real x dólar',
                'Selic x pré',
                'DI x TR'
                ]
    logger = logging.getLogger(__name__)
    logger.addHandler(AzureEventHandler(
                                connection_string=os.environ["DashboardApplicationInsights"]))
    logger.setLevel(logging.INFO)

    #conectando à table de controle de download das funções
    conn_str = os.environ["InputDataLake"]
    table_service_client = TableServiceClient.from_connection_string(conn_str=conn_str)
    table_client = table_service_client.get_table_client(table_name="B3Web")

    #obtendo o último dia útil
    dia = get_last_busday("%Y-%m-%d")

    for filename in arquivos:
        #verifica o status do arquivo na table
        try:
            entity = table_client.get_entity(filename, dia)
        
        #caso não exista para o dia, o mesmo é criado
        except ResourceNotFoundError:
            entity = {
                'PartitionKey': filename,
                'RowKey' : dia,
                'Timestamp': datetime.today(),
                'Status' : 'pending'
                }
            table_client.create_entity(entity=entity)
            entity = table_client.get_entity(filename, dia)
        
        #verifica se o arquivo já foi salvo no DataLake, e em caso negativo
        #o baixa
        try:
            if entity["Status"] != "done":
                #se o arquivo ainda não foi baixado
                df = get_taxa_referencial(dia, filename)    #scrapper dos dados

                #preparando arquivo a ser salvo no datalake
                file_content = io.StringIO()
                df.to_csv(file_content, index=False)
                file_content = file_content.getvalue()
                container_name="btresweb"

                #exportando o arquivo
                result = ExportadorInput(container_name,
                                         filename,
                                         dia,
                                         ).exporta_blob(file_content, filename_extension='.csv')

                #altera status na table de controle do downloader
                if result == "Ok":
                    entity['Status'] = 'done'
                    table_client.update_entity(entity)
                    
                #adicionando informações ao ApplicationInsights
                properties = {
                        'custom_dimensions': {
                                        'filename':filename,
                                        'status': entity['Status'],
                                            }
                            }
                logger.info('downloader_btresweb_Curves_Swaps_Prices', extra=properties)

        except Exception as e: logging.info(e)
    logging.info("Função executada com sucesso. Verifique na table se todos os arquivos foram baixados.")
    