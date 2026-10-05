#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pruebas_actividad3.py - Ejecuta las pruebas de la Tabla 6 y las adicionales del inciso e)

Uso:  python pruebas_actividad3.py
      (deja los tres programas en la misma carpeta; genera pruebas_resultados.json)

Cada prueba define ANTES de ejecutar el resultado esperado; después se registra lo
obtenido y se compara. Los programas no se modifican para que la prueba pase.
"""

import json
import os
import tempfile
from fractions import Fraction

import mapa_ramas_ia as mapa
import matriz_riesgos_ia as matriz
import mini_modelo_lenguaje as modelo

RESULTADOS = []


def probar(id_, programa, entrada, esperado, ejecutar, verificar):
    """ejecutar() -> texto obtenido; verificar(texto) -> bool."""
    try:
        obtenido = ejecutar()
    except Exception as error:  # una excepción también es un resultado observado
        obtenido = "EXCEPCIÓN %s: %s" % (type(error).__name__, error)
    ok = bool(verificar(obtenido))
    RESULTADOS.append({"id": id_, "programa": programa, "entrada": entrada,
                       "esperado": esperado, "obtenido": obtenido, "correcto": ok})
    print("[%s] %s | %s\n  Esperado: %s\n  Obtenido: %s\n  Resultado: %s\n" % (
        id_, programa, entrada, esperado, obtenido.replace("\n", "\n            "),
        "CORRECTO" if ok else "FALLO"))


def capturar_error(f, *args, **kwargs):
    try:
        f(*args, **kwargs)
        return "no hubo error"
    except ValueError as error:
        return "ValueError: %s" % error


# ----------------------------- mapa_ramas_ia.py ------------------------------
probar("M01", "mapa_ramas_ia.py", "consultar('PLN')",
       "Muestra que trabaja con lenguaje, su conexión con redes neuronales y que el LLM no es obligatorio.",
       lambda: mapa.consultar("PLN"),
       lambda t: "lenguaje" in t and "no es obligatorio" in t and "Redes neuronales" in t)
probar("M02", "mapa_ramas_ia.py", "consultar('blockchain') (rama inexistente)",
       "Informa «término no registrado».",
       lambda: mapa.consultar("blockchain"), lambda t: t.startswith("término no registrado"))
probar("M03", "mapa_ramas_ia.py", "consultar('') (consulta vacía)",
       "Solicita escribir una rama.",
       lambda: mapa.consultar(""), lambda t: t.startswith("Consulta vacía"))
probar("M04", "mapa_ramas_ia.py", "consultar('lógica difusa')",
       "Muestra pertenencia entre 0 y 1 y la nota de que no es probabilidad; sin enlaces registrados.",
       lambda: mapa.consultar("lógica difusa"),
       lambda t: "entre 0 y 1" in t and "no es una probabilidad" in t and "Sin enlaces registrados" in t)
probar("M05", "mapa_ramas_ia.py", "consultar('reforzamiento')",
       "Muestra recompensa y el enlace «forma parte de» aprendizaje automático.",
       lambda: mapa.consultar("reforzamiento"),
       lambda t: "recompensas" in t and "forma parte de" in t)
probar("M06", "mapa_ramas_ia.py", "orientar('', 'clasificar mensajes', 'ninguna')",
       "Responde «información insuficiente» y pide el tipo de entrada.",
       lambda: mapa.orientar("", "clasificar mensajes", "ninguna"),
       lambda t: t.startswith("información insuficiente") and "tipo de entrada" in t)
probar("M07", "mapa_ramas_ia.py", "orientar('texto', 'orientar sobre un reglamento', 'sin datos personales')",
       "Sugiere PLN, aclara que el LLM no es requisito y menciona la guía de preguntas frecuentes.",
       lambda: mapa.orientar("texto", "orientar sobre un reglamento", "sin datos personales"),
       lambda t: "Procesamiento de lenguaje natural" in t and "no un requisito" in t)

# ---------------------------- matriz_riesgos_ia.py ---------------------------
base = {"id": "R99", "riesgo": "prueba", "descripcion": "d", "afectados": "a",
        "probabilidad": 2, "severidad": 3, "control": "c", "responsable": "Operador"}


def prueba_p2s3():
    limpio, errores = matriz.validar_registro(base)
    return "errores=%s | %s" % (errores, matriz.linea(limpio))


probar("R01", "matriz_riesgos_ia.py", "P = 2, S = 3",
       "Sin errores; prioridad 6 y revisión humana.",
       prueba_p2s3, lambda t: "errores=[]" in t and "prioridad = 6" in t and "requiere revisión humana" in t)


def prueba_p4():
    _, errores = matriz.validar_registro({**base, "probabilidad": 4})
    return "errores=%s" % errores


probar("R02", "matriz_riesgos_ia.py", "P = 4",
       "Se rechaza explicando que solo se admiten 1, 2 o 3.",
       prueba_p4, lambda t: "solo se admiten los enteros 1, 2 o 3" in t)


def prueba_resp_vacio():
    _, errores = matriz.validar_registro({**base, "responsable": "  "})
    return "errores=%s" % errores


probar("R03", "matriz_riesgos_ia.py", "responsable vacío",
       "Se rechaza: el campo es obligatorio.",
       prueba_resp_vacio, lambda t: "'responsable' es obligatorio" in t)


def prueba_orden():
    return ", ".join(r["id"] for r in matriz.ordenar(matriz.RIESGOS_BASE))


probar("R04", "matriz_riesgos_ia.py", "ordenar los 7 riesgos de la matriz base",
       "R03, R05, R07 (R = 6, S = 3), R01 (R = 6, S = 2), R02, R04, R06 (R = 4).",
       prueba_orden, lambda t: t == "R03, R05, R07, R01, R02, R04, R06")


def prueba_csv():
    ruta = os.path.join(tempfile.mkdtemp(), "matriz.csv")
    matriz.exportar_csv(matriz.RIESGOS_BASE, ruta)
    with open(ruta, encoding="utf-8-sig") as f:
        filas = f.read().splitlines()
    return "filas=%d (1 encabezado + datos) | encabezado: %s" % (len(filas), filas[0])


probar("R05", "matriz_riesgos_ia.py", "exportar a CSV",
       "Archivo con 8 filas (encabezado + 7 riesgos) y todos los campos.",
       prueba_csv, lambda t: "filas=8" in t and "prioridad" in t and "responsable" in t)

# --------------------------- mini_modelo_lenguaje.py -------------------------
conteos = modelo.contar_bigramas(modelo.CORPUS_DEFECTO)
probar("L01", "mini_modelo_lenguaje.py", "proporciones tras «biblioteca», corpus de la sección 4",
       "abre 0.75; cierra 0.25 (antes de sortear).",
       lambda: str(modelo.proporciones(conteos, "biblioteca")),
       lambda t: "'abre': 0.75" in t and "'cierra': 0.25" in t)
probar("L02", "mini_modelo_lenguaje.py", "proporciones tras «abre», corpus completo",
       "tarde 1/3 y temprano 2/3.",
       lambda: str({k: str(Fraction(v).limit_denominator(10)) for k, v in modelo.proporciones(conteos, "abre").items()}),
       lambda t: "'tarde': '1/3'" in t and "'temprano': '2/3'" in t)
sin4 = modelo.contar_bigramas(modelo.CORPUS_DEFECTO[:3])
probar("L03", "mini_modelo_lenguaje.py", "retirar la cuarta frase; proporciones tras «biblioteca»",
       "abre 2/3 y cierra 1/3.",
       lambda: str({k: str(Fraction(v).limit_denominator(10)) for k, v in modelo.proporciones(sin4, "biblioteca").items()}),
       lambda t: "'abre': '2/3'" in t and "'cierra': '1/3'" in t)
probar("L04", "mini_modelo_lenguaje.py", "corpus vacío ([] y solo espacios)",
       "Se rechaza explicando el motivo.",
       lambda: capturar_error(modelo.contar_bigramas, []) + " | " + capturar_error(modelo.contar_bigramas, ["  "]),
       lambda t: t.count("Corpus vacío") == 2)
probar("L05", "mini_modelo_lenguaje.py", "inicio «museo»",
       "Se detiene por «contexto no observado» y no genera texto.",
       lambda: "texto=%r | motivo=%s" % modelo.generar(conteos, "museo", 0, 5)[::2],
       lambda t: "contexto no observado" in t and "texto=''" in t)
probar("L06", "mini_modelo_lenguaje.py", "modo máximo desde «la», límite 10",
       "la biblioteca abre temprano; parada por <FIN>.",
       lambda: "texto=%r | motivo=%s" % modelo.generar(conteos, "la", 0, 10, "maximo")[::2],
       lambda t: "texto='la biblioteca abre temprano'" in t and "<FIN>" in t)
probar("L07", "mini_modelo_lenguaje.py", "inicio «la», límite 3 (parada por límite)",
       "Texto de exactamente 3 palabras; motivo: límite alcanzado.",
       lambda: "texto=%r | motivo=%s" % modelo.generar(conteos, "la", 0, 3, "maximo")[::2],
       lambda t: "texto='la biblioteca abre'" in t and "límite de 3" in t)
probar("L08", "mini_modelo_lenguaje.py", "inicio «la», límite 1",
       "Solo la palabra inicial; motivo: límite alcanzado.",
       lambda: "texto=%r | motivo=%s" % modelo.generar(conteos, "la", 0, 1)[::2],
       lambda t: "texto='la'" in t and "límite de 1" in t)
probar("L09", "mini_modelo_lenguaje.py", "límites 0, 51 y semilla no entera",
       "Los tres se rechazan.",
       lambda: " | ".join([capturar_error(modelo.generar, conteos, "la", 0, 0),
                           capturar_error(modelo.generar, conteos, "la", 0, 51),
                           capturar_error(modelo.generar, conteos, "la", "a", 5)]),
       lambda t: t.count("ValueError") == 3)

t1, tr1, m1 = modelo.generar(conteos, "la", 1, 10)
t2, tr2, m2 = modelo.generar(conteos, "la", 3, 10)
t1b, tr1b, _ = modelo.generar(conteos, "la", 1, 10)
probar("L10", "mini_modelo_lenguaje.py", "semillas 1 y 3 desde «la», límite 10; repetir la semilla 1",
       "La misma semilla repite texto y traza. Dos semillas distintas pueden dar o no el mismo texto; ninguna es error.",
       lambda: "semilla 1: %r (%s) | semilla 3: %r (%s) | semilla 1 repetida igual: %s" % (
           t1, m1, t2, m2, (t1, tr1) == (t1b, tr1b)),
       lambda t: "repetida igual: True" in t)

# ------------------------ verificación de cálculos a mano --------------------


def difusa(T):
    mu = 0 if T <= 20 else (1 if T >= 30 else (T - 20) / 10)
    w2, w1 = mu, 1 - mu
    return mu, (w1 * 20 + w2 * 80) / (w1 + w2)


probar("C01", "cálculo (lógica difusa)", "T = 20, 25 y 30 °C",
       "20 °C: μ = 0, 20 %; 25 °C: μ = 0.5, 50 %; 30 °C: μ = 1, 80 %.",
       lambda: " | ".join("%d °C: μ = %.1f, u = %.0f %%" % ((T,) + difusa(T)) for T in (20, 25, 30)),
       lambda t: "20 °C: μ = 0.0, u = 20 %" in t and "25 °C: μ = 0.5, u = 50 %" in t
       and "30 °C: μ = 1.0, u = 80 %" in t)
probar("C02", "cálculo (Q-Learning)", "Q = 2, r = 10, estado terminal, α = 0.25",
       "Q nuevo = 2 + 0.25 × (10 − 2) = 4.",
       lambda: "Q nuevo = %.2f" % (2 + 0.25 * (10 - 2)), lambda t: t == "Q nuevo = 4.00")


def tabla_verdad():
    filas = []
    for f in (True, False):
        for r in (True, False):
            for s in (True, False):
                a = f and r and (not s)
                filas.append("f=%s r=%s s=%s -> a=%s" % (f, r, s, a))
    return "\n".join(filas)


probar("C03", "cálculo (lógica proposicional)", "a ↔ (f ∧ r ∧ ¬s), 8 combinaciones",
       "Solo f = V, r = V, s = F autoriza la publicación (1 de 8).",
       tabla_verdad, lambda t: t.count("a=True") == 1 and "f=True r=True s=False -> a=True" in t)

# --------------------------------- resumen -----------------------------------
total = len(RESULTADOS)
correctas = sum(1 for r in RESULTADOS if r["correcto"])
print("RESUMEN: %d de %d pruebas correctas." % (correctas, total))
with open("pruebas_resultados.json", "w", encoding="utf-8") as archivo:
    json.dump({"pruebas": RESULTADOS,
               "trazas": {"semilla_1": modelo.formatear_traza(tr1), "semilla_2": modelo.formatear_traza(tr2),
                          "texto_1": t1, "texto_2": t2}}, archivo, ensure_ascii=False, indent=2)
