import json
from datetime import datetime
import os

def montarLogEnvioRemessa(msg, msgErro, chave_pacote=None, numero_lote=None, identificador_remessa=None, tipo_retorno="envio"):
    # Cria o diretório de logs se não existir
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Define o nome do arquivo baseado no identificador da remessa
    if identificador_remessa:
        log_file = os.path.join(log_dir, f"{identificador_remessa}.json")
    else:
        # Se não tiver identificador, usa um nome padrão com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"log_sem_identificador_{timestamp}.json")
    
    log_entry = {
        "mensagem": msg,
        "erro": msgErro,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "chave_pacote": chave_pacote,
        "numero_lote": numero_lote,
        "identificador_remessa": identificador_remessa,
        "tipo_retorno": tipo_retorno
    }

    # Se o arquivo não existe, cria com um array vazio
    if not os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    with open(log_file, 'r+', encoding='utf-8') as logger:
        try:
            logs = json.load(logger)
        except json.JSONDecodeError:
            logs = []
        logs.append(log_entry)
        logger.seek(0)
        json.dump(logs, logger, ensure_ascii=False, indent=2)
        logger.truncate()
    