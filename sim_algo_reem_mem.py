#!/usr/bin/env python

marcos_libres = [0x0,0x1,0x2]
reqs = [ 0x00, 0x12, 0x64, 0x65, 0x8D, 0x8F, 0x19, 0x18, 0xF1, 0x0B, 0xDF, 0x0A ]
segmentos =[ ('.text', 0x00, 0x1A),
             ('.data', 0x40, 0x28),
             ('.heap', 0x80, 0x1F),
             ('.stack', 0xC0, 0x22),
            ]

def procesar(segmentos, reqs, marcos_libres):
    tabla_paginas = {}
    marcos_ocupados = []
    resultado = []
    max_direccion = 0x1FF

    # Helper para verificar si una dirección pertenece a un segmento válido
    def direccion_valida(direccion):
        for nombre, base, limite in segmentos:
            if base <= direccion < base + limite:
                return True
        return False

    # Algoritmo FIFO: elimina el más antiguo
    def reemplazar_marco():
        marco_viejo = marcos_ocupados.pop(0)
        # Eliminar de la tabla de páginas
        for pagina in list(tabla_paginas):
            if tabla_paginas[pagina] == marco_viejo:
                del tabla_paginas[pagina]
                break
        return marco_viejo

    for req in reqs:
        if not direccion_valida(req):
            resultado.append((req, max_direccion, "Segmentation Fault")) # Direccion invalida
            continue

        pagina = req >> 4  # Tamaño de página de 16 bytes
        offset = req & 0xF # Posicion exacta dentro de una pagina donde se encuentra la direccion logica

        if pagina in tabla_paginas:
            marco = tabla_paginas[pagina]
            direccion_fisica = (marco << 4) | offset
            resultado.append((req, direccion_fisica, "Marco ya estaba asignado"))
        else:
            if marcos_libres:
                marco = marcos_libres.pop(0)
                tabla_paginas[pagina] = marco
                marcos_ocupados.append(marco)
                direccion_fisica = (marco << 4) | offset
                resultado.append((req, direccion_fisica, "Marco libre asignado"))
            else:
                marco = reemplazar_marco()
                tabla_paginas[pagina] = marco
                marcos_ocupados.append(marco)
                direccion_fisica = (marco << 4) | offset
                resultado.append((req, direccion_fisica, "Marco asignado"))

    return resultado
    
def print_results(results):
    for result in results:
        print(f"Req: {result[0]:#0{4}x} Direccion Fisica: {result[1]:#0{4}x} Acción: {result[2]}")

if __name__ == '__main__':
    results = procesar(segmentos, reqs, marcos_libres)
    print_results(results)

