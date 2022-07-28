import requests
import json
from mods.datadog2 import Datadog
from unidecode import unidecode
import mods.config as config
import mods.bd as bd
import datetime

url_api_token = config.SMS_TOKEN_URL
url_api = config.CLARO_API_URL
authorization = config.CLARO_API_TOKEN
url_api_transaction = config.CLARO_ACCESS_TRANSACTION
authorization_transaction = config.CLARO_ACCESS_TRANSACTION_TOKEN

#create new ticket payload
def create_req_order(body):
    valid_params = validate_order_params(body) 
    response = {}
    if valid_params['error']:
        response = valid_params
    else:
        if 'caso_asic_detail' in body and 'caso_asic_summary' in body:
            body["caso_asic_detail"] = unidecode(body['caso_asic_detail'])
            body["caso_asic_summary"] = unidecode(body['caso_asic_summary'])
        
        url = url_api + "crearordentrabajo.php"
        files=[]
        headers = {'Authorization': authorization}
        payload={'Service_Categorization_Tier_1': body['Service_Categorization_Tier_1'],
                'Service_Categorization_Tier_2': body['Service_Categorization_Tier_2'],
                'Service_Categorization_Tier_3': body['Service_Categorization_Tier_3'],
                'Product_Categorization_Tier_1': body['Product_Categorization_Tier_1'],
                'Product_Categorization_Tier_2': body['Product_Categorization_Tier_2'],
                'Product_Categorization_Tier_3': body['Product_Categorization_Tier_3'],
                'Product_Name': body['Product_Name'],
                'Manufacturer': body['Manufacturer'],
                'ReconciliationIdentity': body['ReconciliationIdentity'],
                'NetworkUser': body['NetworkUser'],
                'BusinessService': body['BusinessService'],
                'Details': body['Details']}
        
        log = Datadog()
        log.send_log("body enviado a soap: " + json.dumps(payload))
        log.send_log("parametros del format", [body['Service_Categorization_Tier_1'],body['Service_Categorization_Tier_2'] , body['Service_Categorization_Tier_3'], body['Product_Categorization_Tier_1'],body["Product_Categorization_Tier_2"], body["Product_Categorization_Tier_3"],body["Product_Name"],body["Manufacturer"],body["ReconciliationIdentity"],body["NetworkUser"],body["BusinessService"],body["Details"] ])
        response = valid_params
        resp = requests.post(url,headers=headers,data=payload ,files=files)
        respons_case= resp.json()
        response['error'] = resp.status_code != 200 or ("alert" in respons_case and respons_case["alert"]== "invalid")
        log.send_log("respuesta desde form-data request: " + resp.text)
        if not response['error']:
            print("#####Crearincidente claro####")
            response['caso_asic'] = respons_case['Request_Number']
            print(response)
        else:
            response['caso_asic'] = False
    return response

#create incident caso_asic payload
def create_incident(body):
    valid_params = validate_order_params(body)
    valid_params = body
    if 'crear_transaccion' in body:
        valid_params['error'] = False
    response = {}
    payload_catalog = {'idcatalogo': '44'}
    catalog = query_catalog(payload_catalog)
    
    if valid_params['error']:
        response = valid_params
    else:
        
        if 'caso_asic_detail' in body and 'caso_asic_summary' in body:
            body["caso_asic_detail"] = unidecode(body['caso_asic_detail'])
            body["caso_asic_summary"] = unidecode(body['caso_asic_summary'])
        elif 'caso_asic_detail' in body and 'porQueDeriva' in body:
            body["caso_asic_detail"] = unidecode(body['caso_asic_detail'])
            body["caso_asic_summary"] = unidecode(body['porQueDeriva'])
            
        url = url_api + "crearincidente.php"
        files=[]
        headers = {'Authorization': authorization}
        payload={'Product_Name': 'Usuario de Red',
                'Manufacturer': 'Claro Colombia IT',
                'ReconciliationIdentity': 'OI-7983F42C4CD811E8A082FA163E1077D3',
                'NetworkUser':  body['remedy_login_id'],
                'BusinessService':  body['caso_asic_summary'],
                'Details':  body['caso_asic_detail']}
        payload_update = dict(catalog, **payload)
        print("Payload update create incident")
        print(payload_update)
        log = Datadog()
        log.send_log("body enviado a rest crear incidente: " + json.dumps(payload_update))
        response = valid_params
        resp = requests.post(url,headers=headers,data=payload_update ,files=files)
        respons_case= resp.json()
        response['error'] = resp.status_code != 200 or ("alert" in respons_case and respons_case["alert"]== "invalid")
        log.send_log("respuesta desde Res crear incidente: " + resp.text)
        
        if not response['error']:
            print("#####Crearincidente claro####")
            response['caso_asic'] = respons_case['Request_Number']
            print(response)
        else:
            response['caso_asic'] = False
    return response

