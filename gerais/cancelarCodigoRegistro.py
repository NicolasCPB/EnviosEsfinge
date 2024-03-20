import tkinter as tk
from tkinter import filedialog
import requests
import json

def cancelar_codigos_de_registro(codigos):
    with open('config.json', 'r') as file:
        config_data = json.load(file)
    headers = config_data['headers']
    url_base = config_data['urlBase']
    url = url_base + '/servicosGerais/cancelarPorCodigoRegistroInformacao'
    try:
        for codigo in codigos:
            dados = {
                "codigoRegistro": codigo.strip(),
                "justificativa": 'teste'
            }
            response = requests.post(url, headers=headers, json=dados)
            response.raise_for_status()
            print(f'Cancelamento do código de registro {codigo.strip()} realizado com sucesso.')
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Erro ao cancelar código de registro: {e.response.json()}')
        return response.status_code
    
# Para o cancelamento varios envios, salvar todos os codigos em um .txt separados por virgula
#  Exemplo
#  3991F36C46EEBE6230AC6B9E95FA09EFCE2BEA78,
#  5465288227535B20F70C9B1AE56E73AA8A3040EA,
#  E210A140041AD243DE98F003630C94CCED59F191,
#  C13F1C0BD243866257ABF9F544CEAEAF809AB66C

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()  
    file_path = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt")])
    if file_path:
        with open(file_path, 'r') as file:
            codigos = file.read().split(',')
        status_code = cancelar_codigos_de_registro(codigos)
        print(f'Status Code: {status_code}')

if __name__ == "__main__":
    selecionar_arquivo()