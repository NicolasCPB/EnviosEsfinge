import requests
import json
from colorama import Fore, Style, init
import os
import time
import base64

# Inicialização de Colorama
init()

# Caminhos
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
pasta_arquivos = os.path.join(diretorio_atual, 'arquivos_gerados')
pasta_teste = os.path.join(diretorio_atual, 'teste_de_relatorios')
os.makedirs(pasta_arquivos, exist_ok=True)
os.makedirs(pasta_teste, exist_ok=True)

# Carregar configuração
def carregar_config():
    try:
        with open('config.json', 'r') as file:
            config_data = json.load(file)
        return config_data['urlBase'], config_data['headers']
    except FileNotFoundError:
        print(Fore.RED + "Arquivo 'config.json' não encontrado." + Style.RESET_ALL)
        exit(1)
    except json.JSONDecodeError:
        print(Fore.RED + "Erro ao decodificar o arquivo 'config.json'." + Style.RESET_ALL)
        exit(1)

# Carregar lista de relatórios
def carregar_lista_relatorios():
    caminho_relatorio = os.path.join(pasta_arquivos, 'retorno_relatorio.json')
    with open(caminho_relatorio, 'r') as file:
        lista_relatorios = json.load(file)
        # Ordenar pela chave 'identificadorRelatorio'
        lista_relatorios.sort(key=lambda x: x['identificadorRelatorio'])
    return lista_relatorios

# Obter parâmetros do arquivo existente
def obter_parametros_do_arquivo(idRelatorio):
    arquivo_parametros = os.path.join(pasta_arquivos, f'parametros_relatorio_{idRelatorio}.json')
    with open(arquivo_parametros, 'r') as file:
        parametros = json.load(file)
    return parametros

# Buscar valor existente em arquivos gerados
def buscar_valor_existente(parametroNome):
    for arquivo in os.listdir(pasta_arquivos):
        if arquivo.startswith('parametros_relatorio_') and arquivo.endswith('.json'):
            caminho_arquivo = os.path.join(pasta_arquivos, arquivo)
            with open(caminho_arquivo, 'r') as file:
                parametros = json.load(file)
                for parametro in parametros['parametros']:
                    if parametro['parametroNome'] == parametroNome and parametro['valor']:
                        return parametro['valor']
    return None

# Preencher valores dos parâmetros, solicitar se não houver no arquivo
def preencher_parametros(parametros):
    print(Fore.GREEN + f"\nPreenchendo parâmetros para o relatório {parametros['identificadorRelatorio']}:" + Style.RESET_ALL)
    for parametro in parametros['parametros']:
        if not parametro['valor']:
            # Tentar buscar um valor existente
            valor_existente = buscar_valor_existente(parametro['parametroNome'])
            if valor_existente:
                parametro['valor'] = valor_existente
                print(Fore.YELLOW + f"Usando valor existente para '{parametro['parametroNome']}': {valor_existente}" + Style.RESET_ALL)
            else:
                parametro['valor'] = input(f"Digite o valor para '{parametro['parametroNome']}' (Tipo: {parametro['parametroTipo']}): ")
    return parametros

# Salvar arquivo de log detalhado
def salvar_log(mensagem):
    caminho_log = os.path.join(pasta_teste, 'log_operacoes.txt')
    with open(caminho_log, 'a', encoding='utf-8') as log_file:
        log_file.write(mensagem + '\n')

# Exportar dados do relatório
def exportar_dados(status_resultado, idRelatorio, formato_exportacao):
    if "base64Dados" in status_resultado:
        base64_dados = status_resultado["base64Dados"]
        dados_decodificados = base64.b64decode(base64_dados)
        
        # Exportar para o formato especificado
        if formato_exportacao == 'xlsx':
            caminho_saida = os.path.join(pasta_teste, f'relatorios_{idRelatorio}.xlsx')
            with open(caminho_saida, 'wb') as file:
                file.write(dados_decodificados)
        elif formato_exportacao == 'json':
            caminho_saida = os.path.join(pasta_teste, f'relatorios_{idRelatorio}.json')
            with open(caminho_saida, 'w', encoding='utf-8') as file:
                json.dump(json.loads(dados_decodificados), file, ensure_ascii=False, indent=4)
        print(Fore.GREEN + f"Relatório salvo em '{caminho_saida}'." + Style.RESET_ALL)
        salvar_log(f"Relatório {idRelatorio} exportado com sucesso em {caminho_saida}")
    else:
        print(Fore.RED + "Dados Base64 não encontrados." + Style.RESET_ALL)
        salvar_log(f"Erro ao exportar relatório {idRelatorio}: dados Base64 não encontrados.")

# Executar fluxo completo de cada relatório
def executar():
    urlBase, headers = carregar_config()
    lista_relatorios = carregar_lista_relatorios()
    
    for relatorio in lista_relatorios:
        idRelatorio = relatorio['identificadorRelatorio']
        print(Fore.YELLOW + f"\nProcessando relatório ID {idRelatorio} - {relatorio['nomeRelatorio']}" + Style.RESET_ALL)
        salvar_log(f"Iniciando o relatório {idRelatorio}")
        
        try:
            # Obter e preencher parâmetros
            parametros = obter_parametros_do_arquivo(idRelatorio)
            parametros_preenchidos = preencher_parametros(parametros)
            
            # Enviar solicitação
            response = requests.post(f"{urlBase}/relatorio/gerar", json=parametros_preenchidos, headers=headers)
            response.raise_for_status()
            resultado = response.json()
            idSolicitacao = resultado.get("idSolicitacao")
            salvar_log(f"Solicitação enviada para o relatório {idRelatorio}, ID Solicitação: {idSolicitacao}")
            
            # Verificar status até sucesso
            while True:
                time.sleep(5)
                response_status = requests.get(f"{urlBase}/relatorio/status/{idSolicitacao}", headers=headers)
                response_status.raise_for_status()
                status_resultado = response_status.json()
                
                status = status_resultado.get("status")
                salvar_log(f"Status para relatório {idRelatorio} ({idSolicitacao}): {status}")
                
                if status == "PROCESSADO_SUCESSO":
                    exportar_dados(status_resultado, idRelatorio, parametros_preenchidos['tipoRelatorio'])
                    break
                elif status == "PROCESSADO_ERRO_INTERNO":
                    print(Fore.RED + "Erro interno ao processar o relatório." + Style.RESET_ALL)
                    salvar_log(f"Erro no processamento do relatório {idRelatorio}")
                    break
        except Exception as e:
            print(Fore.RED + f"Erro ao processar o relatório {idRelatorio}: {e}" + Style.RESET_ALL)
            salvar_log(f"Erro ao processar o relatório {idRelatorio}: {str(e)}")

if __name__ == '__main__':
    executar()