#validate parameters create incident
def validate_order_params(body):
    required_params=['Product_Name','Manufacturer','ReconciliationIdentity','NetworkUser','BusinessService','Details']
    missing_parameters = list(set(required_params) - set(list(body.keys())))
    if missing_parameters:
        return { 'error': True, 'caso_asic': False, 'message': f"Faltan los siguientes parámetros: {', '.join(missing_parameters)}" }
    else:
        return { 'error': False }

#query identification user
def query_identification_user(body):
    response = {}
    if 'cedula' not in body:
        response['error'] = True
        return  response
    
    url = url_api + "obtenerusuario.php"
    headers = { 'Authorization': authorization}
    payload={'numerodocumento': {body['cedula']}}
    files=[] 
    resp = requests.post(url,headers=headers,data=payload ,files=files)
    respons_user= resp.json()
    response['error'] = resp.status_code != 200 or ("alert" in respons_user and respons_user["alert"]== "invalid")
    log = Datadog()
    log.send_log("response object: " + json.dumps(response))
    
    if resp.status_code == 500:
        response['consulta_cedula'] = True
    if not response['error']:
        print("###Obtenerusuario claro##")
        response.update(extract_icard_data(resp.json()))
        print(response)
    return response

#format response json  query identification user
def extract_icard_data(dict_response):
    try: 
        response = {'nombre_usuario': dict_response['First_Name'] if 'First_Name' in dict_response else '',
            'apellido_usuario': dict_response['Last_Name'] if 'Last_Name' in dict_response else '',
            'telefono_usuario': dict_response['Phone_Number_Business'] if 'Phone_Number_Business' in dict_response else '',
            'email_usuario': dict_response['Internet_E-mail'] if 'Internet_E-mail' in dict_response else '',
            'empresa_usuario': dict_response['Company'] if 'Company' in dict_response else '',
            'consulta_cedula': True,
            'remedy_login_id': dict_response['Remedy_Login_ID'] if 'Remedy_Login_ID' in dict_response else ''}
    except:
        response = {'consulta_cedula': False }
    return response

#query ticket requirement
def query_req_ticket(body):
    response = {}
    if 'numero_ticket' not in body:
        response['error'] = True
        return  response
    
    body['numero_ticket'] = "REQ" + "000000000000"[len(body['numero_ticket']):] + body['numero_ticket']
    compose_ticket_number = body['numero_ticket']
    url = url_api + "consultarrequerimiento.php"
    payload={'idrequerimiento': compose_ticket_number}
    files=[]
    headers = {'Authorization': authorization}
    resp = requests.post(url,headers=headers,data=payload ,files=files)
    respons_user= resp.json()
    response['error'] = resp.status_code != 200 or ("alert" in respons_user and respons_user["alert"]== "invalid")
        
    if resp.status_code == 500:
        response['consulta_ticket'] = True
        response['error'] = True
    if not response['error']:
        print("###Consultarrequerimiento claro")
        response.update(extract_ticket_data(resp.json()))
        response.update({"numero_ticket": compose_ticket_number })
        print(response)
    return response

