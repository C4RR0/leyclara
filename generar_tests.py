"""Genera las páginas de test online (una por ley) a partir de las preguntas de las muestras gratis,
más la portada /test/, sitemap.xml y robots.txt. Pensado para que Google las encuentre
(«test ley 41/2002», «test estatuto marco»...).

Uso: python generar_tests.py   (desde la carpeta web/)
"""
import html
import json
import re
from pathlib import Path

WEB = Path(__file__).resolve().parent
URL = "https://c4rr0.github.io/leyclara/"
TIENDA = "https://carrosphere.gumroad.com/l/"

LEYES = [  # carpeta, slug, nombre corto, tema, nombre completo, precio, nº de test del pack
    ("ley55", "ley-55-2003", "Ley 55/2003", "Estatuto Marco",
     "Ley 55/2003, de 16 de diciembre, del Estatuto Marco del personal estatutario de los servicios de salud", "8,90", 95),
    ("ley41", "ley-41-2002", "Ley 41/2002", "autonomía del paciente",
     "Ley 41/2002, de 14 de noviembre, básica reguladora de la autonomía del paciente y de derechos y obligaciones en materia de información y documentación clínica", "6,90", 62),
    ("ley14", "ley-14-1986", "Ley 14/1986", "General de Sanidad",
     "Ley 14/1986, de 25 de abril, General de Sanidad", "6,90", 85),
    ("ley44", "ley-44-2003", "Ley 44/2003", "ordenación de las profesiones sanitarias",
     "Ley 44/2003, de 21 de noviembre, de ordenación de las profesiones sanitarias", "6,90", 100),
    ("ley16", "ley-16-2003", "Ley 16/2003", "cohesión y calidad del SNS",
     "Ley 16/2003, de 28 de mayo, de cohesión y calidad del Sistema Nacional de Salud", "6,90", 102),
    ("ley31", "ley-31-1995", "Ley 31/1995", "prevención de riesgos laborales",
     "Ley 31/1995, de 8 de noviembre, de Prevención de Riesgos Laborales", "6,90", 102),
    ("lo3_2007", "lo-3-2007", "LO 3/2007", "igualdad efectiva de mujeres y hombres",
     "Ley Orgánica 3/2007, de 22 de marzo, para la igualdad efectiva de mujeres y hombres", "6,90", 90),
    ("lo3_2018", "lo-3-2018", "LO 3/2018", "protección de datos",
     "Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales", "6,90", 98),
]

