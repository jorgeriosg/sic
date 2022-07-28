import requests
import json
from mods.config import *

class Datadog():

	def __init__(self):
		self.ddsource = DATADOG_SOURCE
		self.ddtags = DATADOG_TAGS
		self.hostname = 'local-integraciones'
		self.service = DATADOG_SERVICE
		self.api_key = DATADOG_API_KEY
		self.url = DATADOG_URL

	def send_log(self, message, body=None, status_code=200, severity='INFO'):
		data = {
			'ddsource': self.ddsource,
			'ddtags': self.ddtags,
			'hostname': self.hostname,
			'message': message,
			'service': self.service,
            'status_code': status_code,
			'severity': severity
		}

		if body:
			data['body'] = json.dumps(body)

		headers = {
			'Content-Type':'application/json',
			'DD-API-KEY': self.api_key
		}

		response = requests.post(self.url, data=json.dumps(data), headers=headers)
		
		if response.status_code == 200:
			return True
		else:
			return False
