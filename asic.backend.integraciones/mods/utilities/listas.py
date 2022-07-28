# -*- coding: utf-8 -*-
import traceback
from collections import OrderedDict

def sortElement(val):
    return val[0]

def lista_distribuida(lista=[],cantidad_elementos_devolver=5):
    lista_aux = []
    try:
        cantidad_buscada = cantidad_elementos_devolver - 2
        total_para_buscar = len(lista)
        distancia = int(total_para_buscar / cantidad_buscada) 
        lista_aux.append(lista[0])
        posicion = 1
        for i in range(1,cantidad_buscada+1):
            lista_aux.append(lista[posicion])
            posicion = posicion+distancia
        lista_aux.append(lista[-1])
        lista_aux = list(OrderedDict.fromkeys(lista_aux))
    except:
        lista_aux = lista[:cantidad_elementos_devolver]
    return lista_aux

def busqueda_iterativa(lista_buscada=[],lista_completa=[],posicion=0,mas_de_uno=False,lista_completa_sin_modificar=[]):
    """ busca las coincidencias de los elementos de una lista en otra lista 
    0: No existe ninguna coincidencia 
    1: existe solo 1 coincidencia estricta (devuelve indice de la lista donde esta la unica coincidencia)
    2: existe mas de una coincidencia (devuelve una lista donde estan las coincidencias)
    -1: no coincide completamente
    """

    coincidencias = 0
    indice_encontrado = 0
    indice = 0
    lista_auxiliar = []

    if len(lista_buscada) <= posicion and not mas_de_uno:
        return 0,'No existe',[]
    
    if len(lista_buscada) <= posicion and mas_de_uno:
        return 2,'Existe mas de una coincidencia',lista_completa
    
    for lista in lista_completa:
        if lista_buscada[posicion] and lista_buscada[posicion] in lista:
            coincidencias += 1
            indice_encontrado = indice
            lista_auxiliar.append(lista)
        indice += 1
    
    if coincidencias == 0:
        return busqueda_iterativa(lista_buscada=lista_buscada,lista_completa=lista_completa,posicion=posicion+1,mas_de_uno=mas_de_uno,lista_completa_sin_modificar=lista_completa_sin_modificar)
    elif coincidencias == 1:
        
        # Busqueda estricta: si hay informacion que no coincide completamente se avisa.
        for lista in lista_buscada:
            if lista and lista not in lista_completa[indice_encontrado]:
                return -1,'No coincide completamente',lista_completa
        indice_encontrado = lista_completa_sin_modificar.index(lista_completa[indice_encontrado])
        return 1,indice_encontrado,[]
    else:
        mas_de_uno = True
        return busqueda_iterativa(lista_buscada=lista_buscada,lista_completa=lista_auxiliar,posicion=posicion+1,mas_de_uno=mas_de_uno,lista_completa_sin_modificar=lista_completa_sin_modificar)


if __name__ == "__main__":
    lista_completa = ['próximo jueves 29 en la tarde', 'próximo viernes 30 en la mañana', 'jueves 12 de septiembre en la tarde']
    
    dia_relativo = ''
    dia_bloque = ''
    tipo_bloque = 'en la tarde'
    dia_numero = '12'
    mes = 'de agosto'
    #lista_buscada = (dia_relativo,dia_bloque,dia_numero,tipo_bloque,mes)
    #print(busqueda_iterativa(lista_buscada=lista_buscada,lista_completa=lista_completa,lista_completa_sin_modificar=lista_completa))
    
    lista = ['09:00','09:15','09:30','09:45','10:00','10:15','10:30','11:15','12:00','12:30']
    lista = ['14:00','14:15','14:30','14:45','15:00','15:15','15:30']
