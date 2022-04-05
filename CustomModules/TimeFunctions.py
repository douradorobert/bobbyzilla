from datetime import timedelta, date, datetime
from numpy import busday_count

def next_dc(data_inicial:str, quantidade=1, last=False):
    """
    Parameters
    ----------
    data_inicial : string
        DESCRIPTION. Data de referência ao qual se deve contar os dias corridos, no formato yyyy-mm-dd.
    quantidade : int, optional
        DESCRIPTION. The default is 1. Numero de dias em que se deve somar ou subtrair da referencia.
    last : bool, optional
        DESCRIPTION. The default is False. Parametro que define se a funcao ira somar ou subtrair a quantidade de dias.

    Returns
    -------
    string
        DESCRIPTION. Data final calculada no formato yyyy-mm-dd.
    """
    data0 = datetime.strptime(data_inicial, "%Y-%m-%d").date()

    if last:        #dias corridos para tras
        next_dc = data0 - timedelta(days=quantidade)
    else:           #dias corridos para frente
        next_dc = data0 + timedelta(days=quantidade)
    
    return next_dc.strftime("%Y-%m-%d")     #yyyy-mm-dd

def dias_corridos(data_inicial, data_final):
    """
    Parameters
    ----------
    data_inicial : string
        data inicial, no formato yyyy-mm-dd
    data_final : string
        data final, no formato yyyy-mm-dd

    Returns
    -------
    dc : int
        quantidade de dias corridos entre as duas datas.

    """
    data0 = datetime.strptime(data_inicial, "%Y-%m-%d").date()
    data1 = datetime.strptime(data_final, "%Y-%m-%d").date()

    return abs((data1 - data0).days)

def get_last_busday(format="%Y-%m-%d",hora_limite=20, feriados=list()):
    if datetime.today().hour in range(hora_limite,24):
        data = datetime.today()
    else:
        data = datetime.today() - timedelta(days=1)      

    while (data.isoweekday() in [6,7]) or (data.strftime("%Y-%m-%d") in feriados):
        data = data - timedelta(days=1)
    
    data = data.strftime(format)
    return data

def dias_uteis(data_inicial:str, data_final:str, holidays = list()):
    data_final = datetime.strptime(data_final, "%Y-%m-%d").date()
    next_dc = data_final + timedelta(days=1)
    return busday_count(data_inicial, next_dc, holidays=holidays)-1