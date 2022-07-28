import json
import requests
import socket
import traceback
import mods.config as config


def registrar_datadog(error='', status_code=500):
    try:
        url = config.DATADOG_URL + config.DATADOG_API_KEY
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            hostname = socket.gethostbyname(socket.gethostname())
        except Exception as e:
            hostname = 'localhost'
        
        body = {
            'message': 'ERROR: '+error,
            'hostname': hostname,
            'ddtags': config.DATADOG_TAGS,
            'service': config.DATADOG_SERVICE,
            'ddsource': config.DATADOG_SOURCE,
            'status_code':status_code,
            'severity': "ERROR"
        }
        requests.post(url, headers=headers, data=json.dumps(body),timeout=10)
    except Exception as e:
        pass

def print_datadog(input='',status_code=500,severity='INFO'):
    try:
        url = config.DATADOG_URL+config.DATADOG_API_KEY
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            hostname = socket.gethostbyname(socket.gethostname())
        except:
            hostname = 'localhost'

        try:
            conversacion = json.loads(input)
            inp = conversacion['input'] if 'input' in conversacion else ''
            output = conversacion['output'] if 'output' in conversacion else ''
            cid = conversacion['cid'] if 'cid' in conversacion else ''
            request = conversacion['request'] if 'request' in conversacion else ''
            body = {
                'input':inp,
                'output':output,
                'cid':cid,
                'request':request,
                'hostname': hostname,
                'ddtags': config.DATADOG_TAGS,
                'service': config.DATADOG_SERVICE,
                'ddsource': config.DATADOG_SOURCE,
                'status_code':status_code,
                'severity': severity
            }
        except:
            body = {
                'message':input,
                'hostname': hostname,
                'ddtags': config.DATADOG_TAGS,
                'service': config.DATADOG_SERVICE,
                'ddsource': config.DATADOG_SOURCE,
                'status_code':status_code,
                'severity': severity
            }
        
        requests.post(url, headers=headers, data=json.dumps(body),timeout=10)
    except Exception as e:
        pass

def registrar_datadog_v2(data='', status_code=500, severity: str = 'ERROR', url_path: str = None):
    try:
        url = config.DATADOG_URL + config.DATADOG_API_KEY
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            hostname = socket.gethostbyname(socket.gethostname())
        except Exception as e:
            hostname = 'localhost'

        body = {
            'message': severity + ': ' + str(data),
            'hostname': hostname,
            'ddtags': config.DATADOG_TAGS,
            'service': config.DATADOG_SERVICE,
            'ddsource': config.DATADOG_SOURCE,
            'status_code': status_code,
            'severity': severity
        }
        if url_path is not None:
            body['http'] = {
                'url_details': {
                    'path': url_path
                }
            }
        requests.post(url, headers=headers, data=json.dumps(body), timeout=10)
    except Exception as e:
        pass