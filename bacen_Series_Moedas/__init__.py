# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 15:44:50 2022

@author: robert.dourado
"""

import requests
import pandas as pd
import json
import time
import logging
import azure.functions as func
from ExportadoresXML.ExportadorOutput import ExportadorOutput


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    #obtendo parametros
    valores_moedas = req.params.get('valores_moedas')
    if not valores_moedas:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            valores_moedas = req_body.get('valores_moedas')
    
    try:
        cadastro_moedas = cadastro_moedas_marretado()
        classe_bacen = SeriesMoedasBacen(cadastro_moedas,valores_moedas)
        #criando parametros para exportacao do XML
        input_series = {
					"container_name":"bacen",
					"valores":classe_bacen.cadastro_moedas
					}
        #realizando a requisicao

        valores = classe_bacen.cadastro_moedas
        container_name ="bacen"
        versionamento = 'v1'
        filename = 'Moedas'
        dia = '2022-03-13'

        result = ExportadorOutput(container_name, filename, versionamento, dia).ExportadorSeries(valores)	
        return json.dumps({"Resultado":"Ok"})
    except Exception as e:
        return json.dumps({"error":str(e)})

class SeriesMoedasBacen():
    """
    Classe que faz o processamento dos valores das series
    de moedas do banco central, a partir do arquivo de cotações
    disponibilizado pelo Bacen

    Parameters
    ----------
    cadastro_moedas : dict
        Indica a metodologia utilizada para calcular os valores de cada serie
    valores_moedas : dict
        Insumos para os calcular os valores das serie
    """
    def __init__(self, cadastro_moedas, valores_moedas):
        self.set_cadastro_moedas(cadastro_moedas)
        self.set_valores_moedas(valores_moedas)
        self.gen_value()
        
    
    def set_cadastro_moedas(self, cadastro_moedas):
        self.cadastro_moedas = cadastro_moedas    
    
    def set_valores_moedas(self, valores_moedas):
        """
        Faz a limpeza dos valores repassados pelo arquivo de moedas obtido do Bacen
        """
        #criando dataframe
        header = ["data","codigo","tipo","moeda","buyprice", "sellprice", "buypricedollar","sellpricedollar"]	
        try:valores_moedas = json.loads(valores_moedas)
        except:pass
        valores_moedas = pd.DataFrame(valores_moedas)
        valores_moedas.columns = header
        valores_moedas.set_index('moeda', inplace = True)
        valores_moedas.dropna(inplace = True)
        #alterando o tipo das colunas de valores (4 no total)
        for column in header[-4:]:
            valores_moedas.loc[:,column]=valores_moedas.loc[:,column].str.replace(',', '.').astype(float)
        valores_moedas.iloc[:,-4:].astype(float)
        #formatando coluna de datas
        valores_moedas.loc[:,"data"] = valores_moedas.loc[:,"data"].apply(lambda x: time.strftime("%Y-%m-%d",time.strptime(x,"%d/%m/%Y")))

        self.valores_moedas = valores_moedas
        
    def gen_value(self):
        """
        Combinando o dicionário de séries com os valores disponibilizados no arquivo de moedas com base em suas respectivas metodologias
        """
        moedas_sem_cotacao = list()     #caso haja moedas no arquivo sem cotação, séries que utilizam esse valor serão removidos
        for code in self.cadastro_moedas.keys():
            try:          
                #obtendo valor da série
                moeda = self.cadastro_moedas[code]["moeda"]
                campo = self.cadastro_moedas[code]["campo"]
                inverter_valor = self.cadastro_moedas[code]["InverteValor"]
                value = self.valores_moedas.loc[moeda,campo]
                if inverter_valor:
                    value = 1/value
                #adicionando valor ao dicionário
                self.cadastro_moedas[code]["value"] = value     
                # adicionando data formatada
                data = self.valores_moedas.loc[moeda,'data']
                self.cadastro_moedas[code]["date"] = data
            except KeyError as e:
                moedas_sem_cotacao.append(code)
                print(e)
            except Exception as e:
                pass
        #removendo moedas sem valores
        for key in moedas_sem_cotacao:
            self.cadastro_moedas.pop(key, None)

def cadastro_moedas_marretado():
    """
    Mapeamento das series de moedas do Banco Central
    """
    return {
            	"SERABWOTC_AWG/USD": {
            		"moeda": "AWG",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "16398"
            	},
            	"SERANTOTC_ANG/USD": {
            		"moeda": "ANG",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "16566"
            	},
            	"SERAREOTC_AED/USD": {
            		"moeda": "AED",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "16567"
            	},
            	"SERARGOTC_ARS/USD": {
            		"moeda": "ARS",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "16578"
            	},
            	"SERAUSOTC_USD/AUD": {
            		"moeda": "AUD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "16581"
            	},
            	"SERBDIOTC_BIF/USD": {
            		"moeda": "BIF",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "16582"
            	},
            	"SERBGDOTC_BDT/USD": {
            		"moeda": "BDT",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "16584"
            	},
            	"SERBGROTC_BGN/USD": {
            		"moeda": "BGN",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "16585"
            	},
            	"SERBHROTC_BHD/USD": {
            		"moeda": "BHD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "16586"
            	},
            	"SERBLZOTC_BZD/USD": {
            		"moeda": "BZD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "16587"
            	},
            	"SERBOLOTC_BOB/USD": {
            		"moeda": "BOB",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "16588"
            	},
            	"SERBRBOTC_BBD/USD": {
            		"moeda": "BBD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31870"
            	},
            	"SERBRNOTC_BND/USD": {
            		"moeda": "BND",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31871"
            	},
            	"SERBTNOTC_BTN/USD": {
            		"moeda": "BTN",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31872"
            	},
            	"SERBWAOTC_BWP/USD": {
            		"moeda": "BWP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31873"
            	},
            	"SERCANOTC_CAD/USD": {
            		"moeda": "CAD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31877"
            	},
            	"SERCHEOTC_CHF/USD": {
            		"moeda": "CHF",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31881"
            	},
            	"SERCHLOTC_CLP/USD": {
            		"moeda": "CLP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31882"
            	},
            	"SERCHNOTC_CNY/USD": {
            		"moeda": "CNY",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31884"
            	},
            	"SERCOLOTC_COP/USD": {
            		"moeda": "COP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31885"
            	},
            	"SERCYMOTC_KYD/USD": {
            		"moeda": "KYD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31890"
            	},
            	"SERCOMOTC_KMF/USD": {
            		"moeda": "KMF",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31886"
            	},
            	"SERCPVOTC_CVE/USD": {
            		"moeda": "CVE",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31887"
            	},
            	"SERCRIOTC_CRC/USD": {
            		"moeda": "CRC",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31888"
            	},
            	"SERCUBOTC_CUP/USD": {
            		"moeda": "CUP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31889"
            	},
            	"SERCZEOTC_CZK/USD": {
            		"moeda": "CZK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31892"
            	},
            	"SERDJIOTC_DJF/USD": {
            		"moeda": "DJF",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31674"
            	},
            	"SERDNKOTC_DKK/USD": {
            		"moeda": "DKK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31675"
            	},
            	"SERDOMOTC_DOP/USD": {
            		"moeda": "DOP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31676"
            	},
            	"SERDZAOTC_DZD/USD": {
            		"moeda": "DZD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31677"
            	},
            	"SEREGYOTC_EGP/USD": {
            		"moeda": "EGP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31679"
            	},
            	"SERETHOTC_ETB/USD": {
            		"moeda": "ETB",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31682"
            	},
            	"SEREUROTC_USD/EUR": {
            		"moeda": "EUR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31691"
            	},
            	"SERFLKOTC_FKP/USD": {
            		"moeda": "FKP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31692"
            	},
            	"SERGBROTC_USD/GBP": {
            		"moeda": "GBP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31701"
            	},
            	"SERGIBOTC_GIP/USD": {
            		"moeda": "GIP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31703"
            	},
            	"SERGMBOTC_GMD/USD": {
            		"moeda": "GMD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31704"
            	},
            	"SERGTMOTC_GTQ/USD": {
            		"moeda": "GTQ",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31705"
            	},
            	"SERGUYOTC_GYD/USD": {
            		"moeda": "GYD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31706"
            	},
            	"SERHKGOTC_HKD/USD": {
            		"moeda": "HKD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31708"
            	},
            	"SERHNDOTC_HNL/USD": {
            		"moeda": "HNL",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31709"
            	},
            	"SERHRVOTC_HRK/USD": {
            		"moeda": "HRK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31710"
            	},
            	"SERHTIOTC_HTG/USD": {
            		"moeda": "HTG",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31711"
            	},
            	"SERHUNOTC_HUF/USD": {
            		"moeda": "HUF",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31712"
            	},
            	"SERIDNOTC_IDR/USD": {
            		"moeda": "IDR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31713"
            	},
            	"SERINDOTC_INR/USD": {
            		"moeda": "INR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31714"
            	},
            	"SERISLOTC_ISK/USD": {
            		"moeda": "ISK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31715"
            	},
            	"SERISROTC_ILS/USD": {
            		"moeda": "ILS",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31716"
            	},
            	"SERJAMOTC_JMD/USD": {
            		"moeda": "JMD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31732"
            	},
            	"SERJOROTC_JOD/USD": {
            		"moeda": "JOD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31733"
            	},
            	"SERJPNOTC_JPY/USD": {
            		"moeda": "JPY",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31774"
            	},
            	"SERKENOTC_KES/USD": {
            		"moeda": "KES",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31783"
            	},
            	"SERKHMOTC_KHR/USD": {
            		"moeda": "KHR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31784"
            	},
            	"SERKOROTC_KRW/USD": {
            		"moeda": "KRW",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31786"
            	},
            	"SERKWTOTC_KWD/USD": {
            		"moeda": "KWD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31787"
            	},
            	"SERLAOOTC_LAK/USD": {
            		"moeda": "LAK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31788"
            	},
            	"SERLBNOTC_LBP/USD": {
            		"moeda": "LBP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31789"
            	},
            	"SERLBYOTC_LYD/USD": {
            		"moeda": "LYD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31790"
            	},
            	"SERLKAOTC_LKR/USD": {
            		"moeda": "LKR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31791"
            	},
            	"SERLSOOTC_LSL/USD": {
            		"moeda": "LSL",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31792"
            	},
            	"SERMACOTC_MOP/USD": {
            		"moeda": "MOP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31795"
            	},
            	"SERMAROTC_MAD/USD": {
            		"moeda": "MAD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31796"
            	},
            	"SERMDAOTC_MDL/USD": {
            		"moeda": "MDL",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31797"
            	},
            	"SERMEXOTC_MXN/USD": {
            		"moeda": "MXN",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31817"
            	},
            	"SERMOZOTC_MZN/USD": {
            		"moeda": "MZN",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "512151"
            	},
            	"SERMKDOTC_MKD/USD": {
            		"moeda": "MKD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31818"
            	},
            	"SERMMROTC_MMK/USD": {
            		"moeda": "MMK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31820"
            	},
            	"SERMNGOTC_MNT/USD": {
            		"moeda": "MNT",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31821"
            	},
            	"SERMUSOTC_MUR/USD": {
            		"moeda": "MUR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31823"
            	},
            	"SERMWIOTC_MWK/USD": {
            		"moeda": "MWK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31824"
            	},
            	"SERMYSOTC_MYR/USD": {
            		"moeda": "MYR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31825"
            	},
            	"SERNGAOTC_NGN/USD": {
            		"moeda": "NGN",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31826"
            	},
            	"SERNICOTC_NIO/USD": {
            		"moeda": "NIO",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31827"
            	},
            	"SERNOROTC_NOK/USD": {
            		"moeda": "NOK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31828"
            	},
            	"SERNPLOTC_NPR/USD": {
            		"moeda": "NPR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31829"
            	},
            	"SERNZLOTC_USD/NZD": {
            		"moeda": "NZD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31831"
            	},
            	"SEROMNOTC_OMR/USD": {
            		"moeda": "OMR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31832"
            	},
            	"SERPAKOTC_PKR/USD": {
            		"moeda": "PKR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31833"
            	},
            	"SERPANOTC_PAB/USD": {
            		"moeda": "PAB",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31908"
            	},
            	"SERPEROTC_PEN/USD": {
            		"moeda": "PEN",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "31909"
            	},
            	"SERPHLOTC_PHP/USD": {
            		"moeda": "PHP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32231"
            	},
            	"SERPOLOTC_PLN/USD": {
            		"moeda": "PLN",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32233"
            	},
            	"SERPRYOTC_PYG/USD": {
            		"moeda": "PYG",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32235"
            	},
            	"SERQATOTC_QAR/USD": {
            		"moeda": "QAR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32237"
            	},
            	"SERRUSOTC_RUB/USD": {
            		"moeda": "RUB",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32239"
            	},
            	"SERRWAOTC_RWF/USD": {
            		"moeda": "RWF",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32243"
            	},
            	"SERSAUOTC_SAR/USD": {
            		"moeda": "SAR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32244"
            	},
            	"SERSGPOTC_SGD/USD": {
            		"moeda": "SGD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32245"
            	},
            	"SERSHNOTC_SHP/USD": {
            		"moeda": "SHP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32246"
            	},
            	"SERSLBOTC_SBD/USD": {
            		"moeda": "SBD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32247"
            	},
            	"SERSLEOTC_SLL/USD": {
            		"moeda": "SLL",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32248"
            	},
            	"SERSLVOTC_SVC/USD": {
            		"moeda": "SVC",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32249"
            	},
            	"SERSOMOTC_SOS/USD": {
            		"moeda": "SOS",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32250"
            	},
            	"SERSWEOTC_SEK/USD": {
            		"moeda": "SEK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32254"
            	},
            	"SERSWZOTC_SZL/USD": {
            		"moeda": "SZL",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32255"
            	},
            	"SERSYCOTC_SCR/USD": {
            		"moeda": "SCR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32256"
            	},
            	"SERSYROTC_SYP/USD": {
            		"moeda": "SYP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32257"
            	},
            	"SERTHAOTC_THB/USD": {
            		"moeda": "THB",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32258"
            	},
            	"SERTONOTC_TOP/USD": {
            		"moeda": "TOP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32259"
            	},
            	"SERTTOOTC_TTD/USD": {
            		"moeda": "TTD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32260"
            	},
            	"SERTUNOTC_TND/USD": {
            		"moeda": "TND",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32261"
            	},
            	"SERTUROTC_TRY/USD": {
            		"moeda": "TRY",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32263"
            	},
            	"SERTWNOTC_TWD/USD": {
            		"moeda": "TWD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32279"
            	},
            	"SERTZAOTC_TZS/USD": {
            		"moeda": "TZS",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32281"
            	},
            	"SERUGAOTC_UGX/USD": {
            		"moeda": "UGX",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32282"
            	},
            	"SERUKROTC_UAH/USD": {
            		"moeda": "UAH",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32283"
            	},
            	"SERURYOTC_UYU/USD": {
            		"moeda": "UYU",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32284"
            	},
            	"SERUSAOTC_USD/USD": {
            		"moeda": "USD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32443"
            	},
            	"SERVNMOTC_VND/USD": {
            		"moeda": "VND",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32463"
            	},
            	"SERPYFOTC_XPF/USD": {
            		"moeda": "XPF",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32236"
            	},
            	"SERYEMOTC_YER/USD": {
            		"moeda": "YER",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32464"
            	},
            	"SERZAFOTC_ZAR/USD": {
            		"moeda": "ZAR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "32466"
            	},
            	"SEREUROTC_EUR/USD": {
            		"moeda": "EUR",
            		"campo": "sellpricedollar",
            		"InverteValor": True,
            		"IDSerie": "31689"
            	},
            	"SERNZLOTC_NZD/USD": {
            		"moeda": "NZD",
            		"campo": "sellpricedollar",
            		"InverteValor": True,
            		"IDSerie": "31830"
            	},
            	"SERGBROTC_GBP/USD": {
            		"moeda": "GBP",
            		"campo": "sellpricedollar",
            		"InverteValor": True,
            		"IDSerie": "31700"
            	},
            	"SERAUSOTC_AUD/USD": {
            		"moeda": "AUD",
            		"campo": "sellpricedollar",
            		"InverteValor": True,
            		"IDSerie": "16580"
            	},
            	"SERBRAOTC_USD_AED": {
            		"moeda": "AED",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101478"
            	},
            	"SERBRAOTC_USD_ARS": {
            		"moeda": "ARS",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101479"
            	},
            	"SERBRAOTC_USD_BOB": {
            		"moeda": "BOB",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101481"
            	},
            	"SERBRAOTC_USD_CAD": {
            		"moeda": "CAD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101484"
            	},
            	"SERBRAOTC_USD_CHF": {
            		"moeda": "CHF",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101485"
            	},
            	"SERBRAOTC_USD_CLP": {
            		"moeda": "CLP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101486"
            	},
            	"SERBRAOTC_USD_CNY": {
            		"moeda": "CNY",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101487"
            	},
            	"SERBRAOTC_USD_COP": {
            		"moeda": "COP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101488"
            	},
            	"SERBRAOTC_USD_CUP": {
            		"moeda": "CUP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101489"
            	},
            	"SERBRAOTC_USD_CZK": {
            		"moeda": "CZK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101490"
            	},
            	"SERBRAOTC_USD_DKK": {
            		"moeda": "DKK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101491"
            	},
            	"SERBRAOTC_USD_DOP": {
            		"moeda": "DOP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101492"
            	},
            	"SERBRAOTC_USD_GTQ": {
            		"moeda": "GTQ",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101497"
            	},
            	"SERBRAOTC_USD_HKD": {
            		"moeda": "HKD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101498"
            	},
            	"SERBRAOTC_USD_HUF": {
            		"moeda": "HUF",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101499"
            	},
            	"SERBRAOTC_USD_IDR": {
            		"moeda": "IDR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101500"
            	},
            	"SERBRAOTC_USD_ILS": {
            		"moeda": "ILS",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101501"
            	},
            	"SERBRAOTC_USD_INR": {
            		"moeda": "INR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101502"
            	},
            	"SERBRAOTC_USD_JPY": {
            		"moeda": "JPY",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101503"
            	},
            	"SERBRAOTC_USD_KRW": {
            		"moeda": "KRW",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101505"
            	},
            	"SERBRAOTC_USD_MAD": {
            		"moeda": "MAD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101506"
            	},
            	"SERBRAOTC_USD_MXN": {
            		"moeda": "MXN",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101507"
            	},
            	"SERUSAOTC_USD_MXN": {
            		"moeda": "MXN",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "116681"
            	},
            	"SERBRAOTC_USD_MYR": {
            		"moeda": "MYR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101508"
            	},
            	"SERBRAOTC_USD_NOK": {
            		"moeda": "NOK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101509"
            	},
            	"SERBRAOTC_USD_PEN": {
            		"moeda": "PEN",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101511"
            	},
            	"SERBRAOTC_USD_PHP": {
            		"moeda": "PHP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101512"
            	},
            	"SERBRAOTC_USD_PLN": {
            		"moeda": "PLN",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101513"
            	},
            	"SERBRAOTC_USD_PYG": {
            		"moeda": "PYG",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "550425"
            	},
            	"SERBRAOTC_USD_RUB": {
            		"moeda": "RUB",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101514"
            	},
            	"SERBRAOTC_USD_SAR": {
            		"moeda": "SAR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101515"
            	},
            	"SERBRAOTC_USD_SEK": {
            		"moeda": "SEK",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101516"
            	},
            	"SERBRAOTC_USD_SGD": {
            		"moeda": "SGD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101517"
            	},
            	"SERBRAOTC_USD_THB": {
            		"moeda": "THB",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101519"
            	},
            	"SERBRAOTC_USD_TRY": {
            		"moeda": "TRY",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "107492"
            	},
            	"SERBRAOTC_USD_TWD": {
            		"moeda": "TWD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101520"
            	},
            	"SERBRAOTC_USD_UYU": {
            		"moeda": "UYU",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101521"
            	},
            	"SERBRAOTC_USD_VND": {
            		"moeda": "VND",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101522"
            	},
            	"SERBRAOTC_USD_ZAR": {
            		"moeda": "ZAR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101523"
            	},
            	"SERBRAOTC_AUD_USD": {
            		"moeda": "AUD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101480"
            	},
            	"SERBRAOTC_EUR_USD": {
            		"moeda": "EUR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101494"
            	},
            	"SERBRAOTC_GBP_USD": {
            		"moeda": "GBP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101496"
            	},
            	"SERBRAOTC_NZD_USD": {
            		"moeda": "NZD",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "101510"
            	},
            	"SERBRAOTC_USD_AUD": {
            		"moeda": "AUD",
            		"campo": "sellpricedollar",
            		"InverteValor": True,
            		"IDSerie": "116327"
            	},
            	"SERBRAOTC_USD_EUR": {
            		"moeda": "EUR",
            		"campo": "sellpricedollar",
            		"InverteValor": True,
            		"IDSerie": "116329"
            	},
            	"SERBRAOTC_USD_GBP": {
            		"moeda": "GBP",
            		"campo": "sellpricedollar",
            		"InverteValor": True,
            		"IDSerie": "116328"
            	},
            	"SERBRAOTC_USD_NZD": {
            		"moeda": "NZD",
            		"campo": "sellpricedollar",
            		"InverteValor": True,
            		"IDSerie": "116326"
            	},
            	"SERBRAOTC_AUD_BRL": {
            		"moeda": "AUD",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "127986"
            	},
            	"SERBRAOTC_CAD_BRL": {
            		"moeda": "CAD",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "127987"
            	},
            	"SERBRAOTC_CHF_BRL": {
            		"moeda": "CHF",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "127988"
            	},
            	"SERBRAOTC_EUR_BRL": {
            		"moeda": "EUR",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "101495"
            	},
            	"SERBRAOTC_GBP_BRL": {
            		"moeda": "GBP",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "127989"
            	},
            	"SERBRAOTC_JPY_BRL": {
            		"moeda": "JPY",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "127990"
            	},
            	"SERBRAOTC_SEK_BRL": {
            		"moeda": "SEK",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "127978"
            	},
            	"SERBRAOTC_USD_BRL": {
            		"moeda": "USD",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "101482"
            	},
            	"SERBRAOTC_MXN_BRL": {
            		"moeda": "MXN",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "475292"
            	},
            	"SERBRAOTC_COP_BRL": {
            		"moeda": "COP",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1001717"
            	},
            	"SERBRAOTC_ARS_BRL": {
            		"moeda": "ARS",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482814"
            	},
            	"SERBRAOTC_RUB_BRL": {
            		"moeda": "RUB",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1478159"
            	},
            	"SERBRAOTC_TRY_BRL": {
            		"moeda": "TRY",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1471874"
            	},
            	"SERBRAOTC_RON_BRL": {
            		"moeda": "RON",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1478160"
            	},
            	"SERBRAOTC_AED_BRL": {
            		"moeda": "AED",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1478161"
            	},
            	"SERBRAOTC_HKD_BRL": {
            		"moeda": "HKD",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482798"
            	},
            	"SERBRAOTC_AOA_BRL": {
            		"moeda": "AOA",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482799"
            	},
            	"SERBRAOTC_CLP_BRL": {
            		"moeda": "CLP",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482800"
            	},
            	"SERBRAOTC_CNY_BRL": {
            		"moeda": "CNY",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482801"
            	},
            	"SERBRAOTC_EGP_BRL": {
            		"moeda": "EGP",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482802"
            	},
            	"SERBRAOTC_HUF_BRL": {
            		"moeda": "HUF",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482803"
            	},
            	"SERBRAOTC_KRW_BRL": {
            		"moeda": "KRW",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482804"
            	},
            	"SERBRAOTC_KWD_BRL": {
            		"moeda": "KWD",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482805"
            	},
            	"SERBRAOTC_MYR_BRL": {
            		"moeda": "MYR",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482806"
            	},
            	"SERBRAOTC_NGN_BRL": {
            		"moeda": "NGN",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482807"
            	},
            	"SERBRAOTC_OMR_BRL": {
            		"moeda": "OMR",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482808"
            	},
            	"SERBRAOTC_PLN_BRL": {
            		"moeda": "PLN",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482815"
            	},
            	"SERBRAOTC_QAR_BRL": {
            		"moeda": "QAR",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482810"
            	},
            	"SERBRAOTC_SAR_BRL": {
            		"moeda": "SAR",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482811"
            	},
            	"SERBRAOTC_SGD_BRL": {
            		"moeda": "SGD",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482812"
            	},
            	"SERBRAOTC_UYU_BRL": {
            		"moeda": "UYU",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482813"
            	},
            	"SERBRAOTC_VND_BRL": {
            		"moeda": "VND",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "1482816"
            	},
            	"SERBRAOTC_BRL_USD": {
            		"moeda": "USD",
            		"campo": "sellprice",
            		"InverteValor": True,
            		"IDSerie": "101483"
            	},
            	"SERBRAOTC_BRL_JPY": {
            		"moeda": "JPY",
            		"campo": "sellprice",
            		"InverteValor": True,
            		"IDSerie": "101504"
            	},
            	"SERJPNOTC_JPY/BRL": {
            		"moeda": "JPY",
            		"campo": "sellprice",
            		"InverteValor": True,
            		"IDSerie": "550424"
            	},
            	"SERBRAOTC_USD_PTAX": {
            		"moeda": "USD",
            		"campo": "sellprice",
            		"InverteValor": False,
            		"IDSerie": "31860"
            	},
            	"SERBRAOTC_EUR_PTAX": {
            		"moeda": "EUR",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "30970"
            	},
            	"SERBRAOTC_GBP_PTAX": {
            		"moeda": "GBP",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "30985"
            	},
            	"SERBRAOTC_JPY_PTAX": {
            		"moeda": "JPY",
            		"campo": "sellpricedollar",
            		"InverteValor": False,
            		"IDSerie": "30997"
            	}
        }