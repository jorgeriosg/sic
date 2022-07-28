import datetime
import json
import requests
from ibm_watson import AssistantV1
from ibm_watson import AssistantV2
import mods.bd as bd
import mods.rest as rest
import traceback

from mods.datadog import registrar_datadog
from mods.config import CONV_VERSION, CONV_TIMEOUT, CONV_INTENTOS


class WatsonV1():
    """ Clase para conectarse con proyectos que utilizan instancias con Watson V1:
        Workspace ID
        Username
        Password
     """
    CRED_CC = []
    CRED_FAQ = []
    CONV_FAQ = []
    CONV_CHITCHAT = []

    def __init__(self, url=None, version='2019-02-28'):
        self.CRED_CC, self.CRED_FAQ = self.credenciales_watson()

    def credenciales_watson(self):
        base = bd.MysqlBD()
        query = "SELECT * FROM credenciales ORDER BY id"
        parametros = ()
        existen_credenciales, result = base.find_all(query, parametros)
        chitchat_cred = {}
        business_cred = {}
        chitchat = 1
        business = 1
        if existen_credenciales:
            for res in result:
                if res['tipo'] == 'chitchat':
                    nombre = 'instancia%s' % (str(chitchat))
                    chitchat_cred[nombre] = {
                        'url': res['url'],
                        'wid': res['workspace'],
                        'clave': res['pass'],
                        'usuario': res['user'],
                        'instancia': res['instancia']
                    }
                    chitchat += 1

                if res['tipo'] == 'business':
                    nombre = 'instancia%s' % (str(business))
                    business_cred[nombre] = {
                        'url': res['url'],
                        'wid': res['workspace'],
                        'clave': res['pass'],
                        'usuario': res['user'],
                        'instancia': res['instancia']
                    }
                    business += 1
        return chitchat_cred, business_cred

    def watson_call(self, input=None, context={}, tipo='business', intentos=0, traceback=None):
        """
        :param wid:
        :param input:
        :param context:
        :param type:
        :return:
        """
        conv_response = {
            'context': context
        }
        headers = {'Content-Type': 'application/json'}

        data = json.dumps(
            {
                'input': {
                    'text': input
                },
                'context': context
            }
        )
        if intentos == CONV_INTENTOS:
            desc = 'Error en recursividad'
            registrar_datadog('Error en recursividad')
        else:
            if intentos % 2 == 0:

                credenciales = self.CRED_FAQ['instancia1']
                try:
                    conv_response = requests.post(credenciales['url'] + credenciales['wid'] + "/message?version=" + CONV_VERSION, auth=(credenciales['usuario'], credenciales['clave']), data=data, headers=headers, timeout=5)

                    if conv_response.status_code == 200:
                        conv_response = json.loads(conv_response.text)
                    else:
                        intentos += 1
                        return self.watson_call(input, context, tipo, intentos=intentos, traceback=conv_response.text)
                except requests.exceptions.Timeout as e:
                    intentos += 1
                    return self.watson_call(input, context, tipo, intentos=intentos, traceback=traceback.format_exc())
                except requests.exceptions.RequestException as e:
                    intentos += 1
                    return self.watson_call(input, context, tipo, intentos=intentos, traceback=traceback.format_exc())
            elif intentos % 2 == 1:
                credenciales = self.CRED_FAQ['instancia2']
                try:
                    conv_response = requests.post(credenciales['url'] + credenciales['wid'] + "/message?version=" + CONV_VERSION, auth=(credenciales['usuario'], credenciales['clave']), data=data, headers=headers,timeout=5)
                    if conv_response.status_code == 200:
                        conv_response = json.loads(conv_response.text)
                    else:
                        intentos += 1
                        return self.watson_call(input,context,tipo,intentos=intentos,traceback=conv_response.text)
                except requests.exceptions.Timeout as e:
                    intentos += 1
                    return self.watson_call(input,context,tipo,intentos=intentos,traceback=traceback.format_exc())
                except requests.exceptions.RequestException as e:
                    intentos += 1
                    return self.watson_call(input,context,tipo,intentos=intentos,traceback=traceback.format_exc())
        return conv_response

    def chitchat_call(self, texto='', cid=None, context={}):
        conv_response = self.watson_call(input=texto, tipo='chitchat', context=context)
        texto_salida = conv_response['output']['generic'][0]['text']
        es_chitchat = False
        if texto_salida != 'NO CAMBIAR':
            es_chitchat = True
        return es_chitchat,texto_salida,conv_response
    

