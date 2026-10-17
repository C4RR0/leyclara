"""Página /nuevo-estatuto-marco/: qué cambia el Proyecto de Ley del nuevo Estatuto Marco (BOCG 121/000112,
18/09/2026) respecto a la Ley 55/2003 vigente y si entra en el examen (18/10/2026).

Cada fila de CAMBIOS está comprobada contra el texto del proyecto (BOCG-15-A-113-1) y contra la Ley 55/2003
consolidada (NegocioOposiciones/fuentes/ley55_2003_vigente.txt). Si el proyecto cambia en el Congreso o en el
Senado, o se publica en el BOE, hay que revisar esta tabla, ESTADO y la fecha de revisión.

Uso: python estatuto_marco.py   (desde la carpeta web/)
"""
from generar_tests import CONTADOR, PIE, TIENDA, WEB, cabecera_html, e

REVISADO = "18/10/2026"
BOCG = "https://www.congreso.es/public_oficiales/L15/CONG/BOCG/A/BOCG-15-A-113-1.PDF"
BOE_55 = "https://www.boe.es/buscar/act.php?id=BOE-A-2003-23101"

ESTADO = ("Es un <strong>proyecto de ley</strong>: el Gobierno lo aprobó el 1 de septiembre de 2026 y lo envió al "
          "Congreso, que lo publicó el 18 de septiembre (expediente 121/000112). Se tramita en la Comisión de Sanidad "
          "con competencia legislativa plena y después tiene que pasar por el Senado. El plazo de enmiendas fijado "
          "inicialmente terminaba el 6 de octubre. Hasta que se publique en el BOE, <strong>la ley vigente sigue siendo "
          "la Ley 55/2003</strong>, y entrará en vigor a los 20 días de esa publicación (disposición final séptima).")

# tema, Ley 55/2003 vigente, proyecto (artículo del proyecto)
CAMBIOS = [
    ("Edad mínima para presentarse",
     "Tener cumplidos 18 años (art. 30.5.d).",
     "Tener cumplidos 16 años (art. 45.5.e)."),
    ("Jubilación forzosa",
     "A los 65 años (art. 26.2), con posible prolongación voluntaria hasta los 70.",
     "A la edad ordinaria de jubilación de la Seguridad Social, con posible prolongación voluntaria hasta los 70 "
     "(art. 42.2)."),
    ("Reserva para personas con discapacidad",
     "Cupo no inferior al 5 % o al porcentaje vigente para la función pública (art. 30.6).",
     "Al menos el porcentaje vigente con carácter general para la función pública, del que al menos un 2 % de las "
     "plazas es para discapacidad intelectual (art. 45.7)."),
    ("Periodicidad de las convocatorias",
     "Programación periódica, sin plazo fijo.",
     "Al menos cada dos años y resolución en 18 meses como máximo; o cada tres años y resolución en 2 años si se "
     "añaden plazas adicionales (art. 45.1)."),
    ("Grupos de clasificación",
     "Personal de formación universitaria, de formación profesional y otro personal (arts. 6 y 7).",
     "Grupos del 2 al 8 según el nivel del título en el Marco Español de Cualificaciones, MECU (arts. 6 y 7). Por "
     "ejemplo, el personal técnico de FP de grado medio (como TCAE) pasa al Grupo 4 (disposición transitoria cuarta)."),
    ("Tiempo máximo de trabajo semanal",
     "48 horas semanales de promedio en cómputo semestral (art. 48.2).",
     "45 horas semanales de promedio en cómputo cuatrimestral, sumando jornada ordinaria, guardias y otras "
     "modalidades (art. 84)."),
    ("Pausa en la jornada",
     "Al menos 15 minutos si la jornada pasa de 6 horas continuadas (art. 50).",
     "Al menos 20 minutos si pasa de 6 horas, y se considera trabajo efectivo (arts. 86 y 90)."),
    ("Prescripción de las faltas",
     "Muy graves, 4 años; graves, 2 años; leves, 6 meses (art. 72.6).",
     "Muy graves, 3 años; graves, 2 años; leves, 6 meses (art. 105.3)."),
    ("Prescripción de las sanciones",
     "Muy graves, 4 años; graves, 2 años; leves, 6 meses (art. 73.4).",
     "Muy graves, 3 años; graves, 2 años; leves, 1 año (art. 109.8)."),
    ("Sanciones por faltas leves",
     "Solo apercibimiento por escrito (art. 73.1.e).",
     "Apercibimiento por escrito o suspensión de funciones y retribuciones de 1 a 15 días (art. 109.3)."),
    ("Personal temporal",
     "Interino (vacante hasta 3 años, programas hasta 3 años, exceso de tareas 9 meses en 18) y sustituto "
     "(arts. 9 y 9 bis).",
     "Se mantienen los mismos supuestos y plazos, ahora en los arts. 9 (interino) y 10 (sustituto)."),
    ("Período de prueba del personal temporal",
     "Hasta 3 meses (formación universitaria) o 2 meses (resto) (art. 33.3).",
     "Igual: hasta 3 meses en los grupos 8, 7 y 6 y 2 meses en el resto (art. 48.3)."),
]

