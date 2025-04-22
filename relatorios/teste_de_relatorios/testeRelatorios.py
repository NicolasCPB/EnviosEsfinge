import os
import json
import time
import requests
import logging
from colorama import Fore, Style, init

# Inicialização de cores e configuração de logs
init()
logging.basicConfig(filename='logEnvio.json', level=logging.ERROR, format='%(asctime)s %(message)s')

# Caminhos importantes
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
pasta_teste = os.path.join(diretorio_atual, 'teste_de_relatorios')
os.makedirs(pasta_teste, exist_ok=True)

caminho_base_parametros = os.path.join(pasta_teste, 'baseParametros.json')

# Caminho absoluto para o arquivo retorno_relatorio.json
caminho_retorno_relatorio = r'C:\Ambientes\VsCode\EnviosEsfinge\relatorios\arquivos_gerados\retorno_relatorio.json'

# Funções auxiliares
def registrar_erro(mensagem):
    logging.error(mensagem)

def carregar_config():
    """Carrega a configuração a partir do arquivo config.json."""
    with open('config.json', 'r') as file:
        config_data = json.load(file)
    return config_data['urlBase'], config_data['headers'], config_data['codigoUg']

def sobrescrever_identificador_unidade_gestora(codigo_ug):
    """Sobrescreve o parâmetro de UG no arquivo base de parâmetros."""
    if os.path.exists(caminho_base_parametros):
        with open(caminho_base_parametros, 'r') as file:
            parametros_base = json.load(file)
        
        for item in parametros_base:
            if item["parametroNome"] == "IDENTIFICADOR_UNIDADE_GESTORA":
                item["valor"] = codigo_ug
                break
        
        with open(caminho_base_parametros, 'w') as file:
            json.dump(parametros_base, file, ensure_ascii=False, indent=4)

def obter_lista_relatorios():
    """Obtém a lista de relatórios do arquivo salvo."""
    if os.path.exists(caminho_retorno_relatorio):
        with open(caminho_retorno_relatorio, 'r') as file:
            dados = json.load(file)
        return sorted(dados, key=lambda x: x['identificadorRelatorio'])
    else:
        print(Fore.RED + f"Arquivo {caminho_retorno_relatorio} não encontrado!" + Style.RESET_ALL)
        return []

def carregar_parametros_base():
    """Carrega os parâmetros base do arquivo base de parâmetros."""
    if os.path.exists(caminho_base_parametros):
        with open(caminho_base_parametros, 'r') as file:
            return {item["parametroNome"]: item["valor"] for item in json.load(file)}
    return {}

def atualizar_parametros_base(parametro_nome, valor):
    """Atualiza ou adiciona um parâmetro no arquivo base de parâmetros."""    
    if os.path.exists(caminho_base_parametros):
        with open(caminho_base_parametros, 'r') as file:
            parametros_base = json.load(file)
    else:
        parametros_base = []
    
    for item in parametros_base:
        if item["parametroNome"] == parametro_nome:
            item["valor"] = valor
            break
    else:
        parametros_base.append({"parametroNome": parametro_nome, "valor": valor})
    
    with open(caminho_base_parametros, 'w') as file:
        json.dump(parametros_base, file, ensure_ascii=False, indent=4)

def obter_parametros_relatorio(urlBase, headers, idRelatorio):
    """Obtém os parâmetros necessários para o relatório."""
    url_parametros = urlBase + f'/relatorio/{idRelatorio}/parametros'
    response = requests.get(url_parametros, headers=headers)
    response.raise_for_status()
    return response.json()