#get catalog to use in create incident
def query_catalog(body):
    response = {}
    if 'idcatalogo' not in body:
        response['error'] = True
        print(response)
        return  response
    
    url = url_api + "obtenercatalogoid.php"
    files=[]
    headers = {'Authorization': authorization}
    resp = requests.post(url,headers=headers,data=body ,files=files)
    response['error'] = resp.status_code != 200
        
    if resp.status_code == 500:
        response['consulta_ticket'] = True
        response['error'] = True
        
    if not response['error']:
        print("####Obtenercatalagoid claro###") 
        query_idcatalogo_response = resp.json()
        response.update(query_idcatalogo_response)
        print(response)
    return response

#format json query ticket
def extract_ticket_data(dict_response):
    try: 
        response = { 'estado_ticket': dict_response['Status'],'consulta_ticket': True}
    except Exception as _:
        response = {'consulta_ticket': False}
    return response

def create_token(body):
    response = {}
    if 'telefono_usuario' not in body:
        response['error'] = True
        print(response)
        return  response
    
    url = url_api_token + "enviarmensaje.php"
    files=[]
    headers = {'Authorization': authorization}
    payload={'telefono': body['telefono_usuario'],'token': '4','proyecto': 'claro','mensaje': body['email_usuario']}
    log = Datadog()
    log.send_log("body token: " + json.dumps(payload))
    resp = requests.post(url,headers=headers,data=payload ,files=files)
    response['error'] = resp.status_code != 200
    log.send_log("respuesta desde Res token: " + resp.text)

    if resp.status_code == 500 or resp.status_code == 404:
        response['consulta_ticket'] = True
        response['error'] = True
        
    if not response['error']:
        print("####Crear token claro###") 
        token_generate = resp.json()
        response['token'] = token_generate['token']
        print("################TOKEN##############")
        print(response['token'])
        response['msg_sms'] = token_generate['error']
        print(response)
    return response

def get_app(body):
    response = {}
    if 'app' not in body:
        response['error'] = True
        return  response
    
    base = bd.MysqlBD()
    search_app= body["app"].upper()
    print(search_app)
    get_app_data = """ SELECT * from matriz_app WHERE apps = '%s' """ % (search_app)
    successful, data = base.find_all(get_app_data)
    count = (len(data))
    action_app = 0
    
    if successful:
        print("#####consultar app claro####")
        if count == 1:
            response['consulta_app'] = data[0]["accion"] if data[0]["robot"] == 1 else False
            response['app_abreviatura'] = data[0]["abreviatura"] if data[0]["robot"] == 1 else False
        elif count >= 2:
            for x in data:
                if x["robot"] == 1:
                    action_app += 1
            response['consulta_app'] = "ambos" if action_app > 1 else False
            response['app_abreviatura'] = data[0]["abreviatura"] if data[0]["robot"] == 1 else False
        else:
            response['consulta_app'] = False
    else:
        response['consulta_app'] =  False
        response['error'] = True
    print(response)
    log = Datadog()
    log.send_log("respuesta get_app apps list: " + json.dumps(response))
    return response

def create_transaction(body):
    response = {}
    if 'app' not in body:
        response['error'] = True
        return  response
    url = url_api_transaction + "create_transaction.php"
    print(body)
    payload_params = """idocument_type=red&ipass_generate=&idocument_descrip=esunacedula&iacciones_%s=%s&itelefono=%s""" % (body['app_abreviatura'],body['consulta_app'],body['telefono_usuario'])
    payload={'bot_id': '22','form_id': '23','params': payload_params}
    headers = {'X-API-KEY': authorization_transaction}
    log = Datadog()
    log.send_log("body enviado a rest crear incidente: " + json.dumps(payload))
    resp = requests.request("POST", url, headers=headers, data=payload)
    respons_user= resp.json()
    log.send_log("respuesta desde Res token: " + resp.text)
    
    response['error'] = resp.status_code != 200 or ("alert" in respons_user and respons_user["alert"]== "invalid")
    if resp.status_code == 500  or resp.status_code == 404:
        response['crear_transaccion'] = False
        response['error'] = True
    if not response['error']:
        print("###Crear Transaccion acceso claro##")
        response['telefono_usuario'] = body['telefono_usuario']
        response['consulta_app'] = body['consulta_app']
        response['numero_seguimiento'] = respons_user['data']['response']['id_formulario']
        response['crear_transaccion'] = True
        response['bd_transaction']= bd_transaction('INSERT',body,'pendiente',response['numero_seguimiento'])
        print(response)
    return response

