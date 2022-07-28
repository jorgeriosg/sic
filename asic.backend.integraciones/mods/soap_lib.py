import requests
import zeep
from zeep.transports import Transport
from services.xml_services import XMLServices
from mods.datadog2 import Datadog
from unidecode import unidecode

SOAP_URL_FORMULARIO_CONTACTO = ''
SOAP_URL = ''
SOAP_TIMEOUT = 2

def formulario_crm_app(nombre,apellido,rut,telefono,correo,comentario,cid,origen,id_solicitud):

    wsdl = SOAP_URL_FORMULARIO_CONTACTO+'?wsdl'
    transport = Transport(timeout=SOAP_TIMEOUT)
    client = zeep.Client(wsdl=wsdl,transport=transport)

    #id_solicitud = str(randint(10000,99999))
    id_solicitud_hard = '10000'
    formato_id = ''
    
    if id_solicitud == 'contacto':
        if origen == 'Sitio Privado':
            formato_id = 'Asistente_Virtual_001_ConsultaTx'
        elif origen == 'APP':
            formato_id = 'Asistente_Virtual_001_ConsultaApp'
        else:
            formato_id = 'Asistente_Virtual_001_Consulta'
    else:
        formato_id = id_solicitud

    comentario += ' Origen:'+origen

    respuesta = client.service.solicitudesFormularios({'ID_SOLICITUD':id_solicitud_hard,'FORMATO_ID':formato_id,'RUT_TITULAR':rut[0],'DV_TITULAR':rut[1],'NOMBRES':nombre,'APELLIDO_PAT':apellido,'EMAIL':correo,'TELEFONO':telefono,'COMENTARIO':comentario})
    
    return respuesta


