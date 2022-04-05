import logging
import azure.functions as func
from ExportadoresXML.ExportadorOutput import ExportadorOutput
from ExportadoresXML.DictFromDataframe import DictFromDataframe
from CustomModules.TimeFunctions import next_dc, dias_uteis
from CustomModules.Feriados import get_feriados

import json
import pandas as pd

def CRVBRABMF_RATE_SWAP_DI1_TR(valores, dia, feriados=list()):
    try:valores = json.loads(valores)
    except TypeError: pass
    df = pd.DataFrame(valores)
    
    #alterando tipos das colunas
    df["DC"] = df["DC"].astype(float).astype(int)
    df["rate252"] = df["rate252"].astype(float)
        
    #geração de da coluna de maturity
    df["maturity"] = df["DC"].apply(lambda x : next_dc(dia, x))

    #contagem de dias úteis e calculo do vértice
    feriados = get_feriados("CalendarioBrazilOTC")
    df["DU"] = df["maturity"].apply(lambda x : dias_uteis(dia, x, holidays=feriados))
    df["value"] =(1+df["rate252"]/100)**(df["DU"]/252)
    
    return df

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        valores = req.params.get('valores')
        dia = req.params.get('dia')
        if not valores or not dia:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                valores = req_body.get('valores')
                dia = req_body.get('dia')
        
        # gerando os vértices
        data_frame = CRVBRABMF_RATE_SWAP_DI1_TR(valores, dia)
        
        # preparando o upload do arquivo
        valores = DictFromDataframe.curvas('CRVBRABMF_RATE_SWAP_DI1_TR', dia, data_frame)
        container_name="btresweb"
        versionamento = 'DI1_TR_v1'
        filename = 'Swaps_Prices'
        result = ExportadorOutput(
                            container_name=container_name,
                            filename=filename,
                            versionamento=versionamento,
                            dia=dia
                            ).ExportadorCurvas(valores)
        return json.dumps({"Resultado":result})
    except Exception as e:
        return json.dumps({"error":str(e)})
            
            