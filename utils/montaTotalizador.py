import simplejson
import os
import json

def montaTotalizadorRCM(quantidadeArquivos):
    count = 1
    quantidadeAplicacaoFinanceiraPU = 0
    quantidadeConciliacaoBancaria = 0
    quantidadeContaBancaria = 0
    quantidadeDivida = 0
    quantidadeDocumentoDivida = 0
    quantidadeLancamentoContabilPU = 0
    quantidadeSaldosBancarios = 0
    while count < int(quantidadeArquivos) + 1:
        nomeArquivo = str(count) + '.json'

        try:
            caminho_diretorio = os.path.join("C:", "arquivos",)
            caminho_arquivo = os.path.join(caminho_diretorio, nomeArquivo)
            with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                dados = simplejson.load(arquivo, use_decimal=True)
        except UnicodeDecodeError as e:
            print(f"Erro de decodificação: {e}")
        except json.JSONDecodeError as e:
            print(f"Erro de decodificação JSON: {e}")

        try:
            quantidadeAplicacaoFinanceiraPU += len(dados[0]['aplicacoesFinanceiras'])
        except:
            count+=1
            continue

        try:
            quantidadeConciliacaoBancaria += len(dados[0]['conciliacoesBancarias'])
        except:
            count+=1
            continue

        try:
            quantidadeContaBancaria += len(dados[0]['contasBancarias'])
        except:
            count+=1
            continue

        try:
            quantidadeDivida += len(dados[0]['dividas'])
        except:
            count+=1
            continue

        try:
            contador = 0
            while contador < len(dados[0]['dividas']):
                quantidadeDocumentoDivida += len(dados[0]['dividas'][contador]['documentos'])
                contador += 1
        except:
            count+=1
            continue

        try:
            quantidadeLancamentoContabilPU += len(dados[0]['lancamentosContabeis'])
        except:
            count+=1
            continue

        try:
            quantidadeSaldosBancarios += len(dados[0]['saldosBancarios'])
        except:
            count+=1
            continue

        count+=1

    finalizaJson = {
        "quantidadeAplicacaoFinanceiraPU": quantidadeAplicacaoFinanceiraPU,
        "quantidadeConciliacaoBancaria": quantidadeConciliacaoBancaria,
        "quantidadeContaBancaria": quantidadeContaBancaria,
        "quantidadeDivida": quantidadeDivida,
        "quantidadeDocumentoDivida": quantidadeDocumentoDivida,
        "quantidadeLancamentoContabilPU": quantidadeLancamentoContabilPU,
        "quantidadeSaldosBancarios": quantidadeSaldosBancarios
    }

    with open("finalizaJson.json", 'w') as json_file:
        simplejson.dump(finalizaJson, json_file, indent=2)