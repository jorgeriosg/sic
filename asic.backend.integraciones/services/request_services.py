import requests

from .constants import (
    REQUEST_URL_1,
    REQUEST_URL_2,
)
#from mods import config

class RequestServices:

    def do_request(self, request_xml, url=REQUEST_URL_1):
        response = requests.post(url, data=request_xml)
        return response
