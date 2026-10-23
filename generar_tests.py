"""Genera las páginas de test online (una por ley) a partir de las preguntas de las muestras gratis,
más la portada /test/, sitemap.xml y robots.txt. Pensado para que Google las encuentre
(«test ley 41/2002», «test estatuto marco»...).

Uso: python generar_tests.py   (desde la carpeta web/)
"""
import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path

from faq_leyes import FAQ, enlace_boe

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
    ("ley2_1998_and", "ley-2-1998-andalucia", "Ley 2/1998", "Salud de Andalucía",
     "Ley 2/1998, de 15 de junio, de Salud de Andalucía", "6,90", 102),
    ("and_igualdad", "leyes-12-13-2007-andalucia", "Leyes 12 y 13/2007", "igualdad y violencia de género en Andalucía",
     "Ley 12/2007, para la promoción de la igualdad de género en Andalucía, y Ley 13/2007, de medidas de prevención "
     "y protección integral contra la violencia de género (ambas de 26 de noviembre)", "6,90", 90),
    ("ley53", "ley-53-1984", "Ley 53/1984", "incompatibilidades",
     "Ley 53/1984, de 26 de diciembre, de Incompatibilidades del personal al servicio de las Administraciones Públicas", "6,90", 80),
]
# Temario común de las oposiciones de la Administración (packs de Iris, 21/10/2026): no entran en el pack de las 12 leyes
LEYES_ADMIN = [
    ("constitucion", "constitucion-espanola", "Constitución Española", "Carta Magna de 1978",
     "Constitución Española de 1978", "6,90", 118),
    ("ley39", "ley-39-2015", "Ley 39/2015", "procedimiento administrativo común",
     "Ley 39/2015, de 1 de octubre, del Procedimiento Administrativo Común de las Administraciones Públicas", "6,90", 173),
    ("ley40", "ley-40-2015", "Ley 40/2015", "régimen jurídico del sector público",
     "Ley 40/2015, de 1 de octubre, de Régimen Jurídico del Sector Público", "6,90", 132),
    ("trebep", "trebep", "TREBEP", "Estatuto Básico del Empleado Público",
     "Texto refundido de la Ley del Estatuto Básico del Empleado Público (Real Decreto Legislativo 5/2015, de 30 de octubre)", "6,90", 204),
]
TODAS = LEYES + LEYES_ADMIN
ADMIN = {l[0] for l in LEYES_ADMIN}
# Packs aún sin producto en Gumroad: en vez de «Comprar», aviso por Telegram. Quitar el slug al crear el producto.
SIN_TIENDA = {l[1] for l in LEYES_ADMIN}
TELEGRAM = "https://t.me/leyclara_avisos"

# Leyes autonómicas: solo entran en la OPE de su servicio de salud
AMBITO = {"ley2_1998_and": "la OPE del Servicio Andaluz de Salud (SAS)",
          "and_igualdad": "la OPE del Servicio Andaluz de Salud (SAS)",
          **{c: "las oposiciones de la Administración (Estado, comunidades autónomas y ayuntamientos) y de muchas OPE de sanidad"
             for c in ADMIN}}


LANZAMIENTO = "Precios de lanzamiento hasta el 31 de octubre."
TOTAL_TEST = sum(l[6] for l in LEYES)
GRATIS = "ley-53-1984"  # pack entero regalado (0 € en Gumroad) para que prueben la calidad antes de comprar
# leyes que deroga o modifica el proyecto del nuevo Estatuto Marco (página de estatuto_marco.py)
AFECTADAS_EM = {"ley-55-2003": "la derogaba", "ley-16-2003": "la modificaba", "ley-44-2003": "la modificaba"}


def aviso_em(slug, raiz):
    if slug not in AFECTADAS_EM:
        return ""
    return (f'<p class="intro">📌 El proyecto del nuevo Estatuto Marco, que {AFECTADAS_EM[slug]}, caducó al disolverse las Cortes '
            f'(6/10/2026): esta ley sigue vigente. <a href="{raiz}nuevo-estatuto-marco/">Qué cambiaba y qué se estudia</a>.</p>')
SUELTAS = f"{sum(float(l[5].replace(',', '.')) for l in LEYES):.2f}".replace(".", ",")

# Páginas reales del pack (ventas/vistas_previas.py las genera en web/vistas/<slug>/)
VISTAS = {"0-indice": "Índice de las 12 leyes", "1-ley-explicada": "Ley explicada", "2-esquema": "Esquema",
          "3-test": "Test con solución", "4-fichas": "Fichas de repaso"}


def vistas_previas(slug, raiz):
    imgs = sorted((WEB / "vistas" / slug).glob("*.jpg"))
    if not imgs:
        return ""
    celdas = "".join(
        f'<a href="{raiz}vistas/{slug}/{i.name}" target="_blank" rel="noopener">'
        f'<img src="{raiz}vistas/{slug}/{i.name}" width="640" height="906" loading="lazy" '
        f'alt="Página de muestra del pack: {VISTAS.get(i.stem, i.stem)}"><span>{VISTAS.get(i.stem, i.stem)}</span></a>'
        for i in imgs)
    return (f'<div class="por-dentro"><h3>Así es el pack por dentro</h3>'
            f'<p>Páginas reales del PDF. Pulsa en cualquiera para verla en grande.</p><div class="vistas">{celdas}</div></div>')


