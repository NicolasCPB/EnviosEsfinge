import tkinter as tk
from tkinter import filedialog
import json
import os

def generate_objects():
    num_objects = int(entry_num_objects.get())
    initial_value = float(entry_initial_value.get())
    directory = filedialog.askdirectory()
    
    lancamentosCreditosTributarios = []
    for i in range(num_objects):
        data =  {
        "anoLancamentoCreditoTributario": 2024,
        "anoLancamentoCreditoTributarioOriginal": 2024,
        "anoMesCompetencia": 202401,
        "codigoLancamentoCreditoTributario": f"Teste1.{i+1}",
        "codigoLancamentoCreditoTributarioOriginal": "",
        "dataLancamento": "2024-01-01",
        "numeroInscricaoImobiliaria": f"Teste1.{i+1}",
        "numeroMatriculaContribuinte": f"Teste1.{i+1}",
        "tipoCredito": 1,
        "tipoOperacao": 1,
        "valorLancamentoCreditoTributario": 1009.79
      }
        lancamentosCreditosTributarios.append(data)
    
    file_path = os.path.join(directory, "lancamentosCreditosTributarios.json")
    if os.path.exists(file_path):
        base, extension = os.path.splitext(file_path)
        i = 1
        while os.path.exists(f"{base}_{i}{extension}"):
            i += 1
        file_path = f"{base}_{i}{extension}"
    
    with open(file_path, 'w') as f:
        json.dump({"lancamentosCreditosTributarios": lancamentosCreditosTributarios}, f, indent=4)
    
    print("Arquivo salvo com sucesso!")

root = tk.Tk()
root.title("Gerador de Objetos Imobiliários")

label_num_objects = tk.Label(root, text="Quantidade de Objetos:")
label_num_objects.pack()
entry_num_objects = tk.Entry(root)
entry_num_objects.pack()

label_initial_value = tk.Label(root, text="Valor Inicial:")
label_initial_value.pack()
entry_initial_value = tk.Entry(root)
entry_initial_value.pack()

generate_button = tk.Button(root, text="Gerar Objetos", command=generate_objects)
generate_button.pack()

root.mainloop()
