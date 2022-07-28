# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from mods.factory import FactoryIntegration
from mods import asic
from datetime import timedelta
import datetime
import re
import json
import unidecode
import traceback
import mods.utilities.validadores as validadores
import mods.bd as bd
import mods.utilities.fechas as fechas
import mods.utilities.listas as listas
import mods.datadog as datadog
import mods.utilities.fechas as fechas
import mods.flujo
from mods.datadog2 import Datadog

"""
llamada_vdn_30550 -> derivar a ejecutivo al vdn 30550 
consultar_ips -> consulta datos del usuario con un número de identificación
llamada_vdn_acorde_ips -> derivar a ejecutivo al vdn de cada usuario 
sms_turno -> enviar un sms de turno virtual (mensaje pendiente) 
estado_afiliacion -> se consulta después de los datos del ips
sms_ips -> enviar el mensaje con los datos del ips
"""


def integraciones_toAnswer(conv_response={}):
    print("################################")
    print("conv_response IN")
    print(conv_response)
    datadog.registrar_datadog_v2(
        data=conv_response, status_code=200, severity='INFO')
    base = bd.MysqlBD()
    hay_integracion = False
    nueva_llamada = False
    derivar = False
    context = conv_response['context'] if 'context' in conv_response else {}
    log = Datadog()
    log.send_log('recibido por integraciones_toAnswer', conv_response)

    platform_toanswer = context['toAnswer']
    platform_context = context['plataforma']
    if 'toAnswer' in context and 'plataforma' in context:
        platform_module = FactoryIntegration.get_integration(
            platform_toanswer, platform_context)

        if context['toAnswer'] == 'obtener_catalogo':
            hay_integracion = True
            nueva_llamada = True
            response = platform_module.obtener_catalago(context)
            conv_response['context'].update(response)
            print(conv_response)
        elif context['toAnswer'] == 'caso_asic':
            hay_integracion = True
            nueva_llamada = True
            if context['asic_req'] == 'WO':
                response = platform_module.caso_asic_wo(context)
            elif context['asic_req'] == 'INC':
                response = platform_module.caso_asic_inc(context)
            else:
                response = platform_module.caso_asic(context)
            print(response,"############# prueba")
            conv_response['context'].update(response)
            conv_response['context']['error'] = False
            conv_response['context']['caso_asic'] = response['caso_asic']
            conv_response['context']['caso_asic_2'] = response['caso_asic_2']
            
            print(conv_response)
        elif context['toAnswer'] == 'consulta_cedula':
            hay_integracion = True
            nueva_llamada = True
            response = platform_module.consulta_cedula(context)
            conv_response['context'].update(response)
            print(conv_response)
        elif context['toAnswer'] == 'consulta_ticket':
            hay_integracion = True
            nueva_llamada = True
            response = platform_module.consulta_ticket(context)
            conv_response['context'].update(response)
            print(conv_response)
        elif context['toAnswer'] == 'token':
            response = platform_module.enviar_token(context)
            conv_response['context'].update(response)
            print(conv_response)
        elif context['toAnswer'] == 'consulta_app':
            hay_integracion = True
            nueva_llamada = True
            response = platform_module.consulta_app(context)
            conv_response['context'].update(response)
            print(conv_response)

        elif context['toAnswer'] == 'crear_transaccion':
            hay_integracion = True
            nueva_llamada = True
            context.update(platform_module.buscar_transaction_bd(context))
            if context['estado_solicitud']:
                context.update(platform_module.consulta_transaccion(context))
                if context['status'] not in ('no exitoso', 'pendiente', 'proceso'):
                    context.update(platform_module.crear_transaccion(context))
                else:
                    context.update(
                        {'consulta_transaccion': False, 'crear_transaccion': False, 'status': 'no exitoso'})
            else:
                context.update(platform_module.crear_transaccion(context))
            print(conv_response)
        elif context['toAnswer'] == 'ticket_derivar':
            hay_integracion = True
            nueva_llamada = True
            response = platform_module.caso_asic(context)
            conv_response['context']['error'] = response['error']
            conv_response['context']['caso_asic'] = response['caso_asic']
            print(conv_response)
            asignar_agentes = conv_response['context']['asignar_agentes']
            response = asic.derivar(asignar_agentes)
            conv_response['context']['derivar'] = response
            derivar = True
        elif context['toAnswer'] == 'derivar':
            hay_integracion = True
            nueva_llamada = True
            asignar_agentes = conv_response['context']['asignar_agentes']
            response = asic.derivar(asignar_agentes)
            conv_response['context']['derivar'] = response
            derivar = True
            print(conv_response)
        elif context['toAnswer'] == "consultaWoExistente":
            hay_integracion = True
            nueva_llamada = True
            response = platform_module.consulta_wo(context)
            conv_response['context'].update(response)
            print(conv_response)
        elif context['toAnswer'] == 'nuevo_ticket':
            hay_integracion = True
            nueva_llamada = True
            nuevo_ticket = '8899'
            response = platform_module.nuevoTicket(context)
            conv_response['context']['nuevo_ticket'] = response.get(
                'nuevo_ticket')
            conv_response['context']['nuevo_ticket_numero'] = response.get(
                'nuevo_ticket_numero')
        else:
            pass
    else:
        pass

    conv_response['context']['toAnswer'] = None
    del base
    print("")
    print("conv_response OUT")
    print(conv_response)
    return hay_integracion, conv_response, nueva_llamada, derivar


