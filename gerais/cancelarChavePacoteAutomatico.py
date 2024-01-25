import requests
import json

def cancelarChavePacote(chavePacote):
    with open('config.json', 'r') as file:
        config_data = json.load(file)
    headers = config_data['headers']
    urlBase = config_data['urlBase']['QA']
    url = urlBase + '/servicosGerais/cancelarEnvioParcial'
    try:
        params = {
            'chavePacote': chavePacote
        }
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()

        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Erro ao cancelar chavePacote: {e.response.json()}')
        return response.status_code