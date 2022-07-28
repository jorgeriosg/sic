
import mods.request_asic2 as service_request


def consulta_cedula(body):
    print("#######OBTENER GET USER DNI###")
    return service_request.get_user_dni(body)

# def consulta_cedula(body):
#     return service_request.wo_listado_usuario(body)

def caso_asic_inc(body):
    return service_request.inc_crear_asignado(body)

def caso_asic_wo(body):
    return service_request.crear_wo(body)


def consulta_ticket(body):
    return service_request.consultar_wo(body)

# def crear_wo(body):
#     return service_request.create_wo(body)

def crear_incidente(body):
    return service_request.create_incidente(body)































# import mods.response_conversation_builder as conversation
# import mods.soap_lib as soap_service

# def consulta_cedula(cedula_entregada):
#     datos_consulta = {"cedula":cedula_entregada}
#     print(datos_consulta, "aca")
#     if (cedula_entregada == '1122'):
#         result_status = 'True'
#         result = {"nombre_usuario":'Alberto', "apellido_usuario":'Gómez', "email_usuario":"","telefono_usuario":"","empresa_usuario":"","status":result_status}
#         datos_consulta.update(result)
   
#         return datos_consulta
#     else:
#         result_status = 'False'
#         result = {"nombre_usuario":'first name', "apellido_usuario":'lastName', "email_usuario":" intenet email", "telefono_usuario":"phone number", "empresa_usuario":"company", "status":result_status}
#         datos_consulta.update(result) 
#         return datos_consulta

# def consultaWoExistente(numero_ticket):
#     datos_consulta = {"numero_ticket":numero_ticket}
#     if (numero_ticket == '8899'):
#         result_status = 'True'
#         result = {"Work Order ID":"WO0000000"+numero_ticket, "estado_ticket":'cerrado', "status":result_status}
#         datos_consulta.update(result)
#         return datos_consulta
#     else:
#         result_status = 'False'
#         result = {"Work Order ID":"WO0000000"+numero_ticket, "estado_ticket":'abierto', "status":result_status}
#         datos_consulta.update(result) 
#         return datos_consulta
    