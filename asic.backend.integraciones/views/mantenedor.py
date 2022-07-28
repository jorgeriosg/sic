import mods.bd as bd
import mods.base64_encoder as b64
import mods.csv_generator as csv_generator
import datetime

def format_fecha(fecha, time):
	aux = fecha.split("/")
	aux_2 = aux[2] + "-" + aux[1] + "-" + aux[0]
	aux_2 = aux_2 + " " + time
	return aux_2

def get_clientes():
	data_base = bd.MysqlBD()
	data = {
		'clientes': []
	}
	query = """SELECT id_cliente, nombre_cliente FROM parametros_cliente WHERE estado=1 ORDER BY 2;"""
	query_response = data_base.find_all(query)
	for x in query_response[1]:
		data['clientes'].append({
				"id": x['id_cliente'],
				"nombre_cliente": x['nombre_cliente']
			})
	return data

def estadisticas_llamadas(request):
	# {
	#     fecha_inicio: “”,
	#     fecha_termino: “”,
	#     id_cliente: “”,
	# }
	fecha_ini = format_fecha(request["fecha_inicio"], "00:00:00")
	fecha_fin = format_fecha(request["fecha_termino"], "23:59:59")
	
	fecha_ini_mongo = format_fecha(request["fecha_inicio"], "T00:00:00")
	fecha_fin_mongo = format_fecha(request["fecha_termino"], "T23:59:59")
	get_client_data_query = """SELECT
							   al.call_id, ca.id_cliente, pc.nombre_cliente, al.numero_origen, ca.anexo, al.hora_inicio, al.hora_termino, TIMESTAMPDIFF(SECOND,al.hora_inicio,al.hora_termino) as duracion_llamada, al.estado_llamada
							   FROM auditoria_llamadas as al
							   INNER JOIN 
							   clientes_anexo as ca ON ca.anexo = al.numero_destino
							   INNER JOIN parametros_cliente as pc ON pc.id_cliente = ca.id_cliente
							   WHERE al.hora_inicio BETWEEN '%s' and '%s'
							   and ca.id_cliente = %s
							   ORDER BY al.hora_termino ASC;
							   """ % (fecha_ini,fecha_fin,request["id_cliente"])

	data = {
		    "data": {
		        "llamadas": [
		        ]
		    },
		    "estado": {
		        "codigoEstado": 200,
		        "glosaEstado": "ok"
		    },
		    "total": {
		        "b64": "hora;dia;mes;total",
		        "llamadasDerivadas": 0,
		        "llamadasGestionadas": 0,
		        "llamadasNoEntendidas": 0, # Objeto de los call_id
		        "llamadasPerdidas": 0,
		        "llamadasTotales": 0,
		        "porcentajeDerivadas": 0,
		        "porcentajeGestionadas": 0,
		        "porcentajeNoEntendidas": 0,
		        "porcentajePerdidas": 0,
		        "porcentajeSegundasLlamadas": 0,
		        "segundasLlamadas": 0
		    }
		}
	# auditoria_llamadas
	query_1 = """SELECT DATE_FORMAT(al.hora_inicio, "%s") as fecha, COUNT(call_id) as total_llamadas
				FROM auditoria_llamadas as al
				INNER JOIN clientes_anexo as ca
				ON ca.anexo = al.numero_destino
				WHERE al.hora_inicio BETWEEN '%s' and '%s'
				and ca.id_cliente = %s
				GROUP BY DATE(hora_inicio);""" % ("%d-%m-%Y",fecha_ini,fecha_fin,request["id_cliente"])
	data_base = bd.MysqlBD()
	query_1_response = data_base.find_all(query_1)
	for x in query_1_response[1]:
		data["data"]["llamadas"].append(
			{
                "fecha": x['fecha'],
                "llamadasTotales": x["total_llamadas"]
            },
		)

	query_2 = """SELECT ca.anexo, al.call_id, al.estado_llamada, al.numero_origen, al.hora_inicio
				FROM auditoria_llamadas as al
				INNER JOIN clientes_anexo as ca
				ON CAST(ca.anexo as UNSIGNED) = CAST(al.numero_destino as UNSIGNED)
				WHERE al.hora_inicio BETWEEN '%s' and '%s' and ca.id_cliente = %s;"""  % (fecha_ini,fecha_fin,request["id_cliente"])

	query_2_response = data_base.find_all(query_2)
	data["total"]["llamadasTotales"] = len(query_2_response[1])
	unique_calls = [x["call_id"] for x in query_2_response[1]]
	segundas = {}
	for x in query_2_response[1]:
		if x["estado_llamada"] == "failed":
			data["total"]["llamadasPerdidas"] += 1 # Estado de llamadas Failed
		elif x["estado_llamada"] == "convTransfer":
			data["total"]["llamadasDerivadas"] += 1
			data["total"]["llamadasGestionadas"] += 1
		else:		
			data["total"]["llamadasGestionadas"] += 1 # Estado de llamadas distinto a failed
	if data["total"]["llamadasTotales"] != 0:
		data["total"]["porcentajePerdidas"] = round((data["total"]["llamadasPerdidas"]*100)/data["total"]["llamadasTotales"], 2) if data["total"]["llamadasTotales"] > 0 else 0
		data["total"]["porcentajeGestionadas"] = round((data["total"]["llamadasGestionadas"]*100)/data["total"]["llamadasTotales"], 2) if data["total"]["llamadasTotales"] > 0 else 0
	
	query_3 = """SELECT ca.anexo, al.call_id, al.hora_inicio, al.numero_origen, COUNT(*)-1 as segundas_llamadas
				FROM auditoria_llamadas as al 
				INNER JOIN clientes_anexo as ca
				ON CAST(ca.anexo as UNSIGNED) = CAST(al.numero_destino as UNSIGNED) 
				WHERE ca.id_cliente = %s and
				al.hora_inicio BETWEEN '%s' and '%s'
				GROUP BY al.numero_origen, DATE_FORMAT(al.hora_inicio, "%%d-%%m-%%Y");""" % (request["id_cliente"],fecha_ini,fecha_fin)
	query_3_response = data_base.find_all(query_3)
	for x in query_3_response[1]:
		data["total"]["segundasLlamadas"] += x["segundas_llamadas"]
	if data["total"]["llamadasTotales"] != 0:
		data["total"]["porcentajeSegundasLlamadas"] = round((data["total"]["segundasLlamadas"]*100)/data["total"]["llamadasTotales"], 2) if data["total"]["llamadasTotales"] > 0 else 0
	fecha_ini_m = datetime.datetime.strptime(fecha_ini_mongo, '%Y-%m-%d T%H:%M:%S')
	fecha_fin_m = datetime.datetime.strptime(fecha_fin_mongo, '%Y-%m-%d T%H:%M:%S')
	find_str = {'interaction.context.no_entendi':True, 'interaction.context.derivar':True, 'interaction.context.xentricCallId': {'$in': unique_calls}} # ...no_entendi = True
	# find_str = {'interaction.context.derivar':True,'interaction.context.no_entendi':True} # Mantener la condición derivar:True?
	# Unique call contain call_ids array
	interactions = bd.mongo_Connect().find(find_str)
	q_no_entendidas = []
	
	for x in interactions:
		q_no_entendidas.append(x["interaction"]["context"]["conversation_id"])
	# data["total"]["llamadasDerivadas"] = len(unique_id_derivar) # Query SQL, estado llamada convTransfer, cambiar por llamadas no entendidas
	
	data["total"]["llamadasNoEntendidas"] = len(set(q_no_entendidas)) 
	if data["total"]["llamadasTotales"] != 0:
		data["total"]["porcentajeDerivadas"] = round((data["total"]["llamadasDerivadas"]*100)/data["total"]["llamadasTotales"], 2) if data["total"]["llamadasTotales"] > 0 else 0

	data["total"]["porcentajeNoEntendidas"] = round((data["total"]["llamadasNoEntendidas"]*100)/data["total"]["llamadasTotales"], 2) if data["total"]["llamadasTotales"] > 0 else 0
	success, result_get_client_data_query = data_base.find_all(get_client_data_query)
	base64_encoded = csv_generator.list_to_csv(success, result_get_client_data_query)
	#base64_encoded = csv_path # b64.csv_to_base64(csv_path)
	data["total"]["b64"] = base64_encoded
	return data

