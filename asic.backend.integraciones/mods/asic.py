#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mods.response_conversation_builder as conversation
import mods.soap_lib as soap_service

def consultaCedula(cedula_entregada):
    datos_consulta = {"cedula":cedula_entregada}
    if (cedula_entregada == '1122'):
        result_status = 'True'
        result = {"nombre_usuario":'Alberto', "apellido_usuario":'Gómez', "status":result_status}
        datos_consulta.update(result)
        return datos_consulta
    else:
        result_status = 'False'
        result = {"nombre_usuario":'name', "apellido_usuario":'lastName', "status":result_status}
        datos_consulta.update(result) 
        return datos_consulta

def consultaTicket(dias_pendientes_ticket_entregado, numero_ticket_entregado):
    datos_consulta = {"dias_pendientes_ticket":dias_pendientes_ticket_entregado, "numero_ticket":numero_ticket_entregado}
    if (dias_pendientes_ticket_entregado == '3'):
        if (numero_ticket_entregado   == '2233'):
            ticket_status = "cerrado"
            result_status = 'True'
        elif (numero_ticket_entregado == '3344'):
            ticket_status = "abierto"
            result_status = 'True'
        elif (numero_ticket_entregado == '4455'):
            ticket_status = "asignado"
            result_status = 'True'
        elif (numero_ticket_entregado == '5566'):
            ticket_status = "pendiente"
            result_status = 'True'
        else:
            ticket_status = "not_found"
            result_status = 'False'

        result = {'status':result_status, 'estado_ticket':ticket_status}
        datos_consulta.update(result)
        return datos_consulta
    else:
        result_status = False
        result = {'status':result_status}
        datos_consulta.update(result) 
        return datos_consulta

def derivar(asignar_agentes):
    values = ['sofia', 'correo', 'vpn', 'install', 'normal','garantia']
    if asignar_agentes in values:
        return True
    else:
        return False

def nuevoTicket(nuevo_ticket):
    datos_consulta = {}
    if(nuevo_ticket == '8899'):
        result = {'nuevo_ticket_numero':nuevo_ticket, 'nuevo_ticket': 'True'}
        datos_consulta.update(result) 
        return datos_consulta
    else:
        result = {'nuevo_ticket_numero':'not_found', 'nuevo_ticket':'not_found'}
        datos_consulta.update(result) 
        return datos_consulta

def caso_asic(body):
    return soap_service.create_order(body)

def consulta_cedula(body):
    return soap_service.query_identification_card(body)

def consulta_ticket(body):
    return soap_service.query_ticket(body)

def history_conversation(cid):
    # Add toAnswer as null or not exists to query
    # return struct_base(cid)
    return conversation.build(cid)

def struct_base(cid):
    return {"title": 'Historial de conversacion',"date": '13-02-2020',"cliente": {"id": 1,"rut": '15.849.339-2',"nombre": 'Pablo Briones'},"conversation": [{"id": 1,"date": '13-02-2020',"hour": '14:32',"msg": 'Bienvenido!'},{"id": 1,"date": '13-02-2020',"hour": '14:32',"msg": 'Indíqueme la razón de su llamado'},{"id": 2,"date": '13-02-2020',"hour": '14:32',"msg": 'Tengo problemas con la impresora'},{"id": 2,"date": '13-02-2020',"hour": '14:32',"msg": 'Necesito ayuda'},{"id": 1,"date": '13-02-2020',"hour": '14:32',"msg": '¿Es primera vez que llama por esto ?'},{"id": 2,"date": '13-02-2020',"hour": '14:32',"msg": 'Así es, primera vez que ocurre esto'},{"id": 1,"date": '13-02-2020',"hour": '14:32',"msg": 'Lo transfiero con el área especialista'}]}

