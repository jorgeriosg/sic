#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mods.request_form as form_service



def consulta_cedula(body):
    return form_service.query_identification_user(body)

def consulta_ticket(body):
    return form_service.query_req_ticket(body)

def crear_orden(body):
    return form_service.create_req_order(body)

def caso_asic(body):
    return form_service.create_incident(body)

def crear_transaccion(body):
    return form_service.create_transaction(body)

def consulta_transaccion(body):
    return form_service.query_transaction(body)

def consulta_app(body):
    return form_service.get_app(body)

def enviar_token(body):
    return form_service.create_token(body)

def obtener_catalago(body):
    return form_service.query_catalog(body)

def buscar_transaction_bd(body):
    return form_service.search_transaction(body)
