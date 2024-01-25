import requests
import json
from colorama import Fore, Style, init

init()

with open('config.json', 'r') as file:
    config_data = json.load(file)

def autenticar():
    codigoAcesso = input('Código acesso: ')
    codigoUg = input('Código UG: ')

    url = config_data['urlBase']['QA'] + '/autenticacao/login'
    headers = {
        'codigoAcesso': codigoAcesso,
        'senha': '123456'
    }
    params = {
        'codigoUg': codigoUg,
        'descricaoEmpresaTI': 'teste',
        'descritivoSoftware': 'teste'
    }

    try:
        response = requests.post(url, headers=headers, params=params)
        response.raise_for_status()

        token = response.json()['chave']
        print(Fore.GREEN + "Login realizado com sucesso!")
        return token
    except requests.exceptions.RequestException as e:
        try:
            return print(Fore.RED + f"Erro na requisição: {e.response.json()}")
        except json.JSONDecodeError:
            return print(Fore.RED + f"Erro na requisição: {e}")
            

Style.RESET_ALL
token = autenticar()
config_data['headers']['AUTH_TOKEN'] = token

with open('config.json', 'w') as file:
    json.dump(config_data, file)