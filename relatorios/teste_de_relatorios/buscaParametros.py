import os
import json

def buscar_parametros(pasta):
    lista_parametros = set()  # Usar um conjunto para evitar duplicatas
    
    # Percorre todos os arquivos na pasta
    for nome_arquivo in os.listdir(pasta):
        caminho_arquivo = os.path.join(pasta, nome_arquivo)
        
        # Verifica se é um arquivo JSON e se o nome corresponde ao padrão desejado
        if os.path.isfile(caminho_arquivo) and nome_arquivo.startswith('parametros_relatorio_') and nome_arquivo.endswith('.json'):
            with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                try:
                    # Carrega o conteúdo JSON
                    conteudo = json.load(arquivo)
                    
                    # Extrai "parametroNome" e "valor"
                    for parametro in conteudo.get('parametros', []):
                        # Adiciona uma tupla (parametroNome, valor) ao conjunto
                        lista_parametros.add((parametro.get("parametroNome"), parametro.get("valor")))
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON no arquivo {nome_arquivo}: {e}")

    # Converte o conjunto de volta para uma lista de dicionários
    lista_parametros = [{"parametroNome": nome, "valor": valor} for nome, valor in lista_parametros]

    # Salva a lista de parâmetros em um novo arquivo JSON
    if lista_parametros:
        with open('baseParametros2.json', 'w', encoding='utf-8') as arquivo_saida:
            json.dump(lista_parametros, arquivo_saida, ensure_ascii=False, indent=4)
        print("Lista de parâmetros salva em 'baseParametros.json'.")
    else:
        print("Nenhum parâmetro encontrado.")

# Exemplo de uso
pasta = r'C:\Ambientes\VsCode\EnviosEsfinge\relatorios\arquivos_gerados'  # Usando string bruta
buscar_parametros(pasta)
