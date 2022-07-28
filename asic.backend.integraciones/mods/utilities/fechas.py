# -*- coding: utf-8 -*-
import datetime
import re
import locale
from datetime import timedelta
import pytz
import unidecode
import traceback

from mods.utilities.numero_texto import numero_a_texto


diccionario_tiempos = {
    "medio día":'12:00',
    "cuarto":"15",
    "media":"30",
    "en punto":"00"
}

class ManejadorFechas():
    
    timezone='America/Santiago'
    
    def __init__(self,timezone=None):
        self.timezone = timezone if timezone else self.timezone

    def fecha_relativa(self,fecha=None,formato='%Y-%m-%d'):
        '''
        Recibe una fecha y retorna lo relativo al dia de hoy.
        '''
        zona = pytz.timezone(self.timezone)
        fecha_local = datetime.datetime.now(tz=zona)
        try:
            fecha_consultada = datetime.datetime.strptime(fecha,formato).astimezone(zona)
        except:
            fecha_local = datetime.datetime.now()
            fecha_consultada = datetime.datetime.strptime(fecha,formato)
        if formato == '%Y-%m-%d':
            fecha_consultada = fecha_consultada.replace(hour=fecha_local.hour,minute=fecha_local.minute,second=fecha_local.second,microsecond=fecha_local.microsecond)
        if fecha_consultada > fecha_local:
            diferencia  = fecha_consultada - fecha_local
            if diferencia.days > 0:
                if diferencia.days == 1:
                    return "mañana"
                if diferencia.days == 2:
                    return "pasado mañana"
                return numero_a_texto(diferencia.days)+" días más"
            else:
                if diferencia.seconds % 60:
                    return numero_a_texto(int(diferencia.seconds/60))+" minutos y "+numero_a_texto(diferencia.seconds % 60)+" segundos más"
                return numero_a_texto(int(diferencia.seconds/60))+" minutos más"
                
        elif fecha_consultada < fecha_local:
            diferencia = fecha_local - fecha_consultada
            if diferencia.days > 0:
                if diferencia.days == 1:
                    return "ayer"
                if diferencia.days == 2:
                    return "antes de ayer"
                return numero_a_texto(diferencia.days)+" días atrás"
            else:
                if diferencia.seconds % 60:
                    return numero_a_texto(int(diferencia.seconds/60))+" minutos y "+numero_a_texto(diferencia.seconds % 60)+" segundos atrás"
                return numero_a_texto(int(diferencia.seconds/60))+" minutos atrás"
        
        else:
            return "ahora"
    
    def es_mayor_igual_a_hoy(self,fecha=None,formato='%Y-%m-%d'):
        '''
        Recibe una fecha y retorna si la fecha es igual o mayor al dia actual.
        '''
        zona = pytz.timezone(self.timezone)
        fecha_local = datetime.datetime.now(tz=zona)
        try:
            fecha_consultada = datetime.datetime.strptime(fecha,formato).astimezone(zona)
        except:
            fecha_local = datetime.datetime.now()
            fecha_consultada = datetime.datetime.strptime(fecha,formato)
        if formato == '%Y-%m-%d':
            fecha_consultada = fecha_consultada.replace(hour=fecha_local.hour,minute=fecha_local.minute,second=fecha_local.second,microsecond=fecha_local.microsecond)
            
        if fecha_consultada >= fecha_local:
            return True
        else:
            return False
    
    def hora_a_bloque(self,hora_str=''):
        '''
        Recibe una hora y devuelve a que bloque pertenece [manana,medio dia, tarde]
        '''
        hora = datetime.datetime.strptime(hora_str,'%H:%M')
        medio_dia_inferior = datetime.datetime.strptime('12:00','%H:%M')
        medio_dia_superior = datetime.datetime.strptime('13:59','%H:%M')
        if hora < medio_dia_inferior:
            return "en la mañana"
        elif medio_dia_inferior <= hora < medio_dia_superior:
            return "al medio día"
        else:
            return "en la tarde"
    
    def hora_a_bloque_orden(self,hora_str=''):
        '''
        Recibe una hora y devuelve a que bloque pertenece [manana,medio dia, tarde]
        '''
        hora = datetime.datetime.strptime(hora_str,'%H:%M')
        medio_dia_inferior = datetime.datetime.strptime('12:00','%H:%M')
        medio_dia_superior = datetime.datetime.strptime('13:59','%H:%M')
        if hora < medio_dia_inferior:
            return 0
        elif medio_dia_inferior <= hora < medio_dia_superior:
            return 1
        else:
            return 2
    
    def es_hora_bloque(self,hora_str='',bloque_evaluar=''):
        '''
        Recibe una hora y evalua si pertenece a bloque para evaluar
        '''
        if self.hora_a_bloque(hora_str=hora_str) == bloque_evaluar:
            return True
        else:
            return False
    
    def extraer_dia_fecha(self,fecha='',formato='%Y-%m-%d'):
        '''
        Extrae dia de una fecha.
        '''
        return datetime.datetime.strptime(fecha,formato).strftime('%d')
    
    def extraer_dia_semana_fecha(self,fecha='',formato='%Y-%m-%d'):
        '''
        Extrae el dia en formato: lunes,martes,miercoles,jueves,viernes,sabado,domingo.
        '''
        locale.setlocale(locale.LC_TIME, "es_ES")
        respuesta = datetime.datetime.strptime(fecha,formato).strftime('%A')
        return unidecode.unidecode(respuesta).lower()

    def extraer_dia_semana_fecha_ingles(self,fecha='',formato='%Y-%m-%d'):
        '''
        Extrae el dia en formato: monday,tuesday,wednesday,thursday,friday,saturday,sunday. Hay maquinas aws que tienen problemas con locale
        '''
        #locale.setlocale(locale.LC_TIME, "es_ES")
        respuesta = datetime.datetime.strptime(fecha,formato).strftime('%A')
        return unidecode.unidecode(respuesta).lower()
    
    def extraer_hora_de_texto(self,texto='',hora_detectada=False,minutos_detectados=False):
        '''
        Recibe texto y extrae la hora en formato: hora:minuto.
        Como hay hora entre 8:00 y 19:59, se deben transformar las horas de 1 a 7 si son detectadas como por ejemplo: 1:30 -> 13:30
        Ademas, en caso de que watson reconozca hora y minutos, se utilizan como un caso particular
        '''
        reg = re.findall(r'(\d{2}:\d{2})|(\d{1}:\d{2})|(\d{2}:\d{1})|(\d{1}:\d{1})',texto)
        if reg:
            for r in reg:
                if r[0]:
                    try:
                        hora = datetime.datetime.strptime(r[0],'%H:%M')
                        return True,hora.strftime("%H"),hora.strftime("%M")
                    except:
                        return False,traceback.format_exc(),''
                elif r[1]:
                    try:
                        hora = datetime.datetime.strptime(r[1],'%H:%M')
                        if 0 < hora.hour <= 7:
                            hora = hora + datetime.timedelta(hours=12)
                        return True,hora.strftime("%H"),hora.strftime("%M")
                    except:
                        return False,traceback.format_exc(),''
                elif r[2]:
                    try:
                        hora = datetime.datetime.strptime(r[2],'%H:%M')
                        return True,hora.strftime("%H"),hora.strftime("%M")
                    except:
                        return False,traceback.format_exc(),''
                elif r[3]:
                    try:
                        hora = datetime.datetime.strptime(r[3],'%H:%M')
                        if 0 < hora.hour <= 7:
                            hora = hora + datetime.timedelta(hours=12)
                        return True,hora.strftime("%H"),hora.strftime("%M")
                    except:
                        return False,traceback.format_exc(),''
                else:
                    return False, 'extraer_hora_de_texto, no coincide en ningun grupo:'+texto,''
        
        # no se usan todos los casos ya que watson tiene problemas con los minutos. Solo usar con hora detectada
        elif hora_detectada and not minutos_detectados:
            find_digit = re.findall(r'\d+', texto)
            concat_digit = ''.join(find_digit)
            # se utilizan solo los 2 primeros digitos detectados para suponer que es un minuto valido.
            minutos = concat_digit[2:]
            if not minutos:
                minutos = '00'
            concat_hora = str(hora_detectada)+':'+str(minutos)
            try:
                hora = datetime.datetime.strptime(concat_hora,'%H:%M')
                if 0 < hora.hour <= 7:
                    hora = hora + datetime.timedelta(hours=12)
                minutos = '15' if 'cuarto' in texto else '30' if 'media' in texto else hora.strftime("%M")
                return True,hora.strftime("%H"),minutos
            except:
                return False,traceback.format_exc(),''
            
        elif hora_detectada and minutos_detectados and hora_detectada != minutos_detectados:
            concat_hora = str(hora_detectada)+':'+str(minutos_detectados)
            try:
                hora = datetime.datetime.strptime(concat_hora,'%H:%M')
                if 0 < hora.hour <= 7:
                    hora = hora + datetime.timedelta(hours=12)
                minutos = '15' if 'cuarto' in texto else '30' if 'media' in texto else hora.strftime("%M")
                return True,hora.strftime("%H"),minutos
            except:
                return False,traceback.format_exc(),''
        else:
            find_digit = re.findall(r'\d+', texto)
            concat_digit = ''.join(find_digit)
            concat_digit = concat_digit[:4]
            if len(concat_digit) == 1:
                concat_digit = concat_digit + ':00'
                try:
                    hora = datetime.datetime.strptime(concat_digit,'%H:%M')
                    if 0 < hora.hour <= 7:
                        hora = hora + datetime.timedelta(hours=12)
                    minutos = '15' if 'cuarto' in texto else '30' if 'media' in texto else hora.strftime("%M")
                    return True,hora.strftime("%H"),minutos
                except:
                    return False,traceback.format_exc(),''
            elif len(concat_digit) == 2:
                concat_digit = concat_digit + ':00'
                try:
                    hora = datetime.datetime.strptime(concat_digit,'%H:%M')
                    if 0 < hora.hour <= 7:
                        hora = hora + datetime.timedelta(hours=12)
                    minutos = '15' if 'cuarto' in texto else '30' if 'media' in texto else hora.strftime("%M")
                    return True,hora.strftime("%H"),minutos
                except:
                    return False,traceback.format_exc(),''
            elif len(concat_digit) == 3:
                try:
                    hora = datetime.datetime.strptime(concat_digit,'%H%M')
                    if 0 < hora.hour <= 7:
                        hora = hora + datetime.timedelta(hours=12)
                    minutos = '15' if 'cuarto' in texto else '30' if 'media' in texto else hora.strftime("%M")
                    return True,hora.strftime("%H"),minutos
                except:
                    return False,traceback.format_exc(),''
            elif len(concat_digit) == 4:
                try:
                    hora = datetime.datetime.strptime(concat_digit,'%H%M')
                    if 0 < hora.hour <= 7:
                        hora = hora + datetime.timedelta(hours=12)
                    minutos = '15' if 'cuarto' in texto else '30' if 'media' in texto else hora.strftime("%M")
                    return True,hora.strftime("%H"),minutos
                except:
                    return False,'Hora no reconocida: '+str(concat_digit),''
            else:
                
                return False, 'extraer_hora_de_texto, no coincide en ningun largo: '+texto,''
                
    def dia_texto(self,dia='',formato='%Y-%m-%d'):
        '''
        Recibe un dia y devuelve el dia de la semana en texto. Ejemplo: 2019-03-02 -> proximo lunes/proximo proximo lunes.
        '''
        locale.setlocale(locale.LC_TIME, "es_ES")
        respuesta = ''
        zona = pytz.timezone(self.timezone)
        fecha_local = datetime.datetime.now(tz=zona)
        try:
            fecha_consultada = datetime.datetime.strptime(dia,formato).astimezone(zona)
        except:
            fecha_local = datetime.datetime.now()
            fecha_consultada = datetime.datetime.strptime(dia,formato)
        fecha_consultada = fecha_consultada.replace(hour=fecha_local.hour,minute=fecha_local.minute,second=fecha_local.second,microsecond=fecha_local.microsecond)
        diferencia_semana  = int(fecha_consultada.strftime('%U')) - int(fecha_local.strftime('%U'))

        if diferencia_semana == 0:
            diferencia_dia = fecha_consultada - fecha_local
            if diferencia_dia.days == 0:
                respuesta = 'hoy '+datetime.datetime.strptime(dia,formato).strftime('%A %d')
            elif diferencia_dia.days == 1:
                respuesta = 'mañana '+datetime.datetime.strptime(dia,formato).strftime('%A %d')
            else:
                respuesta = datetime.datetime.strptime(dia,formato).strftime('%A %d')
        elif fecha_consultada.month != fecha_local.month:
            respuesta = datetime.datetime.strptime(dia,formato).strftime('%A %d de %B')
        elif diferencia_semana == 1:
            respuesta = 'próximo '+datetime.datetime.strptime(dia,formato).strftime('%A %d')
        elif diferencia_semana == 2:
            respuesta = datetime.datetime.strptime(dia,formato).strftime('%A %d')
        else:
            respuesta = datetime.datetime.strptime(dia,formato).strftime('%A %d')
        return respuesta
    
    def mes_a_texto(self,mes='',formato='%m'):
        locale.setlocale(locale.LC_TIME, "es_ES")
        if mes:
            return datetime.datetime.strptime(mes,formato).strftime('de %B')
        else:
            return ''
    
    def extraer_mes_fecha(self,fecha='',formato='%Y-%m-%d'):
        locale.setlocale(locale.LC_TIME, "es_ES")
        if fecha:
            return datetime.datetime.strptime(fecha,formato).strftime('%m')
        else:
            return ''
    
    def mes_a_texto_no_mes_actual(self,mes='',formato='%m'):
        locale.setlocale(locale.LC_TIME, "es_ES")
        if mes:
            zona = pytz.timezone(self.timezone)
            mes_consultado = datetime.datetime.strptime(mes,formato).strftime('%B')
            mes_local = datetime.datetime.now(tz=zona).strftime('%B')
            if mes_consultado != mes_local:
                return datetime.datetime.strptime(mes,formato).strftime('de %B')
            else:
                return ''
        else:
            return ''
        
    def crear_fecha_dia_mes(self,dia='',mes='',formato='%Y-%m-%d'):
        '''
        Recibe un dia y mes y devuelve en string formato de fecha
        '''  
        zona = pytz.timezone(self.timezone)
        mes_local = datetime.datetime.now(tz=zona).strftime('%m')
        ano_local = datetime.datetime.now(tz=zona).strftime('%Y')
        if not mes:
            mes = datetime.datetime.now(tz=zona).strftime('%m')
            
        if mes < mes_local:
            ano_local = str(int(ano_local) - 1)
            fecha_creada = datetime.datetime.strptime(ano_local+'-'+mes+'-'+dia,'%Y-%m-%d')
        else:
            fecha_creada = datetime.datetime.strptime(ano_local+'-'+mes+'-'+dia,'%Y-%m-%d')
            
        return fecha_creada.strftime(formato)
    
    def restar_tiempo_ahora(self,horas=0):
        '''
        Recibe un rango de tiempo y resta a tiempo real. UTC 0
        '''  
        fecha_local_utc = datetime.datetime.utcnow()
        fecha = fecha_local_utc - datetime.timedelta(hours=horas)
        return fecha

if __name__ == "__main__":
    manejador_fechas = ManejadorFechas()
    texto = """ hola """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto))
    texto = """ 13:03 """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto))
    texto = """ 13:69 """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto))
    texto = """ asdasd 13 asd 40 """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto))
    texto = """ 1:10 """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto))
    texto = """ 01:10 """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto))
    texto = """ 010 """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto))
    texto = """ 1 """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto))
    texto = """ 1302 """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto))
    texto = """ 19:21 01231"""
    print(manejador_fechas.extraer_hora_de_texto(texto=texto))
    texto = """ hola doce y media """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto,hora_detectada=12,minutos_detectados=30))
    texto = """ 13 """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto,hora_detectada=13,minutos_detectados=False))
    texto = """ quince y cuarto """
    print(manejador_fechas.extraer_hora_de_texto(texto=texto,hora_detectada=15,minutos_detectados=''))