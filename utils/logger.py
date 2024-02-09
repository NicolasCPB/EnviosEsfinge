import simplejson

def montarLogEnvioRemessa(msg, msgErro):

    if msgErro != "":
        msg += msgErro

    with open("logEnvio.txt", 'a') as logger:
        simplejson.dump(msg, logger, indent=2)
