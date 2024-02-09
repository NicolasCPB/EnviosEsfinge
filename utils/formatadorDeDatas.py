def formatToDDMMYYYYHHMMSS(data):
    formato_desejado = "%d/%m/%Y %H:%M:%S"
    data_formatada = data.strftime(formato_desejado)

    return data_formatada