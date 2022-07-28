import datetime
import psycopg2
import psycopg2.extras
import pymongo
import pymysql
import traceback
import mods.config as config
import mods.datadog as datadog

posthost = config.POSTGRE_HOST
postdbname = config.POSTGRE_DB
postuser = config.POSTGRE_USER
postpass = config.POSTGRE_PASS
postssl = 'require'

mysqlhost = config.MYSQL_HOST
mysqldb = config.MYSQL_NAME
mysqluser = config.MYSQL_USER
mysqlpass = config.MYSQL_PASS

mongo_uri = config.MONGO_URI
mongo_data_base = config.DATA_BASE
mongo_colleccion = config.MONGO_COL
mongo_colleccion_agentes = config.MONGO_COLLECTION_AGENTS


class PostgreBD():
    host = ''
    dbname = ''
    user = ''
    password = ''
    tipo = 'require'
    connection = False

    def __init__(self,host=None,dbname=None,user=None,password=None,tipo=None):
        self.host = host if host else posthost
        self.dbname = dbname if dbname else postdbname
        self.user = user if user else postuser
        self.password = password if password else postpass
        self.tipo = tipo if tipo else postssl
        self.connection = self.connect()
        
    def __del__(self): 
        if self.connection:
            self.connection.close() 

    def connect(self,ssl_mode=None):
        if ssl_mode:
            connect_str = "dbname='{}' user='{}' host='{}' password='{}' sslmode='{}'".format(
                self.dbname, self.user, self.host, self.password, self.tipo)
        else:
            connect_str = "dbname='{}' user='{}' host='{}' password='{}'".format(
                self.dbname, self.user, self.host, self.password)
        return psycopg2.connect(connect_str)

    def find_one(self,query, parameters):
        result = []
        try:
            with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(query, parameters)
                result1 = cursor.fetchone()
                if result1:
                    return True, dict(result1)
                else:
                    return False, result
        except Exception:
            result = traceback.format_exc()
            return False, result

    def find_all(self, query, parameters=None):
        result = []
        exito = False
        try:
            with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                result1 = cursor.fetchall()
                exito = True
                return exito, result1

        except Exception:
            result = traceback.format_exc()
            return exito, result

    def update(self, query, parameters):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, parameters)
                result = cursor.fetchall()
                updated_rows = cursor.rowcount
                self.connection.commit()
                if updated_rows > 0:
                    return True, result
                else:
                    return False, 'Not Updated'
        except Exception:
            result = traceback.format_exc()
            return False, result

    def insert(self, query, parameters):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, parameters)
                self.connection.commit()
            return True, 'Inserted'
        except Exception:
            result = traceback.format_exc()
            return False, result

    def insert_query_concat(self, query):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
            return True, 'Inserted'
        except Exception:
            result = traceback.format_exc()
            return False, result

    def delete(self, query, parameters):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, parameters)
                updated_rows = cursor.rowcount
                self.connection.commit()
                if updated_rows > 0:
                    return True, 'Deleted'
                else:
                    return False, 'Not Deleted'
        except Exception:
            result = traceback.format_exc()
            return False, result

class MysqlBD():
    host = ''
    dbname = ''
    user = ''
    password = ''
    connection = False

    def __init__(self,host=None,dbname=None,user=None,password=None,tipo=None):
        self.host = host if host else mysqlhost
        self.dbname = dbname if dbname else mysqldb
        self.user = user if user else mysqluser
        self.password = password if password else mysqlpass
        self.connection = self.connect()
        
    def __del__(self): 
        self.connection.close() 

    def connect(self,ssl_mode=None):
        return pymysql.connect(host=self.host,
                           user=self.user,
                           password=self.password,
                           db=self.dbname,
                           charset='utf8',
                           use_unicode=True,
                           cursorclass=pymysql.cursors.DictCursor)

    def find_one(self,query, parameters):
        result = []
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, parameters)
                result1 = cursor.fetchone()
                if result1:
                    return True, dict(result1)
                else:
                    return False, result
        except Exception:
            result = traceback.format_exc()
            return False, result

    def find_all(self, query, parameters=None):
        result = []
        exito = False
        try:
            with self.connection.cursor() as cursor:
                if parameters:
                    cursor.execute(query, parameters)
                else:
                    cursor.execute(query)
                result1 = cursor.fetchall()
                exito = True
                return exito, result1

        except Exception:
            result = traceback.format_exc()
            return exito, result

    def update(self, query, parameters):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, parameters)
                result = cursor.fetchall()
                updated_rows = cursor.rowcount
                self.connection.commit()
                if updated_rows > 0:
                    return True, result
                else:
                    return False, 'Not Updated'
        except Exception:
            result = traceback.format_exc()
            return False, result

    def insert(self, query, parameters):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, parameters)
                id_registro = cursor.lastrowid
                self.connection.commit()
            return True, id_registro
        except Exception:
            result = traceback.format_exc()
            datadog.registrar_datadog(error=traceback.format_exc(), status_code=500)
            return False, result

    def insert_query_concat(self, query):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
            return True, 'Inserted'
        except Exception:
            result = traceback.format_exc()
            return False, result

    def insert_many(self,query,parameters):
        try:
            with self.connection.cursor() as cursor:
                cursor.executemany(query, parameters)
                id_registro = cursor.lastrowid
                self.connection.commit()
            return True, id_registro
        except Exception:
            result = traceback.format_exc()
            return False, result
        
        
    def delete(self, query, parameters):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, parameters)
                updated_rows = cursor.rowcount
                self.connection.commit()
                if updated_rows > 0:
                    return True, 'Deleted'
                else:
                    return False, 'Not Deleted'
        except Exception:
            result = traceback.format_exc()
            return False, result

def mongo_Connect(colleccion=mongo_colleccion):
    mongo = pymongo.MongoClient(mongo_uri)
    db = mongo[mongo_data_base]
    return db[colleccion]

def mongo_Connect_agents(colleccion=mongo_colleccion):
    mongo = pymongo.MongoClient(mongo_uri)
    db = mongo[mongo_data_base]
    return db[mongo_colleccion_agentes]