import requests
import json

def cancelarCodigoRegistro(codigoRegistro):
    with open('config.json', 'r') as file:
        config_data = json.load(file)
    headers = config_data['headers']
    urlBase = config_data['urlBase']
    url = urlBase + '/servicosGerais/cancelarPorCodigoRegistroInformacao'
    try:
        dados = {
            "codigoRegistro": codigoRegistro,
            "justificativa": 'teste'
        }
        response = requests.post(url, headers=headers, json=dados)
        response.raise_for_status()

        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Erro ao cancelar codigoRegistro: {e.response.json()}')
        return response.status_code

codigoRegistro = input('Código de registro: ')
cancelarCodigoRegistro(codigoRegistro)