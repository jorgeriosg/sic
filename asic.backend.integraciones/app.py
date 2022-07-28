# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask
from flask import request
from flask import session
from flask import jsonify
from flask_cors import cross_origin
from datetime import timedelta
import traceback
import json
from icecream import ic

from mods.config import XENTRIC_PASS, XENTRIC_USER, IP_CENTRAL
import mods.asic as asic
from mods.datadog2 import *
import mods.soap_lib as soap_service
from mods.datadog import registrar_datadog_v2
from mods.datadog2 import Datadog
from views.xentric_handler import processMessage as xentricHandler
from views.callback_status import status_callback
import views.registro_errores as registro_errores
import views.asistente as asistente
from views.mantenedor import get_clientes, estadisticas_llamadas
from routes.connect import connect
from routes.utils import utils

APP = Flask(__name__)
VERBOSE = False
ALLOWED_ORIGIN = '*'

APP.register_blueprint(connect, url_prefix='/connect')
APP.register_blueprint(utils)

@APP.route('/')
def inicio():
    return jsonify({'status': '200'})

@APP.route('/xentric/callback-status',methods=['POST'])
@cross_origin(cross_origin=ALLOWED_ORIGIN)
def register_status():
    
    if 'application/json' in request.headers['Content-Type']:       
        data = request.get_json()

        return status_callback(data)

    return "error"

@APP.route('/estadisticas_dashboard',methods=['POST'])
@cross_origin(cross_origin=ALLOWED_ORIGIN)
def estadisticas_dashboard():
    try:
        if 'application/json' in request.headers['Content-Type']:       
            data = request.get_json()
            response = estadisticas_llamadas(data)
            return jsonify({
                'estado': {
                    'codigo': "200",
                    'glosa': "ok"
                },
                'data': response,
            })
        else:
            return jsonify({
                'estado': {
                    'codigo': "400",
                    'glosa': "formato de entrada incorrecto"
                },
                'data': '',
            })

    except Exception as e:
        return jsonify({
            'estado': {
                'codigo': "400",
                'glosa': str(traceback.format_exc())
            },
            'data': '',
        })

@APP.route('/clientes_list',methods=['GET'])
@cross_origin(cross_origin=ALLOWED_ORIGIN)
def clientes_list():
    try:
        response = get_clientes()
        return jsonify({
            'estado': {
                'codigo': "200",
                'glosa': "ok"
            },
            'data': response,
        })
    except Exception as e:
        return jsonify({
            'estado': {
                'codigo': "400",
                'glosa': str(traceback.format_exc())
            },
            'data': '',
        })

    
# ----- Xentric voice endpoints -----
@APP.route('/xentric/voice_webhook', methods=['POST'])
@cross_origin(cross_origin=ALLOWED_ORIGIN)
@registro_errores.exception_asistente_texto
def voiceWebhook():
    """
    input:
        {
            "idCall": uuid,
            "from": str,
            "message": str
        }
    :return:
    """
    error_body = {
        'idCall': '',
        'from': request.json["from"] if 'from' in request.json else '123',
        'message': 'CallCid vacio',
        'reply_type': 'bye'
    }
    try:
        log = Datadog()
        log.send_log('json recibido por webbook desde xentric', request.json)
        if "idCall" in request.json and request.json["idCall"] == "":
                log.send_log('ERROR: id call vacio en la peticion', request.json, status_code=400, severity='ERROR')
                log.send_log('ERROR: Respuesta de request idCall vacio', error_body, status_code=400, severity='ERROR')
                return jsonify(error_body), 200
        print('Request desde voice_webhook')
        authCredentials = request.authorization
        if authCredentials is None or 'username' not in authCredentials or 'password' not in authCredentials:
            return asistente.formato_salida_texto(codigo=400, glosa='Faltan credenciales de usuario y contraseña.')

        if authCredentials.username != XENTRIC_USER or authCredentials.password != XENTRIC_PASS:
            return asistente.formato_salida_texto(codigo=400, glosa='Credenciales incorrectas!.')

        if 'application/json' in request.headers['Content-Type']:
            
            print('Validaciones iniciales completas!')
            print("###### REQUEST DESDE XENTRIC ###")
            print(request.json)
            data = xentricHandler(request.json)
            return data
    except Exception as e:
        log.send_log('error en webhook' + str(e), {}, status_code=400, severity='ERROR')

    return jsonify(error_body), 200

