import mods.date_parse as date_manage
import mods.documentos as mongo_manage
from bson.json_util import loads, dumps
import json
from mods.datadog2 import Datadog
import traceback
import re

def remove_html_tags(text):
    pattern = re.compile(r'<.*?>')
    clean_text = pattern.sub('', text)
    return clean_text

def build(cid):
    list_documents = mongo_manage.buscar_interaccion_xentric(cid)
    json_format = parse_bson(list_documents)
    return build_json_response(json_format)

def parse_bson(record):
    return json.loads(dumps(record))

def build_json_response(raw_json):
    array_conversation = []
    log = Datadog()
    anterior = ""
    for doc in raw_json:
        if 'toAnswer' in doc['interaction']['context'] and (doc['interaction']['context']['toAnswer'] is None or  doc['interaction']['context']['toAnswer'] == ""):
            if doc['interaction']['input']['text'] and doc['interaction']['input']['text'] != anterior:
                array_conversation.append(format_conversation(doc, doc['interaction']['input']['text'], 'input'))
                if doc['interaction']['input']['text'] in ["si", "no"]:
                    anterior = ""
                else:
                    anterior = doc['interaction']['input']['text']
            if len(doc['interaction']['output']['text']) > 0:
                for text_input in doc['interaction']['output']['text']:
                    msgs = [x["msg"] for x in array_conversation]
                    if text_input not in msgs:
                        array_conversation.append(format_conversation(doc, text_input, 'output'))
    return {'cliente': get_client_data(raw_json[-1]), 'conversation': array_conversation, 'date': date_manage.date(raw_json[-1]['datetime']['$date']/1000), 'title': 'Historial de Conversación' }

def format_conversation(doc, text, type):
    date_dict = date_manage.dict_full_date(doc['datetime']['$date']/1000)
    return {'date': date_dict['date'], 'hour': date_dict['hour'], 'id': define_id(type), 'msg': remove_html_tags(text)}

def define_id(type):
    return 2 if type == 'input' else 1

def get_client_data(last_document):
    return { 'id': id_client(last_document), 'nombre': full_name(last_document), 'rut': cedula(last_document), 'email': get_email_data(last_document), 'telefono': get_phone_data(last_document), 'empresa': get_company_data(last_document), 'ticket': get_ticket_data(last_document) }

def full_name(last_document):
    if last_document['interaction']['context']['nombre_usuario'] and last_document['interaction']['context']['apellido_usuario']:
        return "{} {}".format(last_document['interaction']['context']['nombre_usuario'], last_document['interaction']['context']['apellido_usuario'])
    return ""

def id_client(last_document):
    return 1

def cedula(last_document):
    if 'cedula' in last_document['interaction']['context']: 
        return last_document['interaction']['context']['cedula']
    return ''

def get_email_data(last_document):
    if "email_usuario" in last_document["interaction"]["context"]:
        return last_document['interaction']['context']['email_usuario']
    return ""

def get_ticket_data(last_document):
    if "caso_asic" in last_document["interaction"]["context"]:
        return last_document['interaction']['context']['caso_asic']
    return ""

def get_phone_data(last_document):
    if "telefono_usuario" in last_document["interaction"]["context"]:
        return last_document['interaction']['context']['telefono_usuario']
    return ""

def get_company_data(last_document):
    if "empresa_usuario" in last_document["interaction"]["context"]:
        return last_document['interaction']['context']['empresa_usuario']
    return ""
