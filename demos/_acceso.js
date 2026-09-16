/* Control de acceso de las exploraciones de De Cero a Uno.
   La exploracion queda abierta 48 horas desde la primera visita de cada
   navegador. Pasado ese plazo se difumina y aparece un boton para volver
   a pedirla, que avisa por mail y la reabre por otras 48 horas.
   Todo el estado vive en el localStorage del visitante. */
(function () {
  var slug = (location.pathname.match(/\/demos\/([^\/]+)/) || [])[1];
  if (!slug || slug.charAt(0) === "_") return;

  var CLAVE = "dca:" + slug;
  var VENTANA = 48 * 60 * 60 * 1000;
  var ahora = Date.now();
  var st = null;
  try { st = JSON.parse(localStorage.getItem(CLAVE) || "null"); } catch (e) {}

  function guardar() { try { localStorage.setItem(CLAVE, JSON.stringify(st)); } catch (e) {} }
  function avisar(evento) {
    try {
      fetch("/api/aviso", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ demo: slug, evento: evento }),
        keepalive: true,
      }).catch(function () {});
    } catch (e) {}
  }

  if (!st || !st.desde) {
    st = { desde: ahora };
    guardar();
    avisar("abrio");
    return;                      // recien la abre: se ve entera
  }
  if (ahora - st.desde <= VENTANA) return;   // sigue dentro de las 48 horas

  /* ---------- pasaron las 48 horas: difuminar y pedir de nuevo ---------- */
  var css = document.createElement("style");
  css.textContent =
    '.dca-velo{position:fixed;inset:0;z-index:2147483000;display:flex;align-items:center;' +
    'justify-content:center;padding:24px;background:rgba(248,248,250,.72);backdrop-filter:blur(9px);' +
    '-webkit-backdrop-filter:blur(9px);font-family:system-ui,-apple-system,"Segoe UI",sans-serif}' +
    '.dca-caja{background:#fff;max-width:440px;width:100%;border-radius:18px;padding:36px 32px;' +
    'text-align:center;box-shadow:0 24px 70px rgba(16,16,16,.22)}' +
    '.dca-caja h2{font-size:25px;line-height:1.2;margin:0 0 12px;color:#101010;letter-spacing:-.02em}' +
    '.dca-caja p{font-size:16.5px;line-height:1.6;color:#5c5c5c;margin:0 0 26px}' +
    '.dca-btn{display:block;width:100%;border:0;cursor:pointer;background:#002FA7;color:#fff;' +
    'font-size:17px;font-weight:700;padding:17px 22px;border-radius:999px;font-family:inherit}' +
    '.dca-btn:hover{background:#101010}.dca-btn[disabled]{opacity:.65;cursor:default}' +
    '.dca-pie{margin:18px 0 0;font-size:13.5px;color:#8a8a8a}' +
    '.dca-pie a{color:#002FA7}' +
    '.dca-ok{color:#0F8A4B;font-weight:600}' +
    '@media(prefers-reduced-motion:reduce){.dca-velo{backdrop-filter:blur(9px)}}';
  document.head.appendChild(css);

  var velo = document.createElement("div");
  velo.className = "dca-velo";
  velo.innerHTML =
    '<div class="dca-caja" role="dialog" aria-modal="true" aria-label="Volver a ver la exploracion">' +
    '<h2>Esta exploracion estuvo abierta 48 horas</h2>' +
    '<p>La preparamos sin compromiso para mostrar el cambio posible. Si la queres ver de nuevo, ' +
    'tocá el boton y se reabre al instante.</p>' +
    '<button class="dca-btn" type="button">Volver a ver la exploracion</button>' +
    '<p class="dca-pie">La preparó <a href="https://deceroauno.com.ar" target="_blank" rel="noopener">De Cero a Uno</a></p>' +
    "</div>";
  document.documentElement.appendChild(velo);

  velo.querySelector(".dca-btn").addEventListener("click", function () {
    var b = this;
    b.disabled = true;
    b.textContent = "Listo, abriendo...";
    if (!st.pidio) { avisar("volvio"); st.pidio = true; }
    st.desde = Date.now();                 // se reabre por otras 48 horas
    st.pidio = false;
    guardar();
    setTimeout(function () { velo.remove(); }, 450);
  });
})();
