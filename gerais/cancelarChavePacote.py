import requests
import json
from colorama import Fore, Style, init

init()

def cancelarChavePacote(chavePacote):
    with open('config.json', 'r') as file:
        config_data = json.load(file)
    headers = config_data['headers']
    urlBase = config_data['urlBase']['LOCAL']
    url = urlBase + '/servicosGerais/cancelarEnvioParcial'
    try:
        params = {
            'chavePacote': chavePacote
        }
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()

        print(Fore.GREEN + "Chave de pacote cancelada com sucesso.")
        Style.RESET_ALL
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f'Erro ao cancelar chavePacote: {e.response.json()}')
        Style.RESET_ALL
        return response.status_code

chavePacote = input('Chave de pacote: ')
cancelarChavePacote(chavePacote)