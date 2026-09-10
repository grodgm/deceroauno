#!/usr/bin/env python3
"""
Generador de demos de De Cero a Uno.

Uso:
  python3 generar_demo.py demos/ortodoncia-salud/datos.json

Toma la plantilla de demos/_plantilla/plantilla.html, la completa con los
datos del JSON y escribe demos/<slug>/index.html.
Después: git add, commit, push, y la demo queda publicada en
https://deceroauno.com.ar/demos/<slug>/

Reglas de oro al cargar el JSON:
- Solo datos reales sacados de la web actual del prospect. Nunca inventar
  cifras, años de trayectoria, cantidad de pacientes ni reseñas.
- El copy se reescribe (no se copia textual de su web).
- Las fotos van como placeholder; las reales las pone el cliente si avanza.
"""

import json
import re
import sys
from pathlib import Path

PLANTILLA = Path(__file__).parent / "demos" / "_plantilla" / "plantilla.html"

ICONOS = ["🦷", "✨", "😁", "🌙", "🔧", "🪥", "💎", "🧒", "📐", "🩺"]


def wsp_link(numero: str, nombre: str) -> str:
    digitos = re.sub(r"\D", "", numero or "")
    if not digitos:
        return "#turno"
    if not digitos.startswith("54"):
        digitos = "54" + ("9" if not digitos.startswith("9") else "") + digitos
    texto = f"Hola! Quiero pedir un turno en {nombre}."
    from urllib.parse import quote
    return f"https://wa.me/{digitos}?text={quote(texto)}"


def main():
    datos_path = Path(sys.argv[1])
    d = json.loads(datos_path.read_text(encoding="utf-8"))
    html = PLANTILLA.read_text(encoding="utf-8")

    servicios_html = ""
    for i, s in enumerate(d["servicios"]):
        icono = ICONOS[i % len(ICONOS)]
        servicios_html += f'''<div class="servicio">
        <div class="icono">{icono}</div>
        <h3>{s["nombre"]}</h3>
        <p>{s["descripcion"]}</p>
      </div>\n'''

    razones_html = ""
    for r in d["razones"]:
        razones_html += f'''<div class="razon"><b>{r["titulo"]}</b><p>{r["texto"]}</p></div>\n'''

    confianza_html = ""
    for c in d.get("confianza", []):
        confianza_html += f'''<div><b>{c["dato"]}</b><span>{c["etiqueta"]}</span></div>\n'''

    franja_html = ""
    for f in d.get("franja", []):
        franja_html += f"<span><i></i>{f}</span>\n"

    nombre = d["nombre"]
    partes = nombre.split(" ", 1)
    logo_html = f'{partes[0]} <span>{partes[1]}</span>' if len(partes) > 1 else nombre

    reemplazos = {
        "{{NOMBRE}}": nombre,
        "{{LOGO_HTML}}": logo_html,
        "{{ZONA}}": d["zona"],
        "{{TITULAR}}": d["titular"],
        "{{SUBTITULO}}": d["subtitulo"],
        "{{TELEFONO}}": d["telefono"],
        "{{TEL_LINK}}": re.sub(r"\D", "", d["telefono"]),
        "{{WSP_LINK}}": wsp_link(d.get("whatsapp", ""), nombre),
        "{{DIRECCION}}": d["direccion"],
        "{{TRANSPORTE}}": d["transporte"],
        "{{HORARIOS}}": d["horarios"],
        "{{SERVICIOS_INTRO}}": d["servicios_intro"],
        "{{SERVICIOS_HTML}}": servicios_html,
        "{{RAZONES_HTML}}": razones_html,
        "{{CONFIANZA_HTML}}": confianza_html,
        "{{FRANJA_HTML}}": franja_html,
        "{{ACCENT}}": d.get("color", "#0e7c86"),
        "{{ACCENT_OSCURO}}": d.get("color_oscuro", "#0a5a62"),
    }
    for k, v in reemplazos.items():
        html = html.replace(k, v)

    faltantes = re.findall(r"\{\{[A-Z_]+\}\}", html)
    if faltantes:
        print("ATENCIÓN, quedaron placeholders sin completar:", set(faltantes))

    salida = datos_path.parent / "index.html"
    salida.write_text(html, encoding="utf-8")
    print(f"Demo generada: {salida}")
    print(f"Cuando pushees queda en: https://deceroauno.com.ar/demos/{datos_path.parent.name}/")


if __name__ == "__main__":
    main()
