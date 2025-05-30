import requests
import json
from colorama import Fore, Style, init
import os
import sys
import simplejson
import gc
import time
from datetime import datetime, timedelta
import base64

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

identificador_remessa = None
continuando_remessa = False

def extrair_identificador_remessa(chave_pacote):
    try:
        chave_decodificada = base64.b64decode(chave_pacote).decode('utf-8')
        chave_json = json.loads(chave_decodificada)
        return chave_json.get('identificadorINT_RemessaOnLine', '')
    except Exception as e:
        print(Fore.RED + f"Erro ao extrair identificador da remessa: {str(e)}" + Style.RESET_ALL)
        return None

def aguardar_tempo(tempo_minutos):
    tempo_espera = tempo_minutos * 60
    print(Fore.YELLOW + f"\nAguardando {tempo_minutos} minutos antes de tentar novamente...")
    print(f"Início da espera: {datetime.now().strftime('%H:%M:%S')}")
    
    for i in range(tempo_espera, 0, -1):
        minutos = i // 60
        segundos = i % 60
        print(f"\rTempo restante: {minutos:02d}:{segundos:02d}", end="")
        time.sleep(1)
    
    print("\n" + Style.RESET_ALL)
    print(Fore.YELLOW + "Tempo de espera concluído. Tentando novamente..." + Style.RESET_ALL)
    return True  # Retorna True para indicar que o tempo de espera foi concluído

def verificaSeTodosPacotesSucesso():
    print(Fore.YELLOW + "\nIniciando verificação do status dos lotes..." + Style.RESET_ALL)
    tentativas = 0
    max_tentativas = 30  # Limite de tentativas para evitar loop infinito
    
    while tentativas < max_tentativas:
        try:
            url = urlBase + '/servicosGerais/consultarStatusLotePorChavePacote/' + chavePacote
            response = requests.post(url, headers)
            response.raise_for_status()
            resposta = response.json()

            if not resposta:
                print(Fore.YELLOW + "Nenhum lote encontrado para verificação." + Style.RESET_ALL)
                return False
                
            # Contadores para acompanhamento
            total_lotes = len(resposta)
            lotes_processados = 0
            lotes_em_processamento = 0
            lotes_com_erro = 0
            
            # Verifica o status de cada lote
            for lote in resposta:
                status = lote.get('situacao')
                numero_lote = lote.get('numeroLote')
                
                if status == 'PROCESSADO_SUCESSO':
                    lotes_processados += 1
                    print(Fore.GREEN + f"Lote {numero_lote}: Processado com sucesso" + Style.RESET_ALL)
                elif status == 'EM_PROCESSAMENTO':
                    lotes_em_processamento += 1
                    print(Fore.YELLOW + f"Lote {numero_lote}: Em processamento..." + Style.RESET_ALL)
                elif status in ['PROCESSADO_ERRO_INTERNO', 'PROCESSADO_ERRO_NEGOCIO', 'ABORTADO_ERRO_LOTE_ANTERIOR']:
                    lotes_com_erro += 1
                    print(Fore.RED + f"Lote {numero_lote}: Erro - {status}" + Style.RESET_ALL)
                    return False
            
            # Exibe resumo do progresso
            print(Fore.CYAN + f"\nResumo do processamento:" + Style.RESET_ALL)
            print(f"Total de lotes: {total_lotes}")
            print(f"Processados com sucesso: {lotes_processados}")
            print(f"Em processamento: {lotes_em_processamento}")
            print(f"Com erro: {lotes_com_erro}")
            
            # Se todos os lotes foram processados com sucesso
            if lotes_processados == total_lotes:
                print(Fore.GREEN + "\nTodos os lotes foram processados com sucesso!" + Style.RESET_ALL)
                return True
                
            # Se ainda há lotes em processamento, aguarda e tenta novamente
            if lotes_em_processamento > 0:
                print(Fore.YELLOW + "\nAguardando processamento dos lotes restantes..." + Style.RESET_ALL)
                time.sleep(5)  # Aguarda 5 segundos antes de verificar novamente
                tentativas += 1
                continue
                
            # Se chegou aqui e não há lotes em processamento, mas também não foram todos processados
            print(Fore.RED + "\nNem todos os lotes foram processados com sucesso." + Style.RESET_ALL)
            return False

        except requests.exceptions.RequestException as e:
            msg = 'Erro ao consultar o status dos lotes.'
            montarLogEnvioRemessa(msg, str(e), chave_pacote=chavePacote, identificador_remessa=identificador_remessa)
            print(Fore.RED + f"Erro na requisição: {str(e)}" + Style.RESET_ALL)
            return False
            
    print(Fore.RED + f"\nNúmero máximo de tentativas ({max_tentativas}) atingido." + Style.RESET_ALL)
    return False

