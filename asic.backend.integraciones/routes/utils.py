from flask import Blueprint, jsonify, request, send_file, request
from flask_cors import cross_origin
import traceback
from pathlib import Path
from uuid import uuid4

from mods.config import EFS_PATH
import mods.bd as bd

utils = Blueprint('utils', __name__)
ALLOWED_ORIGIN = '*'


def find_wav_file(filename):
    path = Path(EFS_PATH)
    wav_file = path / filename
    exists = wav_file.exists()
    if exists is False:
        return exists, None
    else:
        return exists, wav_file.resolve()


@utils.route("/get-audio", methods=["POST"])
@cross_origin(cross_origin=ALLOWED_ORIGIN)
def get_audio():
    if 'Content-Type' not in request.headers or 'application/json' not in request.headers['Content-Type']:
        return jsonify({"error": "Bad request"}), 400

    call_id = request.json['callId'] if 'callId' in request.json else None
    if call_id is None:
        return jsonify({"error": "Invalid request"}), 400
        
    db = bd.MysqlBD()
    query = """
        SELECT 
            audio_path 
        FROM 
            auditoria_llamadas
        WHERE
            call_id = %(call_id)s
        """
    params = {'call_id': call_id}

    fetched, data = db.find_one(query, params)
    if fetched is False:
        return jsonify({"error": "Invalid call id"}), 404
    
    audio_path = data['audio_path']

    if audio_path is None:
        return jsonify({"error": "Missing audio file"}), 404

    exists, wav_file = find_wav_file(audio_path)

    if exists is False:
        return jsonify({"error": "Missing audio file"}), 404
    else:
        filename = f"{uuid4()}.wav"
        return send_file(wav_file, as_attachment=True, mimetype='audio/x-wav', attachment_filename=filename)

