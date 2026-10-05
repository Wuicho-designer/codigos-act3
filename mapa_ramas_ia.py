#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mapa_ramas_ia.py - Mapa de relaciones de las ramas de la IA
Actividad 3 - Fundamentos de Inteligencia Artificial (E-FIA-3)
Universidad Politécnica de Pachuca

INSTRUCCIONES DE USO
    Menú interactivo:       python mapa_ramas_ia.py
    Consulta directa:       python mapa_ramas_ia.py "PLN"
    Orientar una tarea:     opción 2 del menú (pide tipo de entrada, tarea y restricciones)

Requisitos: Python 3.8 o superior. Solo usa la biblioteca estándar.
Todos los datos son didácticos (tomados de la Actividad 3); no describen experimentos.

Estructura de datos:
    RAMAS   -> diccionario: clave de rama -> ficha (diccionario con definición, datos, etc.)
    ENLACES -> lista de tuplas (origen, vinculo, destino): es el grafo de relaciones.
"""

import sys
import unicodedata

# ---------------------------------------------------------------------------
# Fichas: las siete ramas, en el mismo orden de la Tabla 2 de la actividad.
# ---------------------------------------------------------------------------
RAMAS = {
    "evolutivos": {
        "nombre": "Algoritmos evolutivos",
        "alias": ["algoritmos evolutivos", "evolutivos", "algoritmos geneticos", "ae"],
        "tipo": "familia de métodos de búsqueda y optimización",
        "definición": "Métodos de búsqueda y optimización inspirados en la evolución de "
                      "poblaciónes de soluciones.",
        "datos": "Una representación de las soluciones (individuos), una población inicial, "
                 "una función de aptitud y las restricciones del problema.",
        "técnica": "Ciclo de selección, cruzamiento, mutación y reemplazo hasta un criterio de parada.",
        "aplicaciones": ["Organizar horarios", "Asignar turnos con restricciones",
                         "Buscar buenos parametros de un diseño"],
        "nota": "Encontrar una buena propuesta no demuestra que sea la mejor posible.",
    },
    "redes": {
        "nombre": "Redes neuronales",
        "alias": ["redes neuronales", "redes", "red neuronal", "rn"],
        "tipo": "modelo de unidades de cálculo conectadas",
        "definición": "Modelos de unidades de cálculo conectadas mediante pesos ajustables.",
        "datos": "Ejemplos con entradas numéricas y, en el caso supervisado, respuestas conocidas.",
        "técnica": "Suma ponderada con sesgo y función de activación; los pesos se ajustan "
                   "comparando la salida con la respuesta conocida.",
        "aplicaciones": ["Reconocer un carácter escrito", "Clasificar mensajes (perceptrón)",
                         "Apoyar tareas de vision por computadora"],
        "nota": "Se necesitan ejemplos adecuados y revision de errores.",
    },
    "difusa": {
        "nombre": "Lógica difusa (sistemas difusos)",
        "alias": ["lógica difusa", "difusa", "sistemas difusos", "sistema difuso", "fuzzy"],
        "tipo": "marco de razonamiento",
        "definición": "Marco de razonamiento basado en conjuntos con grados de pertenencia "
                      "entre 0 y 1.",
        "datos": "Valores de entrada continuos (por ejemplo, una temperatura) y reglas "
                 "fijadas por personas.",
        "técnica": "Funciones de pertenencia, reglas y promedio ponderado (Sugeno de orden cero).",
        "aplicaciones": ["Regular un ventilador", "Controlar velocidades de forma gradual",
                         "Representar categorías graduales como 'caliente'"],
        "nota": "Un grado de pertenencia no es una probabilidad.",
    },
    "aprendizaje": {
        "nombre": "Aprendizaje automático",
        "alias": ["aprendizaje automático", "aprendizaje", "machine learning", "ml", "aa"],
        "tipo": "campo de la IA",
        "definición": "Campo de la IA que estudia métodos para aprender modelos o criterios "
                      "de decisión a partir de datos.",
        "datos": "Ejemplos con características y etiquetas (supervisado), datos sin etiquetas "
                 "(no supervisado) o experiencia (reforzamiento).",
        "técnica": "Por ejemplo, k vecinos más cercanos: se asigna la categoria mas frecuente "
                   "entre los k casos más próximos.",
        "aplicaciones": ["Clasificar mensajes", "Predecir si un estudiante aprueba",
                         "Clasificar piezas por su longitud"],
        "nota": "Debe evaluarse con casos no usados para ajustar el modelo.",
    },
    "vision": {
        "nombre": "Visión por computadora",
        "alias": ["vision por computadora", "vision", "vision artificial", "cv"],
        "tipo": "campo de estudio",
        "definición": "Campo dedicado al análisis e interpretación computacional de imágenes y videos.",
        "datos": "Imagenes o videos representados como matrices de pixeles.",
        "técnica": "Umbralización, segmentación, métodos geométricos o redes neuronales.",
        "aplicaciones": ["Detectar defectos visibles", "Reconocer caracteres de un aviso fotografiado",
                         "Localizar objetos"],
        "nota": "La iluminación y la calidad de la imagen afectan el resultado.",
    },
    "pln": {
        "nombre": "Procesamiento de lenguaje natural (PLN)",
        "alias": ["procesamiento de lenguaje natural", "pln", "nlp", "lenguaje natural"],
        "tipo": "campo de estudio",
        "definición": "Campo de la representación, el análisis y la generación computacional "
                      "del lenguaje humano.",
        "datos": "Texto en lenguaje natural (preguntas, documentos, mensajes).",
        "técnica": "Tokenización, conteos, modelos de bigramas o modelos de lenguaje de gran escala (LLM).",
        "aplicaciones": ["Orientar sobre un reglamento", "Clasificar mensajes",
                         "Traducir o redactar respuestas"],
        "nota": "Puede utilizar un LLM, pero no es obligatorio. La respuesta debe respetar la "
                "fuente consultada.",
    },
    "reforzamiento": {
        "nombre": "Aprendizaje por reforzamiento (por refuerzo)",
        "alias": ["aprendizaje por reforzamiento", "reforzamiento", "refuerzo",
                  "aprendizaje por refuerzo", "q-learning", "rl"],
        "tipo": "modalidad de aprendizaje",
        "definición": "Modalidad de aprendizaje basada en la interacción de un agente con un "
                      "entorno y recompensas.",
        "datos": "Estados, acciónes y recompensas obtenidos al interactuar con un entorno "
                 "(en esta práctica, simulado).",
        "técnica": "Q-Learning: se estima el valor de cada acción en cada estado y se corrige "
                   "tras cada transición observada.",
        "aplicaciones": ["Guiar un robot en simulación", "Navegar una cuadrícula",
                         "Aprender una política de decisión"],
        "nota": "Una recompensa alta no garantiza una conducta segura.",
    },
}

# ---------------------------------------------------------------------------
# Grafo de relaciones (origen, vinculo, destino). Un enlace ausente NO significa
# incompatibilidad: esta solo se justifica por una restriccion explicita.
# ---------------------------------------------------------------------------
ENLACES = [
    ("reforzamiento", "forma parte de", "aprendizaje"),
    ("aprendizaje", "incluye métodos como", "redes"),
    ("redes", "pueden utilizarse en", "vision"),
    ("vision", "entrega texto que luego puede procesar", "pln"),
    ("pln", "puede utilizar (por ejemplo, en un LLM)", "redes"),
    ("evolutivos", "pueden combinarse con", "redes"),
]

# Reglas simples para orientar una tarea: (palabras clave, ramas, motivo)
REGLAS_ORIENTACION = [
    (("texto", "mensaje", "pregunta", "lenguaje", "documento", "reglamento"), ["pln"],
     "La entrada es lenguaje humano."),
    (("imagen", "foto", "video", "pixel"), ["vision"],
     "La entrada es información visual."),
    (("etiqueta", "ejemplos", "historial", "clasificar", "predecir"), ["aprendizaje"],
     "Hay ejemplos de los que se pueden aprender criterios de decisión."),
    (("recompensa", "simulacion", "entorno", "robot", "agente"), ["reforzamiento"],
     "Hay un agente que actua en un entorno y recibe recompensas."),
    (("horario", "optimizar", "asignar", "turnos", "combinacion"), ["evolutivos"],
     "Se busca una buena solucion entre muchas posibles."),
    (("temperatura", "gradual", "sensor", "velocidad"), ["difusa"],
     "Hay una variable continua con categorías graduales y reglas fijadas por personas."),
]


def normalizar(texto):
    """Minusculas y sin acentos, para comparar terminos."""
    t = unicodedata.normalize("NFD", texto.strip().lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


INDICE = {}
for _clave, _ficha in RAMAS.items():
    INDICE[normalizar(_ficha["nombre"])] = _clave
    for _alias in _ficha["alias"]:
        INDICE[normalizar(_alias)] = _clave


def relaciones_de(clave):
    """Enlaces del grafo donde participa la rama indicada."""
    lineas = []
    for origen, vinculo, destino in ENLACES:
        if clave in (origen, destino):
            lineas.append("%s %s %s" % (RAMAS[origen]["nombre"], vinculo, RAMAS[destino]["nombre"]))
    return lineas


def consultar(texto):
    """Devuelve la ficha de una rama. Consulta vacía o inexistente: mensaje explicativo."""
    if texto is None or not texto.strip():
        return "Consulta vacía: escribe el nombre de una rama (por ejemplo, PLN)."
    clave = INDICE.get(normalizar(texto))
    if clave is None:
        disponibles = ", ".join(f["nombre"] for f in RAMAS.values())
        return "término no registrado: '%s'.\nRamas disponibles: %s." % (texto.strip(), disponibles)
    f = RAMAS[clave]
    salida = [
        "%s (%s)" % (f["nombre"], f["tipo"]),
        "Definición: " + f["definición"],
        "Datos que utiliza: " + f["datos"],
        "Técnica: " + f["técnica"],
        "Aplicaciones:",
    ]
    salida += ["  - " + a for a in f["aplicaciones"]]
    salida.append("Relaciones:")
    rel = relaciones_de(clave)
    if rel:
        salida += ["  - " + r for r in rel]
    else:
        salida.append("  - Sin enlaces registrados (esto no significa incompatibilidad).")
    salida.append("Nota: " + f["nota"])
    return "\n".join(salida)


def orientar(entrada, tarea, restricciones):
    """Orienta la elección de técnica. Si falta un dato, responde 'información insuficiente'."""
    faltan = [n for n, v in (("tipo de entrada", entrada), ("tarea", tarea),
                             ("restricciones (escribe 'ninguna' si no hay)", restricciones))
              if v is None or not v.strip()]
    if faltan:
        return "información insuficiente: falta " + ", ".join(faltan) + "."
    texto = normalizar(entrada + " " + tarea)
    ramas, motivos = [], []
    for palabras, claves, motivo in REGLAS_ORIENTACION:
        if any(p in texto for p in palabras):
            for c in claves:
                if c not in ramas:
                    ramas.append(c)
            motivos.append(motivo)
    if not ramas:
        return "información insuficiente: no hay elementos para elegir una técnica con fundamento."
    nombres = ", ".join(RAMAS[c]["nombre"] for c in ramas)
    salida = ["Ramas candidatas: " + nombres, "Motivo: " + " ".join(motivos),
              "Restricciones declaradas: " + restricciones.strip()]
    if "pln" in ramas:
        salida.append("Un LLM es una opción, no un requisito: compara con una guía de preguntas frecuentes.")
    salida.append("Esta orientación no sustituye la justificación de la elección.")
    return "\n".join(salida)


def listar_enlaces():
    return "\n".join("- %s %s %s" % (RAMAS[o]["nombre"], v, RAMAS[d]["nombre"]) for o, v, d in ENLACES)


def leer(mensaje):
    try:
        return input(mensaje)
    except EOFError:
        return "0"


def menu():
    opciones = ("\n=== Mapa de ramas de la IA ===\n1. Consultar una rama\n2. Orientar una tarea\n"
                "3. Ver todos los enlaces\n0. Salir")
    while True:
        print(opciones)
        op = leer("Opción: ").strip()
        if op == "1":
            print(consultar(leer("Rama (p. ej., PLN, lógica difusa): ")))
        elif op == "2":
            e = leer("Tipo de entrada (texto, imagen, datos, simulacion...): ")
            t = leer("Tarea que se desea resolver: ")
            r = leer("Restricciones: ")
            print(orientar(e, t, r))
        elif op == "3":
            print(listar_enlaces())
        elif op == "0":
            print("Hasta luego.")
            return
        else:
            print("Opción no válida. Elige 1, 2, 3 o 0.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(consultar(" ".join(sys.argv[1:])))
    else:
        menu()
