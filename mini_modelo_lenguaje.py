#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mini_modelo_lenguaje.py - Modelo de bigramas: elegir palabras mediante conteos
Actividad 3 - Fundamentos de Inteligencia Artificial (E-FIA-3)
Universidad Politécnica de Pachuca

NO es un LLM: es un generador probabilístico por conteos que se puede revisar a mano.

INSTRUCCIONES DE USO
    Interactivo:     python mini_modelo_lenguaje.py
    Con argumentos:  python mini_modelo_lenguaje.py --inicio la --semilla 7 --limite 10
    Solo proporciones tras una palabra:   python mini_modelo_lenguaje.py --proporciones biblioteca
    Modo determinista (siempre la más frecuente):   --modo maximo
    Corpus propio:   --corpus archivo.txt   (una frase por línea, UTF-8)

REGLAS
    - Cada frase se pasa a minúsculas, se separa por espacios y termina con <FIN>.
      No se tratan signos de puntuación: separar solo por espacios (ver informe).
    - Los bigramas no enlazan el final de una frase con el inicio de otra.
    - P(v|u) = C(u, v) / N(u), solo si N(u) > 0 (ecuación 11 de la actividad).
    - Límite de palabras: entero de 1 a 50, incluye la palabra inicial; <FIN> no cuenta.
    - La semilla (entero) permite repetir el sorteo con el mismo código, versión y datos.
    - La generación se detiene al elegir <FIN>, al alcanzar el límite o al hallar una
      palabra sin continuación; el programa informa el motivo.
    - En el modo maximo, un empate se resuelve por orden alfabético.

Requisitos: Python 3.8+, solo biblioteca estándar (collections.Counter, random).
"""

import argparse
import random
from collections import Counter

FIN = "<FIN>"

# Corpus ficticio de la sección 4 (la primera frase se repite deliberadamente).
CORPUS_DEFECTO = [
    "la biblioteca abre temprano",
    "la biblioteca abre tarde",
    "la biblioteca cierra temprano",
    "la biblioteca abre temprano",
]


def contar_bigramas(corpus):
    """Cuenta parejas consecutivas por frase. Rechaza un corpus vacío antes de calcular."""
    if corpus is None:
        raise ValueError("Corpus vacío: no hay frases con las que calcular.")
    frases = [f.strip().lower() for f in corpus if f is not None and f.strip()]
    if not frases:
        raise ValueError("Corpus vacío: no hay frases con las que calcular.")
    conteos = {}
    for frase in frases:
        palabras = frase.split() + [FIN]
        for anterior, siguiente in zip(palabras, palabras[1:]):
            conteos.setdefault(anterior, Counter())[siguiente] += 1
    return conteos


def proporciones(conteos, palabra):
    """Devuelve {continuación: proporción} o None si N(u) = 0 (contexto no observado)."""
    palabra = palabra.strip().lower()
    opciones = conteos.get(palabra)
    if not opciones:
        return None
    total = sum(opciones.values())
    return {v: c / total for v, c in sorted(opciones.items())}


def validar_parametros(semilla, limite):
    if isinstance(semilla, bool) or not isinstance(semilla, int):
        raise ValueError("La semilla debe ser un entero.")
    if isinstance(limite, bool) or not isinstance(limite, int) or not 1 <= limite <= 50:
        raise ValueError("El límite debe ser un entero de 1 a 50.")


def generar(conteos, inicio, semilla=0, limite=10, modo="sorteo"):
    """
    Genera texto a partir de 'inicio'. Devuelve (texto, traza, motivo).
    modo 'sorteo': sorteo ponderado con random.Random(semilla), pesos = frecuencias.
    modo 'maximo': siempre la continuación más frecuente (empate: orden alfabético).
    """
    validar_parametros(semilla, limite)
    actual = inicio.strip().lower()
    if not actual:
        raise ValueError("La palabra inicial no puede estar vacía.")
    if actual not in conteos:
        return "", [], "contexto no observado: el corpus no tiene continuaciones para '%s'" % actual
    rng = random.Random(semilla)
    palabras, traza = [actual], []
    while True:
        if len(palabras) >= limite:
            return " ".join(palabras), traza, "límite de %d palabra(s) alcanzado" % limite
        opciones = conteos.get(actual)
        if not opciones:
            return " ".join(palabras), traza, "palabra sin continuación: '%s'" % actual
        ordenadas = sorted(opciones.items())
        total = sum(c for _, c in ordenadas)
        if modo == "maximo":
            elegida = min(ordenadas, key=lambda par: (-par[1], par[0]))[0]
        else:
            elegida = rng.choices([v for v, _ in ordenadas], weights=[c for _, c in ordenadas], k=1)[0]
        traza.append({"paso": len(traza) + 1, "actual": actual,
                      "opciones": [(v, c, c / total) for v, c in ordenadas], "elegida": elegida})
        if elegida == FIN:
            return " ".join(palabras), traza, "se eligió %s" % FIN
        palabras.append(elegida)
        actual = elegida


def formatear_traza(traza):
    lineas = []
    for t in traza:
        opciones = ", ".join("%s (peso %d, P = %.2f)" % (v, c, p) for v, c, p in t["opciones"])
        lineas.append("paso %d | actual: %s | opciones: %s | elegida: %s" % (
            t["paso"], t["actual"], opciones, t["elegida"]))
    return "\n".join(lineas)


def cargar_corpus(ruta):
    with open(ruta, encoding="utf-8") as archivo:
        return archivo.read().splitlines()


def leer(mensaje, defecto):
    try:
        texto = input("%s [%s]: " % (mensaje, defecto)).strip()
    except EOFError:
        texto = ""
    return texto or str(defecto)


def main():
    ap = argparse.ArgumentParser(description="Mini modelo de lenguaje por bigramas (no es un LLM).")
    ap.add_argument("--corpus", help="archivo de texto UTF-8, una frase por línea")
    ap.add_argument("--inicio", help="palabra inicial")
    ap.add_argument("--semilla", type=int, default=None, help="entero para repetir el sorteo")
    ap.add_argument("--limite", type=int, default=None, help="palabras a mostrar, de 1 a 50")
    ap.add_argument("--modo", choices=["sorteo", "maximo"], default="sorteo")
    ap.add_argument("--proporciones", metavar="PALABRA", help="solo muestra P(v|PALABRA)")
    args = ap.parse_args()

    try:
        corpus = cargar_corpus(args.corpus) if args.corpus else CORPUS_DEFECTO
        conteos = contar_bigramas(corpus)
    except (ValueError, OSError) as error:
        print("Error: %s" % error)
        return 1

    if args.proporciones:
        prop = proporciones(conteos, args.proporciones)
        if prop is None:
            print("contexto no observado: sin continuaciones para '%s'" % args.proporciones)
            return 1
        for v, p in prop.items():
            print("P(%s | %s) = %.4f" % (v, args.proporciones.lower(), p))
        return 0

    try:
        inicio = args.inicio or leer("Palabra inicial", "la")
        semilla = args.semilla if args.semilla is not None else int(leer("Semilla (entero)", 42))
        limite = args.limite if args.limite is not None else int(leer("Límite de palabras (1-50)", 10))
        texto, traza, motivo = generar(conteos, inicio, semilla, limite, args.modo)
    except ValueError as error:
        print("Error: %s" % error)
        return 1

    print("Texto generado: " + (texto if texto else "(vacío)"))
    print("Motivo de parada: " + motivo)
    if traza:
        print("Traza:")
        print(formatear_traza(traza))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