def test_base_generator(request):
    	# {
	#     fecha_inicio: “”,
	#     fecha_termino: “”,
	#     id_cliente: “”,
	# }
	fecha_ini = format_fecha(request["fecha_inicio"], "00:00:00")
	fecha_fin = format_fecha(request["fecha_termino"], "23:59:59")
	
	fecha_ini_mongo = format_fecha(request["fecha_inicio"], "T00:00:00")
	fecha_fin_mongo = format_fecha(request["fecha_termino"], "T23:59:59")

	get_client_data_query = """SELECT
							   al.id_cliente, pc.nombre_cliente, al.anexo_cliente, DATE_FORMAT(al.hora_inicio, "%s"), DATE_FORMAT(al.hora_termino, "%s"), al.call_id
							   FROM auditoria_llamadas as al
							   INNER JOIN 
							   clientes_anexo as ca ON ca.anexo = al.numero_destino
							   INNER JOIN parametros_cliente as pc ON pc.id_cliente = ca.id_cliente
							   WHERE
							   WHERE al.hora_inicio BETWEEN '%s' and '%s'
							   and ca.id_cliente = %s
							   """ % ("%d-%m-%Y",fecha_ini,fecha_fin,request["id_cliente"])

	data = {
		    "data": {
		        "llamadas": [
		        ]
		    },
		    "estado": {
		        "codigoEstado": 200,
		        "glosaEstado": "ok"
		    },
		    "total": {
		        "b64": "hora;dia;mes;total",
		        "llamadasDerivadas": 0,
		        "llamadasGestionadas": 0,
		        "llamadasNoEntendidas": 0,
		        "llamadasPerdidas": 0,
		        "llamadasTotales": 0,
		        "porcentajeDerivadas": 0,
		        "porcentajeGestionadas": 0,
		        "porcentajeNoEntendidas": 0,
		        "porcentajePerdidas": 0,
		        "porcentajeSegundasLlamadas": 0,
		        "segundasLlamadas": 0
		    }
		}


	result_get_client_data_query = data_base.find_all(get_client_data_query)
	csv_path = csv_generator.list_to_csv(result_get_client_data_query)
	base64_encoded = b64.csv_to_base64(csv_path)
	data["total"]["b64"] = base64_encoded
	return data

