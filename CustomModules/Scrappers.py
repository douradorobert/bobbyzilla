import pandas as pd
import requests
from bs4 import BeautifulSoup
import lxml.etree as etree
from datetime import date
import time
import sys

def get_taxa_referencial(dia, ativo:str):
    """
    Parameters
    ----------
    dia : string
        data de análise, no formato yyyy-mm-dd.
    ativo : string
        Nome do ativo, no formato de leitura, em vez de \"ticket\".
    colunas:list
        Lista contendo os nomes das colunas para a taxa referêncial solicitada
        Obs: Taxas referencias possuem 2 ou 3 colunas: Dias, taxa252 e/ou taxa360.

    Returns
    -------
    df : pandas.DataFrame
        tabela com os dias corridos, e as taxas disponibilizadas para aquele ativo.
    """
    
    dicionario = {
        "Ajuste cupom":"ACC","Alumínio":"ALD","DI x Anbid":"AN","Anbid x pré":"ANP",
        "Ajuste pré":"APR","IBrX-50":"BRP","Cobre":"CBD","Cupom Cambial OC1":"DCO",
        "DI x IPCA":"DIC","DI x IGP-M":"DIM","Cupom limpo":"DOC","DI x dólar":"DOL",
        "Dólar x pré":"DP","DI x euro":"EUC","Real x euro":"EUR","IPCA":"IAP",
        "Ibovespa":"INP","IGP-M":"IPR","Real x iene":"JPY","Libor":"LIB","Níquel":"NID",
        "Chumbo":"PBD","Prob. não default":"PDN","DI x pré":"PRE","Real x dólar":"PTX",
        "Spread Libor Euro x Dólar":"SDE","Selic x pré":"SLP","Estanho":"SND",
        "TBF x pré":"TFP","TR x pré":"TP","DI x TR":"TR","Zinco":"ZND"
        }
    if ativo not in dicionario.keys():
        print("Nome do ativo incorreto")
        sys.exit(-1)
    try:
        data = time.strptime(dia, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Formato de data errado, o correto é yyyy-mm-dd")
        
    data = date(data.tm_year, data.tm_mon, data.tm_mday)
    
    # Carregando dados'
    url = ''.join(
        ["https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-bmf-ptBR.asp?Data=",
         data.strftime("%d/%m/%Y"),
         "&Data1=",
         data.strftime("%d%m%Y"),
         "&slcTaxa=",
         dicionario[ativo]]
                  )
    
    #request table
    r = requests.session()
    request = r.get(url)
    soup = BeautifulSoup(request.text, "html.parser")
    #isolando a table
    table = str(soup.find('table', {'id': 'tb_principal1'}))
    doc = etree.fromstring(table)
    
    num_colunas = int(doc.find('.//th[@colspan]').attrib['colspan']) + 1
    #montando o dataframe com base no html
    lista = list()
    i=1
    row = list()
    for elem in doc.findall('td'):
        row.append(elem.text)
        if i%num_colunas == 0:
            lista.append(row)
            row = list()
        i+=1
    if num_colunas == 2:
        colunas = ['DC','value']
    elif num_colunas == 3:
        colunas = ['DC','rate252','rate360']
        
    df = pd.DataFrame(lista, columns = colunas)     #criando o objeto pandas
    try:
        df[colunas[-1]] = df[colunas[-1]].str.replace(",",".").astype(float)    #alterando o tipo das colunas
        df[colunas[-2]] = df[colunas[-2]].str.replace(",",".").astype(float)
    except KeyError: pass
    return df