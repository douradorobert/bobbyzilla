import logging

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:

    logging.info("Função executada com sucesso. Verifique na table se todos os arquivos foram baixados.")