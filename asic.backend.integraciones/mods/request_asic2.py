import requests
import json
from mods.datadog2 import Datadog
from unidecode import unidecode
import mods.config as config
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
url_api = config.ASIC_2_API_URL
authorization = config.ASIC_2_TOKEN

def crear_wo(body):
    
    response = {}
    url = url_api + "WO/create.php"
    headers = {'Authorization': authorization}
    usuario = body['nombre_usuario']
    empresa = body['empresa_usuario']
    print("#############EMPRESA############")
    print(empresa)
    print(usuario)
    print(body)
    if 'caso_asic_detail' in body and 'caso_asic_summary' in body and 'empresa_usuario' in body:
            body["caso_asic_detail"] = unidecode(body['caso_asic_detail'])
            body["caso_asic_summary"] = unidecode(body['caso_asic_summary'])
            body["empresa_usuario"] = unidecode(body['empresa_usuario'])
   
    payload={
        'customer_first_name': body['nombre_usuario'],
        'customer_last_name': body['apellido_usuario'],
        'company': body['empresa_usuario'],
        'summary': body['caso_asic_summary'],
        'detailed_description': body['caso_asic_detail'],
        'priority': '3-Medium',
        'work_order_type': 'General',
        'request_manager_company': 'Casa Editorial El Tiempo S.A',
        'manager_support_organization': 'DIRECCIÓN TICS',
        'manager_support_group_name': 'Segundo Nivel Telecomunicaciones',
        'request_manager': 'Wilson Camilo Diaz Bohorquez',
        'support_company': body['empresa_usuario'],
        'support_organization': 'DIRECCIÓN TICS',
        'support_group_name': 'Segundo Nivel Telecomunicaciones',
        'categorization_tier_1': 'TELECOMUNICACIONES ',
        'categorization_tier_2': 'TELEFONIA ',
        'categorization_tier_3': 'Solicitud',
        'product_cat_tier_1': 'SOFTWARE ',
        'product_cat_tier_2': 'TELECOMUNICACIONES ',
        'product_cat_tier_3': 'SOFTPHONE ',
        'product_name': 'Cisco Jabber',
        'reported_source': 'ChatBot',
        'status': 'Assigned',
        'request_assignee': ''}
    
    print(payload)
    
    try:  
        resp = requests.request("POST", url, headers=headers, data=payload)
        resp.raise_for_status() 

        if not resp.status_code  == 200: 
            print( "Error: Unexpected response {}".format(resp))
            response['error'] = True
            response['caso_asic_2'] = False
            response['caso_asic'] = False
        
        resp_api = resp.json()
        print("RESP USER JSON")
        print(response)
        print(resp_api)

        if  response == {}:
            print("### crear woo##")
            

            response['caso_asic'] = resp_api['SRID_Number']
            response['caso_asic_2'] = resp_api['WorkOrder_ID']
            response['error'] = False
            print("#############UPDATE")
            print(response)
     
        else:
            response['caso_asic_2'] = False
            response['caso_asic'] = False
            response['error'] = True
    
    
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError, Exception) as errh:
        print (errh)
        print ("Error  : ",str(errh))
        response['error'] = True
        response['caso_asic_2'] = False
        response['caso_asic'] = False
        
        print("####RESPONSE FINAL ###")
        print(response)
        
    return response
   
    
    
    
def consultar_wo(body):
    response ={}
    body['numero_ticket'] = "WO" + "0000000000000"[len(body['numero_ticket']):] + body['numero_ticket']
    url = url_api + "WO/search.php?work_order_id=" +  body['numero_ticket']
    headers = {'Authorization': authorization}
    payload={}
    
    try:
      resp = requests.get(url,headers=headers,data=payload)
      resp.raise_for_status()
      response_api = resp.json()
    
      print(response_api,"response api########")
      if not resp.status_code  == 200: 
        print( "Error: Unexpected response {}".format(resp))
        response['error'] = True
        
      if  response == {}:
       print("### crear woo##")
  
       response['numero_ticket'] = body['numero_ticket']
       response['consulta_ticket'] = True
       response['estado_ticket'] = response_api['entries'][0]['values']['Status']
       response['error'] = False
       print("#############UPDATE")
       print(response)
    
      else:
        response['consulta_ticket'] = False
        response['error'] = True
                
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError, Exception) as errh:
        print (errh)
        print ("Error wo : ",str(errh))
        response['error'] = True   
          
    print(response)
    return response