CSS = """
  :root { --azul:#1f4e79; --azul-2:#2e6da4; --claro:#eaf2fa; --texto:#1b2430; --suave:#5b6675; --borde:#d8e2ee;
          --fondo:#ffffff; --tarjeta:#ffffff; --ok:#1e7d4f; --ok-fondo:#e3f4ea; --mal:#b3261e; --mal-fondo:#fbe9e7; --acento:#ffd400; }
  @media (prefers-color-scheme: dark) {
    :root { --texto:#e8eef5; --suave:#a7b3c2; --borde:#2c3a4b; --fondo:#0f1620; --tarjeta:#162130; --claro:#142235;
            --ok-fondo:#123524; --mal-fondo:#3a1715; }
  }
  * { box-sizing: border-box; }
  html, body { overflow-x: clip; }
  body { overflow-wrap: anywhere; margin: 0; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
         color: var(--texto); background: var(--fondo); line-height: 1.55; }
  a { color: inherit; }
  .envoltorio { max-width: 820px; margin: 0 auto; padding: 0 16px; }
  header { border-bottom: 1px solid var(--borde); }
  header .envoltorio { display: flex; align-items: center; justify-content: space-between; height: 60px; }
  .marca { font-weight: 800; font-size: 1.2rem; text-decoration: none; letter-spacing: -0.02em; }
  .marca span { color: var(--azul-2); }
  header nav a { margin-left: 16px; text-decoration: none; color: var(--suave); font-size: .95rem; }
  .cabecera { padding: 36px 0 12px; background: linear-gradient(180deg, var(--claro), transparent); }
  h1 { font-size: clamp(1.6rem, 4.2vw, 2.4rem); line-height: 1.15; margin: 0 0 12px; letter-spacing: -0.02em; }
  .intro { color: var(--suave); margin: 0 0 8px; }
  .marcador { position: sticky; top: 0; z-index: 5; background: var(--fondo); border-bottom: 1px solid var(--borde);
              padding: 10px 0; font-weight: 700; }
  .marcador .envoltorio { display: flex; justify-content: space-between; gap: 12px; }
  .pregunta { border: 1px solid var(--borde); border-radius: 14px; padding: 18px; margin: 18px 0; background: var(--tarjeta); }
  .pregunta h2 { font-size: 1.08rem; margin: 0 0 12px; line-height: 1.4; }
  .pregunta h2 b { color: var(--azul-2); margin-right: 6px; }
  .opciones { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
  .opciones button { width: 100%; text-align: left; font: inherit; color: inherit; background: var(--claro);
                     border: 2px solid transparent; border-radius: 10px; padding: 11px 14px; cursor: pointer; }
  .opciones button:hover:not(:disabled) { border-color: var(--azul-2); }
  .opciones button:disabled { cursor: default; }
  .opciones button.bien { background: var(--ok-fondo); border-color: var(--ok); font-weight: 700; }
  .opciones button.mal { background: var(--mal-fondo); border-color: var(--mal); }
  .opciones .letra { font-weight: 800; margin-right: 8px; color: var(--azul-2); }
  .solucion { display: none; margin: 12px 0 0; padding: 10px 14px; border-left: 4px solid var(--ok); background: var(--claro);
              border-radius: 0 8px 8px 0; font-size: .95rem; }
  .pregunta.hecha .solucion { display: block; }
  .final { border: 2px solid var(--azul-2); border-radius: 16px; padding: 24px; margin: 30px 0; background: var(--tarjeta); }
  .final h2 { margin: 0 0 8px; }
  .nota-pago { margin: 14px 0 0; font-size: .92rem; color: var(--suave, #555); }
  .boton { display: inline-block; padding: 12px 20px; border-radius: 10px; font-weight: 700; text-decoration: none;
           border: 2px solid var(--azul); margin: 6px 8px 0 0; }
  .boton.lleno { background: var(--azul); color: #fff; }
  .otros { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; list-style: none; }
  .otros a { display: inline-block; border: 1px solid var(--borde); border-radius: 99px; padding: 6px 12px;
             text-decoration: none; font-size: .92rem; }
  .rejilla { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(250px, 100%), 1fr)); gap: 16px; margin: 20px 0 40px; }
  .tarjeta { border: 1px solid var(--borde); border-radius: 14px; padding: 18px; background: var(--tarjeta); text-decoration: none; display: block; }
  .tarjeta h2 { font-size: 1.1rem; margin: 0 0 4px; }
  .tarjeta p { margin: 0; color: var(--suave); font-size: .93rem; }
  footer { border-top: 1px solid var(--borde); padding: 24px 0 36px; color: var(--suave); font-size: .86rem; margin-top: 30px; }
  @media (max-width: 520px) { header nav { display: none; } }
"""

CONTADOR = """<script>
(function () {
  function contar(n) { try { new Image().src = 'https://hits.sh/c4rr0.github.io/leyclara/' + n + '.svg'; } catch (e) {} }
  window.leyclaraContar = contar;
  var g = (new URLSearchParams(location.search).get('g') || '').replace(/[^a-z0-9-]/gi, '').toLowerCase();
  contar('visita'); if (g) contar('visita-' + g);
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest('a'); if (!a) return;
    var h = a.getAttribute('href') || '', m = h.match(/muestras\\/(.+)\\.pdf$/);
    if (m) contar('descarga-' + m[1]);
    m = h.match(/gumroad\\.com\\/l\\/([\\w-]+)/); if (m) contar('comprar-' + m[1]);
  });
})();
</script>"""


def e(t: str) -> str:
    return html.escape(t, quote=True)


def leer(carpeta: str) -> list[dict]:
    est = (WEB / "shorts" / "preguntas" / carpeta / "muestra" / "estudio.md").read_text(encoding="utf-8")
    test = est.split("## Preguntas tipo test")[1]
    preg_txt, sol_txt = test.split("### Soluciones")
    sol = {int(m.group(1)): (m.group(2), m.group(3).strip())
           for m in re.finditer(r"(?m)^(\d+)\. ([a-d])\) (.*)$", sol_txt)}
    preguntas = []
    for m in re.finditer(r"(?ms)^(\d+)\. (.*?)(?=^\d+\. |\Z)", preg_txt):
        n, lineas = int(m.group(1)), m.group(2).strip().splitlines()
        opciones = [re.sub(r"^[a-d]\)\s*", "", x).strip() for x in lineas[1:5]]
        letra, expl = sol[n]
        preguntas.append({"n": n, "enunciado": lineas[0].strip(), "opciones": opciones,
                          "correcta": "abcd".index(letra), "explicacion": expl})
    return preguntas


