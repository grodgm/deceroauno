// Aviso por mail cuando alguien abre una exploracion o pide volver a verla.
// Necesita dos variables de entorno en Vercel:
//   RESEND_API_KEY  = la key de Resend
//   AVISO_TO        = a que casilla llega el aviso (opcional, por defecto la de abajo)

const DESTINO_POR_DEFECTO = "gonzalo@papumba.com";
const REMITENTE = "Avisos De Cero a Uno <avisos@escapadasba.com.ar>";

// solo avisamos de demos que existen, asi nadie usa el endpoint de pasarela
const DEMOS = new Set([
  "estudio-ali", "sociedades-online", "garcia-caro",
  "tejerina-anchorena", "cocuzza", "ortodoncia-salud",
]);

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const { demo, evento } = req.body || {};
  if (!DEMOS.has(demo)) return res.status(400).json({ error: "demo desconocida" });
  if (!["abrio", "volvio"].includes(evento)) return res.status(400).json({ error: "evento desconocido" });

  const key = process.env.RESEND_API_KEY;
  if (!key) return res.status(500).json({ error: "falta RESEND_API_KEY" });

  const volvio = evento === "volvio";
  const asunto = volvio
    ? `Volvieron a pedir acceso: ${demo}`
    : `Abrieron la exploracion: ${demo}`;
  const titulo = volvio
    ? "Pidieron volver a ver la exploracion"
    : "Abrieron la exploracion por primera vez";
  const bajada = volvio
    ? "Pasaron mas de 48 horas desde que la vieron y volvieron a entrar. Es la senal mas fuerte que vas a tener: quisieron mostrarsela a alguien o volver a mirarla."
    : "Es la primera vez que la abren desde este navegador.";

  const cuando = new Date().toLocaleString("es-AR", { timeZone: "America/Argentina/Buenos_Aires" });
  const ref = (req.headers["referer"] || "").slice(0, 200);
  const ua = (req.headers["user-agent"] || "").slice(0, 200);

  const html = `<div style="font-family:system-ui,-apple-system,sans-serif;max-width:520px;color:#101010">
    <p style="font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:${volvio ? "#B45309" : "#002FA7"};font-weight:700;margin:0">
      ${volvio ? "Volvieron" : "Primera visita"}
    </p>
    <h2 style="font-size:22px;margin:8px 0 0">${titulo}</h2>
    <p style="color:#555;margin:10px 0 20px">${bajada}</p>
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <tr><td style="padding:8px 0;border-top:1px solid #e6e6e6;color:#777;width:90px">Demo</td>
          <td style="padding:8px 0;border-top:1px solid #e6e6e6"><b>${demo}</b></td></tr>
      <tr><td style="padding:8px 0;border-top:1px solid #e6e6e6;color:#777">Cuando</td>
          <td style="padding:8px 0;border-top:1px solid #e6e6e6">${cuando}</td></tr>
      <tr><td style="padding:8px 0;border-top:1px solid #e6e6e6;color:#777">Dispositivo</td>
          <td style="padding:8px 0;border-top:1px solid #e6e6e6;color:#777;font-size:12px">${ua}</td></tr>
    </table>
    <p style="margin-top:22px">
      <a href="https://deceroauno.com.ar/demos/${demo}/" style="background:#002FA7;color:#fff;text-decoration:none;padding:12px 22px;border-radius:6px;font-weight:600;display:inline-block">Ver la exploracion</a>
    </p>
    ${ref ? `<p style="color:#999;font-size:12px;margin-top:18px">Vino de: ${ref}</p>` : ""}
  </div>`;

  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        from: REMITENTE,
        to: [process.env.AVISO_TO || DESTINO_POR_DEFECTO],
        subject: asunto,
        html,
      }),
    });
    if (!r.ok) return res.status(502).json({ error: "resend", detalle: (await r.text()).slice(0, 300) });
    return res.status(200).json({ ok: true });
  } catch (e) {
    return res.status(500).json({ error: String(e).slice(0, 200) });
  }
}
