import logging
from unittest import result
import azure.functions as func
from ExportadoresXML.ExportadorOutput import ExportadorOutput
from ExportadoresXML.DictFromDataframe import DictFromDataframe
from CustomModules.TimeFunctions import next_dc

import json
import pandas as pd
import time

def anbima_series_bonds_deb(dia:str, valores:dict, versionamento="PU_550_v1"):
    try:valores = json.loads(valores)
    except TypeError: pass
    df = pd.DataFrame(valores)

    #filtrando as colunas de interesse e renomeando-as
    df = df.iloc[:,[0,2,10]]
    df.columns = ['ticker', 'venc', 'value']

    #manipulando colunas de datas
    df['venc'] = df['venc'].apply(lambda x : time.strftime("%Y%m%d",time.strptime(x,"%d/%m/%Y")))
    df['date'] = dia

    #gerando o codigo da serie, e filtrando as colunas de interesse 
    if versionamento == "PU_550_v1":
        df['codigo']="SERBRAOTC_" + df['ticker'] + '_' + df['venc']
        df['value'] = df['value'].str.replace(",",".")
    df = df[['codigo','value','date']]
    df = df.set_index("codigo")

    #montando o dicionario utilizado para exportar o xml
    result = df.to_dict(orient="index")

    return result


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    versionamento = req.params.get('versionamento')
    valores = req.params.get('valores')
    dia = req.params.get('dia')
    if not versionamento or not valores or not dia:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            versionamento = req_body.get('versionamento')
            valores = req_body.get('valores')
            dia = req_body.get('dia')
        
    try:
        # preparando o upload do arquivo
        valores = anbima_series_bonds_deb(dia, valores)

        result = ExportadorOutput(
                            container_name="anbima",
                            filename='Bonds',
                            versionamento=versionamento,
                            dia=dia
                            ).ExportadorSeries(valores)
        return json.dumps({"Resultado":result})
    except Exception as e:
        return json.dumps({"error":str(e)})