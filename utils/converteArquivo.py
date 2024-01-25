import simplejson
import os
from decimal import Decimal

diretorio_arquivos = 'testes/arquivos/'

def converterTxtToJson(arquivo_txt):
    objetos_json = []

    with open(arquivo_txt, 'r', encoding='utf-8') as arquivo:
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

def serialize_decimal(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Tipo não serializável")
