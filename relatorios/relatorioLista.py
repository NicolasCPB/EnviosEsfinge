import requests
import json
from colorama import Fore, Style, init
import os
import sys
import time
import base64

init()

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(diretorio_atual, '..', '..'))

pasta_arquivos = os.path.join(diretorio_atual, 'arquivos_gerados')
os.makedirs(pasta_arquivos, exist_ok=True)

arquivos_gerados = [
    'retorno_relatorio.json',
    'parametros_relatorio_{idRelatorio}.json',
    'retorno_solicitacao.json',
    'status_solicitacao.json',
    'status_solicitacao_novo.json',
    'dados_decodificados.json'
]

def excluir_arquivos_anteriores():
    for arquivo in arquivos_gerados:
        caminho_arquivo = os.path.join(pasta_arquivos, arquivo)
        if os.path.exists(caminho_arquivo):
            os.remove(caminho_arquivo)
            print(Fore.YELLOW + f"Arquivo '{arquivo}' excluído." + Style.RESET_ALL)

def carregar_config():
    try:
        with open('config.json', 'r') as file:
            config_data = json.load(file)
        return config_data['urlBase'], config_data['headers']
    except FileNotFoundError:
        print(Fore.RED + "Arquivo 'config.json' não encontrado." + Style.RESET_ALL)
        sys.exit(1)
    except json.JSONDecodeError:
        print(Fore.RED + "Erro ao decodificar o arquivo 'config.json'." + Style.RESET_ALL)
        sys.exit(1)

def salvar_arquivo(dados, nome_arquivo):
    caminho_arquivo = os.path.join(pasta_arquivos, nome_arquivo)
    with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=4)
    print(Fore.GREEN + f"Arquivo salvo em '{caminho_arquivo}'." + Style.RESET_ALL)
    return caminho_arquivo

def obter_lista_relatorios(urlBase, headers):
    url = urlBase + '/relatorio'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    dados = response.json()
    salvar_arquivo(dados, 'retorno_relatorio.json')
    print(Fore.BLUE + "\nLista de relatórios disponíveis:" + Style.RESET_ALL)
    for relatorio in dados:
        print(f"ID: {relatorio['identificadorRelatorio']} - Nome: {relatorio['nomeRelatorio']}")
    return dados

def obter_parametros_relatorio(urlBase, headers, idRelatorio):
    url_parametros = urlBase + f'/relatorio/{idRelatorio}/parametros'
    response = requests.get(url_parametros, headers=headers)
    response.raise_for_status()
    parametros = response.json()
    salvar_arquivo(parametros, f'parametros_relatorio_{idRelatorio}.json')
    return parametros

def preencher_parametros(parametros):
    tipoRelatorio = input(Fore.YELLOW + "Digite o valor para 'tipoRelatorio' (0 para XLSX, 1 para JSON): " + Style.RESET_ALL)
    formato_exportacao = 'xlsx' if tipoRelatorio == '0' else 'json'
    parametros['tipoRelatorio'] = tipoRelatorio
    
    print(Fore.GREEN + "\nPreencha os valores dos parâmetros do relatório:" + Style.RESET_ALL)
    for parametro in parametros['parametros']:
        parametro_nome = parametro['parametroNome']
        parametro_tipo = parametro['parametroTipo']
        valor = input(f"Digite o valor para '{parametro_nome}' (Tipo: {parametro_tipo}): ")
        parametro['valor'] = valor
    
    salvar_arquivo(parametros, f'parametros_relatorio_{parametros["identificadorRelatorio"]}.json')
    return parametros, formato_exportacao

def enviar_solicitacao(urlBase, headers, parametros):
    url_gerar = urlBase + '/relatorio/gerar'
    response = requests.post(url_gerar, json=parametros, headers=headers)
    response.raise_for_status()
    resultado = response.json()
    salvar_arquivo(resultado, 'retorno_solicitacao.json')
    return resultado['idSolicitacao']