def wo_listado_usuario(body):
    url = url_api + "WO/list-by-user.php"
    headers = {'Authorization': authorization}
    payload={{"dni":body['user_'],"limit":body['limit']}}
    resp = requests.post(url,headers=headers,data=payload)
    response = resp.json()
    print(response )
    return response

def get_username(body):
    url = url_api + "USER/by-username.php"
    headers = {'Authorization': authorization}
    payload={"username":body['username']} 
    resp = requests.post(url,headers=headers,data=payload)
    response = resp.json()
    print(response )
    return response

def get_user_dni(body):
    response = {}
    response['error'] = False
    print("BODY GET USER DNI")
    print(body)
    print("#######URL###")
    print(url_api)
    if 'consulta_cedula' not in body:
        response['error'] = True
        return  response
    
    url = url_api + "USER/by-dni.php"
    headers = {'Authorization': authorization}
    payload={"dni":body['cedula']} 
    
    try:
        resp = requests.post(url,headers=headers,data=payload)
        print("#######OBTENER GET USER DNI###")
        # log = Datadog()
        resp.raise_for_status() 
        if not resp.status_code  == 200: 
            print( "Error: Unexpected response {}".format(resp))
            response['error'] = True
            response['consulta_cedula'] = False
            # log.send_log("Error status code get_user_dni: " , resp.status_code)
        
        resp_user = resp.json()
        # response['error'] = resp_user["alert"] == "invalid" or  "200" not in resp_user["code"]
        print("RESP USER JSON")
        print(resp_user)
        # log.send_log("Request consulta dni: " , json.dumps(resp_user))
        print(  response['error'])
        if not response['error']:
            print("###Obtenerusuario asic 2##")
            response.update(extract_data_user(resp_user))
            print("#############UPDATE")
            print(response)
        else:
            response['consulta_cedula'] = False
            response['error'] = True

    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError, Exception) as errh:
        print (errh)
        print ("Error get_user_dni : ",str(errh))
        # log.send_log("Error get_user_dni: " , str(errh))
        response['error'] = True
        response['consulta_cedula'] = False
        
    print("####RESPONSE FINAL ###")
    print(response)
    return response

def extract_data_user(dict_response):
    try: 
        print("extract_data_user")
        response = {           
            'nombre_usuario': dict_response['First Name'] if 'First Name' in dict_response else '',
            'apellido_usuario': dict_response['Last Name'] if 'Last Name' in dict_response else '',
            'email_usuario': dict_response['Internet E-mail'] if 'Internet E-mail' in dict_response else '',
            'telefono_usuario': dict_response['Phone Number Business'] if 'Phone Number Business' in dict_response else '',
            'empresa_usuario': dict_response['Company'] if 'Company' in dict_response else '',
            'consulta_cedula': True,
        }
    except:
        response = { 'consulta_cedula': False }
    return response



def listado_inicidentes_usuarios(body):
    url = url_api + "INC/list-by-user.php"
    headers = {'Authorization': authorization}
    payload={"dni": body["dni"],"limit": body["limit"]}
    resp = requests.post(url,headers=headers,data=payload)
    response = resp.json()
    print(response )
    return response