def monto_remanente_old(rut,ano):
    url=SOAP_URL
    #headers = {'content-type': 'application/soap+xml'}
    headers = {'content-type': 'text/xml','SOAPAction':'ServicioRemanente'}
    body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:rem="http://remanente.core.coopeuch.cl">
                <soapenv:Header/>
                <soapenv:Body>
                    <rem:consultaRemanente>
                        <entrada>
                            <userId>SRVMBK</userId>
                            <rut>%s</rut>
                            <anio>%s</anio>
                        </entrada>
                    </rem:consultaRemanente>
                </soapenv:Body>
            </soapenv:Envelope>"""%(rut,ano)

    response = requests.post(url,data=body,headers=headers)

    if response.status_code == 200:

        if 'error' in response.text:
            return 'error'
        else:
            monto = find_between(response.text, "<montoTotal>", "</montoTotal>" )
            return monto
    else:
        return 'error'


def find_between( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return "error"


def getValueFromSoap(response, value):
    obtained_value = find_between(response,'<'+value+'>','</'+value+'>')
    return obtained_value

def create_order(body):
    valid_params = validate_order_params(body)
    response = {}
    if valid_params['error']:
        response = valid_params
    else:
        body["caso_asic_detail"] = unidecode(body['caso_asic_detail'])
        body["caso_asic_summary"] = unidecode(body['caso_asic_summary'])

        url = 'https://sg.asicamericas.com/arsys/services/ARService?server=asbogprovremlb&webService=SRM_RequestInterface_Create_WS'
        headers = {'content-type': 'text/xml', 'SOAPAction': 'Request_Submit_Service'}
        body_soap = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:SRM_RequestInterface_Create_WS">
                        <soapenv:Header>
                            <urn:AuthenticationInfo>
                                <urn:userName>{body["Login_ID"]}</urn:userName>
                                <urn:password>{body["Login_ID"]}</urn:password>
                            </urn:AuthenticationInfo>
                        </soapenv:Header>
                        <soapenv:Body>
                            <urn:Request_Submit_Service>
                                <urn:Submitter>$USER$</urn:Submitter>
                                <urn:Status>Submitted</urn:Status>
                                <urn:Short_Description>.</urn:Short_Description>
                                <urn:FormKeyword>SERVICE_REQUEST_INTERFACE</urn:FormKeyword>
                                <urn:SR_Type_Field_1>{body['caso_asic_field1']}</urn:SR_Type_Field_1>
                                <urn:SR_Type_Field_2>{body['caso_asic_field2']}</urn:SR_Type_Field_2>
                                <urn:Form_Name>$SCHEMA$</urn:Form_Name>
                                <urn:OfferingTitle>.</urn:OfferingTitle>
                                <urn:AppRequestSummary>{body['caso_asic_summary']}</urn:AppRequestSummary>
                                <urn:TitleInstanceID>{body["TitleInstanceID"]}</urn:TitleInstanceID>
                                <urn:Entitlement_Qual>1=0</urn:Entitlement_Qual>
                                <urn:Source_Keyword>Interface Form</urn:Source_Keyword>
                                <urn:SRD_TurnaroundTimeX>0</urn:SRD_TurnaroundTimeX>
                                <urn:z1D_Action>CREATE</urn:z1D_Action>
                                <urn:Add_Request_For_>Individual</urn:Add_Request_For_>
                                <urn:Details>{body['caso_asic_detail']}</urn:Details>
                                <urn:Urgency>4-Low</urn:Urgency>
                                <urn:Impact>4-Minor/Localized</urn:Impact>
                                <urn:Login_ID>{body["remedy_login_id"]}</urn:Login_ID>
                                <urn:Customer_Login>{body["remedy_login_id"]}</urn:Customer_Login>
                                <urn:RequestQuantity>1</urn:RequestQuantity>
                            </urn:Request_Submit_Service>
                        </soapenv:Body>
                    </soapenv:Envelope>
                """
        log = Datadog()
        log.send_log("body enviado a soap: " + body_soap)
        log.send_log("parametros del format", [body['caso_asic_field1'],body['caso_asic_field2'] ,body['caso_asic_summary'], body['caso_asic_detail'], body["TitleInstanceID"], body["Login_ID"], body["Customer_Login"]])
        response = valid_params
        resp = requests.post(url,data=body_soap,headers=headers)
        response['error'] = resp.status_code != 200
        log.send_log("respuesta desde soap: " + resp.text)
        if not response['error']:
            response['caso_asic'] = extract_number_case(resp.text)
        else:
            response['caso_asic'] = False
    return response
    
def validate_order_params(body):
    required_params = ['caso_asic_field1','caso_asic_field2', 'caso_asic_summary', 'caso_asic_detail']
    missing_parameters = list(set(required_params) - set(list(body.keys())))
    if missing_parameters:
        return { 'error': True, 'message': f"Faltan los siguientes parámetros: {', '.join(missing_parameters)}" }
    else:
        return { 'error': False }

def extract_number_case(text_response):
    dict_response = XMLServices().to_dict(text_response)
    case_number = dict_response['soapenv:Envelope']['soapenv:Body']['ns0:Request_Submit_ServiceResponse']['ns0:Request_Number']
    return case_number

