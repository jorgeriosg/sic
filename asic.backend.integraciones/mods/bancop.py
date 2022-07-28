#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mods.request_banco as service_request


def consulta_cedula(body):
    return service_request.query_id_user(body)

def consulta_ticket(body):
    return service_request.query_sd(body)

def caso_asic(body):
    return service_request.create_interaction(body)


