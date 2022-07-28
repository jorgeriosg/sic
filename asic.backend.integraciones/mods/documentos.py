import datetime
import traceback
import mods.bd as bd
import mods.datadog as datadog

def guardar_interaccion(conv_response={},enviar_dashbot=False,tipo='business',tipo_documento='watson',telefono=''):
    """
    :param conv_response:
    :param type:
    :param ws_name:
    :param dashbot:
    :return:
    """

    document = {
        'interaction': conv_response,
        'datetime': datetime.datetime.utcnow(),
        'workspace_type': tipo,
        'tipo_documento':tipo_documento,
        'telefono':telefono
    }
        
    _id = bd.mongo_Connect().insert_one(document)
    return str(_id.inserted_id)

def guardar_interaccion_agente(documento={}):
    """
    :param conv_response:
    :param type:
    :param ws_name:
    :param dashbot:
    :return:
    """ 
    _id = bd.mongo_Connect_agents().insert_one(documento)
    return str(_id.inserted_id)

def buscar_interaccion(cid=None, sort=False):
    """
    :param cid:
    :param type:
    :return:
    """
    find_str = {'interaction.context.conversation_id': cid}
    if sort:
        last_interaction = bd.mongo_Connect().find(find_str).sort('datetime', 1)
        if last_interaction is not []:
            last_interaction = list(last_interaction)
        return last_interaction
    
    last_interaction = bd.mongo_Connect().find(
        find_str
    ).sort('datetime', 1)
    if last_interaction is not []:
        try:
            last_interaction = list(last_interaction)
        except:
            #datadog.registrar_datadog(error=traceback.format_exc()+' '+str(cid),status_code=500)
            last_interaction = []
    return last_interaction

def buscar_interaccion_xentric(cid=None, sort=False):
    """
    :param cid:
    :param type:
    :return:
    """
    find_str = {'interaction.context.xentricCallId': {"$regex":"^" + str(cid)}, "tipo_documento": "watson"}
    if sort:
        last_interaction = bd.mongo_Connect().find(find_str).sort('datetime', 1)
        if last_interaction is not []:
            last_interaction = list(last_interaction)
        return last_interaction
    
    last_interaction = bd.mongo_Connect().find(
        find_str
    ).sort('datetime', 1)
    if last_interaction is not []:
        try:
            last_interaction = list(last_interaction)
        except:
            #datadog.registrar_datadog(error=traceback.format_exc()+' '+str(cid),status_code=500)
            last_interaction = []
    return last_interaction


def buscar_interaccion_sessionId(sessionId=None, sort=False):
    """
    :param cid:
    :param type:
    :return:
    """
    find_str = {'interaction.context.sessionId': sessionId}
    if sort:
        last_interaction = bd.mongo_Connect().find(find_str).sort('datetime', 1)
        if last_interaction is not []:
            last_interaction = list(last_interaction)
        return last_interaction
    
    last_interaction = bd.mongo_Connect().find(
        find_str
    ).sort('datetime', 1)
    if last_interaction is not []:
        try:
            last_interaction = list(last_interaction)
        except:
            #datadog.registrar_datadog(error=traceback.format_exc()+' '+str(cid),status_code=500)
            last_interaction = []
    return last_interaction

def eliminar_interacciones_sessionId(sessionId=None):
    delete_str = {'interaction.context.sessionId': sessionId}
    x = bd.mongo_Connect().delete_many(delete_str)
    if x:
        return True
    else:
        return False


def buscar_interaccion_xentric_callId(xentricCallId: str = None, sort: bool = False) -> dict:
    """Search for an mongodb documment from the xentric call id in interaction.context data

    Args:

        xentricCallId (str, optional): The uuid generated from xentric. Defaults to None.
        sort (bool, optional): Indicates if you want to default sort the data. Defaults to False.

    Returns:

        dict: The document as dicttionary of data.
    """
    find_str = {'interaction.context.xentricCallId': xentricCallId}
    if sort:
        last_interaction = bd.mongo_Connect().find(find_str).sort('datetime', 1)
        if last_interaction is not []:
            last_interaction = list(last_interaction)
        return last_interaction

    last_interaction = bd.mongo_Connect().find(
        find_str
    ).sort('datetime', -1).limit(1)
    if last_interaction is not []:
        try:
            last_interaction = list(last_interaction)[0]
        except Exception as unknownError:
            # datadog.registrar_datadog(error=traceback.format_exc()+' '+str(cid),status_code=500)
            last_interaction = []
    return last_interaction