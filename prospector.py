#!/usr/bin/env python3
"""
Prospector de De Cero a Uno.
Le das un CSV con una columna 'url' y te devuelve el mismo CSV con
diagnóstico automático de cada web: velocidad, mobile, WhatsApp, CTA,
antigüedad aparente y un puntaje de oportunidad (0 a 100, más alto = mejor prospect).

Uso:
  pip3 install requests beautifulsoup4
  python3 prospector.py prospectos.csv

Genera prospectos_scoreado.csv en la misma carpeta.
"""

import csv
import re
import sys
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

TIMEOUT = 15
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"


def analizar(url: str) -> dict:
    resultado = {
        "carga_seg": None,
        "peso_kb": None,
        "https_ok": False,
        "viewport_mobile": False,
        "tiene_whatsapp": False,
        "tiene_tel_click": False,
        "tiene_formulario": False,
        "cta_visible": False,
        "senales_vejez": [],
        "error": "",
    }
    if not url.startswith("http"):
        url = "https://" + url
    try:
        inicio = time.time()
        r = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": UA}, allow_redirects=True)
        resultado["carga_seg"] = round(time.time() - inicio, 2)
        resultado["peso_kb"] = round(len(r.content) / 1024)
        resultado["https_ok"] = r.url.startswith("https")
        html = r.text
    except Exception as e:
        resultado["error"] = str(e)[:120]
        return resultado

    soup = BeautifulSoup(html, "html.parser")
    texto = soup.get_text(" ", strip=True).lower()
    html_lower = html.lower()

    # mobile
    vp = soup.find("meta", attrs={"name": "viewport"})
    resultado["viewport_mobile"] = vp is not None

    # contacto
    resultado["tiene_whatsapp"] = "wa.me" in html_lower or "api.whatsapp.com" in html_lower
    resultado["tiene_tel_click"] = 'href="tel:' in html_lower or "href='tel:" in html_lower
    resultado["tiene_formulario"] = soup.find("form") is not None

    # CTA: botones o links con verbos de acción en el primer tramo de la página
    primer_tramo = html_lower[:15000]
    resultado["cta_visible"] = bool(
        re.search(r"(pedir turno|reservar|sacar turno|solicitar turno|agendar|consultar ahora|contactanos|contáctanos)", primer_tramo)
    )

    # señales de vejez
    señales = []
    if "jquery/1." in html_lower or "jquery-1." in html_lower:
        señales.append("jQuery 1.x (2013 o anterior)")
    if "table" in html_lower and "bgcolor=" in html_lower:
        señales.append("layout con tablas y bgcolor")
    if "flash" in html_lower and ".swf" in html_lower:
        señales.append("Flash")
    m = re.search(r"(?:©|copyright)\s*(19\d{2}|20[01]\d|202[0-3])", texto)
    if m:
        señales.append(f"copyright {m.group(1)}")
    gen = soup.find("meta", attrs={"name": "generator"})
    if gen and gen.get("content"):
        señales.append(f"generator: {gen['content'][:40]}")
    if not resultado["viewport_mobile"]:
        señales.append("sin meta viewport (no adaptada a mobile)")
    resultado["senales_vejez"] = señales
    return resultado


def puntaje(r: dict) -> int:
    """Más alto = peor web = mejor prospect."""
    if r["error"]:
        return 90  # una web caída o rota es el mejor prospect de todos
    p = 0
    if r["carga_seg"] and r["carga_seg"] > 3:
        p += 20
    if r["carga_seg"] and r["carga_seg"] > 6:
        p += 10
    if r["peso_kb"] and r["peso_kb"] > 3000:
        p += 10
    if not r["https_ok"]:
        p += 15
    if not r["viewport_mobile"]:
        p += 20
    if not r["tiene_whatsapp"]:
        p += 10
    if not r["tiene_tel_click"]:
        p += 5
    if not r["cta_visible"]:
        p += 10
    p += min(len(r["senales_vejez"]) * 5, 15)
    return min(p, 100)


def observacion(r: dict) -> str:
    """La frase concreta y verificable para personalizar el mail."""
    frases = []
    if r["error"]:
        return "la web directamente no carga o da error"
    if r["carga_seg"] and r["carga_seg"] > 3:
        frases.append(f"tarda {r['carga_seg']:.0f} segundos en cargar")
    if not r["viewport_mobile"]:
        frases.append("no está adaptada al celular")
    if not r["tiene_whatsapp"]:
        frases.append("no tiene botón de WhatsApp")
    if not r["cta_visible"]:
        frases.append("no invita a sacar turno en la primera pantalla")
    if not r["https_ok"]:
        frases.append("el navegador la marca como no segura")
    if not frases:
        return "la web está correcta; prospect de baja prioridad"
    return " y ".join(frases[:2])


def main():
    entrada = sys.argv[1] if len(sys.argv) > 1 else "prospectos.csv"
    salida = entrada.replace(".csv", "_scoreado.csv")

    with open(entrada, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))

    campos_nuevos = ["score", "observacion_para_mail", "carga_seg", "mobile", "whatsapp", "senales_vejez"]
    for fila in filas:
        url = (fila.get("url") or "").strip()
        if not url:
            continue
        print(f"Analizando {url} ...")
        r = analizar(url)
        fila["score"] = puntaje(r)
        fila["observacion_para_mail"] = observacion(r)
        fila["carga_seg"] = r["carga_seg"]
        fila["mobile"] = "sí" if r["viewport_mobile"] else "NO"
        fila["whatsapp"] = "sí" if r["tiene_whatsapp"] else "NO"
        fila["senales_vejez"] = "; ".join(r["senales_vejez"])
        time.sleep(1)  # ser buenos vecinos

    campos = list(filas[0].keys())
    for c in campos_nuevos:
        if c not in campos:
            campos.append(c)

    filas.sort(key=lambda x: int(x.get("score") or 0), reverse=True)

    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(filas)

    print(f"\nListo: {salida} (ordenado de mejor a peor prospect)")


if __name__ == "__main__":
    main()
