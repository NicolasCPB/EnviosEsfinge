import requests
import json
import simplejson

with open('config.json', 'r') as file:
    config_data = json.load(file)
urlBase = config_data['urlBase']
headers = config_data['headers']

def finaliza():
    try:
        url = urlBase + '/tributario/finalizarEnvio'

        with open("finalizaJson.json", "r", encoding="utf-8") as arquivo:
            dados = simplejson.load(arquivo)

        response = requests.post(url, headers=headers, json=dados)
        response.raise_for_status()

        resposta = response.json()

        print(resposta)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao finalizar o pacote: {e.response.json()}")

print("Adicione o JSON da finaliza no diretório raiz com o nome finalizaJson.json.")
finaliza()