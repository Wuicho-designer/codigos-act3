#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
matriz_riesgos_ia.py - Matriz de riesgos: decidir qué revisar primero
Actividad 3 - Fundamentos de Inteligencia Artificial (E-FIA-3)
Universidad Politécnica de Pachuca

INSTRUCCIONES DE USO
    Menú interactivo:      python matriz_riesgos_ia.py
    Exportar a CSV:        python matriz_riesgos_ia.py --exportar [ruta.csv]
    (por defecto se guarda matriz_riesgos_ia.csv en la carpeta actual)

REGLAS
    - Probabilidad (P) y severidad (S) solo admiten los enteros 1, 2 o 3.
    - Prioridad R = P x S (ecuación 12 de la actividad).
    - Orden: mayor R primero; en empate, mayor S; si continúa el empate, id ascendente.
    - Toda severidad 3 queda marcada para revisión humana, sin importar R.
    - Los textos obligatorios no pueden quedar vacíos.

Requisitos: Python 3.8+, solo biblioteca estándar (csv). Datos ficticios: biblioteca BIB-01.
"""

import csv
import os
import sys

CAMPOS_TEXTO = ["id", "riesgo", "descripcion", "afectados", "control", "responsable"]
CAMPOS_CSV = ["id", "riesgo", "descripcion", "afectados", "probabilidad", "severidad",
              "prioridad", "revision_humana", "control", "responsable"]

# Los siete riesgos de la Tabla 4, adaptados al asistente de la biblioteca ficticia.
RIESGOS_BASE = [
    {"id": "R01", "riesgo": "errores plausibles",
     "descripcion": "El asistente entrega un plazo o requisito inventado con redacción convincente.",
     "afectados": "Estudiantes que consultan el reglamento", "probabilidad": 3, "severidad": 2,
     "control": "Exigir respaldo en BIB-01 v1 y revisión de cada afirmación antes de publicar.",
     "responsable": "Bibliotecario"},
    {"id": "R02", "riesgo": "sesgo",
     "descripcion": "Consultas de igual significado reciben trato desigual por su redacción.",
     "afectados": "Estudiantes con distinta forma de escribir", "probabilidad": 2, "severidad": 2,
     "control": "Comparar pares de preguntas equivalentes y exigir la misma respuesta.",
     "responsable": "Equipo evaluador"},
    {"id": "R03", "riesgo": "privacidad",
     "descripcion": "La pregunta o la salida incluye datos personales de estudiantes.",
     "afectados": "Estudiantes", "probabilidad": 2, "severidad": 3,
     "control": "No usar datos reales; detener la entrada y pedir reformular sin identificadores.",
     "responsable": "Operador"},
    {"id": "R04", "riesgo": "opacidad",
     "descripcion": "El usuario no puede revisar de dónde salió una respuesta.",
     "afectados": "Estudiantes y bibliotecario", "probabilidad": 2, "severidad": 2,
     "control": "Mostrar código de la fuente, versión y fragmento de respaldo.",
     "responsable": "Diseñador"},
    {"id": "R05", "riesgo": "uso indebido",
     "descripcion": "Se solicita falsificar un permiso o autorizar un trámite.",
     "afectados": "Biblioteca y otros estudiantes", "probabilidad": 2, "severidad": 3,
     "control": "Rechazar la solicitud y no conectar el asistente con trámites.",
     "responsable": "Administrador"},
    {"id": "R06", "riesgo": "dependencia tecnológica",
     "descripcion": "No hay atención cuando el sistema falla.",
     "afectados": "Estudiantes", "probabilidad": 2, "severidad": 2,
     "control": "Mantener una guía de preguntas frecuentes y atención humana en el mostrador.",
     "responsable": "Coordinación"},
    {"id": "R07", "riesgo": "responsabilidad difusa",
     "descripcion": "La persona afectada no sabe a quién acudir para corregir una respuesta.",
     "afectados": "Estudiantes", "probabilidad": 2, "severidad": 3,
     "control": "Asignar revisión y un canal de corrección con folio de registro.",
     "responsable": "Coordinación"},
]


def validar_registro(registro):
    """Valida un registro. Devuelve (registro_limpio, lista_de_errores)."""
    errores = []
    limpio = {}
    for campo in CAMPOS_TEXTO:
        valor = registro.get(campo)
        if valor is None or not str(valor).strip():
            errores.append("El campo '%s' es obligatorio y no puede quedar vacío." % campo)
        else:
            limpio[campo] = str(valor).strip()
    for campo in ("probabilidad", "severidad"):
        valor = registro.get(campo)
        try:
            numero = int(str(valor).strip())
            if str(numero) != str(valor).strip() or numero not in (1, 2, 3):
                raise ValueError
            limpio[campo] = numero
        except (ValueError, TypeError):
            errores.append("'%s' = %r no es válido: solo se admiten los enteros 1, 2 o 3." % (campo, valor))
    return limpio, errores


def prioridad(registro):
    """R = P x S (ecuación 12)."""
    return registro["probabilidad"] * registro["severidad"]


def requiere_revision_humana(registro):
    """Toda severidad 3 se marca para revisión humana, cualquiera que sea su producto."""
    return registro["severidad"] == 3


def ordenar(registros):
    """Mayor prioridad primero; empate: mayor severidad; después id ascendente."""
    return sorted(registros, key=lambda r: (-prioridad(r), -r["severidad"], r["id"]))


def linea(registro):
    marca = "requiere revisión humana" if requiere_revision_humana(registro) else \
        "revisión humana no obligatoria"
    return "%s; %s; P = %d; S = %d; prioridad = %d; %s" % (
        registro["id"], registro["riesgo"], registro["probabilidad"], registro["severidad"],
        prioridad(registro), marca)


def mostrar(registros):
    for r in ordenar(registros):
        print(linea(r))
        print("    afecta a: %s | control: %s | responsable: %s" % (
            r["afectados"], r["control"], r["responsable"]))


def exportar_csv(registros, ruta="matriz_riesgos_ia.csv"):
    """Exporta todos los campos a CSV y devuelve la ruta; si falla, explica el problema."""
    try:
        with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=CAMPOS_CSV)
            escritor.writeheader()
            for r in ordenar(registros):
                fila = dict(r)
                fila["prioridad"] = prioridad(r)
                fila["revision_humana"] = "sí" if requiere_revision_humana(r) else "no"
                escritor.writerow({k: fila[k] for k in CAMPOS_CSV})
    except OSError as error:
        print("No se pudo guardar el CSV en '%s': %s" % (ruta, error))
        return None
    absoluta = os.path.abspath(ruta)
    print("CSV guardado en: " + absoluta)
    return absoluta


def siguiente_id(registros):
    numeros = [int(r["id"][1:]) for r in registros if r["id"][1:].isdigit()]
    return "R%02d" % (max(numeros) + 1 if numeros else 1)


def leer(mensaje):
    try:
        return input(mensaje)
    except EOFError:
        return "0"


def capturar_registro(registros):
    """Pide cada campo y lo repite hasta que sea válido (la entrada incorrecta se explica)."""
    nuevo = {"id": siguiente_id(registros)}
    preguntas = [("riesgo", "Nombre corto del riesgo: "), ("descripcion", "Descripción: "),
                 ("afectados", "Personas afectadas: "), ("probabilidad", "Probabilidad (1, 2 o 3): "),
                 ("severidad", "Severidad (1, 2 o 3): "), ("control", "Control propuesto: "),
                 ("responsable", "Responsable de la revisión: ")]
    for campo, texto in preguntas:
        while True:
            nuevo[campo] = leer(texto)
            _, errores = validar_registro({**{c: "x" for c in CAMPOS_TEXTO},
                                           "probabilidad": 1, "severidad": 1, campo: nuevo[campo]})
            if not errores:
                break
            print("  " + errores[0] + " Inténtalo de nuevo.")
    limpio, errores = validar_registro(nuevo)
    if errores:  # no debería ocurrir, pero se informa
        print("\n".join(errores))
        return None
    return limpio


def menu(registros):
    while True:
        print("\n=== Matriz de riesgos ===\n1. Ver matriz ordenada\n2. Agregar un riesgo\n"
              "3. Exportar a CSV\n0. Salir")
        op = leer("Opción: ").strip()
        if op == "1":
            mostrar(registros)
        elif op == "2":
            nuevo = capturar_registro(registros)
            if nuevo:
                registros.append(nuevo)
                print("Registrado: " + linea(nuevo))
        elif op == "3":
            exportar_csv(registros, leer("Ruta del CSV (Enter = matriz_riesgos_ia.csv): ").strip()
                         or "matriz_riesgos_ia.csv")
        elif op == "0":
            print("Hasta luego.")
            return
        else:
            print("Opción no válida. Elige 1, 2, 3 o 0.")


if __name__ == "__main__":
    datos = [dict(r) for r in RIESGOS_BASE]
    if len(sys.argv) > 1 and sys.argv[1] == "--exportar":
        exportar_csv(datos, sys.argv[2] if len(sys.argv) > 2 else "matriz_riesgos_ia.csv")
    else:
        menu(datos)