@APP.route('/history_conversation', methods = ['POST'])
def history_conversation():
    try:
        if request.json['cid'] is None or request.json['cid'] == '':
            print("HISTORY FALLO ---- CID VACIO")
            return jsonify({
                'estado': {
                    'codigo': "400",
                    'glosa': "cid no puede ser null/vacio"
                },
                'data': '',
            })
        return { "conversation": asic.history_conversation(request.json['cid']) }
    except Exception as e:
        return jsonify({
            'estado': {
                'codigo': "400",
                'glosa': str(traceback.format_exc())
            },
            'data': '',
        })

@APP.route('/soap', methods = ['POST'])
def soap():
    test = soap_service.create_order(request.json)
    return test

@APP.route('/soap_identification_card', methods = ['POST'])
def soap_identification_card():
    test = soap_service.query_identification_card(request.json)
    return test

@APP.route('/soap_query_ticket', methods = ['POST'])
def soap_consulta_ticket():
    test = soap_service.query_ticket(request.json)
    return test

@APP.route('/consulta_cedula')
def consulta_cedula():
    cedula =  '1122'
    result = asic.consultaCedula(cedula)
    status           = result.get("status")
    nombre_usuario   = result.get("nombre_usuario")
    apellido_usuario = result.get("apellido_usuario")
    return status

@APP.route('/consulta_ticket')
def consulta_ticket():
    dias_pendientes_ticket = "3"
    result = str(asic.consultaTicket(dias_pendientes_ticket))
    return result

@APP.route('/derivar')
def derivar():
    asignar_agentes = "sofia"
    result = str(asic.derivar(asignar_agentes))
    return result

@APP.route('/external_message', methods=['POST'])
@registro_errores.exception_asistente_texto
def message():
    """
    :return:
    """
    log = Datadog()
    log.send_log('request.json - /external_message', {})

    print("################ /external_message - request.json ##################")
    print(request.json)
    print("################  FIN ##############################################")

    if request.headers['Content-Type'] == 'application/json':
        if not asistente.validar_entrada(request.json):
            return asistente.formato_salida_texto(codigo=400, glosa='Error en parametros de entrada')
        return asistente.llamada_asistente_texto(request.json)
    return asistente.formato_salida_texto(codigo=400, glosa='Error en formato de request.')