def inc_crear_resuelto(body):
    url = url_api + "INC/create.php"
    headers = {'Authorization': authorization}
    payload={
    'firstname': body['firstname'],
    'lastname': body['lastname'],
    'summary': body['summary'],
    'impact': body['impact'],
    'urgency': body['urgency'],
    'reported_source': body['reported_source'],
    'service_type': body['service_type'],
    'description': body['description'],
    'categorization_tier_1': body['categorization_tier_1'],
    'categorization_tier_2': body['categorization_tier_2'],
    'categorization_tier_3': body['categorization_tier_3'],
    'categorization_tier_1_p': body['categorization_tier_1_p'],
    'categorization_tier_2_p': body['categorization_tier_2_p'],
    'categorization_tier_3_p': body['categorization_tier_3_p'],
    'product_name': body['product_name'],
    'support_organization': body['support_organization'],
    'support_group': body['support_group'],
    'company': body['company'],
    'status': body['status'],
    'assignee': body['assignee'],
    'status_reason': body['status_reason'],
    'resolution_copy': body['resolution_copy'],
    'resolution_method': body['resolution_method'],
    'res_cat_1': body['res_cat_1'],
    'res_cat_2': body['res_cat_2'],
    'res_cat_3': body['res_cat_3'],}
    resp = requests.post(url,headers=headers,data=payload)
    response = resp.json()
    print(response )
    return response

def inc_crear_asignado(body):
    print("######## body inc crear",body)
    response = {}
 
    url = url_api+"INC/create.php"
    headers = {'Authorization': authorization}
    payload={
        'firstname': body['nombre_usuario'],
        'lastname': body['apellido_usuario'],
        'summary': body['caso_asic_summary'],
        'impact': body['impact'],
        'urgency': body['urgency'],
        'reported_source': body['reported_source'],
        'service_type': body['service_type'],
        'description': body['BO_TipoProducto'],
        'categorization_tier_1': body['categorization_tier_1'],
        'categorization_tier_2': body['categorization_tier_2'],
        'categorization_tier_3': body['categorization_tier_3'],
        'categorization_tier_1_p': body['categorization_tier_1_p'],
        'categorization_tier_2_p': body['categorization_tier_2_p'],
        'categorization_tier_3_p':  body['categorization_tier_3_p'],
        'product_name': body['product_name'],
        'support_organization': 'CENTRO DE GESTIÓN',
        'support_group': 'Mesa de Ayuda',
        'company': body['empresa_usuario'],
        'status': body["status"], }
    print("#############PAYLOAD",payload)
    try:
      resp = requests.post(url,headers=headers,data=payload)
      resp.raise_for_status() 
      print("#############RESPONSE",resp.json())
      if not resp.status_code  == 200: 
        print( "Error: Unexpected response {}".format(resp))
        response['error'] = True
        response['caso_asic_2'] = False
        response['caso_asic'] = False
        
      resp_user = resp.json()
      print("RESP USER JSON")
      print(resp_user)
    
      print("#############RESPONSE####",response)
    
      if  response == {}:
        print("### inc asic 2##")
        # response.update(extract_data_payload_inc(body))
        response.update(extract_response(resp_user))

        print("#############UPDATE")
        print(response)
      else:
        response['caso_asic_2'] = False
        response['caso_asic'] = False
        response['error'] = True
        
    
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError, Exception) as errh:
        print (errh)
        print ("Error get_user_dni : ",str(errh))
        response['error'] = True
        response['caso_asic_2'] = False
        response['caso_asic'] = False
        
    print("####RESPONSE FINAL ###")
    print(response)
    return response

def extract_data_payload_inc(dict_response):
    try: 
        print("extract_data_use_inc")
        response = {           
            'nombre_usuario': dict_response['Firstname'] if 'firstname' in dict_response else '',
            'apellido_usuario': dict_response['Lastname'] if 'lastname' in dict_response else '',
            'caso_asic_summary': dict_response['summary'] if 'summary' in dict_response else '',
            'caso_asic_detail': dict_response['description'] if 'description' in dict_response else '',
            'empresa_usuario': dict_response['company'] if 'company' in dict_response else '',
        }
    except:
        response = { 'INC': False }
    return response

def extract_response(dict_response):
    
    try: 
        response = {
            'caso_asic': dict_response['SRID_Number'],
            'caso_asic_2': dict_response['Incident_Number'],
            'error': False,
        }
       
    except Exception as _:
        response = {'error': True, 'caso_asic': False},
        
    return response

  
       
def get_dni(body):
    url = url_api + "USER/by-dni.php"
    headers = {'Authorization': authorization}
    payload={{"dni":body['dni']}} 
    resp = requests.post(url,headers=headers,data=payload)
    response = resp.json()
    print(response )
    return response



