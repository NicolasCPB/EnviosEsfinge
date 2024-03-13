

import os
import tkinter as tk
from tkinter import filedialog

def rename_files(directory):
    count = 1
    for file in os.listdir(directory):
        old_path = os.path.join(directory, file)
        new_name = f"{count}.json"
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        count += 1

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        rename_files(directory)
        status_label.config(text="Arquivos renomeados com sucesso!")

# Configuração da janela
root = tk.Tk()
root.title("Renomear JSON")
root.geometry("300x150")

# Descrição
instruction_label = tk.Label(root, text="Para renomear selecione a pasta")
instruction_label.pack(pady=5)

# Botão de seleção de diretório
select_button = tk.Button(root, text="Selecionar", command=select_directory)
select_button.pack(pady=10)

# Rótulo de status
status_label = tk.Label(root, text="")
status_label.pack(pady=5)

root.mainloop()