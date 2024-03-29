import requests
import json
from colorama import Fore, Style, init
import os
import sys
import simplejson
import gc

diretorio_atual = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(diretorio_atual, '..', '..'))

from gerais.cancelarChavePacoteAutomatico import cancelarChavePacote
from utils.converteArquivo import converterTxtToJson
from utils.montaTotalizador import montaTotalizadorTributario
from utils.logger import montarLogEnvioRemessa
from utils.dataUtil import getDataAtualString

init()

with open('config.json', 'r') as file:
    config_data = json.load(file)

urlBase = config_data['urlBase']
headers = config_data['headers']

def verificaSeTodosPacotesSucesso():
    while True:
        try:
            url = urlBase + '/servicosGerais/consultarStatusLotePorChavePacote/' + chavePacote

            response = requests.post(url, headers)
            response.raise_for_status()

            resposta = response.json()

            parar = 0
            for i in range(len(resposta)):
                if resposta[i]['situacao'] == 'PROCESSADO_SUCESSO':
                    parar += 1
                if (parar == len(resposta)):
                    break

        except requests.exceptions.RequestException as e:
            msg = 'Erro ao consultar o status dos lotes.'
            montarLogEnvioRemessa(msg, e.request.json())
            break

def obterChavePacote():
    anoMes = input("anoMes: ")
    def pegarChave(anoMes):
        try:
            url = urlBase + '/tributario/iniciarEnvio'
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
        if(int(input('Já há uma chave de pacote, deseja continuar o envio? [1] Sim | [2] Não: ')) == 2):
            cancela = cancelarChavePacote(retorno['chavePacote'])
            if (cancela == 200):
                retorno = pegarChave(anoMes)
        else:
            return retorno

    return retorno

def enviaMultiplosJsons(quantidadeArquivos):
    count = 1
    print("Enviando...")
    while count < int(quantidadeArquivos) + 1:
        nomeArquivo = str(count) + '.json'
        try:
            url = urlBase + '/tributario/enviarParcialLote'

            params = {
                'chavePacote': chavePacote
            }
            try:
                caminho_diretorio = os.path.join("C:", "arquivos",)
                caminho_arquivo = os.path.join(caminho_diretorio, nomeArquivo)
                with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                    dados = simplejson.load(arquivo)
            except UnicodeDecodeError as e:
                print(f"Erro de decodificação: {e}")
            except json.JSONDecodeError as e:
                print(f"Erro de decodificação JSON: {e}")
            
            response = requests.post(url, headers=headers, params=params, json=dados)
            response.raise_for_status()

            #Limpa os dados da memória
            del dados
            gc.collect()

            numero_lote = response.json()['numeroLote']
            msg = f'Json de número: {count} | chavePacote: {chavePacote} | número lote: {numero_lote} | enviado na data: {getDataAtualString()}'
            montarLogEnvioRemessa(msg, "")
            Style.RESET_ALL
            count+=1
        except requests.exceptions.RequestException as e:
            print("Envio finalizado")
            msg = f'Erro ao enviar parcial de número: {count}'
            montarLogEnvioRemessa(msg, e)
            break
    print("Envio finalizado")
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
        print("Verificando se todos os lotes foram processados. Aguarde, não pare o sistema.")
        verificaSeTodosPacotesSucesso()
        try:
            url = urlBase + '/tributario/finalizarEnvio'

            montaTotalizadorTributario(quantidadeArquivos)

            with open("finalizaJson.json", "r", encoding="utf-8") as arquivo:
                dados = simplejson.load(arquivo)

            dados['chavePacote'] = chavePacote

            response = requests.post(url, headers=headers, json=dados)
            response.raise_for_status()

            resposta = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao finalizar o pacote: {e.response.json()}")