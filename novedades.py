"""Página /novedades/: reformas recientes de las leyes de Administración, resumidas en pocas líneas y con enlace
al test y al pack de cada ley (28/10/2026). Cada dato está comprobado contra el texto consolidado del BOE.

Cuando el BOE modifique otra ley de los packs, añadir su fila a NOVEDADES y volver a generar:
    python novedades.py   (desde la carpeta web/)
"""
from generar_tests import CONTADOR, PIE, TIENDA, WEB, cabecera_html, e

# slug, ley, artículo, fecha, qué cambia (3 líneas como máximo), qué sigue igual
NOVEDADES = [
    ("constitucion-espanola", "Constitución Española", "Art. 69.3 (Senado)", "20/05/2026",
     "Formentera pasa a elegir un senador propio: ya no forma una circunscripción conjunta con Ibiza. El art. 69.3 "
     "da ahora tres senadores a cada isla mayor (Gran Canaria, Mallorca y Tenerife) y uno a cada una de estas: Ibiza, "
     "Formentera, Menorca, Fuerteventura, La Gomera, El Hierro, Lanzarote y La Palma.",
     "Cuatro senadores por provincia (art. 69.2) y dos por Ceuta y Melilla (art. 69.4)."),
    ("trebep", "TREBEP (RDL 5/2015)", "Art. 49.e (hijo con cáncer o enfermedad grave)", "23/10/2026",
     "Si la persona a cargo tiene gran discapacidad o gran dependencia y necesita cuidados directos, continuos y "
     "permanentes, la reducción de jornada puede prorrogarse más allá de los límites de edad mientras persista la "
     "necesidad y la convivencia. Ambos progenitores pueden compartir la reducción hasta el máximo del 100 %.",
     "La regla base: reducción de al menos la mitad de la jornada, con retribuciones íntegras, hasta los 23 años "
     "(26 con discapacidad igual o superior al 65 %)."),
    ("ley-39-2015", "Ley 39/2015, Procedimiento Administrativo Común", "Sin reformas en 2026", "",
     "En el texto consolidado del BOE no figura ninguna modificación de 2026: el pack sigue vigente.", ""),
    ("ley-40-2015", "Ley 40/2015, Régimen Jurídico del Sector Público", "Sin reformas en 2026", "",
     "En el texto consolidado del BOE no figura ninguna modificación de 2026: el pack sigue vigente.", ""),
]


def main() -> None:
    ruta = "novedades/"
    tarjetas = []
    for slug, ley, art, fecha, cambia, igual in NOVEDADES:
        vigor = f" · en vigor desde el {fecha}" if fecha else ""
        sigue = f"<p><b>Qué sigue igual:</b> {e(igual)}</p>" if igual else ""
        tarjetas.append(f"""<article class="novedad">
  <h2>{e(ley)}</h2>
  <p class="art">{e(art)}{vigor}</p>
  <p>{e(cambia)}</p>
  {sigue}
  <p class="enlaces"><a class="boton" href="../test/{slug}/?g=novedades">Hacer el test de esta ley</a>
  <a href="{TIENDA}{slug}?g=novedades" rel="noopener">Pack con la ley actualizada</a></p>
</article>""")
    h = [cabecera_html("Novedades legales: qué ha cambiado en las leyes de Administración | LeyClara",
                       "Reformas recientes de la Constitución y el TREBEP que pueden caer en tu oposición, resumidas y "
                       "comprobadas con el BOE, con enlace al test de cada ley.", ruta,
                       "<style>.novedad{border-bottom:1px solid var(--borde);padding:18px 0}.novedad h2{margin:0 0 4px}"
                       ".art{color:var(--ok);font-weight:700;margin:0 0 8px}.enlaces{display:flex;gap:16px;"
                       "flex-wrap:wrap;align-items:center}</style>")]
    h.append(f"""<section class="cabecera"><div class="envoltorio">
  <h1>Novedades legales</h1>
  <p class="intro">Lo que ha cambiado en las leyes de Administración y puede caer en el examen. Cada reforma está comprobada con el texto consolidado del BOE.</p>
</div></section>
<main class="envoltorio">
  {"".join(tarjetas)}
  <p>¿Quieres la hoja de una página? <a href="../descargas/que-cambio-2026-administracion.pdf">Descargar «Qué cambió en 2026»</a> (gratis). Comprobamos el BOE cada semana: mira <a href="../actualizaciones/">actualizaciones y erratas</a>.</p>
</main>
""")
    h.append(PIE + CONTADOR + "\n</body>\n</html>\n")
    (WEB / ruta).mkdir(exist_ok=True)
    (WEB / ruta / "index.html").write_text("\n".join(h), encoding="utf-8")
    print("novedades/ generada")


if __name__ == "__main__":
    main()
