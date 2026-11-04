"""Página /glosario/: 15 términos jurídicos de oposiciones de Administración en dos líneas, cada uno con su artículo y
enlace al test y al pack de la ley (tarea de Lola, 4/11/2026). Cada definición está comprobada contra el texto
consolidado del BOE (negocio/fuentes/). Para añadir un término, agregar una fila a TERMINOS y volver a generar:
    python glosario.py   (desde la carpeta web/)
"""
from generar_tests import CONTADOR, PIE, TIENDA, cabecera_html, e, WEB

# término, ley, slug del test y del pack, artículo, definición (2 líneas)
TERMINOS = [
    ("Silencio administrativo", "Ley 39/2015", "ley-39-2015", "art. 24",
     "Si vence el plazo máximo sin resolución expresa, el interesado puede entender estimada su solicitud, salvo que una "
     "norma con rango de ley o de Derecho de la UE diga lo contrario. Es desestimatorio, entre otros, en el derecho de petición."),
    ("Interesado", "Ley 39/2015", "ley-39-2015", "art. 4",
     "Quien promueve el procedimiento como titular de derechos o intereses legítimos, quien tiene derechos que pueden verse "
     "afectados por la decisión y quien se persona antes de la resolución definitiva por tener intereses legítimos afectados."),
    ("Plazos en días hábiles", "Ley 39/2015", "ley-39-2015", "art. 30",
     "Salvo que una ley o el Derecho de la UE diga otra cosa, los plazos por días son hábiles: se excluyen sábados, "
     "domingos y festivos. Se cuentan desde el día siguiente a la notificación, publicación o efecto del silencio."),
    ("Nulidad de pleno derecho", "Ley 39/2015", "ley-39-2015", "art. 47",
     "Vicio más grave de un acto: lesionar derechos susceptibles de amparo constitucional, órgano manifiestamente "
     "incompetente por materia o territorio, contenido imposible, infracción penal o prescindir total y absolutamente del procedimiento."),
    ("Anulabilidad", "Ley 39/2015", "ley-39-2015", "art. 48",
     "Cualquier otra infracción del ordenamiento jurídico, incluida la desviación de poder, hace anulable el acto. "
     "El defecto de forma solo lo anula si falta un requisito indispensable o causa indefensión."),
    ("Caducidad del procedimiento", "Ley 39/2015", "ley-39-2015", "art. 95",
     "Si el interesado paraliza un procedimiento iniciado a su solicitud, la Administración le advierte y, pasados tres "
     "meses sin actuar, archiva las actuaciones. La caducidad no produce por sí sola la prescripción de las acciones."),
    ("Revisión de oficio", "Ley 39/2015", "ley-39-2015", "art. 106",
     "En cualquier momento, y con dictamen favorable del Consejo de Estado u órgano consultivo equivalente, la "
     "Administración declara la nulidad de actos firmes en vía administrativa que incurran en el art. 47.1."),
    ("Recurso de alzada", "Ley 39/2015", "ley-39-2015", "arts. 121 y 122",
     "Se interpone ante el órgano superior jerárquico contra actos que no ponen fin a la vía administrativa. "
     "Plazo de un mes si el acto es expreso; si no lo es, en cualquier momento desde que se produzcan los efectos del silencio."),
    ("Recurso de reposición", "Ley 39/2015", "ley-39-2015", "art. 124",
     "Recurso potestativo ante el mismo órgano que dictó el acto: un mes si es expreso, y un mes para resolverlo. "
     "Contra su resolución no cabe volver a interponer reposición."),
    ("Delegación de competencias", "Ley 40/2015", "ley-40-2015", "art. 9",
     "Un órgano puede delegar el ejercicio de sus competencias en otros órganos de la misma Administración o en organismos "
     "vinculados. No cambia la titularidad de la competencia, y hay materias que no se pueden delegar (art. 9.2)."),
    ("Avocación", "Ley 40/2015", "ley-40-2015", "art. 10",
     "El órgano superior toma para sí un asunto que correspondía a un órgano dependiente, por circunstancias técnicas, "
     "económicas, sociales, jurídicas o territoriales. Exige acuerdo motivado y contra él no cabe recurso."),
    ("Encomienda de gestión", "Ley 40/2015", "ley-40-2015", "art. 11",
     "Encargo de actividades materiales o técnicas a otro órgano o entidad de Derecho Público por razones de eficacia "
     "o falta de medios. No cede la titularidad de la competencia ni puede tener por objeto prestaciones propias de los contratos."),
    ("Funcionario de carrera", "TREBEP", "trebep", "art. 9",
     "Quien, por nombramiento legal, se vincula a una Administración con una relación estatutaria regulada por el "
     "Derecho Administrativo para servicios profesionales retribuidos de carácter permanente."),
    ("Funcionario interino", "TREBEP", "trebep", "art. 10",
     "Nombrado con carácter temporal, por necesidad y urgencia, para funciones de funcionario de carrera: plaza vacante "
     "(máx. 3 años), sustitución transitoria, programa temporal o exceso de tareas (9 meses en 18)."),
    ("Decreto-ley", "Constitución", "constitucion-espanola", "art. 86",
     "Disposición legislativa provisional del Gobierno en caso de extraordinaria y urgente necesidad, que no puede afectar a "
     "las instituciones básicas, a los derechos del Título I, a las CC. AA. ni al Derecho electoral. El Congreso la convalida en 30 días."),
]


def main() -> None:
    ruta = "glosario/"
    filas = []
    for termino, ley, slug, art, definicion in TERMINOS:
        filas.append(f"""<article class="termino">
  <h2>{e(termino)}</h2>
  <p class="art">{e(ley)}, {e(art)}</p>
  <p>{e(definicion)}</p>
  <p class="enlaces"><a class="boton" href="../test/{slug}/?g=glosario">Test de {e(ley)}</a>
  <a href="{TIENDA}{slug}?g=glosario" rel="noopener">Pack de {e(ley)}</a></p>
</article>""")
    h = [cabecera_html("Glosario de términos jurídicos para oposiciones de Administración | LeyClara",
                       "15 términos clave de la Ley 39/2015, la Ley 40/2015, el TREBEP y la Constitución explicados en dos "
                       "líneas, con su artículo y enlace al test de cada ley.", ruta,
                       "<style>.termino{border-bottom:1px solid var(--borde);padding:18px 0}.termino h2{margin:0 0 4px}"
                       ".art{color:var(--ok);font-weight:700;margin:0 0 8px}.enlaces{display:flex;gap:16px;"
                       "flex-wrap:wrap;align-items:center}</style>")]
    h.append(f"""<section class="cabecera"><div class="envoltorio">
  <h1>Glosario jurídico para opositores</h1>
  <p class="intro">Quince términos que se repiten en los exámenes de Administración, explicados en dos líneas. Cada definición está comprobada con el texto consolidado del BOE.</p>
</div></section>
<main class="envoltorio">
  {"".join(filas)}
  <p>Mira también las <a href="../novedades/">novedades legales</a> de las leyes de Administración.</p>
</main>
""")
    h.append(PIE + CONTADOR + "\n</body>\n</html>\n")
    (WEB / ruta).mkdir(exist_ok=True)
    (WEB / ruta / "index.html").write_text("\n".join(h), encoding="utf-8")
    print("glosario/ generada")


if __name__ == "__main__":
    main()
