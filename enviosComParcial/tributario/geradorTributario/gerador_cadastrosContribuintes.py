import json
import tkinter as tk
from tkinter import simpledialog, filedialog
import os
import random

def calcular_digito_verificador(cpf_parcial):
    def calcular_digito(cpf, peso_inicial):
        soma = sum(int(digito) * peso for digito, peso in zip(cpf, range(peso_inicial, 1, -1)))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    cpf_parcial = ''.join(cpf_parcial)
    digito1 = calcular_digito(cpf_parcial, 10)
    digito2 = calcular_digito(cpf_parcial + digito1, 11)
    return cpf_parcial + digito1 + digito2

def gerar_cpf_unico(lista_cpfs):
    while True:
        cpf_parcial = [str(random.randint(0, 9)) for _ in range(9)]
        cpf_completo = calcular_digito_verificador(cpf_parcial)
        if cpf_completo not in lista_cpfs:
            return cpf_completo

def multiplicar_objeto_json(objeto_json, quantidade):
    objetos_multiplicados = []
    cpfs_gerados = set()
    for i in range(1, quantidade + 1):
        novo_objeto = objeto_json.copy()
        novo_objeto["numeroMatriculaContribuinte"] = f"Teste1.{i}"
        novo_objeto["numeroDocumentoContribuinte"] = gerar_cpf_unico(cpfs_gerados)
        cpfs_gerados.add(novo_objeto["numeroDocumentoContribuinte"])
        objetos_multiplicados.append(novo_objeto)
    return objetos_multiplicados

def salvar_em_json(lista_objetos, nome_arquivo):
    with open(nome_arquivo, 'w') as f:
        json.dump({"cadastrosContribuintes": lista_objetos}, f, indent=4)

def selecionar_diretorio():
    root = tk.Tk()
    root.withdraw()
    diretorio = filedialog.askdirectory()
    return diretorio

def obter_nome_arquivo(diretorio, nome_arquivo):
    nome_base, extensao = os.path.splitext(nome_arquivo)
    contador = 1
    while os.path.exists(os.path.join(diretorio, f"{nome_base}_{contador}{extensao}")):
        contador += 1
    return f"{nome_base}_{contador}{extensao}"

# Tela de definição de quantidade de objetos e onde salvar
root = tk.Tk()
root.withdraw()
quantidade = simpledialog.askinteger("Quantidade de Objetos", "Informe a quantidade de objetos a serem gerados:")
diretorio = selecionar_diretorio()

# Objeto Modelo - alterar conforme a necessidade
objeto_json_original = {
    "dataAtualizacaoCadastral": "2024-01-01",
    "indicativoCadastroAtivo": "S",
    "nomeCompletoContribuinte": "OSVALDO CECILIO",
    "numeroDocumentoContribuinte": "",
    "numeroMatriculaContribuinte": "Teste1.1001",
    "numeroMatriculaContribuinteNovo": "",
    "tipoContribuinte": 1
}

objetos_multiplicados = multiplicar_objeto_json(objeto_json_original, quantidade) # Multiplicar o objeto JSON

# Nome do arquivo
nome_arquivo = "cadastrosContribuintes.json"
nome_arquivo = obter_nome_arquivo(diretorio, nome_arquivo)
caminho_arquivo = os.path.join(diretorio, nome_arquivo)

# Salvar os objetos gerados em um arquivo JSON
salvar_em_json(objetos_multiplicados, caminho_arquivo)

print(f"{quantidade} objetos gerados e salvos em '{caminho_arquivo}'")
