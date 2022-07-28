import requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import json
from mods.datadog2 import Datadog
from unidecode import unidecode
import mods.config as config
from datetime import datetime

url_api = config.BANCOC_API_URL
authorization = config.BANCOC_API_TOKEN


#create incident caso_asic payload
def create_interaction(body):
    print(body)
    valid_params = validate_order_params(body)
    valid_params = body
    response = {}
    
    if valid_params['error']:
        response = valid_params
    else:
        
        if 'caso_asic_detail' in body and 'caso_asic_summary' in body:
            body["caso_asic_detail"] = unidecode(body['caso_asic_detail'])
            body["caso_asic_summary"] = unidecode(body['caso_asic_summary'])
            body["BO_Categoria"] = body['BO_Categoria'].encode("utf-8").decode("utf-8")
            body["BO_SiteCategory"] = body['BO_SiteCategory'].encode("utf-8").decode("utf-8")
            body["BO_Subcategoria"] = body['BO_Subcategoria'].encode("utf-8").decode("utf-8")
            body["BO_TipoProducto"] = body['BO_TipoProducto'].encode("utf-8").decode("utf-8")
            body["BO_TituloCaso"] = body['BO_TituloCaso'].encode("utf-8").decode("utf-8")
        
        print("##########PAYLOAD BANCO OCCIDENTE TIPO PRODUCTO###")    
        print(body["BO_TipoProducto"])    
        print(body["BO_Subcategoria"])    
        print(body["BO_TituloCaso"])    
        url = url_api + "crearinteraccion.php"
        files=[]
        headers = {'Authorization': authorization}
        
        query_user  = query_id_user(body)
        print("###################BANCO OCCIDENTE CONSULTA USUARIO")
        query_day = datetime.today().strftime('%Y-%m-%d')
        print(query_user)
        print(query_day)
        
        payload={'NombreContacto':  body['remedy_login_id'],
        'Urgencia': '4',
        'FechaApertura': query_day,
        'FechaActualizacion': query_day,
        'AbiertoPor': 'ASICVB',
        'ActualizadoPor': 'ASICVB',
        'Descripcion': body['caso_asic_detail'],
        'ServicioAfectado': 'MI PUESTO DE TRABAJO',
        'Dueno': body['remedy_login_id'],
        'Abierto': 'Categorize',
        'NotificadoPor': 'Telephone',
        'GrupoAsignacion': 'MESA DE SERVICIO',
        'Categoria': body["BO_Categoria"],
        'SLA': '177',
        'Prioridad': '4',
        'SiteCategory': body["BO_SiteCategory"],
        'Subcategoria': body["BO_Subcategoria"],
        'TipoProducto': body["BO_TipoProducto"],
        'FaseActual': 'Categorization',
        'Telefono': query_user['telefono_usuario'],
        'Compania': 'BANCO DE OCCIDENTE',
        'NombreUbicacion': query_user['nombre_ubicacion'],
        'ContactoPrimario':  body['remedy_login_id'],
        'Impacto': '4',
        'Folder': 'gcalderon',
        'CI_Afectado': 'Mi puesto de trabajo',
        'TituloCaso':  body["BO_TituloCaso"],
        'AbiertoPorUID': 'ASICVB',
        'ActualizadoPorUID': 'ASICVB',
        'Activo': '1',
        'Origen': '6',
        'Padrino': '',
        'NombrePC': 'KSTABOG15-33',
        'ManagerBDO': body['remedy_login_id'],
        'Departamento': query_user['departamento'],
        'Manager': query_user['manager']}

        #log.send_log("body enviado a banco occidente: " + json.dumps())
        response = valid_params
        try:
            resp = requests.post(url,headers=headers,data=payload ,files=files)
            log = Datadog()
            resp.raise_for_status() 
            if not resp.status_code  == 200: 
                print( "Error: Unexpected response {}".format(resp))
                response['error'] = True
                response['consulta_cedula'] = False
                log.send_log("Error status code: " , resp.status_code)
                
            respons_case = resp.json()
            response['error'] = respons_case["alert"] == "invalid" or  "200" not in respons_case["code"]
            print(respons_case)
            log.send_log("Request crear ticket: " , json.dumps(respons_case))
            
            if not response['error']:
                print("#####Crearinteraccion banco occidente####")
                response['caso_asic'] = respons_case['datos']['Id_Interaccion']
                print(response['caso_asic'])
            else:
                response['caso_asic'] = False
                response['error'] = True
            
        except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError, Exception) as errh:
            print ("Error query_id_user : ",str(errh))
            log.send_log("Error query_id_user: " , str(errh))
            response['error'] = True
            response['consulta_cedula'] = False
            
        print(response)    
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

