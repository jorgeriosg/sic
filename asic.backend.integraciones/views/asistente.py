import json
from flask import jsonify
import traceback
import mods.datadog as datadog
import mods.watson as watson
import mods.documentos as documentos
import mods.spellchecker_lib as spellcheck
from mods.config import DEBUG

from cognitiva_xss_3.xss3 import XssClean
import views.integraciones as integraciones


def limpiar_textos(texto, spell=None):
    """
    funcion que limpia caracteres especiales y envia a revision de gramatica
    :param texto:
    :param spell:
    :return:
    """
    if texto:
        if spell:
            texto = spellcheck.spellchecker(texto)
        texto = texto.lower()
        texto = texto.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        texto = texto.replace(',', '').replace(':', '').replace(';', '').replace('¿', '').replace('?', '').replace('¡', '').replace('!', '')
        texto = texto.replace('\t', '').replace('\v', '')
    return texto


def validar_entrada(request):
    valido = True
    if 'general' not in request or 'msg' not in request:
        valido = False
    return valido


def formato_salida_texto(codigo=200, glosa='', conv_response={}, derivar=False):
    return jsonify({
        'estado': {
            'codigo': codigo,
            'glosa': glosa
        },
        'conv_response': conv_response,
        'derivar': derivar
    })


def llamada_asistente_texto(request):

    # normalizar para xentric
    debug = False
    cid = request['general']['cid'] if 'general' in request and 'cid' in request['general'] and request['general']['cid'] else request['conv_response']['context']['conversation_id'] if 'conv_response' in request and 'context' in request['conv_response'] and 'conversation_id' in request['conv_response']['context'] and request['conv_response']['context']['conversation_id'] else ''

    id_asistente = request['general']['id_asistente'] if 'general' in request and 'id_asistente' in request['general'] and request['general']['id_asistente'] else '1'

    id_usuario = int(request['general']['id_usuario']) if 'general' in request and 'id_usuario' in request['general'] and request['general']['id_usuario'] else 0

    msg = ''.join(request['msg']) if 'msg' in request and type(request['msg']) is list and request['msg'] else request['conv_response']['input']['text'][-1] if 'conv_response' in request and 'input' in request['conv_response'] and 'text' in request['conv_response']['input'] else []

    conv_response = request['conv_response']['interaction'] if 'conv_response' in request and 'interaction' in request['conv_response'] else request['conv_response'] if 'conv_response' in request else None

    id_canal = request['general']['origen'] if 'general' in request and 'origen' in request['general'] else 1

    location = request['general']['location'] if 'general' in request and 'location' in request['general'] and request['general']['location'] else {
        'comuna': '',
        'region': '',
        'pais': ''
    }

    # Sanitizacion a = b if c == d else i if e == f else j
    cid = XssClean.sanitizeHtml(cid)
    msg = XssClean.sanitizeHtml(msg)
    msg = limpiar_textos(texto=msg)

    watsonV1 = watson.WatsonV1()
    api_call = 0

    if not conv_response:
        documento = documentos.buscar_interaccion(cid)
        conv_response = documento['interaction'] if 'interaction' in documento else {}
    
    if not cid:
        contexto = {'socialMedia':'voz', 'id_canal': 6}
        
        conv_response = watsonV1.watson_call(input='', context=contexto)
        return formato_salida_texto(codigo=200, glosa='Ok', conv_response=conv_response)

    if not conv_response:
        return formato_salida_texto(codigo=400, glosa='cid no existe en base de datos', conv_response=conv_response)

    # if msg == 'reset_whatsapp' or msg == 'reset_facebook':
    #    cid = conv_response['context']['conversation_id']
    #    conv_response['context'] = {'conversation_id': cid}

    contexto = conv_response['context']
    contexto['id_canal'] = id_canal
    contexto['id_usuario'] = id_usuario
    contexto['id_asistente'] = id_asistente
    contexto['location'] = location
    contexto['stayResponse'] = ''

    if 'calendar' in contexto and contexto['calendar']:
        contexto['calendar'] = False

    if 'formulario' in contexto and contexto['formulario']:
        contexto['formulario'] = False

    conv_response = watsonV1.watson_call(input=msg, context=contexto)
    api_call += 1
    documentos.guardar_interaccion(conv_response=conv_response)
    contexto = conv_response['context']

    # Integraciones
    hay_integracion, integracion_response, nueva_llamada, derivar = integraciones.integraciones_toAnswer(conv_response=conv_response)

    if hay_integracion:
        documentos.guardar_interaccion(conv_response=integracion_response, tipo_documento='integracion')
        contexto = integracion_response['context']

        if nueva_llamada:
            print("##########CONTEXTO WATSON###") 
            print(contexto)
            conv_response = watsonV1.watson_call(input=msg, context=contexto)
            api_call += 1
            new_hay_integracion = True
            if derivar:
                new_hay_integracion = False
            if new_hay_integracion:
                output_anterior = conv_response['output']['text']
                hay_integracion, integracion_response, nueva_llamada, derivar = integraciones.integraciones_toAnswer(conv_response=conv_response)
                contexto = integracion_response['context']
                if hay_integracion:
                    conv_response = watsonV1.watson_call(input=msg, context=contexto)
                    for text in output_anterior:
                        conv_response["output"]["text"] = conv_response["output"]["text"][::-1]
                        conv_response["output"]["text"].append(text)
                    conv_response["output"]["text"] = conv_response["output"]["text"][::-1]
            documentos.guardar_interaccion(conv_response=conv_response)
        else:
            conv_response = integracion_response

    inp = {
        'input': msg,
        'request': str(request),
        'output': conv_response['output']['text'],
        'cid': conv_response['context']['conversation_id']
    }

    # registrar sesiones de conversacion
    try:
        pais = conv_response['context']['location']['pais'] if 'context' in conv_response and 'location' in conv_response['context'] and 'pais' in conv_response['context']['location'] and conv_response['context']['location']['pais'] else ''
        region = conv_response['context']['location']['region'] if 'context' in conv_response and 'location' in conv_response['context'] and 'region' in conv_response['context']['location'] and conv_response['context']['location']['region'] else ''
        comuna = conv_response['context']['location']['comuna'] if 'context' in conv_response and 'location' in conv_response['context'] and 'comuna' in conv_response['context']['location'] and conv_response['context']['location']['comuna'] else ''
        output = ''.join(conv_response['output']['text']) if 'output' in conv_response and 'text' in conv_response['output'] and conv_response['output']['text'] else ''
        tipo_usuario = conv_response['context']['tipo_rut'] if 'context' in conv_response and 'tipo_rut' in conv_response['context'] and conv_response['context']['tipo_rut'] else ''
        rut = conv_response['context']['rut'] if 'context' in conv_response and 'rut' in conv_response['context'] and conv_response['context']['rut'] else ''
        derivado = 1 if 'context' in conv_response and 'derivado' in conv_response['context'] and conv_response['context']['derivado'] else 0
        tipo_derivacion = conv_response['context']['tipo_derivacion'] if 'context' in conv_response and 'tipo_derivacion' in conv_response['context'] and conv_response['context']['tipo_derivacion'] else ''
        stayResponse = conv_response['context']['stayResponse'] if 'context' in conv_response and 'stayResponse' in conv_response['context'] and conv_response['context']['stayResponse'] else ''
        id_canal = conv_response['context']['id_canal'] if 'context' in conv_response and 'id_canal' in conv_response['context'] and conv_response['context']['id_canal'] else 1

        integraciones.guardar_sesion(cid=cid, pais=pais, region=region, comuna=comuna, input=msg, output=output, canal=id_canal, api_call=api_call, tipo_usuario=tipo_usuario, rut=rut, derivado=derivado, tipo_derivacion=tipo_derivacion, stayResponse=stayResponse)

    except Exception:
        datadog.registrar_datadog(error=traceback.format_exc(), status_code=500)
        pass


    return formato_salida_texto(codigo=200, glosa='Ok', conv_response=conv_response, derivar=derivar)

