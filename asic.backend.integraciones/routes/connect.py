# -*- coding: utf-8 -*-
# !/usr/bin/env python3

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import traceback
import datetime
import json
from icecream import ic

import views.registro_errores as registro_errores
from views.callback_status import status_callback


ALLOWED_ORIGIN = '*'

connect = Blueprint('connect', __name__)

@connect.route('/callback-status',methods=['POST'])
@cross_origin(cross_origin=ALLOWED_ORIGIN)
def register_status():
    
    if 'application/json' in request.headers['Content-Type']:       
        data = request.get_json()
        print("####### CALLBACK-STATUS ###########\n")
        
        if 'sourcetype' in data and data['sourcetype'] == 'vgwCallTransferred':
            return jsonify({"status": "call_transferred"})

        auxXentric ={
                        "idCall": data['event']['globalSessionID'],
                        "status": data['event']["endReason"],
                        "info": None,                 
                        "start_time": datetime.datetime.fromtimestamp(data['event']['startTime']/1000).strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": datetime.datetime.fromtimestamp(data['event']['stopTime']/1000).strftime("%Y-%m-%d %H:%M:%S"),
                        "call_duration": data['event']['callLength']*(1/1000),
                        "audio_link": None,
                        "transcription_link": None,
                        "origin_number": data['event']['sipFromURI'].split("@")[0].split(":")[1],
                        "destination_number": data['event']['sipToURI'].split("@")[0].split(":")[1],
                        "ivg_end_reason": data['event']['endReason'] if data['event']['endReason'] == "callerHangup" else None
                    }
        return status_callback(auxXentric)

    return jsonify({"Error": "No data"}), 400