def query_transaction(body):
    response = {}
    if 'numero_seguimiento' not in body:
        response['error'] = True
        return  response
    
    url = url_api_transaction + "consult_transaction.php"
    payload={'id_history': body['numero_seguimiento']}
    headers = { 'X-API-KEY': authorization_transaction}
    log = Datadog()
    resp = requests.request("POST", url, headers=headers, data=payload)
    respons_user= resp.json()
    response['error'] = resp.status_code != 200 or ("alert" in respons_user and respons_user["alert"]== "invalid")
    if resp.status_code == 500  or resp.status_code == 404:
        response['consulta_transaccion'] = False
        response['error'] = True
    if not response['error']:
        print("###Obtener trasaccion acceso claro##")
        response.update(extract_status_transaction(respons_user['datos']))
        if not response['error']:
            response['bd_transaction']= bd_transaction('UPDATE',body,response['status'],body['numero_seguimiento']  )          
        print(response)
    return response

def extract_status_transaction(dict_response):
    try: 
        if dict_response['estado'] in ('No Exitoso','Pendiente','Proceso') :
            response = {'consulta_transaccion': False,
                        'crear_transaccion': False, 
                        'status': dict_response['estado'].lower()}
        else:
            response = {'status': dict_response['estado'].lower(),
                'numero_ticket': dict_response['ticket_number'],
                'password_sms': dict_response['ipass_generate'] if 'ipass_generate' in dict_response else '',
                'consulta_transaccion': True}
    except Exception as _:
        response = {'consulta_transaccion': False, 'error': True}
    return response

def bd_transaction(action,body,status,number_tracing=''):
    response = {}
    if 'app' not in body:
        response['error'] = True
        return  response
    base = bd.MysqlBD()
    fecha_transaccion = datetime.datetime.now()
    if action == 'INSERT':
        query_insert_transaction = """ INSERT INTO estatus_transacciones(numero_origen,fecha_transaccion,estado_solicitud,app,accion_app,numero_seguimiento) VALUES (%s,%s,%s,%s,%s,%s) """
        parametros = (body['telefono_usuario'],fecha_transaccion, status, body['app'],body['consulta_app'],number_tracing)
        exito_query, datos_query = base.insert(query_insert_transaction, parameters=parametros)
    
    if action == 'UPDATE':
        query_update_seguimiento = """ UPDATE estatus_transacciones SET fecha_transaccion = %s, estado_solicitud = %s WHERE numero_origen = %s and  numero_seguimiento = %s"""
        parametros = (fecha_transaccion, status, body['telefono_usuario'],number_tracing)
        exito_query, datos_query = base.update(query_update_seguimiento, parameters=parametros)
    
    if exito_query:
        exito = 200
        datos = action
        bd_transaction = True
    else:
        exito = 400
        datos = str(datos_query)
        bd_transaction = False
    return bd_transaction

def search_transaction(body):
    response = {}
    if 'app' not in body:
        response['error'] = True
        return  response
    base = bd.MysqlBD()
    get_app_data = """ SELECT estado_solicitud,numero_seguimiento from estatus_transacciones WHERE numero_origen = '%s' and app = '%s' and accion_app = '%s' ORDER BY fecha_transaccion DESC LIMIT 1 """  % (body['telefono_usuario'],body['app'],body['consulta_app'])
    successful, data = base.find_all(get_app_data)
    count = (len(data))
    if successful and count > 0:
        response['estado_solicitud'] = data[0]["estado_solicitud"]
        response['numero_seguimiento'] = data[0]["numero_seguimiento"]
    else:
        response['estado_solicitud'] =  False
        response['error'] = True
    return response

