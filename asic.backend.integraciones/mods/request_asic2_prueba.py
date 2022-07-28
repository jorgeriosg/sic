import requests
import json
# from mods.datadog2 import Datadog
from unidecode import unidecode
import config as config

url_api = config.ASIC_2_API_URL
authorization = config.ASIC_2_TOKEN


def crear_wo():
    url = url_api + "WO/create.php"
    headers = {'Authorization': authorization}
    payload = {
        'customer_first_name': 'Brayan Sebastian',
        'customer_last_name': 'Castellanos Rojas',
        'company': 'Casa Editorial El Tiempo S.A',
        'summary': 'Solicitud  Telefonía',
        'detailed_description': 'Usuario realiza Solicitud de acceso o asignación de Telefonía ',
        'priority': '3-Medium',
        'work_order_type': 'General',
        'request_manager_company': 'Casa Editorial El Tiempo S.A',
        'manager_support_organization': 'DIRECCIÓN TICS',
        'manager_support_group_name': 'Segundo Nivel Telecomunicaciones',
        'request_manager': 'Wilson Camilo Diaz Bohorquez',
        'support_company': 'Casa Editorial El Tiempo S.A',
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

    resp = requests.request("POST", url, headers=headers, data=payload)
    response = resp.json()
    print(response)
    return response


def consultar_wo():
    url = url_api + "WO/search.php?work_order_id=WO00000000552038"
    headers = {'Authorization': authorization}
    payload = {}
    resp = requests.get(url, headers=headers, data=payload)
    response = resp.json()
    print(response)
    return response


def wo_listado_usuario():
    url = url_api + "WO/list-by-user.php"
    headers = {'Authorization': authorization}
    payload = {"dni": '1053346648', "limit": '1'}
    resp = requests.post(url, headers=headers, data=payload)
    response = resp.json()
    print(response)
    return response


def get_username():
    url = url_api + "USER/by-username.php"
    headers = {'Authorization': authorization}
    payload = {"username": '1053346648'}
    resp = requests.post(url, headers=headers, data=payload)
    response = resp.json()
    print(response)
    return response


def listado_inicidentes_usuarios():
    url = url_api + "INC/list-by-user.php"
    headers = {'Authorization': authorization}
    payload = {"dni": '1053346648', "limit": '1'}
    resp = requests.post(url, headers=headers, data=payload)
    response = resp.json()
    print(response)
    return response


def inc_crear_resuelto():
    url = url_api + "INC/create.php"
    headers = {'Authorization': authorization}
    payload = {
        'firstname': 'Brayan Sebastian',
        'lastname': 'Castellanos Rojas',
        'summary': 'Falla en VPN',
        'impact': '3-Moderate/Limited',
        'urgency': '3-Medium',
        'reported_source': 'ChatBot',
        'service_type': 'User Service Request',
        'description': 'Usuario indica que reporta fallas en VPN ',
        'categorization_tier_1': 'TELECOMUNICACIONES',
        'categorization_tier_2': 'VPN ',
        'categorization_tier_3': 'Falla',
        'categorization_tier_1_p': 'SOFTWARE',
        'categorization_tier_2_p': 'TELECOMUNICACIONES',
        'categorization_tier_3_p': 'TELECOMUNICACIONES',
        'product_name': 'VPN',
        'support_organization': 'CENTRO DE GESTIÓN',
        'support_group': 'Mesa de Ayuda',
        'company': 'Casa Editorial El Tiempo S.A',
        'status': 'Resolved',
        'assignee': 'Julio Cesar Ibarguen Martinez',
        'status_reason': 'Automated Resolution Reported',
        'resolution_copy': 'El soporte realizado fue satisfactorio.',
        'resolution_method': 'Service Desk assisted',
        'res_cat_1': 'Soporte',
        'res_cat_2': 'Software',
        'res_cat_3': 'Desbloqueado'}
    resp = requests.post(url, headers=headers, data=payload)
    response = resp.json()
    print(response)
    return response


def inc_crear_asignado():
    url = url_api+"INC/create.php"
    headers = {'Authorization': authorization}
    payload = {
        'firstname': 'Brayan Sebastian',
        'lastname': 'Castellanos Rojas',
        'summary': 'Reporte de Incidente',
        'impact': '3-Moderate/Limited',
        'urgency': '3-Medium',
        'reported_source': 'Phone',
        'service_type': 'User Service Restoration',
        'description': 'ERROR DE APLICACIÓN  OFIMATICA',
        'categorization_tier_1': 'Sin definir',
        'categorization_tier_2': ' ',
        'categorization_tier_3': '',
        'categorization_tier_1_p': '',
        'categorization_tier_2_p': '',
        'categorization_tier_3_p': '',
        'product_name': '',
        'support_organization': 'CENTRO DE GESTIÓN',
        'support_group': 'Mesa de Ayuda',
        'company': 'Casa Editorial El Tiempo S.A',
        'status': 'Assigned', }
    resp = requests.post(url, headers=headers, data=payload)
    response = resp.json()
    print(response)
    return response


def get_dni():
    url = url_api + "USER/by-dni.php"
    headers = {'Authorization': authorization}
    payload = {"dni": "1053346648"}
    resp = requests.post(url, headers=headers, data=payload)
    response = resp.json()
    print(response)
    return response


# get_dni()
# consultar_wo()
# crear_wo()
# wo_listado_usuario()
# get_username()
# inc_crear_asignado()
# inc_crear_resuelto()
# listado_inicidentes_usuarios()
