from azure.storage.blob import ContainerClient
from lxml import etree
import io
import time
import os

class ExportadorOutput():
    def __init__(self, container_name:str, filename:str, versionamento:str, dia:str):
        self.container_name = container_name
        self.filename = filename
        self.data = dia
        self.versionamento = versionamento

        
    
    def exporta_xml(self, conteudo, tipo_contrato, filename_extension=".xml"):
        blobname = "_".join([
                    self.data,
                    self.container_name,
                    tipo_contrato,
                    self.filename,
                    self.versionamento
                    ]) + filename_extension
        
        path = "/".join([
                        tipo_contrato,
                        self.filename,
                        self.versionamento
                        ])
        try:
            name = "/".join([path, blobname])
            #exportando o conteedo gerado para o Blob
            conn_str = os.environ["OutputDataLake"]
            blob_block = ContainerClient.from_connection_string(conn_str=conn_str, container_name=self.container_name)
            blob_block.upload_blob(name, conteudo, overwrite=True, encoding='utf-8')
            return "Ok"
        except Exception as e:
            return str(e)
        
    
    # Create the root element
    def ExportadorCurvas(self, valores:dict):
        page = etree.Element('MARKETCURVES')
    
        dates = dict()
        doc = etree.ElementTree(page)
        for data in valores.keys():
            if data not in dates.keys():
                dates[data] = etree.SubElement(page, "CURVAS", data = data, private = 'false')
            for curva in valores[data].keys():
                # dates[date].append(etree.SubElement(page, "SERIES", data = date, private = 'false'))
                for vertice in valores[data][curva]:            
                    etree.SubElement(dates[data], 'CURVA', code=curva, value=str(vertice['value']))
    
        # For multiple multiple attributes, use as shown above
        output = io.StringIO()
        conteudo = etree.tostring(doc, pretty_print=True, doctype= '<?xml version="1.0" encoding="iso-8859-1"?>')
        
        output = self.exporta_xml(conteudo, "Curvas")
        return output
    
    def ExportadorSeries(self, valores:dict):
        """
        Gera a string do XML de series com base nos parametros.
    
        Parameters
        ----------
        valores : dict
        Insumos contendo data, codigo das series e valores
        """
        # Create the root element
        page = etree.Element('MARKETSERIES')
        
        dates = dict()
        #montando o xml
        doc = etree.ElementTree(page)
        for key in valores.keys():
            date = valores[key]['date']
            if date not in dates.keys():
                dates[date] = etree.SubElement(page, "SERIES", data=date, private='false')
            etree.SubElement(dates[date], 'SERIE', code=key, value=str(valores[key]['value']))
    
        # Gerando a string
        output = io.StringIO()
        conteudo = etree.tostring(doc, pretty_print=True, doctype='<?xml version="1.0" encoding="iso-8859-1"?>')
        output = self.exporta_xml(conteudo, "Series")
        return output