def cabecera_html(titulo, descripcion, ruta, extra_head=""):
    RAIZ = "../../" if ruta.count("/") == 2 else "../"
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descripcion)}">
<link rel="canonical" href="{URL}{ruta}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descripcion)}">
<meta property="og:url" content="{URL}{ruta}">
<meta property="og:type" content="website">
<link rel="icon" href="{RAIZ}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{RAIZ}favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="{RAIZ}apple-touch-icon.png">
<style>{CSS}</style>
{extra_head}
</head>
<body>
<header><div class="envoltorio">
  <a class="marca" href="{'../../' if ruta.count('/') == 2 else '../'}">Ley<span>Clara</span></a>
  <nav><a href="{'../' if ruta.count('/') == 2 else './'}">Todos los test</a><a href="{'../../' if ruta.count('/') == 2 else '../'}#packs">Packs</a></nav>
</div></header>
"""


PIE = """<footer><div class="envoltorio">
  <p>LeyClara · Material de estudio independiente y no oficial, elaborado a partir de la versión consolidada del Boletín Oficial del Estado (BOE). No está vinculado a ninguna administración pública, servicio de salud ni academia. Contamos las visitas de forma anónima y sin cookies.</p>
</div></footer>
"""


def pagina_ley(ley, todas):
    carpeta, slug, corto, tema, completo, precio, n_pack = ley
    qs = leer(carpeta)
    ruta = f"test/{slug}/"
    titulo = f"Test {corto} ({tema}): {len(qs)} preguntas con solución | LeyClara"
    descripcion = (f"Test online gratis de la {corto} de {tema} para oposiciones sanitarias (TCAE, celador, "
                   f"enfermería). {len(qs)} preguntas con la solución y el artículo exacto. Sin registro.")
    datos = {"ley": slug, "correctas": [q["correcta"] for q in qs]}
    ld = {"@context": "https://schema.org", "@type": "Quiz", "name": f"Test {corto} ({tema})",
          "about": {"@type": "Thing", "name": completo}, "educationalLevel": "Oposiciones",
          "inLanguage": "es", "url": URL + ruta,
          "hasPart": [{"@type": "Question", "name": q["enunciado"], "eduQuestionType": "Multiple choice",
                       "suggestedAnswer": [{"@type": "Answer", "text": o} for i, o in enumerate(q["opciones"]) if i != q["correcta"]],
                       "acceptedAnswer": {"@type": "Answer", "text": q["opciones"][q["correcta"]]}} for q in qs]}
    h = [cabecera_html(titulo, descripcion, ruta,
                       f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')]
    h.append(f"""<section class="cabecera"><div class="envoltorio">
  <h1>Test de la {e(corto)} ({e(tema)})</h1>
  <p class="intro">{len(qs)} preguntas tipo test de la <b>{e(completo)}</b>, una de las leyes del temario común de las OPE de los servicios de salud (SAS, SERMAS, Sacyl, SESCAM, Osakidetza…). Pulsa una opción: verás al momento si aciertas y en qué artículo está la respuesta.</p>
  <p class="intro">Texto actualizado con la versión consolidada del BOE.</p>
</div></section>
<div class="marcador"><div class="envoltorio"><span>Aciertos: <span id="aciertos">0</span> / <span id="respondidas">0</span></span><span>{len(qs)} preguntas</span></div></div>
<main class="envoltorio">
""")
    for i, q in enumerate(qs):
        h.append(f'<article class="pregunta" data-i="{i}">\n  <h2><b>{i + 1}.</b>{e(q["enunciado"])}</h2>\n  <ol class="opciones">')
        for j, o in enumerate(q["opciones"]):
            h.append(f'    <li><button type="button" data-j="{j}"><span class="letra">{"abcd"[j]})</span>{e(o)}</button></li>')
        h.append(f'  </ol>\n  <p class="solucion">Correcta: <b>{"abcd"[q["correcta"]]})</b> {e(q["explicacion"])}</p>\n</article>')
    otros = "".join(f'<li><a href="../{l[1]}/">Test {e(l[2])} · {e(l[3])}</a></li>' for l in todas if l[1] != slug)
    h.append(f"""<section class="final" id="final">
  <h2 id="resultado">¿Qué tal te ha ido?</h2>
  <p>Este test son las {len(qs)} preguntas de la muestra gratis. El <b>pack de la {e(corto)}</b> trae la ley explicada y ordenada, esquemas, tablas con los plazos que más caen, fichas de repaso y {n_pack} preguntas tipo test con el artículo de cada respuesta, en PDF y Word.</p>
  <a class="boton lleno" href="{TIENDA}{slug}">Pack {e(corto)} · {precio} €</a>
  <a class="boton" href="{TIENDA}pack-completo">Las 8 leyes · 24,90 €</a>
  <a class="boton" href="../../muestras/muestra-{slug}.pdf" download>Muestra en PDF</a>
  <p class="nota-pago">🔒 Pago seguro a través de <b>Gumroad</b> (tarjeta, Google Pay o PayPal). Si la página de pago te sale en inglés, es normal: pulsa <b>«Compra esto»</b> (o «I want this!»), escribe tu correo y recibirás el PDF y el Word al momento en tu email.</p>
