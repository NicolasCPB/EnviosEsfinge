import requests
import json
from colorama import Fore, Style, init
import os
import sys
import simplejson
import time

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(diretorio_atual, '..', '..'))

from gerais.cancelarChavePacoteAutomatico import cancelarChavePacote
from utils.converteArquivo import converterTxtToJson
from utils.montaTotalizador import montaTotalizadorRCM

init()

with open('config.json', 'r') as file:
    config_data = json.load(file)

urlBase = config_data['urlBase']['QA']
headers = config_data['headers']

def obterChavePacote():
    anoMes = input("anoMes: ")
    def pegarChave(anoMes):
        try:
            url = urlBase + '/registroscontabeis/municipais/iniciarEnvio'
            params = {
                'anoMes': anoMes
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            retorno = {
                'status': 'Sucesso',
                'chavePacote': response.json()['chavePacote']
            }
            return retorno
        except requests.exceptions.RequestException as e:
            try:
                json_response = e.response.json()
                retorno = {
                    'status': 'Chave aberta',
                    'chavePacote': json_response['objetoErro'][0]
                }
                config_data['chavePacote'] = retorno['chavePacote']
                with open('config.json', 'w') as file:
                    json.dump(config_data, file)
                return retorno
            except json.JSONDecodeError:
                print(Fore.RED + 'Erro ao obter chavePacote: ' + e.response.json())
                Style.RESET_ALL
                return None

    retorno = pegarChave(anoMes)

    if retorno['status'] == 'Chave aberta':
        cancela = cancelarChavePacote(retorno['chavePacote'])
        if (cancela == 200):
            retorno = pegarChave(anoMes)

    return retorno

def enviaMultiplosJsons(quantidadeArquivos):
    count = 1
    while count < int(quantidadeArquivos) + 1:
        nomeArquivo = str(count) + '.json'
        try:
            url = urlBase + '/registroscontabeis/municipais/enviarParcial'

            params = {
                'chavePacote': chavePacote
            }
            try:
                caminho_diretorio = os.path.join("C:", "arquivos",)
                caminho_arquivo = os.path.join(caminho_diretorio, nomeArquivo)
                with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                    dados = simplejson.load(arquivo, use_decimal=True)
            except UnicodeDecodeError as e:
                print(f"Erro de decodificação: {e}")
            except json.JSONDecodeError as e:
                print(f"Erro de decodificação JSON: {e}")
            
            response = requests.post(url, headers=headers, params=params, json=dados)
            response.raise_for_status()

            resposta = response.json()
            resposta['chavePacote'] = chavePacote
            print (Fore.GREEN + f'Envio realizado com sucesso: {resposta}')
            Style.RESET_ALL
            count+=1
        except requests.exceptions.RequestException as e:
            print(f"Erro no json de número {count}")
            print(Fore.RED + f'Erro ao enviar parcial: {e.response.json()}')
            break

def enviarParcial():
    umUnicoArquivo = int(input('Os JSON estão em vários arquivo ou em um único? Digite [1] para 1 único arquivo ou [2] para múltiplos arquivos: '))
    if (umUnicoArquivo == 2):
        print(Fore.YELLOW + 'Lembre-se: Renomeie os jsons de envios de 1 em diante')
        quantidadeArquivos = int(input('Quantidade de arquivos a serem enviados: '))
        Style.RESET_ALL
        enviaMultiplosJsons(quantidadeArquivos)
        return quantidadeArquivos
    #1 único arquivo | 1 JSON por linha
    else:
        print(Fore.YELLOW + 'Lembre-se: Renomeie o arquivo para extensão .txt')
        Style.RESET_ALL
        nomeArquivo = input("Qual o nome do arquivo? ")
        converterTxtToJson(nomeArquivo + ".txt")
        quantidadeArquivos = input("Qual a quantidade de Jsons que foram gerados? ")
        enviaMultiplosJsons(quantidadeArquivos)
        return quantidadeArquivos

        
chavePacote = obterChavePacote()['chavePacote']
quantidadeArquivos = enviarParcial()
if (input("Deseja chamar a finaliza? [1] Sim | [2] Não: ") == "1"):
        try:
            url = urlBase + '/registroscontabeis/municipais/finalizarEnvio'

            montaTotalizadorRCM(quantidadeArquivos)

            with open("finalizaJson.json", "r", encoding="utf-8") as arquivo:
                dados = simplejson.load(arquivo)

            dados['chavePacote'] = chavePacote

            response = requests.post(url, headers=headers, json=dados)
            response.raise_for_status()

            resposta = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao finalizar o pacote: {e.response.json()}")