@APP.route('/xentric/ivg_voice_webhook', methods=['POST'])
@cross_origin(cross_origin=ALLOWED_ORIGIN)
def voice_webhook_ivg():
    try:
        
        respuesta = request.json
        registrar_datadog_v2(data={"payload": respuesta}, status_code=200, severity='INFO', url_path='/xentric/ivg_voice_webhook')

        if 'application/json' in request.headers['Content-Type']:
            
            print("###### REQUEST DESDE IVG ###")
            print(respuesta)
            xentricMessage = respuesta['input']['text'] if 'text' in respuesta['input'] else None
            xentricMessage = xentricMessage.replace("#", "").replace("*", "")
            xentricIdCall = respuesta['context']['vgwSessionID'] if 'vgwSessionID' in respuesta['context'] else None
            xentricFrom = respuesta['context']['vgwSIPFromURI'] if 'vgwSIPFromURI' in respuesta['context'] else None
            xentricTo = respuesta['context']['vgwSIPToURI'] if 'vgwSIPToURI' in respuesta['context'] else None
            auxXentric ={
                'idCall': xentricIdCall,
                'from': xentricFrom.split("@")[0].split(":")[1],
                'message': xentricMessage,
                'to': xentricTo.split("@")[0].split(":")[1],
                'reply_type': 'option'
            }
            print("########## INPUT IVG ########")
            print("message: "+str(xentricMessage))

            if xentricMessage in ('vgwHangUp','vgwCallTransferred'):
                return jsonify({"message": xentricMessage}), 202
            
            dataResponse = xentricHandler(auxXentric)
            data = dataResponse[0].json
            msg = str(data["message"].replace("\n",""))

            if len(msg.split('$$$')) > 1:
                audio = json.loads(msg.split('$$$')[0])
                audio_url = list(audio.values())[0]
                audio_url = audio_url.replace('ivg.local',IP_IVG)
                msg = ''
                add_play_url = True
            else:
                add_play_url = False
            
            """
            if xentricMessage == '':
                audio_url = "https://assets-cgtva.s3.us-east-2.amazonaws.com/audios_tp_sura/bienvenida_sample_audio.wav"
                msg = ''
                add_play_url = True
            else:
                add_play_url = False
            """

            response_ivg ={
                        "intents": [], "entities": [], "input": {"text": ""},
                        "output":
                            {
                                "generic": [
                                    {"response_type": "text",
                                        'text': msg
                                    }
                                ],
                                "text":[msg]
                            },      
                        "context":{
                                    "metadata":{
                                        "user_id":respuesta['context']['metadata']["user_id"]
                                    },
                                    "vgwSIPFromURI":respuesta['context']['vgwSIPFromURI'],
                                    "vgwSIPToURI":respuesta['context']['vgwSIPToURI'],
                                    "vgwSessionID":respuesta['context']['vgwSessionID'],
                                    "vgwSIPCallID":respuesta['context']['vgwSIPCallID'],
                                    "vgwSIPRequestURI":respuesta['context']['vgwSIPRequestURI']         
                                    }
                        }

            if data["reply_type"] == "option" or data["reply_type"] == "number":
                response_ivg["output"]["vgwAction"] = {"command":"vgwActCollectDTMF", "parameters":{"dtmfMinCount":1,"dtmfIgnoreSpeech":"true","dtmfInterDigitTimeoutCount":2000} }
            if data["reply_type"] == "transfer":
                xentricTransferArgsTrunk = data["transfer_args"]["trunk"]
                xentricTransferArgsAni = data["transfer_args"]["ani"]
                xentricHexCid = data["transfer_args"]["hex_cid"]
                response_ivg["output"]["vgwAction"] = {
                    "command" : "vgwActTransfer",
                    "parameters":{"transferHeaders":{
                        "ani": xentricTransferArgsAni},
                        # "transferTarget": f"sip:{xentricTransferArgsTrunk}@{IP_CENTRAL}:5060",    # Solo de prueba
                        "transferTarget": f"sip:{xentricTransferArgsTrunk}@{IP_CENTRAL}:5060?User-to-User={xentricHexCid}",
                        "uuiData": xentricHexCid}
                        }
            if data["reply_type"] == "voice":
                response_ivg["output"]["vgwAction"] = {"command" : "vgwActDisableSTTDuringPlayback"}             
            if data["reply_type"] == "bye":
                response_ivg["output"]["vgwAction"] = {"command" : "vgwActHangup"}
            if add_play_url is True:
                response_ivg["output"]["vgwAction"] = {"command" : "vgwActPlayUrl", "parameters" : {"url": audio_url}}
            print(response_ivg)
            return jsonify(response_ivg)
    except Exception as _:
        registrar_datadog_v2(data={"traceback": traceback.format_exc(), "payload": respuesta}, 
            status_code=500, severity='ERROR', url_path='/xentric/ivg_voice_webhook')
        print(traceback.format_exc())
    
    return asistente.formato_salida_texto(codigo=400, glosa='Error en formato de request.')

if __name__ == '__main__':
    APP.run(debug=True)

