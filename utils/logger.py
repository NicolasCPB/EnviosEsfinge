import simplejson
# -*- coding: utf-8 -*-

def montarLogEnvioRemessa(msg, msgErro):

    if msgErro != "":
        msg += str(msgErro)

    with open("logEnvio.txt", 'a', encoding='utf-8') as logger:
        simplejson.dump(msg, logger, indent=2)
        logger.write("\n")
