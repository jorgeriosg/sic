import requests
import traceback

def llamado_recursivo(metodo='POST',url='',data={},headers={},intentos=0,timeout=3,error=None):
    if intentos == 3:
        return True,error
    else:
        if metodo.upper() == 'POST':
            try:
                r = requests.post(url, headers=headers, data=data, timeout=timeout)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc())
        elif metodo.upper() == 'GET':
            try:
                r = requests.get(url, timeout=timeout,headers=headers,data=data)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc())
        elif metodo.upper() == 'PUT':
            try:
                r = requests.put(url,data=data,timeout=timeout)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc())
        elif metodo.upper() == 'DELETE':
            try:
                r = requests.delete(url,timeout=timeout)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc())
        elif metodo.upper() == 'HEAD':
            try:
                r = requests.head(url,timeout=timeout)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc())
        elif metodo.upper() == 'OPTIONS':
            try:
                r = requests.options(url,timeout=timeout)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc())
        else:
            return True,'metodo no reconocido'

def llamado_recursivo_seguro(metodo='POST',url='',data={},headers={},intentos=0,timeout=3,error=None,auth=()):
    if intentos == 3:
        return True,error
    else:
        if metodo.upper() == 'POST':
            try:
                r = requests.post(url, headers=headers, data=data, timeout=timeout,auth=auth)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo_seguro(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc(),auth=auth)
        elif metodo.upper() == 'GET':
            try:
                r = requests.get(url, timeout=timeout,auth=auth)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo_seguro(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc(),auth=auth)
        elif metodo.upper() == 'PUT':
            try:
                r = requests.put(url,data=data,timeout=timeout,auth=auth)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo_seguro(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc(),auth=auth)
        elif metodo.upper() == 'DELETE':
            try:
                r = requests.delete(url,timeout=timeout,auth=auth)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo_seguro(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc(),auth=auth)
        elif metodo.upper() == 'HEAD':
            try:
                r = requests.head(url,timeout=timeout,auth=auth)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo_seguro(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc(),auth=auth)
        elif metodo.upper() == 'OPTIONS':
            try:
                r = requests.options(url,timeout=timeout,auth=auth)
                return False,r
            except:
                intentos += 1
                return llamado_recursivo_seguro(metodo=metodo,url=url,data=data,headers=headers,intentos=intentos,timeout=timeout,error=traceback.format_exc(),auth=auth)
        else:
            return True,'metodo no reconocido'