def obterChavePacote():
    global identificador_remessa, continuando_remessa
    anoMes = input("anoMes: ")
    
    while True:
        try:
            url = urlBase + '/v5/notafiscal/iniciarEnvio'
            params = {
                'anoMes': anoMes
            }
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

            retorno = {
                'status': 'Sucesso',
                'chavePacote': response.json()['chavePacote']
            }
            # Extrai o identificador da remessa da chave do pacote
            identificador_remessa = extrair_identificador_remessa(retorno['chavePacote'])
            if identificador_remessa:
                print(Fore.GREEN + f"Identificador da remessa: {identificador_remessa}" + Style.RESET_ALL)
            continuando_remessa = False  # Reseta a variável ao iniciar nova remessa
            return retorno
        except requests.exceptions.RequestException as e:
            try:
                # Verifica se é um erro de autenticação
                if e.response.status_code in [401, 403]:
                    print(Fore.RED + "\nErro de autenticação. Verifique se suas credenciais estão corretas.")
                    return None
                    
                json_response = e.response.json()
                
                # Verifica se é um erro de remessa em aberto
                if json_response.get('status') == 'BAD_REQUEST' and 'Existe outra remessa em aberto' in json_response.get('mensagem', ''):
                    chave_pacote = json_response.get('objetoErro', [''])[0]
                    if chave_pacote:
                        identificador_remessa = extrair_identificador_remessa(chave_pacote)
                        print(Fore.YELLOW + f"\nExiste uma remessa em aberto com o identificador: {identificador_remessa}")
                        print("Você pode:")
                        print("1. Cancelar a remessa existente e iniciar uma nova")
                        print("2. Continuar com a remessa existente")
                        print("3. Sair do programa")
                        
                        opcao = input("\nEscolha uma opção [1/2/3]: ")
                        
                        if opcao == '1':
                            cancela = cancelarChavePacote(chave_pacote)
                            if cancela == 200:
                                continuando_remessa = False
                                continue  # Continua o loop para tentar novamente
                            return None
                        elif opcao == '2':
                            # Extrai o identificador da remessa da chave do pacote
                            identificador_remessa = extrair_identificador_remessa(chave_pacote)
                            if identificador_remessa:
                                print(Fore.GREEN + f"Identificador da remessa: {identificador_remessa}" + Style.RESET_ALL)
                            continuando_remessa = True  # Marca que estamos continuando uma remessa existente
                            return {
                                'status': 'Chave aberta',
                                'chavePacote': chave_pacote
                            }
                        else:
                            sys.exit(1)
                
                # Verifica se é um erro de negócio
                elif 'erros' in json_response and len(json_response['erros']) > 0:
                    erro = json_response['erros'][0]
                    mensagem_erro = erro.get('mensagem', 'Erro desconhecido')
                    codigo_erro = erro.get('idCodigoErro')
                    
                    print(Fore.RED + f'Erro: {mensagem_erro}')
                    print(f'Código do erro: {codigo_erro}')
                    Style.RESET_ALL
                    
                    # Se for o erro de cancelamentos não efetivados
                    if codigo_erro == 2025034:
                        print(Fore.YELLOW + "\nEste erro requer um tempo de espera de 5 minutos antes de tentar novamente.")
                        print("Você pode:")
                        print("1. Aguardar 5 minutos e tentar novamente")
                        print("2. Tentar novamente imediatamente")
                        print("3. Sair do programa")
                        
                        opcao = input("\nEscolha uma opção [1/2/3]: ")
                        
                        if opcao == '1':
                            if aguardar_tempo(5):  # Se o tempo de espera foi concluído
                                print(Fore.YELLOW + "Tentando novamente..." + Style.RESET_ALL)
                                continue  # Continua o loop para tentar novamente
                        elif opcao == '2':
                            print(Fore.YELLOW + "\nTentando novamente imediatamente..." + Style.RESET_ALL)
                            continue  # Continua o loop para tentar novamente
                        else:
                            sys.exit(1)
                    
                    return None
                
                else:
                    print(Fore.RED + 'Erro ao obter chavePacote: ' + str(json_response))
                    Style.RESET_ALL
                    return None
                    
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(Fore.RED + f'Erro ao processar resposta: {str(e)}')
                Style.RESET_ALL
                return None

