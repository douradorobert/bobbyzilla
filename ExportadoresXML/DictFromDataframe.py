class DictFromDataframe():
    def __init__():
        pass

    def curvas(curva:str, dia:str, data_frame):
        """
        Parameters
        ----------
        curva : str
            codigo da curva a ser processado.
        dia : str
            data base de extração dos dados.
        data_frame : pandas.DataFrame
            Index:
                RangeIndex
            Columns:
                Name: maturity, dtype: str. Formato 'yyyy-mm-dd'
                Name: value, dtype: float
    
        Returns
        -------
        dicionario : dict
            dicionario no formato padronizado para o exportador de curvas.
        """
        dicionario = {
                dia:{
                        curva:data_frame.to_dict(orient='records')
                    }
        }
        return dicionario