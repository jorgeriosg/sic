import re
import json
from flask import jsonify
from flask import request
from binascii import hexlify, unhexlify

from mods import bd
from mods import documentos
from mods import watson
from mods import datadog as dg
from views.asistente import llamada_asistente_texto as asistantCall
from mods.datadog2 import Datadog

def processMessage(request: dict) -> dict:
    """Process the request from the Xentric inbound user call, the main function of this
    process it is to handle new calls, formating data to utilize the existing process of
    messages.

    Args:

        request (dict): Xentric request json data as dict. Expected:
        {
            "idCall": uuid,
            "from": str,
            "message": str
        }

    Returns:

        dict: Xentric response format of data.
    """
    requiredFields = ['idCall', 'from', 'message']
    missingField = next((value for value in requiredFields if value not in request), None)

    if missingField is not None:
        return jsonify({'status': 400, 'msg': f'Falta el campo {missingField} en el request.'}), 400

    userPhone = request['from'] if 'from' in request else None
    userMessage = request['message'] if 'message' in request else ''
    xentricCallId = request['idCall'] if 'idCall' in request else None
    to = request['to'] if 'to' in request else None


    phoneDocument = documentos.buscar_interaccion_xentric_callId(xentricCallId)
    convContext = phoneDocument['interaction'] if 'interaction' in phoneDocument else None

    if not convContext:
        watsonClass = watson.WatsonV1()
        convContext = {
            'canal': 'voz',
            'userPhone': userPhone,
            'xentricCallId': xentricCallId,
            "to": to
        }
        convResponse = watsonClass.watson_call(input='', context=convContext)
        documentos.guardar_interaccion(conv_response=convResponse)
        if convResponse['context'] != {}:

            convResponse['conv_response'] = convResponse
            return __xentricResponse(request, convResponse)

        else:
            return __defaultResponse(userPhone, xentricCallId, replyType='bye')

    cid = convContext['context']['conversation_id']
    convContext["context"]["to"] = to
    asistantData = __asistantRequestParser(cid, convContext, msg=userMessage)
    assistantResponse = asistantCall(asistantData)

    assistantResponse = assistantResponse.json

    if assistantResponse['estado']['codigo'] == 200:
        return __xentricResponse(request, assistantResponse)
    else:
        return __defaultResponse(userPhone, xentricCallId, replyType='bye')

    return __defaultResponse(userPhone, xentricCallId, replyType='bye', message='En estos momentos no podemos atender su solicitud, que tengas buen día.')


def __xentricResponse(xentricRequest: dict, asistantResponse: dict) -> dict:
    """Default format for the response to Xentric service to be sent

    Args:
        xentricRequest (dict): The requeste received from Xentric.
        asistantResponse (dict): The response received from the asistant view.

    Returns:
        Response: The response formated from the handling.
    """
    userPhone = xentricRequest['from'] if 'from' in xentricRequest else None
    xentricCallId = xentricRequest['idCall'] if 'idCall' in xentricRequest else None
    replyType = 'voice'
    responseMessage = ''

    convResponse = asistantResponse['conv_response']

    if 'conv_response' in convResponse:
        convResponse.pop('conv_response')
    
    log = Datadog()
    log.send_log("conv response en xentric", convResponse)
    responseMessage = ''.join(convResponse['output']['text']) if 'output' in convResponse and 'text' in convResponse['output'] and convResponse['output']['text'] else ''
    log.send_log("response message: " + responseMessage)
    if 'context' in convResponse:
        responseContext = convResponse['context']

        if 'xentric_reply_type' in responseContext:
            replyType = responseContext['xentric_reply_type']
            convResponse['context'].pop('xentric_reply_type')
            documentos.guardar_interaccion(conv_response=convResponse, tipo_documento='xentric_call')
    if 'derivar' in asistantResponse:    
        derivar = asistantResponse['derivar']
    else:
        derivar = False
    if 'anexo_vdn' in responseContext:
        vdn = responseContext['anexo_vdn']
    else:
        vdn = ''

    if 'derivar_mensaje' in responseContext and len(convResponse['output']['text']) <= 1:
        responseMessage = responseContext['derivar_mensaje']

    if 'conversation_id' in responseContext:
        cid = responseContext['xentricCallId']
    else:
        cid = ''
    return __defaultResponse(userPhone, xentricCallId, replyType=replyType, message=responseMessage, vdn=vdn, cid=cid, derivar=derivar)


def __asistantRequestParser(cid: str, convResponse: dict, msg: str) -> dict:
    """Formater of data to use the actual asistant process

    Args:

        cid (str): Cconversation ID generated from watson.
        msg (str): Message to send to watson.
        convResponse (dict): conv_response from the mongodb.

    Returns:

        dict: A dict of data simulating the minumum for the asistant process.
    """
    formatedData = {
        'general': {
            'cid': cid,
            'origen': 6
        },
        'msg': [
            msg
        ],
        'conv_response': convResponse
    }
    return formatedData


def __defaultResponse(userPhone: str, xentricCallId: str, replyType: str = 'voz', message: str = None, vdn: str = None, cid: str = None, derivar: str = None) -> dict:
    """Default formater to return to xentric request

    Args:

        userPhone (str): The phone number from the user who made the call.
        xentricCallId (str): UUid generated from Xentric.
        replyType (str, optional): The type of reply expected to receive. Defaults to 'voz'.
        message (str, optional): The message to return to the user. Defaults to None and setted to an error response.

    Returns:

        dict: Response formated with code 200.
    """
    message = 'En estos momentos tenemos problemas en nuestro asistente, por favor intentalo mas tarde.' if message is None else message
    responseFormat = {
        'idCall': xentricCallId,
        'from': userPhone,
        'message': message,
        'reply_type': replyType
    }
    if derivar:
        responseFormat['reply_type'] = 'transfer'
        responseFormat['transfer_args'] = {"trunk": vdn, "ani": cid, "hex_cid": cid_to_hex(cid)}
    datadogInfo = {
        'request': request.json,
        'response': responseFormat
    }
    log = Datadog()
    log.send_log('respuesta de webhook a xentric', responseFormat)
    dg.registrar_datadog_v2(data=datadogInfo, status_code=200, severity='INFO', url_path='/xentric/voice_webhook')
    return jsonify(responseFormat), 200

def cid_to_hex(cid):
    hex_cid = hexlify(cid[:12].encode())
    str_cid = hex_cid.decode("utf-8")
    # str_cid = f"04{str_cid};encoding=hex"
    # str_cid = f"04C8{str_cid};encoding=hex"
    str_cid = f"04C80C{str_cid};encoding=hex"
    return str_cid