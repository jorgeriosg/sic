import sys
import re
from itertools import cycle


def valida_rut(texto):
    rut = ''
    try:
        verificador = ''
        find_digit = re.findall(r'\d+', texto)
        concat_digit = ''.join(find_digit)

        if ('k' in texto or 'K' in texto or 'ca' in texto or 'CA' in texto) and len(concat_digit) <= 8:
            verificador = 'K'
        if ('cero' in texto or 'CERO' in texto or 'Cero' in texto or 'zero' in texto) and len(concat_digit) <= 8:
            verificador = '0'

        rut = concat_digit + verificador
        rut = rut.upper()
        rut = rut.replace("-", "")
        rut = rut.replace(".", "")
        aux = rut[:-1]
        dv = rut[-1:]

        revertido = map(int, reversed(str(aux)))
        factors = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(revertido, factors))
        res = (-s) % 11
        if str(res) == dv:
            return True, rut
        elif (dv == "K" and res == 10) or ((dv == "1" or dv == "0") and res == 10):
            lista = list(rut)
            lista[-1] = 'K'
            rut = ''.join(lista)
            return True, rut
        else:
            return False, rut
    except Exception:
        return False, rut
