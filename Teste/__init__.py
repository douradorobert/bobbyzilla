from datetime import datetime
import logging
import os
import pandas as pd
import requests
import re

import azure.functions as func

from CustomModules.TimeFunctions import get_last_busday
from CustomModules.Tables import ConectaTableControle
from ExportadoresXML.ExportadorInput import ExportadorInput
from opencensus.ext.azure.log_exporter import AzureEventHandler

class DownloaderAnbima():
    """Classe destinada a obter os arquivos da Anbima usados na rotina.
    """
    def __init__(self, dia):
        self.dia = dia
        self.dia_formatado = datetime.strptime(dia, "%Y-%m-%d").date().strftime("%y%m%d")

    def get_deb(self):
        """Obtem o conteudo do arquivo de debentures, em formato csv.

        Returns:
            str: string no formato csv do arquivo de debentures, com separador "@".
        """
        url = "".join([
                    "https://www.anbima.com.br/informacoes/merc-sec-debentures/arqs/db",
                    self.dia_formatado,
                    ".txt"
                    ])
                    
        text =  self.__baixa_html(url)
        #limpando o conteudo obito
        rows = re.findall(r'......@.*', text)   #regex para separar o conteudo de interesse
        csv = "\n".join(rows)                   #csv em formato string
        return csv

    def get_ms(self):
        """Obtem o conteudo do arquivo de Mercado Secundario, em formato csv.

        Returns:
            str: string no formato csv do arquivo de debentures, com separador "@".
        """
        url = "".join([
                    "http://www.anbima.com.br/informacoes/merc-sec/arqs/ms",
                    self.dia_formatado,
                    ".txt"
                    ])
                    
        text =  self.__baixa_html(url)
        #limpando o conteudo obito
        rows = re.findall(r'......@.*', text)   #regex para separar o conteudo de interesse
        csv = "\n".join(rows)                   #csv em formato string
        return csv

    def get_ima(self):
        """Obtem o conteudo do arquivo de Indices ANBIMA, em formato xml.

        Returns:
            str: string no formato xml do arquivo de Indices ANBIMA.
        """
        url = "http://www.anbima.com.br/informacoes/ima/arqs/ima_completo.xml"
        text =  self.__baixa_html(url)
        return text
    
    def get_indpreco(self):
        """Obtem o conteudo do arquivo de Indices de Precos ANBIMA, em formato xml.

        Returns:
            str: string no formato xml do arquivo de Indices precos ANBIMA.
        """
        url = "http://www.anbima.com.br/informacoes/indicadores/arqs/indicadores.xls"
        content =  self.__baixa_arquivo(url)
        df = pd.read_excel(content)
        text = bytes(
                df.to_csv(index = False),
                encoding="utf-8"
                )
        return text    

    def get_curvazero(self):
        """Obtem o conteudo do arquivo de Indices de Precos ANBIMA, em formato xml.

        Returns:
            str: string no formato xml do arquivo de Indices precos ANBIMA.
        """
        url = "http://www.anbima.com.br/informacoes/est-termo/CZ-down.asp"
        text =  self.__baixa_arquivo(url)
        return text

    def get_res_550(self):
        """Obtem o conteudo do arquivo de Indices de Precos ANBIMA, em formato xml.

        Returns:
            str: string no formato xml do arquivo de Indices precos ANBIMA.
        """
        url = "".join([
                    "http://www.anbima.com.br/informacoes/res-550/arqs/20",
                    self.dia_formatado,
                    "_550.tex"
                ])
        text =  self.__baixa_arquivo(url)
        return text

    def get_ipcaProj(self):
        """Obtem o conteudo do arquivo de Indices ANBIMA, em formato xml.

        Returns:
            str: string no formato xml do arquivo de Indices ANBIMA.
        """
        url = "http://www.anbima.com.br/pt_br/informar/estatisticas/precos-e-indices/projecao-de-inflacao-gp-m.htm"
        text =  self.__baixa_html(url)
        dfs = pd.read_html(text)

        # tratando as tables separadamente, e entao concatenando-as
        df_projecao_mes = dfs[3]
        df_projecao_mes.columns = ["Mês de Coleta","Data","projvalue","validdate"]
        df_projecao_mes = df_projecao_mes.iloc[1:]

        df_hist = dfs[5]
        df_hist.columns = ["Mês de Coleta","Data","projvalue","validdate","IPCAefetivo"]
        df_hist = df_hist.iloc[1:2]

        ipcaProj = pd.concat([df_projecao_mes,df_hist], join='inner')
        text = bytes(
                ipcaProj.to_csv(index = False),
                encoding="utf-8"
                )
        return text

    def get_igpmProj(self):
        """Obtem o conteudo do arquivo de Indices ANBIMA, em formato xml.

        Returns:
            str: string no formato xml do arquivo de Indices ANBIMA.
        """
        url = "http://www.anbima.com.br/pt_br/informar/estatisticas/precos-e-indices/projecao-de-inflacao-gp-m.htm"
        text =  self.__baixa_html(url)
        dfs = pd.read_html(text)

        # tratando as tables separadamente, e entao concatenando-as
        df_projecao_mes = dfs[3]
        df_projecao_mes.columns = ["Mês de Coleta","Data","projvalue","validdate"]
        df_projecao_mes = df_projecao_mes.iloc[1:]

        df_hist = dfs[5]
        df_hist.columns = ["Mês de Coleta","Data","projvalue","validdate","IPCAefetivo"]
        df_hist = df_hist.iloc[1:2]

        igpmProj = pd.concat([df_projecao_mes,df_hist], join='inner')
        text = bytes(
                igpmProj.to_csv(index = False),
                encoding="utf-8"
                )
        return text

    def __baixa_html(self, url):
        #realizando a requisicao
        r = requests.session()
        request = r.get(url)
        text = request.text                     #texto do html
        return text

    def __baixa_arquivo(self, url):
        request = requests.get(url)
        content =  request.content
        return content


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    #conectando ao AppInsights
    dia = get_last_busday("%Y-%m-%d")
    logger = logging.getLogger(__name__)
    logger.addHandler(AzureEventHandler(
                                connection_string=os.environ["DashboardApplicationInsights"]))
    logger.setLevel(logging.INFO)

    #preparando a chamada dos arquivos
    dia = get_last_busday("%Y-%m-%d")
    downloader = DownloaderAnbima(dia)
    contents = {
                "curvazero":downloader.get_curvazero,
                "deb":downloader.get_deb,
                "igpmProj":downloader.get_igpmProj,
                "ima":downloader.get_ima,
                "indpreco":downloader.get_indpreco,
                "ipcaProj":downloader.get_ipcaProj,
                "ms":downloader.get_ms,
                "res_550":downloader.get_res_550,
                }
    
    table_controller = ConectaTableControle("Anbima")
    #iteracao sobre os arquivos
    for filename in contents.keys():
        #verifica o status do arquivo na table
        entity = table_controller.verifica_entidade(filename, dia)
        
        #verifica se o arquivo já foi salvo no DataLake, e em caso negativo
        #o baixa
        try:
            if entity["Status"] != "done":
                #se o arquivo ainda não foi baixado
                file_content = contents[filename]()    #obtem o arquivo processado

                #preparando arquivo a ser salvo no datalake
                container_name="anbima"

                #exportando o arquivo
                result = ExportadorInput(container_name,
                                         filename,
                                         dia,
                                         ).exporta_blob(file_content, filename_extension='.txt')

                #altera status na table de controle do downloader
                if result == "Ok":
                    entity['Status'] = 'done'
                    table_controller.atualiza_entidade(entity)
                    
                #adicionando informações ao ApplicationInsights
                properties = {
                        'custom_dimensions': {
                                        'filename':filename,
                                        'status': entity['Status'],
                                            }
                            }
                logger.info('downloader_anbima_Bonds', extra=properties)

        except Exception as e: logging.info(e)
    return "OK"