def verificaStatusLote(numero_lote):
    try:
        url = urlBase + '/servicosGerais/consultarStatusLotePorChavePacote/' + chavePacote
        response = requests.post(url, headers)
        response.raise_for_status()
        resposta = response.json()
        
        if not resposta:
            return None
            
        for lote in resposta:
            if lote.get('numeroLote') == numero_lote:
                return lote.get('situacao')
                
        return None
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Erro ao consultar status do lote {numero_lote}: {str(e)}" + Style.RESET_ALL)
        return None

def registrar_log_sucesso(count, chavePacote, numero_lote, resposta, identificador_remessa):
    if identificador_remessa:
        try:
            # Registra o log sem exibir no console
            montarLogEnvioRemessa(f"Arquivo {count}.json enviado com sucesso!", resposta, chave_pacote=chavePacote, numero_lote=numero_lote, identificador_remessa=identificador_remessa)
        except Exception as e:
            print(Fore.RED + f"Erro ao registrar log: {str(e)}" + Style.RESET_ALL)

def registrar_log_erro(count, status_lote, resposta, identificador_remessa):
    if identificador_remessa:
        try:
            # Registra o log sem exibir no console
            montarLogEnvioRemessa(f"Erro ao enviar arquivo {count}.json", resposta, chave_pacote=chavePacote, numero_lote=count, identificador_remessa=identificador_remessa)
        except Exception as e:
            print(Fore.RED + f"Erro ao registrar log: {str(e)}" + Style.RESET_ALL)

def atualizar_identificador_remessa(resposta, chavePacote):
    global identificador_remessa
    if not identificador_remessa:
        if 'identificadorRemessaOnline' in resposta:
            identificador_remessa = resposta['identificadorRemessaOnline']
            print(Fore.GREEN + f"Identificador da remessa: {identificador_remessa}" + Style.RESET_ALL)
        else:
            identificador_remessa = extrair_identificador_remessa(chavePacote)
            if identificador_remessa:
                print(Fore.GREEN + f"Identificador da remessa: {identificador_remessa}" + Style.RESET_ALL)
    return identificador_remessa

def verificar_status_lote(numero_lote, resposta, count, chavePacote, nomeArquivo, identificador_remessa):
    time.sleep(2)
    status_lote = verificaStatusLote(numero_lote)
    
    if status_lote == 'RECEBIDO':
        registrar_log_sucesso(count, chavePacote, numero_lote, resposta, identificador_remessa)
        return True
    else:
        registrar_log_erro(count, status_lote, resposta, identificador_remessa)
        return False

def consultar_status_final():
    print(Fore.YELLOW + "\nConsultando status final dos lotes..." + Style.RESET_ALL)
    try:
        url = urlBase + '/servicosGerais/consultarStatusLotePorChavePacote/' + chavePacote
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        resposta = response.json()
        
        if not resposta:
            print(Fore.YELLOW + "Nenhum lote encontrado para verificação." + Style.RESET_ALL)
            return
            
        # Contadores para acompanhamento
        total_lotes = len(resposta)
        lotes_processados = 0
        lotes_em_processamento = 0
        lotes_com_erro = 0
        
        # Verifica o status de cada lote
        for lote in resposta:
            status = lote.get('situacao')
            numero_lote = lote.get('numeroLote')
            
            if status == 'PROCESSADO_SUCESSO':
                lotes_processados += 1
                print(Fore.GREEN + f"Lote {numero_lote}: Processado com sucesso" + Style.RESET_ALL)
                # Registra o log de sucesso
                montarLogEnvioRemessa(f"Lote {numero_lote} processado com sucesso", lote, chave_pacote=chavePacote, numero_lote=numero_lote, identificador_remessa=identificador_remessa)
            elif status == 'EM_PROCESSAMENTO':
                lotes_em_processamento += 1
                print(Fore.YELLOW + f"Lote {numero_lote}: Em processamento..." + Style.RESET_ALL)
                # Registra o log de processamento
                montarLogEnvioRemessa(f"Lote {numero_lote} em processamento", lote, chave_pacote=chavePacote, numero_lote=numero_lote, identificador_remessa=identificador_remessa)
            elif status in ['PROCESSADO_ERRO_INTERNO', 'PROCESSADO_ERRO_NEGOCIO', 'ABORTADO_ERRO_LOTE_ANTERIOR']:
                lotes_com_erro += 1
                print(Fore.RED + f"Lote {numero_lote}: Erro - {status}" + Style.RESET_ALL)
                # Registra o log de erro
                montarLogEnvioRemessa(f"Lote {numero_lote} com erro: {status}", lote, chave_pacote=chavePacote, numero_lote=numero_lote, identificador_remessa=identificador_remessa)
        
        # Exibe resumo do progresso
        print(Fore.CYAN + f"\nResumo do processamento:" + Style.RESET_ALL)
        print(f"Total de lotes: {total_lotes}")
        print(f"Processados com sucesso: {lotes_processados}")
        print(f"Em processamento: {lotes_em_processamento}")
        print(f"Com erro: {lotes_com_erro}")
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Erro ao consultar status final: {str(e)}"
        print(Fore.RED + error_msg + Style.RESET_ALL)
        # Registra o erro no arquivo de log
        montarLogEnvioRemessa(error_msg, str(e), chave_pacote=chavePacote, identificador_remessa=identificador_remessa)