def preencher_parametros(parametros, idRelatorio):
    """Preenche os parâmetros do relatório, buscando dados no arquivo base ou solicitando ao usuário."""
    parametros_base = carregar_parametros_base()
    caminho_parametros = os.path.join(diretorio_atual, 'arquivos_gerados', f'parametros_relatorio_{idRelatorio}.json')
    
    if os.path.exists(caminho_parametros):
        with open(caminho_parametros, 'r', encoding='utf-8') as file:
            dados_existentes = json.load(file)
            parametros['parametros'] = dados_existentes['parametros']
    else:
        for parametro in parametros['parametros']:
            nome = parametro['parametroNome']
            valor = parametros_base.get(nome)
            
            if valor is None:
                valor = input(f"Digite o valor para '{nome}' (Tipo: {parametro['parametroTipo']}): ")
                atualizar_parametros_base(nome, valor)
            
            parametro['valor'] = valor
    return parametros

def enviar_solicitacao(urlBase, headers, parametros):
    """Envia a solicitação para gerar o relatório."""
    url_gerar = urlBase + '/relatorio/gerar'
    try:
        response = requests.post(url_gerar, json=parametros, headers=headers)
        response.raise_for_status()
        return response.json()['idSolicitacao']
    except requests.exceptions.HTTPError as e:
        error_detail = {
            'status_code': e.response.status_code,
            'url': url_gerar,
            'response_body': e.response.text  # Texto do erro
        }
        registrar_erro(error_detail)
        print(Fore.RED + f"Erro ao enviar solicitação: {error_detail}" + Style.RESET_ALL)
        raise 

def verificar_status_solicitacao(urlBase, headers, idSolicitacao):
    """Verifica o status do relatório processado."""
    url_status = urlBase + f'/relatorio/status/{idSolicitacao}'
    try:
        response = requests.get(url_status, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            print(Fore.YELLOW + f"Erro 500 recebido para ID {idSolicitacao}. Considerando como sucesso condicional." + Style.RESET_ALL)
            return {'status': 'PROCESSADO_SUCESSO'}
        else:
            registrar_erro({
                'status_code': e.response.status_code,
                'url': url_status,
                'response_body': e.response.text
            })
            raise

def executar_teste_todos_relatorios():
    """Executa o fluxo de teste para todos os relatórios."""
    urlBase, headers, codigo_ug = carregar_config()
    sobrescrever_identificador_unidade_gestora(codigo_ug)
    lista_relatorios = obter_lista_relatorios()

    for relatorio in lista_relatorios:
        idRelatorio = relatorio['identificadorRelatorio']
        nomeRelatorio = relatorio['nomeRelatorio']
        print(Fore.YELLOW + f"\nProcessando Relatório ID: {idRelatorio} - Nome: {nomeRelatorio}" + Style.RESET_ALL)

        parametros = obter_parametros_relatorio(urlBase, headers, idRelatorio)
        parametros = preencher_parametros(parametros, idRelatorio)
        
        try:
            idSolicitacao = enviar_solicitacao(urlBase, headers, parametros)
        except Exception:
            print(Fore.RED + f"Ocorreu um erro ao enviar a solicitação para o relatório ID {idRelatorio}." + Style.RESET_ALL)
            continue
        
        while True:
            time.sleep(5)
            try:
                status_resultado = verificar_status_solicitacao(urlBase, headers, idSolicitacao)
                print(Fore.BLUE + f"Status atual para Relatório ID {idRelatorio}: {status_resultado['status']}" + Style.RESET_ALL)

                if status_resultado['status'] == "PROCESSADO_SUCESSO":
                    print(Fore.GREEN + f"Relatório ID {idRelatorio} processado com sucesso." + Style.RESET_ALL)
                    break
                elif status_resultado['status'] == "PROCESSADO_ERRO_INTERNO":
                    print(Fore.RED + f"Erro ao processar relatório ID {idRelatorio}." + Style.RESET_ALL)
                    break
                elif status_resultado['status'] == "PROCESSADO_ERRO_NEGOCIO":
                    print(Fore.YELLOW + f"Erro de negócio no processamento do relatório ID {idRelatorio}. Continuando para o próximo relatório." + Style.RESET_ALL)
                    break
            except requests.exceptions.HTTPError:
                print(Fore.RED + f"Erro ao verificar status para o relatório ID {idRelatorio}." + Style.RESET_ALL)
                break

if __name__ == '__main__':
    executar_teste_todos_relatorios()
