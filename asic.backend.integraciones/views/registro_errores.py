import functools
import traceback
from flask import jsonify
import uuid
import flask
#from librerias.config import logger
import mods.datadog as datadog


def formato_salida_voz(msg=None,cid=None,cmd=[],mid=None):
    return jsonify({
        'cid':cid,
        "cmd": [
            {
                "command": "vgwActCollectDTMF",
                "parameters": {
                    "dtmfMaxCount": "9"
                }
            },
            {
                "command": "vgwActDisableSTTDuringPlayback"
            },
            {
                "command": "vgwActPlayText",
                "parameters": {
                    "text": [
                        msg
                    ]
                }
            }
        ],
        'mid':mid
            }
        )


def formato_salida_texto(codigo=400,glosa='',conv_response={}):        
    return jsonify({
            'estado':{
                'codigo':codigo,
                'glosa':glosa
            },
            'conv_response':conv_response
            }
        )
    
def formato_salida_sixbell(codigo=200,jwt='',sessionId='',message_type='',text=''):        
    return jsonify(
            {
                "jwt": jwt,
                "sessionId": sessionId,
                "message_type": message_type,
                "text": text
            }
        ),codigo

def exception_asistente_texto(function):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        try:
            return function(*args, **kwargs)
        except Exception as e:
            # log the exception
            msg = 'En este momento no cuento con la información necesaria para darte una respuesta. Te recomiendo que lo intentes más tarde.'
            cmd = []
            cid = None
            mid = None
            try:
                data = flask.request.get_json()
                cid = data['general']['cid']
                datadog.registrar_datadog(error='cid: '+str(cid)+' '+traceback.format_exc(),status_code=500)
                #logger.error(traceback.format_exc())
            except:
                print(traceback.format_exc())
                pass
            return formato_salida_texto(codigo=400,glosa=traceback.format_exc())

            # re-raise the exception
            raise
    return wrapper

def exception_asistente_voz(function):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        try:
            return function(*args, **kwargs)
        except Exception as e:
            # log the exception
            msg = 'En este momento no cuento con la información necesaria para darte una respuesta. Te recomiendo que lo intentes más tarde.'
            cmd = []
            cid = None
            mid = None
            print (traceback.format_exc())
            try:
                data = flask.request.get_json()
                cid = data['cid']
                mid = data['mid']
                datadog.registrar_datadog(error='cid: '+str(cid)+' '+traceback.format_exc(),status_code=500)
                #logger.error(traceback.format_exc())
            except:
                pass
            return formato_salida_voz(msg=msg,cid=cid,cmd=cmd,mid=mid)

            # re-raise the exception
            raise
    return wrapper


def exception_whatsapp_sixbell(function):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        try:
            return function(*args, **kwargs)
        except Exception as e:
            # log the exception
            text = 'En este momento no cuento con la información necesaria para darte una respuesta. Te recomiendo que lo intentes más tarde.'
            jwt = ''
            sessionId = ''
            message_type = ''
            print(traceback.format_exc())
            return formato_salida_sixbell(codigo=400,jwt=jwt,sessionId=sessionId,message_type=message_type,text=str(e))

            # re-raise the exception
            raise
    return wrapper


def exception_whatsapp_sixbell_v1_1(function):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur
    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        try:
            return function(*args, **kwargs)
        except Exception as e:
            # log the exception
            
            error_description = traceback.format_exc()
            error_code = str(uuid.uuid1())
            data = {}
            try:
                data = flask.request.get_json()
            except:
                pass
            
            try:
                inp = {
                        'data':data,
                        'error_code':error_code,
                        'error_description':error_description
                    }
                datadog.print_datadog(input=inp,status_code=500,severity='ERROR')
            except:
                pass
            
            return jsonify({
                        "estado":"error "+error_code+" contactar con administrador de app."
                    }),400

            # re-raise the exception
            raise
    return wrapper