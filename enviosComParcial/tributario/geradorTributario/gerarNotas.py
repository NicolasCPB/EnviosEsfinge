import json
import tkinter as tk
from tkinter import simpledialog, filedialog
import os
import math

def multiplicar_objeto_json(objeto_json, quantidade):
    objetos_multiplicados = []
    for i in range(1, quantidade + 1):
        novo_objeto = json.loads(json.dumps(objeto_json)) 
        valor_sequencial = 9999 + i - 1
        novo_objeto["numeroNFSe"] = str(valor_sequencial)

        if "modeloNFSe" in novo_objeto:
            novo_objeto["modeloNFSe"] = str(valor_sequencial)

        if "serieNFSe" in novo_objeto:
            novo_objeto["serieNFSe"] = str(valor_sequencial)
        
        for item in novo_objeto["itensNotaFicalServico"]:
            item["sequencial"] = str(valor_sequencial)
        
        objetos_multiplicados.append(novo_objeto)
    return objetos_multiplicados

def salvar_em_arquivos_parciais(lista_objetos, diretorio, registros_por_arquivo):
    total_objetos = len(lista_objetos)
    total_arquivos = math.ceil(total_objetos / registros_por_arquivo)
    arquivos_gerados = []
    for numero_arquivo in range(1, total_arquivos + 1):
        inicio = (numero_arquivo - 1) * registros_por_arquivo
        fim = min(inicio + registros_por_arquivo, total_objetos)
        
        objetos_arquivo = lista_objetos[inicio:fim]
        
        arquivo_parcial = {
            "notasFicaisServico": objetos_arquivo
        }
        
        nome_arquivo = f"{numero_arquivo}.json"
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(arquivo_parcial, f, indent=4, ensure_ascii=False)
        
        arquivos_gerados.append(caminho_arquivo)
        print(f"Arquivo {numero_arquivo}.json gerado com {len(objetos_arquivo)} objetos (registros {inicio+1} a {fim})")
    
    return arquivos_gerados

def selecionar_diretorio():
    root = tk.Tk()
    root.withdraw()
    diretorio = filedialog.askdirectory()
    return diretorio

root = tk.Tk()
root.withdraw()

total_registros = simpledialog.askinteger("Total de Registros", "Informe a quantidade total de registros a serem gerados:")

if total_registros is None or total_registros <= 0:
    print("Operação cancelada ou quantidade de registros inválida.")
    exit()

quantidade_arquivos = simpledialog.askinteger("Quantidade de Arquivos", "Informe a quantidade de arquivos que deseja gerar:")

if quantidade_arquivos is None or quantidade_arquivos <= 0:
    print("Operação cancelada ou quantidade de arquivos inválida.")
    exit()

if quantidade_arquivos > total_registros:
    print("Erro: A quantidade de arquivos não pode ser maior que o total de registros.")
    exit()

registros_por_arquivo = math.ceil(total_registros / quantidade_arquivos)

diretorio = selecionar_diretorio()

if not diretorio:
    print("Nenhum diretório selecionado. Operação cancelada.")
    exit()

print(f"\n=== CONFIGURAÇÃO ===")
print(f"Total de registros: {total_registros}")
print(f"Quantidade de arquivos desejados: {quantidade_arquivos}")
print(f"Registros por arquivo: {registros_por_arquivo}")
print(f"Fórmula: {total_registros} ÷ {quantidade_arquivos} = {registros_por_arquivo}")

confirmacao = input("\nDeseja continuar? (s/n): ").lower().strip()
if confirmacao != 's':
    print("Operação cancelada pelo usuário.")
    exit()

objeto_json_original = {
    "numeroMatriculaContribuinte": "13", #chave
    "numeroNFSe": "{i+1}",
    "modeloNFSe": "1",
    "serieNFSe": "1",
    "dataEmissao": "2025-05-14", #chave
    "outrasInformacoes": "Natureza da operação: Tributada Integralmente (TI)Situação tributária do ISSQN: NormalLocal da prestação do serviço: SERRA ALTA - SCNFS-e emitida de acordo com a Lei 136/2011 de 13 de Outubro de 2011.",
    "codigoMunicipio": "4200754", #chave
    "cnpjTomadorServico": "80622319000198",
    "razaoSocialTomadorServico": "MUNICIPIO DE SERRA ALTA",
    "codigoVerificacao": "9989140225094703040821603182025027392451",
    "urlAcessoNFSe": "https://serraalta.atende.net/autoatendimento/servicos/consulta-de-autenticidade-de-nota-fiscal-eletronica-nfse/detalhar/1/identificador/9989140225094703040821603182025027392451",
    "indicativoOptanteSimples": "N",
    "tipoBeneficioFiscal": "09",
    "itensNotaFicalServico": [
        {
            "sequencial": 1,
            "anoLancamentoCreditoTributario": 2024, #chave
            "codigoLancamentoCreditoTributario": 1401, #chave
            "codigoTributacaoMunicipio": 1402,
            "discriminacao": "SERVIÇO DE MÃO DE OBRA PARA CONSERTO E LIMPEZA DE CARBURADOR DE ROÇADEIRA STIHL FS160",
            "codigoLocalPrestacaoServico": 4218202,
            "tipoExigibilidadeISS": 1,
            "codigoMunicipioIncidenciaISS": 4218202,
            "valorServico": "170.00",
            "quantidadeServico": "1.00",
            "valorDeducoes": "0.00",
            "valorISS": "6.80",
            "aliquota": "4.0000",
            "issRetido": "N",
            "indicativoTomadorResponsavelRetencao": "N"
        }
    ],
    "baseCalculo": "170.00",
    "valorISS": "6.80",
    "valorLiquidoNFSe": "170.00"
}

print(f"\nGerando {total_registros} remessas de notas fiscais...")

objetos_multiplicados = multiplicar_objeto_json(objeto_json_original, total_registros)

print(f"Dividindo em {quantidade_arquivos} arquivos com até {registros_por_arquivo} remessas cada...")

arquivos_gerados = salvar_em_arquivos_parciais(objetos_multiplicados, diretorio, registros_por_arquivo)

print(f"\n=== RESUMO FINAL ===")
print(f"Total de registros gerados: {total_registros}")
print(f"Total de arquivos criados: {len(arquivos_gerados)}")
print(f"Registros por arquivo: {registros_por_arquivo}")
print(f"Diretório: {diretorio}")
print("Arquivos gerados:")
for arquivo in arquivos_gerados:
    print(f"  - {os.path.basename(arquivo)}") 