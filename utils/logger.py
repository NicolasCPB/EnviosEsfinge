import json
from datetime import datetime

def montarLogEnvioRemessa(msg, msgErro):
    log_entry = {
        "mensagem": msg,
        "erro": msgErro,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    with open("logEnvio.json", 'r+', encoding='utf-8') as logger:
        try:
            logs = json.load(logger)
        except json.JSONDecodeError:
            logs = []
        logs.append(log_entry)
        logger.seek(0)
        json.dump(logs, logger, ensure_ascii=False, indent=2)
        logger.truncate()
    