def enviaMultiplosJsons(quantidadeArquivos, arquivo_inicial=1):
    global identificador_remessa
    count = arquivo_inicial
    print(f"Enviando a partir do arquivo {arquivo_inicial}.json...")
    
    arquivos_enviados = set()
    
    while count < int(quantidadeArquivos) + 1:
        nomeArquivo = str(count) + '.json'
        
        if nomeArquivo in arquivos_enviados:
            print(Fore.YELLOW + f"Arquivo {nomeArquivo} já foi enviado. Pulando..." + Style.RESET_ALL)
            count += 1
            continue
            
        try:
            url = urlBase + '/v5/notafiscal/enviarParcialLote'
            params = {'chavePacote': chavePacote}
            
            caminho_diretorio = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "arquivos")
            caminho_arquivo = os.path.join(caminho_diretorio, nomeArquivo)
            
            if not os.path.exists(caminho_arquivo):
                print(Fore.RED + f"Arquivo {nomeArquivo} não encontrado em {caminho_diretorio}" + Style.RESET_ALL)
                montarLogEnvioRemessa(
                    f"Arquivo {nomeArquivo} não encontrado",
                    f"Caminho: {caminho_arquivo}",
                    chave_pacote=chavePacote,
                    identificador_remessa=identificador_remessa
                )
                count += 1
                continue
                
            try:
                try:
                    # Primeira tentativa com leitura padrão
                    with open(caminho_arquivo, "r") as arquivo:
                        dados = arquivo.read()
                except UnicodeDecodeError as ude:
                    # Se der erro de charmap, tenta outras codificações
                    if 'charmap' in str(ude):
                        print(Fore.YELLOW + f"Tentando codificações alternativas para o arquivo {nomeArquivo}..." + Style.RESET_ALL)
                        for encoding in ['utf-8-sig', 'latin1', 'cp1252', 'iso-8859-1']:
                            try:
                                with open(caminho_arquivo, "r", encoding=encoding) as arquivo:
                                    dados = arquivo.read()
                                print(Fore.GREEN + f"Arquivo {nomeArquivo} lido com sucesso usando codificação {encoding}" + Style.RESET_ALL)
                                break
                            except UnicodeDecodeError:
                                if encoding == 'iso-8859-1':
                                    raise
                                continue
                    else:
                        raise

                # Atualizando os headers com o content-type correto
                headers_envio = headers.copy()
                headers_envio['Content-Type'] = 'application/json'
                
                # Enviando os dados brutos, sem processamento
                response = requests.post(
                    url,
                    headers=headers_envio,
                    params=params,
                    data=dados  # Usando data em vez de json
                )
                
                # Tenta obter a resposta como JSON
                try:
                    resposta = response.json()
                except json.JSONDecodeError:
                    resposta = {"erro": response.text}
                
                # Registra o início do envio com a chave do pacote apenas no primeiro arquivo
                if count == arquivo_inicial and identificador_remessa:
                    montarLogEnvioRemessa(
                        "Iniciar envio",
                        "",
                        chave_pacote=chavePacote,
                        identificador_remessa=identificador_remessa
                    )
                
                # Verifica se houve erro de validação (422)
                if response.status_code == 422:
                    print(Fore.RED + f"Erro de validação no arquivo {nomeArquivo}: " + Style.RESET_ALL)
                    print(response.text)
                    montarLogEnvioRemessa(
                        f"Erro de validação no arquivo {nomeArquivo}",
                        response.text,
                        chave_pacote=chavePacote,
                        numero_lote=count,
                        identificador_remessa=identificador_remessa
                    )
                    break
                
                response.raise_for_status()
                
                # Se chegou aqui, o envio foi bem sucedido
                print(Fore.GREEN + f"Arquivo {nomeArquivo} enviado com sucesso!" + Style.RESET_ALL)
                montarLogEnvioRemessa(
                    f"Arquivo {nomeArquivo} enviado com sucesso",
                    resposta,
                    chave_pacote=chavePacote,
                    numero_lote=count,
                    identificador_remessa=identificador_remessa
                )
                arquivos_enviados.add(nomeArquivo)
                count += 1

            except UnicodeDecodeError as e:
                msg = f"Erro de decodificação no arquivo {nomeArquivo}"
                print(Fore.RED + f"{msg}: {e}" + Style.RESET_ALL)
                montarLogEnvioRemessa(msg, str(e), chave_pacote=chavePacote, identificador_remessa=identificador_remessa)
                count += 1
                continue
            except json.JSONDecodeError as e:
                msg = f"Erro no formato JSON do arquivo {nomeArquivo}"
                print(Fore.RED + f"{msg}: {e}" + Style.RESET_ALL)
                montarLogEnvioRemessa(msg, str(e), chave_pacote=chavePacote, identificador_remessa=identificador_remessa)
                count += 1
                continue
            except requests.exceptions.RequestException as e:
                msg = f"Erro na requisição para o arquivo {nomeArquivo}"
                print(Fore.RED + f"{msg}: {str(e)}" + Style.RESET_ALL)
                montarLogEnvioRemessa(msg, str(e), chave_pacote=chavePacote, identificador_remessa=identificador_remessa)
                break
                
        except Exception as e:
            msg = f"Erro inesperado ao processar arquivo {nomeArquivo}"
            print(Fore.RED + f"{msg}: {str(e)}" + Style.RESET_ALL)
            montarLogEnvioRemessa(msg, str(e), chave_pacote=chavePacote, identificador_remessa=identificador_remessa)
            break
            
    print(Fore.GREEN + "Envio finalizado" + Style.RESET_ALL)
    # Consulta o status final dos lotes
    consultar_status_final()

