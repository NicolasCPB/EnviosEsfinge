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
            quantidadeAplicacaoFinanceiraPU += len(dados['aplicacoesFinanceiras'])
        except:
            count+=1
            continue

        try:
            quantidadeConciliacaoBancaria += len(dados['conciliacoesBancarias'])
        except:
            count+=1
            continue

        try:
            quantidadeContaBancaria += len(dados['contasBancarias'])
        except:
            count+=1
            continue

        try:
            quantidadeDivida += len(dados['dividas'])
        except:
            count+=1
            continue

        try:
            contador = 0
            while contador < len(dados['dividas']):
                quantidadeDocumentoDivida += len(dados['dividas'][contador]['documentos'])
                contador += 1
        except:
            count+=1
            continue

        try:
            quantidadeLancamentoContabilPU += len(dados['lancamentosContabeis'])
        except:
            count+=1
            continue

        try:
            quantidadeSaldosBancarios += len(dados['saldosBancarios'])
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

def montaTotalizadorTributario(quantidadeArquivos):
    count = 1
    quantidadeBaixaCreditosTributarios = 0
    quantidadeCadastroContribuinte = 0
    quantidadeCadastroImobiliario = 0
    quantidadeCadastroPropriedadeImobiliaria = 0
    quantidadeDiarioGeralArrecadacao = 0
    quantidadeEstornoReceitaDiarioGeralArrecadacao = 0
    quantidadeLancamentoCreditosTributarios = 0
    quantidadeRevisaoValorLancamentoCreditos = 0

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
            quantidadeBaixaCreditosTributarios += len(dados['aplicacoesFinanceiras'])
        except:
            count+=1
            continue

        try:
            quantidadeCadastroContribuinte += len(dados['cadastrosContribuintes'])
        except:
            count+=1
            continue

        try:
            quantidadeCadastroImobiliario += len(dados['cadastrosImobiliarios'])
        except:
            count+=1
            continue

        try:
            quantidadeCadastroPropriedadeImobiliaria += len(dados['cadastrosPropriedadesImobiliarias'])
        except:
            count+=1
            continue

        try:
            quantidadeDiarioGeralArrecadacao += len(dados['diarioGeralArrecadacao'])
        except:
            count+=1
            continue

        try:
            quantidadeEstornoReceitaDiarioGeralArrecadacao += len(dados['estornoReceitasDiarioGeralArrecadacao'])
        except:
            count+=1
            continue

        try:
            quantidadeLancamentoCreditosTributarios += len(dados['lancamentosCreditosTributarios'])
        except:
            count+=1
            continue

        try:
            quantidadeRevisaoValorLancamentoCreditos += len(dados['revisaoValorLancamentosCreditosTributarios'])
        except:
            count+=1
            continue

        count+=1

    finalizaJson = {
        "quantidadeBaixaCreditosTributarios": quantidadeBaixaCreditosTributarios,
        "quantidadeCadastroContribuinte": quantidadeCadastroContribuinte,
        "quantidadeCadastroImobiliario": quantidadeCadastroImobiliario,
        "quantidadeCadastroPropriedadeImobiliaria": quantidadeCadastroPropriedadeImobiliaria,
        "quantidadeDiarioGeralArrecadacao": quantidadeDiarioGeralArrecadacao,
        "quantidadeEstornoReceitaDiarioGeralArrecadacao": quantidadeEstornoReceitaDiarioGeralArrecadacao,
        "quantidadeLancamentoCreditosTributarios": quantidadeLancamentoCreditosTributarios,
        "quantidadeRevisaoValorLancamentoCreditos": quantidadeRevisaoValorLancamentoCreditos
    }

    with open("finalizaJson.json", 'w') as json_file:
        simplejson.dump(finalizaJson, json_file, indent=2)

