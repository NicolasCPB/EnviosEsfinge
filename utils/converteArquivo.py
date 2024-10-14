import simplejson
import os
from decimal import Decimal

diretorio_arquivos = 'testes/arquivos/'

#Converte um único arquivo txt em múltiplos JSONs
def converterTxtToJson(arquivo_txt):
    objetos_json = []
    caminho_diretorio = os.path.join("C:", "arquivos")
    caminho_arquivo = os.path.join(caminho_diretorio, arquivo_txt)
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        linhas = arquivo.readlines()
        for linha in linhas:
            linha = linha.strip()

            try:
                objeto_json = simplejson.loads(linha, parse_float=Decimal)
                objetos_json.append(objeto_json)
            except simplejson.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON na linha: {linha}. Erro: {e}")
    for i in range(len(objetos_json)):
        nomeArquivo = str(i + 1) + ".json"

        caminho_diretorio = os.path.join("C:", "arquivos")
        caminho_arquivo = os.path.join(caminho_diretorio, nomeArquivo)
        if not os.path.exists(caminho_diretorio):
            os.makedirs(caminho_diretorio)

        with open(caminho_arquivo, 'w') as json_file:
            simplejson.dump(objetos_json[i], json_file, indent=2, default=serialize_decimal)

#Converte múltiplos txt em múltiplos JSONs
def converter1TxtTo1Json():
    quantidadeTxt = int(input("Quantidade de arquivos txt para converter: "))
    nomeBase = input("Nome base do arquivo para converter: ")
    count = 1
    while count <= quantidadeTxt:
        nomeArquivoTXT = nomeBase + str(count) + ".txt"
        nomeArquivoJSON = str(count) + ".json"
        caminho_diretorio = os.path.join("C:", "arquivos")
        caminho_arquivoTXT = os.path.join(caminho_diretorio, nomeArquivoTXT)
        caminho_arquivoJSON = os.path.join(caminho_diretorio, nomeArquivoJSON)
        if not os.path.exists(caminho_diretorio):
            os.makedirs(caminho_diretorio)
        os.rename(caminho_arquivoTXT, caminho_arquivoJSON)
        count+=1

def serialize_decimal(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Tipo não serializável")

converterTxtToJson('asd.txt')