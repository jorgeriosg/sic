import requests
import json
from mods.datadog2 import Datadog
from unidecode import unidecode
import mods.config as config

url_api = config.BANCOP_API_URL
authorization = config.BANCOP_API_TOKEN



#create incident caso_asic payload
def create_interaction(body):
    
    valid_params = validate_order_params(body)
    valid_params = body
    response = {}
    
    if valid_params['error']:
        response = valid_params
    else:
        
        if 'caso_asic_detail' in body and 'caso_asic_summary' in body:
            body["caso_asic_detail"] = unidecode(body['caso_asic_detail'])
            body["caso_asic_summary"] = unidecode(body['caso_asic_summary'])
            
        url = url_api + "crearinteraccion.php"
        files=[]
        headers = {'Authorization': authorization}
        
        payload={'ServiceRecipient': body['remedy_login_id'],
                'Urgency': '3',
                'OpenedBy': '1013653276',
                'Description': body['caso_asic_detail'],
                'AffectedService': 'CI1016006',
                'Status': 'Assign',
                'AssignmentGroup': 'MESA DE SERVICIOS',
                'Assignee': '1000179818',
                'Category': 'request for information',
                'Company': 'BANCO POPULAR',
                'CallerDepartment': 'BANCO POPULAR/BANCO POPULAR',
                'CallerLocation': '934',
                'Area': 'CONSULTA',
                'Subarea': 'ASESORIA AL USUARIO',
                'Phase': 'Categorization',
                'Contact': body['remedy_login_id'],
                'Impact': '2',
                'Title':  body['caso_asic_summary'],
                'Source': '1' 
                }
        
        log = Datadog()
        log.send_log("body enviado a banco popular: " + json.dumps(payload))
        response = valid_params
        resp = requests.post(url,headers=headers,data=payload ,files=files)
        
        respons_case= resp.json()
        response['error'] = resp.status_code != 200 or ("alert" in respons_case and respons_case["alert"]== "invalid")
        
        log.send_log("respuesta desde Res: " + resp.text)
        
        if not response['error']:
            print("#####Crearinteraccion banco popular####")
            response['caso_asic'] = respons_case['datos']['CallID']
            print(response['caso_asic'])
        else:
            response['caso_asic'] = False
    return response

#validate parameters create incident
def validate_order_params(body):
    required_params=['ServiceRecipient',
                    'Urgency',
                    'OpenedBy',
                    'Description',
                    'AffectedService',
                    'Status']
    missing_parameters = list(set(required_params) - set(list(body.keys())))
    
    if missing_parameters:
        return { 'error': True, 'caso_asic': False, 'message': f"Faltan los siguientes parámetros: {', '.join(missing_parameters)}" }
    else:
        return { 'error': False }

#query identification user
def query_id_user(body):
    response = {}
    if 'cedula' not in body:
        response['error'] = True
        return  response
    
    url = url_api + "consultarusuario.php"
    headers = { 'Authorization': authorization}
    payload={'ContactName': str(body['cedula'])}
    files=[] 
    resp = requests.post(url,headers=headers,data=payload ,files=files)
    resp_idcard = resp.json()
    
    response['error'] = resp.status_code != 200 or (resp_idcard["alert"] == "invalid" or resp_idcard["error"]== "No se han encontrado (más) registros")  
    
    log = Datadog()
    log.send_log("response object: " + json.dumps(response['error']))
    
    if resp.status_code == 500:
        response['consulta_cedula'] = True
    if not response['error']:
        print("###Obtenerusuario banco popular##")
        response.update(extract_icard_data(resp_idcard['datos']))
        print("#############UPDATE")
        print(response)
    return response

#format response json  query identification user
def extract_icard_data(dict_response):
    try: 
        response = { 
            'nombre_usuario': dict_response['FirstName'] if 'FirstName' in dict_response else '',
            'apellido_usuario': dict_response['LastName'] if 'LastName' in dict_response else '',
            'telefono_usuario': dict_response['WorkPhone'] if 'WorkPhone' in dict_response else '',
            'email_usuario': dict_response['Email'] if 'Email' in dict_response else '',
            'empresa_usuario': dict_response['Company'] if 'Company' in dict_response else '',
            'consulta_cedula': True,
            'remedy_login_id': dict_response['EmployeeID'] if 'EmployeeID' in dict_response else '', 
            'Urgency': dict_response['Urgency'] if 'Urgency' in dict_response else '' 
        }
    except:
        response = { 'consulta_cedula': False }
    return response

#query sd requirement
def query_sd(body):
    
    response = {}
    if 'numero_ticket' not in body:
        response['error'] = True
        return  response
    
    body['numero_ticket'] = "SD" + body['numero_ticket']
    compose_ticket_number = body['numero_ticket']
    url = url_api + "consultarsd.php"
    payload={'CallID': compose_ticket_number}
    files=[]
    headers = {'Authorization': authorization}
    
    resp = requests.post(url,headers=headers,data=payload ,files=files)
    resp_sd = resp.json()
    response['error'] = resp.status_code != 200 or ("alert" in resp_sd and resp_sd["alert"]== "invalid")
    
    if resp.status_code == 500:
        response['consulta_ticket'] = True
        response['error'] = True
    if not response['error']:
        print("###Consultasd banco popular")
        response.update(extract_sd_data(resp_sd['datos']))
        response.update({"numero_ticket": compose_ticket_number })
        print(response)
    return response


#format json query sd
def extract_sd_data(dict_response):
    
    try: 
        response = { 
            'estado_ticket': dict_response['Status'],
            'consulta_ticket': True
        }
    except Exception as _:
        response = {'consulta_ticket': False}
    return response