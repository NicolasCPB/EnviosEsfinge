import json
import os

def generate_objects():
    # Solicita a quantidade total de objetos
    num_objects = int(input("Digite a quantidade total de objetos que deseja gerar: "))
    
    # Define o diretório para salvar os arquivos
    directory = input("Digite o caminho do diretório onde deseja salvar os arquivos JSON: ")
    os.makedirs(directory, exist_ok=True)
    
    # Calcula a quantidade de objetos por arquivo
    objects_per_file = num_objects // 50
    remaining_objects = num_objects % 50

    lancamentosContabeis = []
    for i in range(num_objects):
        data = {
            "anoCriacao": "2022",
            "codigoContaContabil": "1127125001",
            "dataLancamento": "2023-09-01",
            "historicoLancamento": "TESTE DTI",
            "numeroSequencial": "1",
            "numeroSlip": f"{i+1}",
            "tipoLancamento": "2",
            "tipoMovimentoContabil": "2",
            "valorLancamento": "0000000051730.95"
        }
        
        lancamentosContabeis.append(data)
        
        if (i + 1) % objects_per_file == 0 or (i + 1 == num_objects and remaining_objects > 0):
            file_index = (i // objects_per_file) + 1
            file_path = os.path.join(directory, f"{file_index}.json")
            
            if os.path.exists(file_path):
                base, extension = os.path.splitext(file_path)
                j = 1
                while os.path.exists(f"{base}_{j}{extension}"):
                    j += 1
                file_path = f"{base}_{j}{extension}"
            
            with open(file_path, 'w') as f:
                json.dump([{"lancamentosContabeis": lancamentosContabeis}], f, indent=4)
            
            print(f"Arquivo {file_path} salvo com sucesso!")
            
            lancamentosContabeis = []

generate_objects()