</section>
<h2>Más test de legislación sanitaria</h2>
<ul class="otros">{otros}</ul>
</main>
""")
    h.append(PIE)
    h.append(f"""<script>
(function () {{
  var datos = {json.dumps(datos)}, aciertos = 0, hechas = 0, total = datos.correctas.length;
  document.querySelectorAll('.pregunta').forEach(function (p) {{
    var i = +p.dataset.i, botones = p.querySelectorAll('button');
    botones.forEach(function (b) {{
      b.addEventListener('click', function () {{
        if (p.classList.contains('hecha')) return;
        var j = +b.dataset.j, ok = datos.correctas[i];
        p.classList.add('hecha');
        botones.forEach(function (x) {{ x.disabled = true; }});
        botones[ok].classList.add('bien');
        if (j !== ok) b.classList.add('mal'); else aciertos++;
        hechas++;
        document.getElementById('aciertos').textContent = aciertos;
        document.getElementById('respondidas').textContent = hechas;
        if (hechas === 1 && window.leyclaraContar) leyclaraContar('test-empezado-' + datos.ley);
        if (hechas === total) {{
          document.getElementById('resultado').textContent = 'Has acertado ' + aciertos + ' de ' + total + (aciertos >= total * 0.8 ? '. ¡Muy bien!' : '. Toca repasar.');
          if (window.leyclaraContar) leyclaraContar('test-terminado-' + datos.ley);
        }}
      }});
    }});
  }});
}})();
</script>
{CONTADOR}
</body>
</html>
""")
    destino = WEB / ruta
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "index.html").write_text("\n".join(h), encoding="utf-8")
    return ruta


def portada(todas):
    ruta = "test/"
    titulo = "Test de legislación sanitaria para oposiciones: gratis y con solución | LeyClara"
    descripcion = ("Test online gratis de las leyes del temario común de las OPE de sanidad: Estatuto Marco, Ley 41/2002, "
                   "Ley General de Sanidad, prevención de riesgos, igualdad y protección de datos. Con el artículo de cada respuesta.")
    h = [cabecera_html(titulo, descripcion, ruta)]
    h.append("""<section class="cabecera"><div class="envoltorio">
  <h1>Test de legislación sanitaria para oposiciones</h1>
  <p class="intro">Test online gratis de las leyes que entran en el temario común de casi todas las OPE de los servicios de salud: TCAE, celador, enfermería, técnicos y personal de gestión. Cada respuesta indica el artículo exacto. Sin registro.</p>
</div></section>
<main class="envoltorio"><div class="rejilla">""")
    for l in todas:
        h.append(f'<a class="tarjeta" href="{l[1]}/"><h2>Test {e(l[2])}</h2><p>{e(l[3][0].upper() + l[3][1:])} · 20 preguntas</p></a>')
    h.append("</div></main>")
    h.append(PIE + CONTADOR + "\n</body>\n</html>\n")
    (WEB / ruta).mkdir(exist_ok=True)
    (WEB / ruta / "index.html").write_text("\n".join(h), encoding="utf-8")
    return ruta


if __name__ == "__main__":
    rutas = ["", portada(LEYES)] + [pagina_ley(l, LEYES) for l in LEYES]
    mapa = "\n".join(f"  <url><loc>{URL}{r}</loc></url>" for r in rutas)
    (WEB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     f"{mapa}\n</urlset>\n", encoding="utf-8")
    (WEB / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL}sitemap.xml\n", encoding="utf-8")
    print(len(rutas), "páginas en el sitemap")