def guardar_sesion(base=None, cid='', pais='', region='', comuna='', input='', output='', canal=1, api_call=0, tipo_usuario='', rut='', derivado=0, tipo_derivacion='', stayResponse=''):
    if base:
        base_aux = base
    else:
        base_aux = bd.MysqlBD()

    conversacion = '<input>' + input + '</input><output>' + output + '</output>\n'

    parametros = (cid, pais, region, comuna, 1, conversacion, canal, api_call, tipo_usuario, rut, derivado,
                  tipo_derivacion, pais, region, comuna, conversacion, api_call, tipo_usuario, rut, derivado, tipo_derivacion,)
    query = """INSERT into sesiones(cid,pais,region,comuna,interacciones,conversacion,canal,inicio,fin,api_call,tipo_usuario,rut, derivado, tipo_derivacion) VALUES (%s,%s,%s,%s,%s,%s,%s,CURRENT_TIME,CURRENT_TIME,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE
    pais = %s,
    region = %s,
    comuna = %s,
    interacciones = interacciones + 1,
    conversacion = CONCAT(sesiones.conversacion, %s),
    fin = CURRENT_TIME,
    api_call = api_call + %s,
    tipo_usuario = %s,
    rut = %s,
    derivado = %s,
    tipo_derivacion= %s
    """
    insertado, resultado = base_aux.insert(query, parametros)

    if stayResponse:
        query_stay = """ INSERT INTO dialog_topicos(cid,topico,id_canal) VALUES(%s,%s,%s) """
        parametros_stay = (cid, stayResponse, canal)
        insertado_stay, resultado_stay = base_aux.insert(
            query_stay, parametros_stay)

    del base_aux
    return insertado, resultado


def buscar_plantilla(tipo=''):
    try:
        base_aux = bd.MysqlBD()
        query = """SELECT plantilla from parametros_pdf WHERE tipo = %s """
        exito, datos = base_aux.find_one(query, (tipo))
        return exito, datos['plantilla']
    except Exception as e:
        return False, str(e)


def registrar_seguimiento(seguimiento={}, dni=''):
    try:
        base_aux = bd.MysqlBD()

        query = """SELECT * FROM ciclo_cuarentena where dni_paciente =  %s and activo= 1 order by fecha_fin desc limit 1"""
        parametros = (dni,)
        exito, ciclo = base_aux.find_one(query, parameters=parametros)

        # ciclo activo
        if exito and 'id' in ciclo:
            fecha_seguimiento = datetime.datetime.now().replace(
                hour=00, minute=00, second=00, microsecond=00)
            query_seguimiento = """SELECT * FROM seguimiento_diario WHERE id_ciclo_cuarentena = %s and fecha = %s """
            parametros = (ciclo['id'], fecha_seguimiento,)
            exito_seguimiento, ciclo_seguimiento = base_aux.find_one(
                query_seguimiento, parameters=parametros)
            if exito_seguimiento:
                # update
                query_update_seguimiento = """ UPDATE seguimiento_diario SET
                    sintomas = %s
                    WHERE id = %s
                    """
                parametros = (json.dumps(seguimiento), ciclo_seguimiento['id'])
                exito_update, datos_update = base_aux.update(
                    query_update_seguimiento, parameters=parametros)
                if exito_update:
                    exito = 200
                    datos = 'Actualizado correctamente'
                else:
                    exito = 400
                    datos = str(datos_update)
            else:
                # insert
                query_insert_seguimiento = """ INSERT INTO seguimiento_diario(id_ciclo_cuarentena,fecha,sintomas,fecha_actualizacion) VALUES (%s,%s,%s,CURRENT_TIMESTAMP) """
                parametros = (ciclo['id'], fecha_seguimiento,
                              json.dumps(seguimiento),)
                exito_insert, datos_insert = base_aux.insert(
                    query_insert_seguimiento, parameters=parametros)
                if exito_insert:
                    exito = 200
                    datos = 'Insertado correctamente'
                else:
                    exito = 400
                    datos = str(datos_insert)
        else:
            exito = 400
            datos = 'No existe un ciclo activo de cuarentena'

        return exito, datos
    except Exception as e:
        return False, str(e)


def buscar_info_usuario(id_usuario=0):
    try:
        base_aux = bd.MysqlBD()

        query = """
            SELECT p.name as name,
                p.last_name as last_name
            FROM user
            INNER JOIN user_person_company upc
            ON upc.user_id = user.id
            INNER JOIN person as p
            ON upc.person_id = p.id
            WHERE user.id = %s
        """
        resultado, datos = base_aux.find_one(query, (id_usuario,))
        del base_aux
        return resultado, datos
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    # apellido_medico = unidecode.unidecode('Henriquez')
    pass
