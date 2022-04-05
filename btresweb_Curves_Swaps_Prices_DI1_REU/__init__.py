import logging
import azure.functions as func
from ExportadoresXML.ExportadorOutput import ExportadorOutput
from ExportadoresXML.DictFromDataframe import DictFromDataframe
from CustomModules.TimeFunctions import next_dc

import json
import pandas as pd

def CRVBRABMF_RATE_SWAP_DI1_REU(valores, dia, feriados=list()):
    try:valores = json.loads(valores)
    except TypeError: pass
    df = pd.DataFrame(valores)
    
    #alterando tipos das colunas
    df["DC"] = df["DC"].astype(float).astype(int)
    df["value"] = df["value"].astype(float)
    
    #geração de nova coluna e tratamento dos valores
    df["maturity"] = df["DC"].apply(lambda x : next_dc(dia, x))
    df["value"] = 1+(df["value"]/100)*(df["DC"]/360)
    
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
        data_frame = CRVBRABMF_RATE_SWAP_DI1_REU(valores, dia)
        
        # preparando o upload do arquivo
        valores = DictFromDataframe.curvas('CRVBRABMF_RATE_SWAP_DI1_REU', dia, data_frame)
        container_name="btresweb"
        versionamento = 'DI1_REU_v1'
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
            
            