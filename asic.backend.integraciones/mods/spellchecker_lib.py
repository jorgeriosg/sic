import mods.config as config
import requests
import json

def spellchecker(texto):
    """
    texto a enviar a revision de gramatica
    :param texto:
    :return:
    """

    data = {'text': texto.encode('utf-8')}
    params = {
        'mkt': 'es-cl',
        'mode': 'proof'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Ocp-Apim-Subscription-Key': config.SPELL_KEY,
    }
    try:
        response = requests.post(config.SPELL_URL, headers=headers, params=params, data=data, timeout=int(config.SPELL_TIMEOUT))

        if response.status_code == 200:
            response = response.json()
            if response.get('flaggedTokens'):
                if 'flaggedTokens' in response:
                    for resp in response['flaggedTokens']:
                        if resp['suggestions'][0]['score'] > 0.5:
                            texto = texto.replace(resp['token'], resp['suggestions'][0]['suggestion'])
    except Exception:
        pass
    return texto