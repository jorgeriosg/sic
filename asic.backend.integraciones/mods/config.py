#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enviroment vars
"""

from os import environ, getenv
from os.path import join
from os.path import dirname
from dotenv import load_dotenv

DOTENV_PATH = join(dirname(__file__), './.env')
load_dotenv(DOTENV_PATH)

# --------- path ---------
LOCAL_PATH = environ.get('LOCAL_PATH')
EFS_PATH = getenv('EFS_PATH', '/tmp/')

# --------- flask ---------
ALLOWED_ORIGIN = environ.get('ALLOWED_ORIGIN')

# --------- bases de datos ---------
MYSQL_HOST = environ.get('MYSQL_HOST')
MYSQL_NAME = environ.get('MYSQL_NAME')
MYSQL_USER = environ.get('MYSQL_USER')
MYSQL_PASS = environ.get('MYSQL_PASS')

POSTGRE_HOST = environ.get('POSTGRE_HOST')
POSTGRE_DB = environ.get('POSTGRE_DB')
POSTGRE_USER = environ.get('POSTGRE_USER')
POSTGRE_PASS = environ.get('POSTGRE_PASS')

MONGO_URI = environ.get('MONGO_URI')
DATA_BASE = environ.get('DATA_BASE')
MONGO_COL = environ.get('MONGO_COL')
MONGO_COLLECTION_AGENTS = environ.get('MONGO_COL')


# --------- logs ---------
DATADOG_API_KEY = environ.get('DATADOG_API_KEY')
DATADOG_APP_KEY = environ.get('DATADOG_APP_KEY')
DATADOG_URL = environ.get('DATADOG_URL')
DATADOG_TAGS = environ.get('DATADOG_TAGS')
DATADOG_SERVICE = environ.get('DATADOG_SERVICE')
DATADOG_SOURCE = environ.get('DATADOG_SOURCE')

DASHBOT_KEY = environ.get('DASHBOT_KEY')
DASHBOT_URL = environ.get('DASHBOT_URL')


# --------- canales ---------
AZURE_BOT_ID = environ.get('AZURE_BOT_ID')
AZURE_SECRET = environ.get('AZURE_SECRET')

TWILIO_ACCOUNT_SID = environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = environ.get('TWILIO_AUTH_TOKEN')
WHATSAPP_NUMBER = environ.get('WHATSAPP_NUMBER')

FB_ACCESS_TOKEN = environ.get('FB_ACCESS_TOKEN')
FB_VERIFY_TOKEN = environ.get('FB_VERIFY_TOKEN')
FB_LYNN = eval(environ.get('FB_LYNN')) if environ.get('FB_LYNN') is not None else False 

# --------- modulos --------- #todo: en desarollo
CONV_INTENTOS = int(environ.get('CONV_INTENTOS'))
CONV_VERSION  = environ.get('CONV_VERSION')

# --------- spell checker ---------
SPELLCHECKER = eval(environ.get('SPELLCHECKER'))
SPELL_KEY = environ.get('SPELL_KEY')
SPELL_URL = environ.get('SPELL_URL')
SPELL_TIMEOUT = environ.get('SPELL_TIMEOUT')


# --------- client integration ---------
INTEGRACION_TOTAL = eval(environ.get('INTEGRACION_TOTAL'))
URL_INTEGRACIONES = environ.get('URL_INTEGRACIONES')

# --------- client integration ---------
CLASIFICADOR = environ.get('CLASIFICADOR')

# --------- e-contact --------
LYNN_URL = environ.get('LYNN_URL')
LYNN_TEENANT = environ.get('LYNN_TEENANT')
LYNN_TOKEN = environ.get('LYNN_TOKEN')
LYNN_SECRET = environ.get('LYNN_SECRET')
LYNN_HARDCODE = eval(environ.get('LYNN_HARDCODE'))

# ---------claro token integration dev  --------
SMS_TOKEN_URL = environ.get('SMS_TOKEN_URL')

# ---------claro access transaction integration dev  --------
CLARO_ACCESS_TRANSACTION = environ.get('CLARO_ACCESS_TRANSACTION')
CLARO_ACCESS_TRANSACTION_TOKEN = environ.get('CLARO_ACCESS_TRANSACTION_TOKEN')


# --------- claro integration dev  --------
CLARO_API_URL = environ.get('CLARO_API_URL')
CLARO_API_TOKEN = environ.get('CLARO_API_TOKEN')

# --------- banco popular integration dev  --------
BANCOP_API_URL = environ.get('BANCOP_API_URL')
BANCOP_API_TOKEN = environ.get('BANCOP_API_TOKEN')

# --------- banco occidente integration dev  --------
BANCOC_API_URL = environ.get('BANCOC_API_URL')
BANCOC_API_TOKEN = environ.get('BANCOC_API_TOKEN')

# --------- asic_2 dev  --------
ASIC_2_API_URL = environ.get('ASIC_2_API_URL')
ASIC_2_TOKEN = environ.get('ASIC_2_TOKEN')


# ---------timezone history conversation   --------
TIME_ZONE_CONVERSATION_HISTORY = environ.get('TIME_ZONE_CONVERSATION_HISTORY')


# --------- sendgrid  --------
SG_KEY = environ.get('SG_KEY')
SG_FROM = environ.get('SG_FROM')
USAR_CHITCHAT = eval(environ.get('USAR_CHITCHAT'))

# --------- chattigo --------
CHATTIGO_URL = environ.get('CHATTIGO_URL')
CHATTIGO_USER = environ.get('CHATTIGO_USER')
CHATTIGO_PASS = environ.get('CHATTIGO_PASS')
CHATTIGO_DID_WEBCHAT = environ.get('CHATTIGO_DID_WEBCHAT')
CHATTIGO_DID_WHATSAPP = environ.get('CHATTIGO_DID_WHATSAPP')
CHATTIGO_HARCODE = eval(environ.get('CHATTIGO_HARCODE')) if environ.get('CHATTIGO_HARCODE') is not None else None

# --------- sixbell purecloud --------
SIXBELL_PURECLOUD_URL = environ.get('SIXBELL_PURECLOUD_URL')
SIXBELL_PURECLOUD_IDCLIENTE = environ.get('SIXBELL_PURECLOUD_IDCLIENTE')
SIXBELL_PURECLOUD_APITOKEN = environ.get('SIXBELL_PURECLOUD_APITOKEN')

# --------- redis --------------
REDIS_HOST = environ.get('REDIS_HOST') if environ.get('REDIS_HOST') is not None else '127.0.0.1'
REDIS_PORT = environ.get('REDIS_PORT') if environ.get('REDIS_PORT') is not None else 6379

# CONVERSATION
CONV_VERSION = environ.get('CONV_VERSION')
CONV_TIMEOUT = environ.get('CONV_TIMEOUT')
CONV_INTENTOS = int(environ.get('CONV_INTENTOS'))

# DEBUG
DEBUG = True if getenv('DEBUG', '') and int(getenv('DEBUG', '')) == 1 else False

# Xentric creds
XENTRIC_USER = environ.get('XENTRIC_USER')
XENTRIC_PASS = environ.get('XENTRIC_PASS')

#IVG
IP_CENTRAL = environ.get('IP_CENTRAL')