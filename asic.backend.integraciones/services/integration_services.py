from .constants import (
    REQUEST_URL_1,
    REQUEST_URL_2,
)
#from ..mods import config
from .request_services import RequestServices
from .xml_services import XMLServices


class IntegrationServices:

    def __init__(self):
        self.request_services = RequestServices()
        self.xml_services = XMLServices()

    def get_json_response(self, input_xml):
        response = self.request_services.do_request(
            request_xml=input_xml,
            url=REQUEST_URL_1,
        )
        return True