def enviarParcial():
    global continuando_remessa
    umUnicoArquivo = int(input('Os JSON estão em vários arquivo ou em um único? Digite [1] para 1 único arquivo ou [2] para múltiplos arquivos: '))
    if (umUnicoArquivo == 2):
        print(Fore.YELLOW + 'Lembre-se: Renomeie os jsons de envios de 1 em diante')
        quantidadeArquivos = int(input('Quantidade de arquivos a serem enviados: '))
        Style.RESET_ALL
        
        # Se estiver continuando uma remessa existente, solicita o arquivo inicial
        if continuando_remessa:
            while True:
                try:
                    arquivo_inicial = int(input('A partir de qual arquivo deseja continuar o envio? (ex: 2 para começar do 2.json): '))
                    if arquivo_inicial > quantidadeArquivos:
                        print(Fore.RED + f"Erro: O arquivo inicial ({arquivo_inicial}) não pode ser maior que a quantidade total de arquivos ({quantidadeArquivos})" + Style.RESET_ALL)
                        continue
                    if arquivo_inicial < 1:
                        print(Fore.RED + "Erro: O arquivo inicial deve ser maior que 0" + Style.RESET_ALL)
                        continue
                    break
                except ValueError:
                    print(Fore.RED + "Erro: Por favor, insira um número válido" + Style.RESET_ALL)
            
            print(Fore.YELLOW + f"\nContinuando envio a partir do arquivo {arquivo_inicial}.json..." + Style.RESET_ALL)
            enviaMultiplosJsons(quantidadeArquivos, arquivo_inicial)
        else:
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
    print(Fore.YELLOW + "\nVerificando se todos os lotes foram processados. Aguarde, não pare o sistema." + Style.RESET_ALL)
    if verificaSeTodosPacotesSucesso():
        try:
            url = urlBase + '/v5/notafiscal/finalizarEnvio'
            print(Fore.YELLOW + "\nPreparando finalização do envio..." + Style.RESET_ALL)

            montaTotalizadorTributario(quantidadeArquivos)

            with open("finalizaJson.json", "r", encoding="utf-8") as arquivo:
                dados = simplejson.load(arquivo)

            dados['chavePacote'] = chavePacote

            response = requests.post(url, headers=headers, json=dados)
            response.raise_for_status()

            resposta = response.json()
            print(Fore.GREEN + "\nEnvio finalizado com sucesso!" + Style.RESET_ALL)
        except requests.exceptions.RequestException as e:
            print(Fore.RED + f"\nErro ao finalizar o pacote: {e.response.json()}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "\nNão foi possível finalizar o envio devido a erros no processamento dos lotes." + Style.RESET_ALL) 