def query_identification_card(body):
    response = {}
    if 'cedula' not in body:
        response['error'] = True
        return  response
    url = 'https://sg.asicamericas.com/arsys/services/ARService?server=asbogprovremlb&webService=CTM_People_Find_Person'
    headers = {'content-type': 'text/xml', 'SOAPAction': 'New_Get_Operation_0'}
    body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:CTM_People_Find_Person">
                    <soapenv:Header>
                        <urn:AuthenticationInfo>
                            <urn:userName>{body["Login_ID"]}</urn:userName>
                            <urn:password>{body["Login_ID"]}</urn:password>
                            
                        </urn:AuthenticationInfo>
                    </soapenv:Header>
                    <soapenv:Body>
                        <urn:New_Get_Operation_0>
                            <urn:Corporate_ID>{body['cedula']}</urn:Corporate_ID>
                        </urn:New_Get_Operation_0>
                    </soapenv:Body>
               </soapenv:Envelope>
            """
    resp = requests.post(url,data=body,headers=headers)
    response['error'] = resp.status_code != 200
    if resp.status_code == 500 and not_exists_record(resp.text):
        response['consulta_cedula'] = True
    if not response['error']:
        response.update(identification_card_response(resp.text))
    return response

def identification_card_response(text_response):
    dict_response = XMLServices().to_dict(text_response)
    return extract_icard_data(dict_response['soapenv:Envelope']['soapenv:Body']['ns0:New_Get_Operation_0Response']['ns0:getListValues'])

def extract_icard_data(dict_response):
    try: 
        response = { 
            'nombre_usuario': dict_response['ns0:First_Name']['#text'] if 'ns0:First_Name' in dict_response else '',
            'apellido_usuario': dict_response['ns0:Last_Name']['#text'] if 'ns0:Last_Name' in dict_response else '',
            'telefono_usuario': dict_response['ns0:Phone_Number_Business']['#text'] if 'ns0:Phone_Number_Business' in dict_response else '',
            'email_usuario': dict_response['ns0:Internet_E-mail']['#text'] if 'ns0:Internet_E-mail' in dict_response else '',
            'empresa_usuario': dict_response['ns0:Company']['#text'] if 'ns0:Company' in dict_response else '',
            'consulta_cedula': True,
            'remedy_login_id': dict_response['ns0:Remedy_Login_ID']['#text'] if 'ns0:Remedy_Login_ID' in dict_response else '' 
        }
    except:
        response = { 'consulta_cedula': False }
    return response

def not_exists_record(text_response):
    dict_response = XMLServices().to_dict(text_response)
    return "Entry does not exist in database" in dict_response['soapenv:Envelope']['soapenv:Body']['soapenv:Fault']['faultstring']
    
def query_ticket(body):
    response = {}
    if 'numero_ticket' not in body:
        response['error'] = True
        return  response
    body['numero_ticket'] = "REQ" + "000000000000"[len(body['numero_ticket']):] + body['numero_ticket']
    compose_ticket_number = body['numero_ticket']
    url = 'https://sg.asicamericas.com/arsys/services/ARService?server=asbogprovremlb&webService=ASIC:SRM_Request_WS'
    headers = {'content-type': 'text/xml', 'SOAPAction': 'SRM_Request_WS'}
    body = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:urn="urn:SRM_Request_WS">
                    <soapenv:Header>
                        <urn:AuthenticationInfo>
                            <urn:userName>{body["Login_ID"]}</urn:userName>
                            <urn:password>{body["Login_ID"]}</urn:password>
                        </urn:AuthenticationInfo>
                    </soapenv:Header>
                    <soapenv:Body>
                        <urn:GetList>
                            <urn:Qualification>'Request Number'="{body['numero_ticket']}"</urn:Qualification>
                            <urn:startRecord>0</urn:startRecord>
                            <urn:maxLimit>1</urn:maxLimit>
                        </urn:GetList>
                    </soapenv:Body>
               </soapenv:Envelope>
            """
    resp = requests.post(url,data=body,headers=headers)
    if resp.status_code == 500 and not_exists_record(resp.text):
        response['consulta_ticket'] = True
        response['error'] = True
    if not 'error' in response:
        response.update(query_ticket_response(resp.text))
        response.update({"numero_ticket": compose_ticket_number })
    return response

def query_ticket_response(text_response):
    dict_response = XMLServices().to_dict(text_response)
    return extract_ticket_data(dict_response['soapenv:Envelope']['soapenv:Body']['ns0:GetListResponse']['ns0:getListValues'])

def extract_ticket_data(dict_response):
    try: 
        response = { 
            'estado_ticket': dict_response['ns0:Status'],
            'consulta_ticket': True, 
        }
    except Exception as _:
        response = {'consulta_ticket': False}
    return response