#query sd requirement
def query_sd(body):
    
    response = {}
    if 'numero_ticket' not in body:
        response['error'] = True
        return  response
    
    body['numero_ticket'] = "SD" + body['numero_ticket']
    compose_ticket_number = body['numero_ticket']
    url = url_api + "consultarinteraccion.php"
    payload={'Id_Interaccion': compose_ticket_number}
    files=[]
    headers = {'Authorization': authorization}
    
    
    try:
        resp = requests.post(url,headers=headers,data=payload ,files=files)
        log = Datadog()
        resp.raise_for_status() 
        if not resp.status_code  == 200: 
            print( "Error: Unexpected response {}".format(resp))
            response['error'] = True
            response['consulta_cedula'] = False
            log.send_log("Error status code: " , resp.status_code)
            
        resp_sd = resp.json()
        response['error'] = resp_sd["alert"] == "invalid" or  "200" not in resp_sd["code"]
        print(resp_sd)
        log.send_log("Request consulta usuario: " , json.dumps(resp_sd))
        
        if not response['error']:
            print("###Consultasd banco occidente")
            response.update(extract_sd_data(resp_sd['datos']))
            response.update({"numero_ticket": compose_ticket_number })
            print(response)
        else:
            response['caso_asic'] = False
            response['error'] = True

    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError, Exception) as errh:
        print ("Error query_id_user : ",str(errh))
        log.send_log("Error query_id_user: " , str(errh))
        response['error'] = True
        response['consulta_cedula'] = False
        
    print(response)    
    return response

#format json query sd
def extract_sd_data(dict_response):
    
    #status = "Assign" if dict_response['Activo'] else "NotAssign"
    
    try: 
        response = { 
            'estado_ticket': dict_response['Activo'],
            'consulta_ticket': True
        }
    except Exception as _:
        response = {'consulta_ticket': False}
    return response


#query identification user
def query_id_user(body):
    response = {}
    if 'cedula' not in body:
        response['error'] = True
        return  response
    
    url = url_api + "consultarusuario.php"
    headers = { 'Authorization': authorization}
    payload={'Cedula': str(body['cedula'])}
    files=[] 
    
    try:
        resp = requests.post(url,headers=headers,data=payload ,files=files)
        log = Datadog()
        resp.raise_for_status() 
        if not resp.status_code  == 200: 
            print( "Error: Unexpected response {}".format(resp))
            response['error'] = True
            response['consulta_cedula'] = False
            log.send_log("Error status code: " , resp.status_code)
        
        resp_idcard = resp.json()
        response['error'] = resp_idcard["alert"] == "invalid" or  "200" not in resp_idcard["code"]
        print(resp_idcard)
        log.send_log("Request consulta usuario: " , json.dumps(resp_idcard))

        if not response['error']:
            print("###Obtenerusuario banco occidente##")
            response.update(extract_icard_data(resp_idcard['datos']))
            print("#############UPDATE")
            print(response)
        else:
            response['caso_asic'] = False
            response['error'] = True
            
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError, Exception) as errh:
        print ("Error query_id_user : ",str(errh))
        log.send_log("Error query_id_user: " , str(errh))
        response['error'] = True
        response['consulta_cedula'] = False

    return response

#format response json  query identification user
def extract_icard_data(dict_response):
    try: 
        response = { 
            'nombre_usuario': dict_response['Nombres'] if 'Nombres' in dict_response else '',
            'apellido_usuario': dict_response['Apellidos'] if 'Apellidos' in dict_response else '',
            'telefono_usuario': dict_response['Telefono'] if 'Telefono' in dict_response else '',
            'email_usuario': dict_response['Email'] if 'Email' in dict_response else '',
            'empresa_usuario': dict_response['Compania'] if 'Compania' in dict_response else '',
            'consulta_cedula': True,
            'remedy_login_id': dict_response['Cedula'] if 'Cedula' in dict_response else '', 
            'Urgency': dict_response['Urgency'] if 'Urgency' in dict_response else '', 
            'nombre_ubicacion': dict_response['EstructuraDept'] if 'EstructuraDept' in dict_response else '' ,
            'departamento': dict_response['Departmento'] if 'Departmento' in dict_response else '' ,
            'manager': dict_response['Manager'] if 'Manager' in dict_response else ''
        
        }
    except:
        response = { 'consulta_cedula': False }
    return response