OTRAS_LEYES = ("El proyecto también modifica otras leyes del temario: la <a href=\"../test/ley-16-2003/\">Ley 16/2003</a> "
               "(composición de la Comisión de Recursos Humanos del SNS, disposición final segunda) y la "
               "<a href=\"../test/ley-44-2003/\">Ley 44/2003</a> (las profesiones sanitarias pasan a agruparse según el "
               "MECU, disposición final tercera). Y deroga expresamente la Ley 55/2003 (disposición derogatoria única).")


def main() -> None:
    ruta = "nuevo-estatuto-marco/"
    filas = "".join(f"<tr><th scope=\"row\">{e(t)}</th><td>{e(a)}</td><td>{e(n)}</td></tr>" for t, a, n in CAMBIOS)
    h = [cabecera_html("Nuevo Estatuto Marco 2026: qué cambia respecto a la Ley 55/2003 | LeyClara",
                       "Qué cambia el proyecto del nuevo Estatuto Marco frente a la Ley 55/2003 (edad mínima de 16 años, "
                       "jubilación, 45 horas, discapacidad, faltas y sanciones) y si entra en tu examen de la OPE.", ruta,
                       "<style>table{width:100%;border-collapse:collapse;font-size:.93rem;margin:12px 0 24px}"
                       "th,td{border-bottom:1px solid var(--borde);padding:9px 8px;text-align:left;vertical-align:top}"
                       "td,th{hyphens:auto;overflow-wrap:break-word}thead th{background:var(--claro)}tbody th{font-weight:700;min-width:120px}.tabla{overflow-x:auto}"
                       ".clave{background:var(--claro);border-left:4px solid var(--azul-2);padding:12px 14px;border-radius:8px}"
                       ".compromiso{border:1px dashed var(--azul-2);border-radius:12px;padding:14px 16px;margin:18px 0}"
                       ".compromiso a{font-weight:700}</style>")]
    h.append(f"""<section class="cabecera"><div class="envoltorio">
  <h1>Nuevo Estatuto Marco: qué cambia respecto a la Ley 55/2003</h1>
  <p class="intro">Resumen del proyecto de ley que sustituirá al Estatuto Marco, comparado punto por punto con la ley que está en vigor. Revisado el {REVISADO} con el texto publicado por el Congreso.</p>
</div></section>
<main class="envoltorio">
  <h2>¿En qué punto está?</h2>
  <p>{ESTADO}</p>
  <h2>¿Entra en mi examen?</h2>
  <p class="clave">Mientras no se publique en el BOE, no: se estudia la <a href="{BOE_55}" rel="noopener">Ley 55/2003</a>. Las bases de cada convocatoria suelen fijar que se exige la normativa vigente en una fecha concreta (a menudo, la de publicación de la convocatoria), así que revisa las tuyas. Si tu examen es dentro de muchos meses, conviene conocer estos cambios, porque es probable que acaben preguntándose.</p>
  <h2>Los cambios que más pueden caer</h2>
  <div class="tabla"><table>
    <thead><tr><th>Tema</th><th>Ley 55/2003 (vigente)</th><th>Proyecto de nuevo Estatuto Marco</th></tr></thead>
    <tbody>{filas}</tbody>
  </table></div>
  <p>{OTRAS_LEYES}</p>
  <p><small>Fuentes: <a href="{BOCG}" rel="noopener">Proyecto de Ley 121/000112, BOCG Congreso, serie A, núm. 113-1, de 18/09/2026</a> y <a href="{BOE_55}" rel="noopener">Ley 55/2003 consolidada (BOE)</a>. El texto puede cambiar durante la tramitación por las enmiendas: actualizaremos esta página cuando ocurra.</small></p>
  <div class="compromiso" id="final">
    <h2>Si estudias con LeyClara, no pierdes nada</h2>
    <p>El <a href="{TIENDA}ley-55-2003" target="_blank" rel="noopener">pack de la Ley 55/2003</a> está hecho con la versión vigente del BOE. Si el nuevo Estatuto Marco se publica en el BOE, rehacemos el pack con la ley nueva (ley explicada, esquemas, test y fichas) y quien lo haya comprado lo recibe actualizado en su biblioteca de Gumroad sin pagar nada más. Lo mismo con el <a href="{TIENDA}pack-completo" target="_blank" rel="noopener">pack de las 12 leyes</a>.</p>
    <p>Mientras tanto, practica con el <a href="../test/ley-55-2003/">test gratis de la Ley 55/2003</a> (20 preguntas con el artículo de cada respuesta).</p>
  </div>
</main>
""")
    h.append(PIE + CONTADOR + "\n</body>\n</html>\n")
    (WEB / ruta).mkdir(exist_ok=True)
    (WEB / ruta / "index.html").write_text("\n".join(h), encoding="utf-8")
    print("OK", WEB / ruta / "index.html")


if __name__ == "__main__":
    main()
