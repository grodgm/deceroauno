# De Cero a Uno - Instrucciones para el agente

Este repo es la web de De Cero a Uno (deceroauno.com.ar) más su sistema de demos comerciales. Deploya automáticamente en Vercel con cada push a main.

## Tarea principal: generar una demo

Cuando Gonza pida "generá la demo para <URL>" o similar, seguí este flujo completo sin pedir confirmaciones intermedias, salvo el push (ver abajo):

1. **Leer la web actual del prospect** (la URL que pasó Gonza). Extraer: nombre del negocio, rubro, zona/barrio, dirección si figura, teléfono, WhatsApp si figura, servicios o tratamientos que ofrece, años de trayectoria u otros datos de confianza QUE ESTÉN ESCRITOS en su web, horarios si figuran.

2. **Crear la carpeta** `demos/<slug>/` donde slug es el nombre en minúsculas con guiones (ej: `clinica-perez`).

3. **Escribir `demos/<slug>/datos.json`** siguiendo exactamente la estructura de `demos/ortodoncia-salud/datos.json` (usarlo como referencia). Reglas inquebrantables:
   - Solo datos reales que aparezcan en la web del prospect. PROHIBIDO inventar cifras, años, cantidad de pacientes, reseñas o premios.
   - Si un dato no está (ej: WhatsApp), dejarlo vacío o poner "Consultar por teléfono".
   - El copy se reescribe en tono cercano y profesional, voseo argentino, nunca se copia textual de su web.
   - Elegir un color de acento acorde al rubro (salud: verdes azulados o azules; jurídico: azules profundos; estética: tonos cálidos sobrios). Nunca repetir el mismo color de la demo anterior.

4. **Generar**: `python3 generar_demo.py demos/<slug>/datos.json`

5. **Verificar** abriendo el index.html generado: que no queden placeholders {{}} sin reemplazar, que el teléfono y los links de WhatsApp estén bien formados.

6. **Commit y push** con mensaje `Demo: <nombre del negocio>`. Antes de pushear, mostrar a Gonza un resumen de 3 líneas: negocio, qué datos se extrajeron, y qué quedó como placeholder. Con su ok, pushear.

7. **Avisar** con el link final: `https://deceroauno.com.ar/demos/<slug>/` y recordar que Vercel tarda un minuto en deployar.

## Otras tareas de este repo

- **Scoring de prospects**: `python3 prospector.py prospectos.csv` analiza las webs del CSV y genera el archivo scoreado. El CSV maestro lo maneja Gonza.
- **Cambios en la landing**: index.html en la raíz. Estilo: la landing usa Fraunces + Inter, blanco y azul Klein (#002FA7), tono manifiesto en voseo. No usar em dashes (—) en ningún texto: comas, puntos, dos puntos o paréntesis.
- **Nunca** tocar robots.txt para permitir indexar /demos/ (las demos siempre noindex).
- **Nunca** enviar emails ni mensajes a prospects: el outreach lo hace Gonza a mano.

## Estilo de todo texto visible

Voseo argentino, directo, cero jerga corporativa, sin em dashes. Los textos que ven prospects tienen que sonar escritos por una persona, no por una IA.