def verificar_status_solicitacao(urlBase, headers, idSolicitacao):
    url_status = urlBase + f'/relatorio/status/{idSolicitacao}'
    try:
        response = requests.get(url_status, headers=headers)
        response.raise_for_status()
        status_resultado = response.json()
        salvar_arquivo(status_resultado, 'status_solicitacao.json')
        return status_resultado
    except requests.exceptions.HTTPError as e:
        print(Fore.RED + f"Erro HTTP: {e.response.status_code}" + Style.RESET_ALL)
        erro_detalhado = {
            "status": "FALHA_NA_REQUISICAO",
            "erro": e.response.text or 'Erro HTTP sem detalhes',
            "codigo_http": e.response.status_code,
            "detalhes": e.response.headers.get('Content-Type', 'Tipo de conteúdo não especificado')
        }
        salvar_erro(erro_detalhado, idSolicitacao)
        return erro_detalhado
    except requests.RequestException as e:
        print(Fore.RED + f"Erro na requisição: {e}" + Style.RESET_ALL)
        erro_detalhado = {
            "status": "FALHA_NA_REQUISICAO",
            "erro": str(e),
            "detalhes": "Detalhe adicional não disponível"
        }
        salvar_erro(erro_detalhado, idSolicitacao)
        return erro_detalhado

def exportar_dados(status_resultado, formato_exportacao, idRelatorio):
    if "base64Dados" in status_resultado:
        base64_dados = status_resultado["base64Dados"]
        dados_decodificados = base64.b64decode(base64_dados)

        if formato_exportacao == 'xlsx':
            arquivo_saida = os.path.join(pasta_arquivos, f'relatorios_{idRelatorio}.xlsx')
            with open(arquivo_saida, 'wb') as f:
                f.write(dados_decodificados)
            print(Fore.GREEN + f"O relatório foi salvo como '{arquivo_saida}'." + Style.RESET_ALL)

        elif formato_exportacao == 'json':
            arquivo_saida = os.path.join(pasta_arquivos, f'relatorios_{idRelatorio}.json')
            with open(arquivo_saida, 'w', encoding='utf-8') as f:
                json.dump(json.loads(dados_decodificados), f, ensure_ascii=False, indent=4)
            print(Fore.GREEN + f"O relatório foi salvo como '{arquivo_saida}'." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Não há dados em Base64 no retorno do processamento." + Style.RESET_ALL)

def salvar_erro(status_resultado, idRelatorio):
    erro_dados = {
        "status": status_resultado.get('status', 'Status desconhecido'),
        "erro": status_resultado.get('erro', 'Erro desconhecido'),
        "codigo_http": status_resultado.get('codigo_http', 'Código HTTP não disponível'),
        "detalhes": status_resultado.get('detalhes', 'Nenhum detalhe adicional fornecido')
    }
    salvar_arquivo(erro_dados, f'erro_relatorio_{idRelatorio}.json')

def enviar():
    excluir_arquivos_anteriores()
    urlBase, headers = carregar_config()
    
    try:
        lista_relatorios = obter_lista_relatorios(urlBase, headers)
        
        idRelatorio = int(input(Fore.YELLOW + "\nDigite o 'identificadorRelatorio' desejado: " + Style.RESET_ALL))
        parametros = obter_parametros_relatorio(urlBase, headers, idRelatorio)
        parametros, formato_exportacao = preencher_parametros(parametros)
        
        idSolicitacao = enviar_solicitacao(urlBase, headers, parametros)
        
        status_resultado = verificar_status_solicitacao(urlBase, headers, idSolicitacao)
        
        if status_resultado['status'] == "RECEBIDO":
            print(Fore.YELLOW + "Status recebido. Realizando segunda consulta..." + Style.RESET_ALL)
            
            while True:
                time.sleep(5)
                status_resultado = verificar_status_solicitacao(urlBase, headers, idSolicitacao)
                print(Fore.BLUE + f"Novo Status: {status_resultado['status']}" + Style.RESET_ALL)

                if status_resultado['status'] == "PROCESSADO_SUCESSO":
                    print(Fore.GREEN + "Relatório processado com sucesso." + Style.RESET_ALL)
                    exportar_dados(status_resultado, formato_exportacao, idRelatorio)
                    break

                elif status_resultado['status'] == "PROCESSADO_ERRO_INTERNO":
                    print(Fore.RED + "Erro interno ao processar o relatório." + Style.RESET_ALL)
                    salvar_erro(status_resultado, idRelatorio)
                    break
    except requests.RequestException as e:
        print(Fore.RED + f"Erro na requisição: {e}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Erro inesperado: {str(e)}" + Style.RESET_ALL)

if __name__ == '__main__':
    enviar()
