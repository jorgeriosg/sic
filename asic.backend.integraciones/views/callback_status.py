import json
import mods.bd as bd
import traceback
import datetime
from mods import datadog as dg
from flask import jsonify


def status_callback(data):
    statusToReturn = 200
    dataToReturn = {"message": "datos registrados"}
    try:

        base = bd.MysqlBD()
        query = """INSERT into auditoria_llamadas(
            numero_origen,
            numero_destino,
            duracion_llamada,
            hora_inicio,
            hora_termino,
            audio_link,
            transcription_link,
            call_id,
            estado_llamada,
            info_llamada,
            audio_path
        ) VALUES (
            %(numero_origen)s,
            %(numero_destino)s,
            %(duracion_llamada)s,
            %(hora_inicio)s,
            %(hora_termino)s,
            %(audio_link)s,
            %(transcription_link)s,
            %(call_id)s,
            %(estado_llamada)s,
            %(info_llamada)s,
            %(audio_path)s
        );"""
        if "origin_number" not in data:
            data["origin_number"] = None
        parametros = {
            'numero_origen': data['origin_number'],
            'numero_destino': data['destination_number'],
            'duracion_llamada': str(datetime.timedelta(seconds=int(data['call_duration']))),
            'hora_inicio': data['start_time'],
            'hora_termino': data['end_time'],
            'audio_link': data['audio_link'],
            'transcription_link': ','.join(data['transcription_link']) if isinstance(data['transcription_link'], list) else None,
            'call_id': data['idCall'],
            'estado_llamada': data['status'],
            'info_llamada': data['info'],
            'audio_path': f"{data['idCall']}-audio.wav"
        }

        insertado, resultado = base.insert(query, parametros)

        datadogInfo = {
            'request': data,
        }
        dg.registrar_datadog_v2(data=datadogInfo, status_code=200, severity='INFO', url_path='/xentric/callback-status')

    except Exception as errorData:
        statusToReturn = 500
        dataToReturn = {"message": f'Unexpected error storing the data: {errorData}'}
        datadogInfo = {
            'request': data,
            'traceback': traceback.format_exc()
        }
        dg.registrar_datadog_v2(data=datadogInfo, status_code=500, severity='ERROR', url_path='/xentric/callback-status')

    return jsonify(dataToReturn), statusToReturn
