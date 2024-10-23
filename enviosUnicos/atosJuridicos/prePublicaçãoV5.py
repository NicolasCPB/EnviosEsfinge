import requests
import json
from colorama import Fore, Style, init
import os
import sys
import simplejson

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(diretorio_atual, '..', '..'))

init()

with open('config.json', 'r') as file:
    config_data = json.load(file)

urlBase = config_data['urlBase']
headers = config_data['headers']

def enviar():
    try:
        nomeArquivo = str(input("Qual o nome do arquivo? ")) + ".json"
        url = urlBase + '/v5/atosjuridicos/prepublicacao/enviar'
        try:
            caminho_diretorio = os.path.join("C:", "arquivos",)
            caminho_arquivo = os.path.join(caminho_diretorio, nomeArquivo)
            with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                dados = simplejson.load(arquivo, use_decimal=True)
        except UnicodeDecodeError as e:
            print(f"Erro de decodificação: {e}")
        except json.JSONDecodeError as e:
            print(f"Erro de decodificação JSON: {e}")
        
        response = requests.post(url, headers=headers, json=dados)
        response.raise_for_status()

        resposta = response.json()
        print (Fore.GREEN + f'Envio realizado com sucesso: {resposta}')
        Style.RESET_ALL
    except requests.exceptions.RequestException as e:
        print(Fore.RED + "Erro ao enviar. Foi criado um arquivo com o Json resposta de retorno.")
        Style.RESET_ALL
        with open("retornoEnvioUnico.json", 'w', encoding="utf-8") as json_file:
            simplejson.dump(e.response.json(), json_file, indent=2)
    

enviar()