def boe_a(slug, respuesta):
    """Enlace al artículo citado en el BOE (texto consolidado) al final de una respuesta de las FAQ."""
    en = enlace_boe(slug, respuesta)
    if not en:
        return ""
    return f' <a href="{e(en[0])}" target="_blank" rel="noopener">Ver art. {en[1]} en el BOE</a>'


def la(corto):
    """Artículo para el nombre corto: «la Ley 55/2003», «las Leyes 12 y 13/2007», «el TREBEP»."""
    return "las " + corto if corto.startswith("Leyes") else "el " + corto if corto == "TREBEP" else "la " + corto


def de(corto):
    """«de la Ley 55/2003», «del TREBEP»."""
    return re.sub(r"^de el ", "del ", "de " + la(corto))


def publico(carpeta):
    return ("oposiciones de la Administración (auxiliar, administrativo, gestión)" if carpeta in ADMIN
            else "oposiciones sanitarias (TCAE, celador, enfermería)")

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
  .mensaje-final { font-size: 1.08rem; font-weight: 600; background: var(--claro); border-left: 4px solid var(--acento); padding: 12px 14px; border-radius: 8px; }
  .lanzamiento { font-weight: 700; color: var(--azul-2); margin: 14px 0 0; }
  .final h2 { margin: 0 0 8px; }
  .por-dentro { background: var(--claro); border: 1px solid var(--borde); border-radius: 16px; padding: 18px 18px 14px; margin: 18px 0 22px; }
  .por-dentro h3 { margin: 0 0 2px; font-size: 1.05rem; }
  .por-dentro p { margin: 0 0 14px; color: var(--suave); font-size: .9rem; }
  .vistas { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 14px; }
  .vistas a { text-decoration: none; color: var(--texto); font-size: .85rem; font-weight: 600; text-align: center; }
  .vistas img { display: block; width: 100%; height: auto; aspect-ratio: 3 / 4; object-fit: cover; object-position: top;
                border-radius: 8px; background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,.18); margin-bottom: 8px; transition: transform .15s; }
  .vistas a:hover img { transform: translateY(-3px); }
  @media (max-width: 560px) {
    .vistas { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; padding-bottom: 4px; }
    .vistas::-webkit-scrollbar { display: none; }
    .vistas a { flex: 0 0 40%; scroll-snap-align: start; }
  }
  .ahorro { font-weight: 400; opacity: .8; }
  .mitad { border: 1px dashed var(--azul-2); border-radius: 12px; padding: 12px 16px; margin: 18px 0; font-size: .95rem; }
  .mitad a { font-weight: 700; color: var(--azul-2); }
  .regalo { margin: 14px 0 0; padding: 10px 14px; border-left: 4px solid var(--acento); background: var(--claro); border-radius: 8px; font-size: .95rem; }
  .regalo a { font-weight: 700; color: var(--azul-2); }
  .canal-aviso { margin: 14px 0 0; padding: 10px 14px; border-left: 4px solid #229ed9; background: var(--claro); border-radius: 8px; font-size: .95rem; }
  .canal-aviso a { font-weight: 700; color: var(--azul-2); }
  p.siguiente { margin: 12px 0 0; font-size: 1.05rem; }
  a.siguiente { font-weight: 700; color: var(--azul-2); }
  .nota-pago { margin: 14px 0 0; font-size: .92rem; color: var(--suave, #555); }
  .boton { display: inline-block; padding: 12px 20px; border-radius: 10px; font-weight: 700; text-decoration: none;
           border: 2px solid var(--azul); margin: 6px 8px 0 0; }
  .boton.lleno { background: var(--azul); color: #fff; }
  .otros { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; list-style: none; }
  .faq h3 { margin: 18px 0 4px; font-size: 1.05rem; }
  .faq p { margin: 0; }
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
  var g = (new URLSearchParams(location.search).get('g') || '').replace(/[^a-z0-9-]/gi, '').toLowerCase();
  contar('visita'); if (g) contar('visita-' + g);
  // origen de la visita (?g=) guardado mientras navega, para saber qué origen termina tests y pulsa Comprar (20/10)
  var origen = '';
  try { if (g) sessionStorage.setItem('leyclara-g', g); origen = sessionStorage.getItem('leyclara-g') || ''; } catch (e) { origen = g; }
  if (origen) origen = /^tg-/.test(origen) ? 'tg' : ['yt', 'libro', 'pdf'].indexOf(origen) >= 0 ? origen : 'otro';
  function deOrigen(ev) { if (origen) contar(ev + '-de-' + origen); }
  window.leyclaraContar = function (n) { contar(n); if (/^test-terminado-/.test(n)) deOrigen('test-terminado'); };
  // tipo de página, para saber dónde se ve la oferta y desde dónde se pulsa Comprar (embudo, 18/10)
  var ruta = location.pathname, donde = /\\/test\\/$/.test(ruta) ? 'portada-test' : /\\/test\\/[^\\/]+\\//.test(ruta) ? 'test' : /\\/resumen\\/[^\\/]+\\//.test(ruta) ? 'resumen'
    : /estatuto-marco/.test(ruta) ? 'estatuto' : 'otra';
  document.addEventListener('click', function (ev) {
    var a = ev.target.closest('a'); if (!a) return;
    var h = a.getAttribute('href') || '', m = h.match(/muestras\\/(.+)\\.pdf$/);
    if (m) contar('descarga-' + m[1]);
    if (/\\/vistas\\//.test(h)) contar('vista-previa-en-' + donde);
    m = h.match(/gumroad\\.com\\/l\\/([\\w-]+)/); if (m) { contar('comprar-' + m[1]); contar('comprar-en-' + donde); deOrigen('comprar'); }
    if (/t\\.me\\/leyclara_avisos/.test(h)) { contar('telegram-canal-en-' + donde); deOrigen('telegram-canal'); }
    if (a.classList.contains('siguiente')) contar('siguiente-test');
  });
  var fin = document.getElementById('final');
  if (fin && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      if (es[0].isIntersecting) { contar('oferta-vista-' + donde); io.disconnect(); }
    }, {threshold: 0.3});
    io.observe(fin);
  }
})();
</script>"""


def e(t: str) -> str:
    return html.escape(t, quote=True)


def leer(carpeta: str, completo: bool = False) -> list[dict]:
    """Preguntas de la muestra gratis o, con completo=True, todas las del pack (../<carpeta>/estudio.md, fuera del repo)."""
    ruta = (WEB.parent / carpeta / "estudio.md") if completo else (WEB / "shorts" / "preguntas" / carpeta / "muestra" / "estudio.md")
    est = ruta.read_text(encoding="utf-8")
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


# Test por temas (19/10): páginas más concretas que la de cada ley para búsquedas con menos competencia
# («test régimen disciplinario estatuto marco»). Preguntas del pack completo cuyo artículo cae en los rangos.
# carpeta: [(slug, nombre del tema, [(art. desde, art. hasta), ...])]
TEMAS = {
    "ley55": [("personal-temporal", "clasificación del personal, interinos y sustitutos", [(5, 9)]),
              ("seleccion-y-provision", "selección, provisión de plazas y promoción interna", [(29, 35)]),
              ("jornada-y-permisos", "jornada, descansos, vacaciones y permisos", [(46, 61)]),
              ("situaciones", "situaciones del personal estatutario", [(62, 69)]),
              ("regimen-disciplinario", "régimen disciplinario: faltas, sanciones y prescripción", [(70, 75)]),
              ("condicion-de-fijo-y-retribuciones", "condición de fijo, movilidad, carrera y retribuciones", [(17, 28), (36, 45)])],
    "ley41": [("informacion-sanitaria", "principios básicos y derecho a la información sanitaria", [(1, 7)]),
              ("consentimiento-informado", "consentimiento informado e instrucciones previas", [(8, 13)]),
              ("historia-clinica", "historia clínica e informe de alta", [(14, 23)])],
    "ley14": [("sistema-de-salud", "derechos de los ciudadanos y sistema de salud", [(1, 37)]),
              ("areas-de-salud", "servicios de salud, áreas de salud y zonas básicas", [(44, 87)]),
              ("competencias-y-sanidad-privada", "competencias, sanidad privada y productos farmacéuticos", [(38, 43), (88, 116)])],
    "ley44": [("ejercicio-profesional", "profesiones sanitarias y su ejercicio", [(1, 11)]),
              ("formacion-especializada", "formación sanitaria especializada (MIR, EIR) y formación continuada", [(12, 36)]),
              ("desarrollo-profesional", "desarrollo profesional, ejercicio privado y Foro Profesional", [(37, 47)])],
    "ley16": [("cartera-de-servicios", "prestaciones y cartera común de servicios del SNS", [(7, 29)]),
              ("consejo-interterritorial", "principios, calidad y Consejo Interterritorial del SNS", [(1, 6), (59, 79)]),
              ("farmacia-y-profesionales", "farmacia, profesionales, investigación e información sanitaria", [(30, 58)])],
    "ley31": [("derechos-y-obligaciones", "derechos y obligaciones en prevención de riesgos laborales", [(14, 29)]),
              ("delegados-de-prevencion", "delegados de prevención y comité de seguridad y salud", [(33, 40)]),
              ("servicios-de-prevencion", "definiciones, política preventiva y servicios de prevención", [(1, 13), (30, 32), (41, 54)])],
    "lo3_2007": [("igualdad-y-tutela", "principio de igualdad y tutela contra la discriminación", [(1, 13)]),
                 ("politicas-publicas", "políticas públicas para la igualdad", [(14, 35)]),
                 ("igualdad-en-el-trabajo", "igualdad en el trabajo y en los medios de comunicación", [(36, 50)]),
                 ("empleo-publico", "igualdad en el empleo público", [(51, 78)])],
    "lo3_2018": [("principios-y-derechos", "principios y derechos de las personas (acceso, rectificación, supresión…)", [(1, 18)]),
                 ("delegado-de-proteccion-de-datos", "responsable, encargado y delegado de protección de datos", [(19, 39)]),
                 ("autoridades", "Agencia Española de Protección de Datos y procedimientos", [(44, 69)]),
                 ("regimen-sancionador", "régimen sancionador: infracciones y prescripción", [(70, 78)]),
                 ("derechos-digitales", "derechos digitales: desconexión digital e intimidad", [(79, 97)])],
    "ley2_1998_and": [("derechos-de-los-ciudadanos", "derechos, deberes y participación de los ciudadanos", [(1, 14)]),
                      ("actuaciones-en-salud", "actuaciones en salud y Plan Andaluz de Salud", [(15, 42)]),
                      ("ordenacion-sanitaria", "ordenación sanitaria: SAS, áreas y zonas básicas", [(43, 81)])],
    "ley53": [("actividades-publicas", "compatibilidad con un segundo puesto o actividad pública", [(1, 10)]),
              ("actividades-privadas", "actividades privadas y disposiciones comunes", [(11, 20)])],
}
MAX_TEMA = 12  # preguntas por página de tema: el resto se queda en el pack


def articulo(explicacion: str):
    m = re.match(r"Arts?\.\s*(\d+)", explicacion)
    return int(m.group(1)) if m else None


def temas_de(ley):
    """[(ruta, nombre, preguntas)] de los temas de una ley con al menos 8 preguntas."""
    carpeta, slug = ley[0], ley[1]
    if carpeta not in TEMAS:
        return []
    todas = leer(carpeta, completo=True)
    salida = []
    for t_slug, nombre, rangos in TEMAS[carpeta]:
        qs = [q for q in todas if (a := articulo(q["explicacion"])) is not None and any(d <= a <= h for d, h in rangos)]
        if len(qs) < 8:
            continue
        if len(qs) > MAX_TEMA:  # repartidas por todo el tema, no solo las primeras
            qs = [qs[round(i * (len(qs) - 1) / (MAX_TEMA - 1))] for i in range(MAX_TEMA)]
        salida.append((f"test/{slug}-{t_slug}/", nombre, qs))
    return salida


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
  <nav><a href="{RAIZ}test/">Todos los test</a><a href="{RAIZ}resumen/">Resúmenes</a><a href="{RAIZ}#packs">Packs</a></nav>
</div></header>
"""


PIE = """<footer><div class="envoltorio">
  <p>LeyClara · Material de estudio independiente y no oficial, elaborado a partir de la versión consolidada del Boletín Oficial del Estado (BOE). No está vinculado a ninguna administración pública, servicio de salud ni academia. Contamos las visitas de forma anónima y sin cookies.</p>
  <p>📲 <a href="https://t.me/leyclara_avisos">Avisos gratis por Telegram</a> cuando el BOE cambie una ley de tu temario.</p>
  <p><a href="https://c4rr0.github.io/leyclara/actualizaciones/">Actualizaciones, erratas y quién hace LeyClara</a> · Comprobamos cada semana que las leyes de los packs siguen al día con el BOE.</p>
</div></footer>
"""


def pagina_ley(ley, todas, tema_pag=None):
    """Página de test de una ley (muestra gratis) o, con tema_pag=(ruta, nombre, preguntas), de uno de sus temas."""
    carpeta, slug, corto, tema, completo, precio, n_pack = ley
    temas = temas_de(ley)
    if tema_pag:
        ruta, nombre_tema, qs = tema_pag
    else:
        ruta, qs = f"test/{slug}/", leer(carpeta)
    coste = "gratis" if slug == GRATIS else f"{precio} €"
    regalo = "" if slug == GRATIS else (
        f'<p class="regalo">🎁 ¿Quieres ver un pack completo antes de comprar? El de la '
        f'<a href="{TIENDA}{GRATIS}">Ley 53/1984 es gratis</a>: mismo formato, solo te pide el correo para enviártelo.</p>')
    if tema_pag:
        titulo = f"Test {corto}: {nombre_tema} ({len(qs)} preguntas) | LeyClara"
        descripcion = (f"Test gratis {de(corto)} ({tema}) sobre {nombre_tema}, para {publico(carpeta)}. {len(qs)} preguntas con la solución y el artículo exacto. Sin registro.")
        h1 = f"Test {de(corto)}: {nombre_tema}"
        que_es = f"{len(qs)} preguntas tipo test sobre <b>{e(nombre_tema)}</b> de la {e(completo)}"
        sobre_muestra = f"Este test son {len(qs)} preguntas de este tema sacadas del pack"
        mitad = f"Estas {len(qs)} preguntas son solo una parte"
    else:
        titulo = f"Test {corto} ({tema}): {len(qs)} preguntas con solución | LeyClara"
        descripcion = (f"Test online gratis {de(corto)} de {tema} para {publico(carpeta)}. {len(qs)} preguntas con la solución y el artículo exacto. Sin registro.")
        h1 = f"Test {de(corto)} ({tema})"
        que_es = f"{len(qs)} preguntas tipo test de la <b>{e(completo)}</b>"
        sobre_muestra = f"Este test son las {len(qs)} preguntas de la muestra gratis"
        mitad = f"Estas {len(qs)} preguntas son la muestra gratis"
    por_temas = "".join(f'<li><a href="../{r.split("/")[1]}/">{e(n[0].upper() + n[1:])}</a></li>'
                        for r, n, _ in temas if r != ruta)
    if tema_pag:
        por_temas = f'<li><a href="../{slug}/">Test general {e(de(corto))}</a></li>' + por_temas
    # «Siguiente test» al acabar (20/10): el siguiente tema de la misma ley y, tras el último, la ley siguiente
    rutas_temas = [r for r, _, _ in temas]
    if tema_pag and ruta in rutas_temas[:-1]:
        sig_r, sig_n = temas[rutas_temas.index(ruta) + 1][:2]
        sig = (sig_r.split("/")[1], f"{corto}: {sig_n}")
    elif not tema_pag and temas:
        sig = (temas[0][0].split("/")[1], f"{corto}: {temas[0][1]}")
    else:
        l_sig = todas[(next(i for i, l in enumerate(todas) if l[1] == slug) + 1) % len(todas)]
        sig = (l_sig[1], f"{l_sig[2]} ({l_sig[3]})")
    siguiente = f'<p class="siguiente">➡️ <a class="siguiente" href="../{sig[0]}/">Siguiente test: {e(sig[1])}</a></p>'
    datos = {"ley": slug, "correctas": [q["correcta"] for q in qs]}
    ld = {"@context": "https://schema.org", "@type": "Quiz", "name": f"Test {corto}: {nombre_tema}" if tema_pag else f"Test {corto} ({tema})",
          "about": {"@type": "Thing", "name": completo}, "educationalLevel": "Oposiciones",
          "inLanguage": "es", "url": URL + ruta,
          "learningResourceType": "Practice problem", "assesses": f"{corto} ({tema})",
          "hasPart": [{"@type": "Question", "name": q["enunciado"], "text": q["enunciado"], "eduQuestionType": "Multiple choice",
                       "learningResourceType": "Practice problem", "encodingFormat": "text/plain",
                       "assesses": f"{corto} ({tema})", "educationalLevel": "Oposiciones", "typicalAgeRange": "18-",
                       "suggestedAnswer": [{"@type": "Answer", "position": i, "text": o, "encodingFormat": "text/plain"}
                                           for i, o in enumerate(q["opciones"]) if i != q["correcta"]],
                       "acceptedAnswer": {"@type": "Answer", "position": q["correcta"], "text": q["opciones"][q["correcta"]],
                                          "encodingFormat": "text/plain",
                                          "answerExplanation": {"@type": "Comment", "text": q["explicacion"], "encodingFormat": "text/plain"}}}
                      for q in qs]}
    # Preguntas frecuentes visibles (faq_leyes.py, comprobadas contra el BOE), solo en la página general de la ley
    faq, extra_ld = "", ""
    if not tema_pag and slug in FAQ:
        faq = (f'<section class="faq"><h2>Preguntas frecuentes sobre {e(la(corto))}</h2>'
               + "".join(f"<h3>{e(p)}</h3><p>{e(r)}{boe_a(slug, r)}</p>" for p, r in FAQ[slug]) + "</section>")
        ld_faq = {"@context": "https://schema.org", "@type": "FAQPage",
                  "mainEntity": [{"@type": "Question", "name": p, "acceptedAnswer": {"@type": "Answer", "text": r}}
                                 for p, r in FAQ[slug]]}
        extra_ld = f'<script type="application/ld+json">{json.dumps(ld_faq, ensure_ascii=False)}</script>'
    h = [cabecera_html(titulo, descripcion, ruta,
                       f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' + extra_ld)]
    h.append(f"""<section class="cabecera"><div class="envoltorio">
  <h1>{e(h1)}</h1>
  <p class="intro">{que_es}, del temario común de {AMBITO.get(carpeta, "las OPE de los servicios de salud (SAS, SERMAS, Sacyl, SESCAM, Osakidetza…)")}. Pulsa una opción: verás al momento si aciertas y en qué artículo está la respuesta.</p>
  <p class="intro">Texto actualizado con la versión consolidada del BOE.{"" if slug == GRATIS else f' 🎁 ¿Quieres ver un pack completo? <a href="{TIENDA}{GRATIS}">El de la Ley 53/1984 es gratis</a>.'}</p>
  {aviso_em(slug, "../../")}
</div></section>
<div class="marcador"><div class="envoltorio"><span>Aciertos: <span id="aciertos">0</span> / <span id="respondidas">0</span></span><span>{len(qs)} preguntas</span></div></div>
<main class="envoltorio">
""")
    for i, q in enumerate(qs):
        h.append(f'<article class="pregunta" data-i="{i}">\n  <h2><b>{i + 1}.</b>{e(q["enunciado"])}</h2>\n  <ol class="opciones">')
        for j, o in enumerate(q["opciones"]):
            h.append(f'    <li><button type="button" data-j="{j}"><span class="letra">{"abcd"[j]})</span>{e(o)}</button></li>')
        h.append(f'  </ol>\n  <p class="solucion">Correcta: <b>{"abcd"[q["correcta"]]})</b> {e(q["explicacion"])}</p>\n</article>')
        if i == len(qs) // 2 - 1:  # a mitad del test, solo visible cuando se han respondido la mitad
            h.append(f'<aside class="mitad" id="mitad" hidden>Vas por la mitad 💪 {mitad}: '
                     f'el pack {e(de(corto))} trae {n_pack}, cada una con su artículo, además de la ley explicada, esquemas y fichas. '
                     + (f'<a href="{TELEGRAM}" target="_blank" rel="noopener">Sale muy pronto: te aviso por Telegram</a></aside>'
                        if slug in SIN_TIENDA else
                        f'<a href="{TIENDA}{slug}" target="_blank" rel="noopener">Ver el pack ({coste})</a></aside>'))
    otros = "".join(f'<li><a href="../{l[1]}/">Test {e(l[2])} · {e(l[3])}</a></li>' for l in todas if l[1] != slug)
    if slug in SIN_TIENDA:
        comprar = (f'<a class="boton lleno" href="{TELEGRAM}">Pack {e(corto)}: muy pronto · Avísame por Telegram</a>')
        pleno = "¡Pleno! Esta ley la llevas bien. Prueba con el siguiente test para repasar el resto del temario."
    else:
        comprar = (f'<a class="boton lleno" href="{TIENDA}{slug}">Pack {e(corto)} · {coste.capitalize()}</a>\n'
                   f'  <a class="boton" href="{TIENDA}pack-completo">Las 12 leyes · 24,90 € <span class="ahorro">(sueltas {SUELTAS} €)</span></a>')
        pleno = (f"¡Pleno! Esta ley la llevas bien. Para mantener el nivel en todo el temario, el pack completo trae "
                 f"{TOTAL_TEST} preguntas de las 12 leyes con su artículo.")
    h.append(f"""<section class="final" id="final">
  <h2 id="resultado">¿Qué tal te ha ido?</h2>
  <p id="mensaje-final" class="mensaje-final" hidden></p>
  {siguiente}
  <p class="canal-aviso">📲 ¿Quieres seguir practicando? En el canal de Telegram pongo <b>un test cada día</b> y aviso cuando cambia alguna ley del temario. <a href="https://t.me/leyclara_avisos">Únete gratis</a></p>
  {vistas_previas(slug, "../../")}
  {comprar}
  {regalo}
  <p>{sobre_muestra}. El <b>pack {e(de(corto))}</b> trae la ley explicada y ordenada, esquemas, tablas con los plazos que más caen, fichas de repaso y {n_pack} preguntas tipo test con el artículo de cada respuesta, en PDF y Word.</p>
  {f'<p class="lanzamiento">{LANZAMIENTO}</p>' if LANZAMIENTO and slug not in SIN_TIENDA else ''}
  <a class="boton" href="../../muestras/muestra-{slug}.pdf" download>Muestra en PDF</a>
  <a class="boton" href="../../resumen/{slug}/">Resumen y datos clave</a>
  {"" if slug in SIN_TIENDA else '<p class="nota-pago">🔒 Pago seguro a través de <b>Gumroad</b> (tarjeta, Google Pay o PayPal). Precio final con <b>IVA incluido</b>. <b>Garantía de 7 días:</b> si no te sirve, te devolvemos el dinero. Si la página de pago te sale en inglés, es normal: pulsa <b>«Compra esto»</b> (o «I want this!»), escribe tu correo y recibirás el PDF y el Word al momento en tu email.</p>'}
</section>
{f'<h2>Test {e(de(corto))} por temas</h2>{chr(10)}<ul class="otros">{por_temas}</ul>' if por_temas else ''}
{faq}
<h2>Más test de legislación</h2>
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
        if (hechas === Math.floor(total / 2) && hechas < total) document.getElementById('mitad').hidden = false;
        if (hechas === total) {{
          var fallos = total - aciertos, msg = document.getElementById('mensaje-final');
          document.getElementById('resultado').textContent = 'Has acertado ' + aciertos + ' de ' + total + (aciertos >= total * 0.8 ? '. ¡Muy bien!' : '. Toca repasar.');
          msg.textContent = fallos > 0
            ? 'Has fallado ' + fallos + (fallos === 1 ? ' pregunta' : ' preguntas') + ' de solo ' + total + '. En el examen son ese tipo de detalles (plazos, órganos, artículos) los que deciden la plaza. El pack de esta ley trae {n_pack} preguntas, cada una con su artículo, y fichas para repasar justo lo que falles.'
            : '{pleno}';
          msg.hidden = false;
          setTimeout(function () {{ document.getElementById('final').scrollIntoView({{behavior: 'smooth'}}); }}, 1500);
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
  <p class="regalo">🎁 <b>Regalo:</b> el pack completo de la Ley 53/1984 de incompatibilidades (ley explicada, esquema, 80 test y fichas, en PDF y Word) es gratis. <a href="https://carrosphere.gumroad.com/l/ley-53-1984">Descárgalo aquí</a>: solo te pide el correo.</p>
  <p class="canal-aviso">📲 Hago estos tests yo mismo a partir del BOE. En el canal de Telegram pongo <b>un test cada día</b> y aviso cuando cambia alguna ley del temario. <a href="https://t.me/leyclara_avisos">Únete gratis</a></p>
</div></section>
<main class="envoltorio"><div class="rejilla">""")
    for l in todas:
        h.append(f'<a class="tarjeta" href="{l[1]}/"><h2>Test {e(l[2])}</h2><p>{e(l[3][0].upper() + l[3][1:])} · 20 preguntas</p></a>')
    h.append("</div>\n<h2>Test por temas</h2>")
    for l in todas:
        temas = temas_de(l)
        if temas:
            enlaces = "".join(f'<li><a href="{r.split("/")[1]}/">{e(n[0].upper() + n[1:])}</a></li>' for r, n, _ in temas)
            h.append(f'<h3>{e(l[2])} · {e(l[3])}</h3>\n<ul class="otros">{enlaces}</ul>')
    h.append("</main>")
    h.append(PIE + CONTADOR + "\n</body>\n</html>\n")
    (WEB / ruta).mkdir(exist_ok=True)
    (WEB / ruta / "index.html").write_text("\n".join(h), encoding="utf-8")
    return ruta


def md_a_html(md: str) -> str:
    """Markdown sencillo de los pack.md (### títulos, listas, tablas, citas, ==resaltado==, **negrita**) a HTML."""
    def linea(t):
        t = e(t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        return re.sub(r"==(.+?)==", r'<mark>\1</mark>', t)
    out, lista, tabla = [], None, []

    def cerrar():
        nonlocal lista, tabla
        if lista:
            out.append(f"</{lista}>")
            lista = None
        if tabla:
            filas = [f for f in tabla if not re.match(r"^\|[\s\-|]+\|$", f)]
            celdas = [[c.strip() for c in f.strip("|").split("|")] for f in filas]
            out.append('<div class="tabla"><table><thead><tr>' + "".join(f"<th>{linea(c)}</th>" for c in celdas[0])
                       + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{linea(c)}</td>" for c in f) + "</tr>"
                                                          for f in celdas[1:]) + "</tbody></table></div>")
            tabla = []
    for l in md.splitlines():
        s = l.strip()
        if s.startswith("|"):
            if lista:
                out.append(f"</{lista}>")
                lista = None
            tabla.append(s)
            continue
        if tabla:
            cerrar()
        m_ul, m_ol = re.match(r"^\s*- (.*)", l), re.match(r"^\s*\d+\. (.*)", l)
        if m_ul or m_ol:
            tipo = "ul" if m_ul else "ol"
            if lista != tipo:
                cerrar()
                out.append(f"<{tipo}>")
                lista = tipo
            out.append(f"<li>{linea((m_ul or m_ol).group(1))}</li>")
            continue
        cerrar()
        if not s:
            continue
        if s.startswith("### "):
            out.append(f"<h3>{linea(s[4:].capitalize())}</h3>")
        elif s.startswith("> "):
            out.append(f'<p class="clave">{linea(s[2:])}</p>')
        else:
            out.append(f"<p>{linea(s)}</p>")
    cerrar()
    return "\n".join(out)


CSS_RESUMEN = """<style>
  .resumen h3 { margin: 28px 0 10px; font-size: 1.15rem; color: var(--azul-2); }
  .resumen ul, .resumen ol { padding-left: 22px; } .resumen li { margin: 4px 0; }
  .tabla { overflow-x: auto; margin: 12px 0; } table { border-collapse: collapse; width: 100%; font-size: .93rem; }
  th, td { border: 1px solid var(--borde); padding: 7px 10px; text-align: left; vertical-align: top; }
  th { background: var(--claro); }
  .clave { border-left: 4px solid var(--acento); background: var(--claro); padding: 10px 14px; border-radius: 0 8px 8px 0; font-weight: 600; }
  mark { background: #fff3b0; color: #1b2430; padding: 2px 4px; border-radius: 4px; }
</style>"""


def pagina_resumen(ley, todas):
    carpeta, slug, corto, tema, completo, precio, n_pack = ley
    md = (WEB.parent / carpeta / "pack.md").read_text(encoding="utf-8")
    vistazo = md.split("\n## 2.")[0].split("\n", 1)[1]           # sección 1: ficha, estructura, cambios
    vistazo = re.split(r"(?m)^### QUÉ PIDE EL TEMARIO", vistazo)[0] if "QUÉ PIDE" in vistazo else vistazo
    datos = re.split(r"(?m)^## \d+\. DATOS Y PLAZOS QUE MÁS CAEN\s*$", md)[1].split("\n## ")[0]
    ruta = f"resumen/{slug}/"
    titulo = f"Resumen {corto} ({tema}): esquema y datos clave para oposiciones | LeyClara"
    descripcion = (f"Resumen gratis de la {completo}: ficha, estructura, reformas recientes y tabla de datos y plazos "
                   f"que más caen en las oposiciones, con el artículo de cada dato.")
    h = [cabecera_html(titulo, descripcion, ruta, CSS_RESUMEN)]
    h.append(f"""<section class="cabecera"><div class="envoltorio">
  <h1>Resumen {e(de(corto))}: {e(tema)}</h1>
  <p class="intro">{e(completo)}. Lo esencial para la oposición: ficha, estructura, cambios recientes y los datos y plazos que más caen, con su artículo.</p>
  {aviso_em(slug, "../../")}
</div></section>
<main class="envoltorio resumen">""")
    h.append(md_a_html(vistazo))
    h.append(f"<h2>Datos y plazos que más caen</h2>\n{md_a_html(datos)}")
    h.append(f"""<section class="final" id="final">
  <h2>¿Te lo sabes? Compruébalo</h2>
  <p>Haz el <b>test online gratis {e(de(corto))}</b> (20 preguntas con la solución y el artículo) o consigue el <b>pack {e(de(corto))}</b>: la ley explicada, esquema, fichas y {n_pack} preguntas tipo test, en PDF y Word.</p>
  {vistas_previas(slug, "../../")}
  <a class="boton lleno" href="../../test/{slug}/">Hacer el test gratis</a>
  {f'<a class="boton" href="{TELEGRAM}">Pack {e(corto)}: muy pronto · Avísame por Telegram</a>' if slug in SIN_TIENDA else f'<a class="boton" href="{TIENDA}{slug}">Pack {e(corto)} · {"Gratis" if slug == GRATIS else precio + " €"}</a>'}
  <a class="boton" href="../../muestras/muestra-{slug}.pdf" download>Muestra en PDF</a>
</section>""")
    otros = "".join(f'<li><a href="../{l[1]}/">Resumen {e(l[2])} · {e(l[3])}</a></li>' for l in todas if l[1] != slug)
    h.append(f'<h2>Más resúmenes</h2>\n<ul class="otros">{otros}</ul>\n</main>')
    h.append(PIE + CONTADOR + "\n</body>\n</html>\n")
    destino = WEB / ruta
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "index.html").write_text("\n".join(h), encoding="utf-8")
    return ruta


def portada_resumenes(todas):
    ruta = "resumen/"
    titulo = "Resúmenes de legislación sanitaria para oposiciones: esquemas y datos clave | LeyClara"
    descripcion = ("Resúmenes gratis de las leyes del temario común de las OPE de sanidad: ficha, estructura, reformas "
                   "y tabla de datos y plazos que más caen, con el artículo exacto.")
    h = [cabecera_html(titulo, descripcion, ruta)]
    h.append("""<section class="cabecera"><div class="envoltorio">
  <h1>Resúmenes de legislación sanitaria</h1>
  <p class="intro">Lo esencial de cada ley del temario común de las OPE de los servicios de salud: ficha, estructura, cambios recientes y los datos y plazos que más caen. Gratis y sin registro.</p>
</div></section>
<main class="envoltorio"><div class="rejilla">""")
    for l in todas:
        h.append(f'<a class="tarjeta" href="{l[1]}/"><h2>Resumen {e(l[2])}</h2><p>{e(l[3][0].upper() + l[3][1:])}</p></a>')
    h.append("</div></main>")
    h.append(PIE + CONTADOR + "\n</body>\n</html>\n")
    (WEB / ruta).mkdir(exist_ok=True)
    (WEB / ruta / "index.html").write_text("\n".join(h), encoding="utf-8")
    return ruta


if __name__ == "__main__":
    rutas = (["", portada(TODAS)] + [pagina_ley(l, TODAS) for l in TODAS]
             + [pagina_ley(l, TODAS, t) for l in TODAS for t in temas_de(l)]
             + [portada_resumenes(TODAS)] + [pagina_resumen(l, TODAS) for l in TODAS] + ["actualizaciones/", "nuevo-estatuto-marco/"])
    def cambiada(r):
        """Fecha del último cambio de la página (hoy si se acaba de regenerar distinta), para el <lastmod>."""
        f = f"{r}index.html"
        git = lambda *a: subprocess.run(["git", *a], cwd=WEB, capture_output=True, text=True)
        if git("diff", "--quiet", "--", f).returncode:
            return date.today().isoformat()
        return git("log", "-1", "--format=%cs", "--", f).stdout.strip() or date.today().isoformat()
    mapa = "\n".join(f"  <url><loc>{URL}{r}</loc><lastmod>{cambiada(r)}</lastmod></url>" for r in rutas)
    (WEB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     f"{mapa}\n</urlset>\n", encoding="utf-8")
    (WEB / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {URL}sitemap.xml\n", encoding="utf-8")
    print(len(rutas), "páginas en el sitemap")