class WatsonV2():
    """ Clase para conectarse con proyectos que utilizan instancias con Watson V2 
        Workspace ID
        Username:apikey
        Password
    """
    credenciales = []
    conv = [] 
    assistant_id = ''
    session_id = ''


    def __init__(self,url=None,version='2019-02-28',tipo='business'):
        self.credenciales = self.credenciales_watson(tipo=tipo)
        self.conv = AssistantV2(
            iam_apikey=self.credenciales['usuario'],
            version=version
            )

        response = self.conv.create_session(
            assistant_id=self.assistant_id
        ).get_result()
        
        resp_json = json.dumps(response, indent=2)
        self.session_id = resp_json['session_id'] if 'session_id' in resp_json else ''
    
    
    def credenciales_watson(self,tipo='business'):
        base = bd.PostgreBD()
        query = "SELECT * FROM credenciales_watson WHERE version_watson = 'v2' and tipo = %s ORDER BY id"
        parametros = (tipo)
        existen_credenciales,result = base.find_one(query,parametros)
        credenciales = {}
        if existen_credenciales:
            credenciales.update({"usuario":result['usuario']})
            credenciales.update({"clave": result['clave']})
            credenciales.update({"wid": result['wid']})
        return credenciales


    def watson_call(self, input=None,input_type='text',context={}, tipo='business'):
        """
        :param wid:
        :param input:
        :param context:
        :param type:
        :return:
        """
        cambio_workspace = False
        conv_response = {}
        if tipo == 'chitchat':
            response = self.conv.message(
                assistant_id=self.assistant_id,
                session_id=self.session_id,
                return_context=True,
                context=context,
                input={
                    'message_type': input_type,
                    'text': input
                }
            ).get_result()
            conv_response = json.dumps(response, indent=2)
            texto_salida = conv_response['output']['generic'][0]['text']
            if texto_salida != 'NO CAMBIAR':
                cambio_workspace = True
        else:
            response = self.conv.message(
                assistant_id=self.assistant_id,
                session_id=self.session_id,
                return_context=True,
                context=context,
                input={
                    'message_type': input_type,
                    'text': input
                }
            ).get_result()
            conv_response = json.dumps(response, indent=2)
        return cambio_workspace,conv_response


class WatsonCurl():
    CRED_CC = []
    CRED_FAQ = []
    CONV_FAQ = []
    CONV_CHITCHAT = []   
    URL = 'https://gateway.watsonplatform.net/assistant/api/v1/'
    VERSION = '2019-02-28'
    HEADERS = {'Content-Type': 'application/json'}
    
    def __init__(self,url=None,version='2019-02-28'):
        self.CRED_CC, self.CRED_FAQ = self.credenciales_watson()
        self.URL = url if url else self.URL
        self.VERSION = version if version else self.VERSION
        #self.CONV_FAQ = AssistantV1(username=self.CRED_FAQ['usuario'], password=self.CRED_FAQ['clave'], version='2019-02-28')
        #self.CONV_CHITCHAT = AssistantV1(username=self.CRED_CC['usuario'], password=self.CRED_CC['clave'], version='2019-02-28') 
    
    def credenciales_watson(self):
        base = bd.PostgreBD()
        query = "SELECT * FROM credenciales_watson WHERE version_watson = 'v1' ORDER BY id"
        parametros = ()
        existen_credenciales,result = base.find_all(query,parametros)
        chitchat_cred = {}
        business_cred = {}
        if existen_credenciales:
            for res in result:
                if res['tipo'] == 'chitchat':
                    chitchat_cred.update({"usuario":res['usuario']})
                    chitchat_cred.update({"clave": res['clave']})
                    chitchat_cred.update({"wid": res['wid']})
        
                if res['tipo'] == 'business':
                    business_cred.update({"usuario": res['usuario']})
                    business_cred.update({"clave": res['clave']})
                    business_cred.update({"wid": res['wid']})
        return chitchat_cred, business_cred

    def watson_call(self, input=None, context={}, tipo='business'):
        """
        :param wid:
        :param input:
        :param context:
        :param type:
        :return:
        """
        conv_response = {}
        if tipo == 'chitchat':
            wid = self.CRED_CC['wid']
            url = self.URL + 'workspaces/%s/message?version=%s'%(wid,self.VERSION)
            
            data = {
                'input':input,
                'context':context
            }
            error,r = rest.llamado_recursivo_seguro(metodo='POST',url=url,data=data,headers=self.HEADERS,timeout=3,auth=(self.CRED_FAQ['usuario'],self.CRED_FAQ['clave']))
            print(r.text)
            return json.loads

        wid = self.CRED_FAQ['wid']
        url = self.URL + 'workspaces/%s/message?version=%s'%(wid,self.VERSION)
        
        data = {
            'input':input,
            'context':context
        }
        error,r = rest.llamado_recursivo_seguro(metodo='POST',url=url,data=data,headers=self.HEADERS,timeout=3,auth=(self.CRED_FAQ['usuario'],self.CRED_FAQ['clave']))
        
        print(r.text)
        return json.loads(r.text)