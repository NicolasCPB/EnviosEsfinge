import json
import os

def generate_objects():

    num_objects = int(input("Digite a quantidade total de objetos que deseja gerar: "))
    
    directory = input("Digite o caminho do diretório onde deseja salvar o arquivo JSON: ")
    os.makedirs(directory, exist_ok=True)
    
    file_name = input("Digite o nome do arquivo (sem a extensão .json): ")
    file_path = os.path.join(directory, f"{file_name}.json")
    
    EncerramentoContaBancaria = []
    for i in range(num_objects):
        data = {
            "codigoAgencia": "34645",
            "codigoBanco": "2345",
            "codigoConta": f"3463{i+1}",
            "codigoIBGECidadeAgenciaBancaria": "45678",
            "digitoVerificadorAgenciaBancaria": 1,
            "digitoVerificadorContaBancaria": 1,
            "dataAtivacaoContaBancaria": "2024-09-01",
            "nomeConta": f"Teste DTI{i+1}",
            "numeroCNPJTitulaContaBancaria": "02839560976",
            "tipoConta": "1"
        }
        
        EncerramentoContaBancaria.append(data)


    final_data = {
        "EncerramentoContaBancaria": EncerramentoContaBancaria,
        "quantidadeContaBancaria": 0,
        "quantidadeEncerramentoContaBancaria": num_objects
        
    }

    with open(file_path, 'w') as f:
        json.dump(final_data, f, indent=4)
    
    print(f"Arquivo {file_path} salvo com sucesso!")

generate_objects()
