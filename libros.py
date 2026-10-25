"""Página /libros/: los libros de LeyClara en Amazon (25/10/2026).

Cuando un formato pase a «En línea» en KDP, poner su ASIN en LIBROS y volver a generar:
    python libros.py   (desde la carpeta web/)
Los clics a Amazon se cuentan como amazon-<ASIN> y amazon-en-libros (CONTADOR de generar_tests.py).
"""
from generar_tests import CONTADOR, PIE, WEB, cabecera_html, e

AMAZON = "https://www.amazon.es/dp/"

# portada, título, qué incluye, [(formato, precio, ASIN o None si aún no está a la venta, nota)]
LIBROS = [
    ("estatuto-marco.jpg", "Estatuto Marco. Ley 55/2003",
     "Ley explicada, esquema, 95 test con solución y el artículo de cada respuesta, y 32 fichas de repaso.",
     [("Kindle", "5,99 €", "B0HNW172R9", "Gratis con Kindle Unlimited"),
      ("Tapa blanda", "9,99 €", None, "")]),
    ("ley-41-2002.jpg", "Autonomía del paciente. Ley 41/2002",
     "Información sanitaria, consentimiento informado, instrucciones previas e historia clínica. 62 test con solución y 30 fichas.",
     [("Kindle", "3,99 €", "B0HNWFX9DB", "Gratis con Kindle Unlimited"),
      ("Tapa blanda", "9,99 €", None, "")]),
    ("legislacion-sanitaria.jpg", "Legislación sanitaria para oposiciones: las 12 leyes",
     "Todo el temario común en un libro: 12 leyes explicadas, con esquemas, 1.006 test con solución y 296 fichas.",
     [("Kindle", "9,99 €", None, "")]),
    ("agenda-2027.jpg", "Agenda del opositor 2027",
     "Calendario, una página por semana, seguimiento de temas, test y simulacros, registro de errores y horas de estudio.",
     [("Tapa blanda", "", None, "")]),
]

CSS = ("<style>.libro{display:grid;grid-template-columns:150px 1fr;gap:20px;align-items:start;padding:22px 0;"
       "border-bottom:1px solid var(--borde)}.libro img{width:150px;height:auto;border-radius:6px;"
       "box-shadow:0 6px 18px rgba(0,0,0,.18)}.libro h2{margin:0 0 6px}.formatos{display:flex;flex-wrap:wrap;gap:10px;"
       "margin-top:12px}.formato{border:1px solid var(--borde);border-radius:10px;padding:10px 14px;min-width:150px}"
       ".formato b{display:block}.formato small{color:#666}.formato a{display:inline-block;margin-top:6px;font-weight:700}"
       ".pronto{color:#8a6d00;font-weight:600}@media(max-width:560px){.libro{grid-template-columns:96px 1fr;gap:14px}"
       ".libro img{width:96px}}</style>")


def formato_html(f: str, precio: str, asin: str | None, nota: str) -> str:
    cab = f"<b>{e(f)}{' · ' + e(precio) if precio else ''}</b>"
    if asin:
        return (f'<div class="formato">{cab}<small>{e(nota)}</small><br>'
                f'<a href="{AMAZON}{asin}" target="_blank" rel="noopener">Ver en Amazon →</a></div>')
    return f'<div class="formato">{cab}<span class="pronto">En revisión en Amazon: muy pronto</span></div>'


def main() -> None:
    ruta = "libros/"
    h = [cabecera_html("Libros de LeyClara en Amazon: Estatuto Marco, Ley 41/2002 y legislación sanitaria",
                       "Libros de LeyClara para oposiciones sanitarias en Amazon (Kindle y papel): Estatuto Marco, Ley 41/2002, "
                       "las 12 leyes del temario común con 1.006 test y la Agenda del opositor 2027.", ruta, CSS)]
    h.append("""<section class="cabecera"><div class="envoltorio">
  <h1>Los libros de LeyClara</h1>
  <p class="intro">Lo mismo que los packs, en Kindle y en papel: leyes explicadas, esquemas y test con el artículo de cada respuesta, hechos a partir del BOE. Si los tienes en Kindle Unlimited, no pagas nada más.</p>
</div></section>
<main class="envoltorio">""")
    for portada, titulo, desc, formatos in LIBROS:
        h.append(f'<article class="libro"><img src="{portada}" alt="Portada de {e(titulo)}" width="360" height="576" loading="lazy">'
                 f'<div><h2>{e(titulo)}</h2><p>{e(desc)}</p><div class="formatos">'
                 + "".join(formato_html(*f) for f in formatos) + "</div></div></article>")
    h.append("""  <p style="margin-top:22px">¿Prefieres PDF y Word para imprimir o subrayar? Están en los <a href="../#packs">packs</a>. Y para practicar gratis, los <a href="../test/">test online</a>.</p>
  <p>Si un libro te sirve, una reseña en Amazon nos ayuda muchísimo a llegar a más gente. 🙏</p>
</main>""")
    h.append(PIE + CONTADOR + "\n</body>\n</html>\n")
    (WEB / ruta).mkdir(exist_ok=True)
    (WEB / ruta / "index.html").write_text("\n".join(h), encoding="utf-8")
    print("OK", WEB / ruta / "index.html")


if __name__ == "__main__":
    main()
