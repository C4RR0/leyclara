"""Página /actualizaciones/: comprueba contra la API de datos abiertos del BOE si alguna ley de los packs
ha cambiado desde la versión consolidada en la que se basa su pack, y publica el resultado (17/10/2026).

Sale con código 1 si alguna ley ha cambiado (el workflow se pone en rojo y GitHub avisa por correo):
entonces hay que regenerar ese pack, subirlo a Gumroad y actualizar su fecha en LEYES_BOE.

Uso: python actualizaciones.py   (desde la carpeta web/)
"""
import datetime as dt
import json
import sys
import urllib.request

from generar_tests import CONTADOR, PIE, WEB, cabecera_html, e

# slug, nombre, ids del BOE, fecha de la versión consolidada en la que se basa el pack (NegocioOposiciones/packs.json)
LEYES_BOE = [
    ("ley-14-1986", "Ley 14/1986, General de Sanidad", ["BOE-A-1986-10499"], "26/06/2026"),
    ("ley-16-2003", "Ley 16/2003, de cohesión y calidad del SNS", ["BOE-A-2003-10715"], "05/10/2026"),
    ("ley-31-1995", "Ley 31/1995, de Prevención de Riesgos Laborales", ["BOE-A-1995-24292"], "22/06/2026"),
    ("ley-41-2002", "Ley 41/2002, de autonomía del paciente", ["BOE-A-2002-22188"], "18/12/2025"),
    ("ley-44-2003", "Ley 44/2003, de ordenación de las profesiones sanitarias", ["BOE-A-2003-21340"], "24/09/2026"),
    ("ley-55-2003", "Ley 55/2003, del Estatuto Marco", ["BOE-A-2003-23101"], "18/12/2025"),
    ("lo-3-2007", "Ley Orgánica 3/2007, de igualdad", ["BOE-A-2007-6115"], "19/12/2025"),
    ("lo-3-2018", "Ley Orgánica 3/2018, de protección de datos", ["BOE-A-2018-16673"], "08/10/2026"),
    ("ley-53-1984", "Ley 53/1984, de incompatibilidades", ["BOE-A-1985-151"], "16/12/2025"),
    ("ley-2-1998-andalucia", "Ley 2/1998, de Salud de Andalucía", ["BOE-A-1998-18720"], "18/12/2025"),
    ("leyes-12-13-2007-andalucia", "Leyes 12/2007 y 13/2007 de Andalucía", ["BOE-A-2008-2492", "BOE-A-2008-2493"], "16/01/2026"),
]

QUIEN = """<h2>Quién hace LeyClara</h2>
<p>LeyClara es un proyecto independiente: no hay academia ni editorial detrás. Cada pack se elabora a partir del
texto consolidado del BOE, artículo por artículo, y cada pregunta indica el artículo en el que se basa para que
puedas comprobarla tú mismo en el texto oficial. Las leyes autonómicas se señalan como tales, para que sepas si
entran en tu oposición.</p>
<p>Si encuentras un error, lo corregimos, y quien ya compró el pack recibe la versión nueva gratis en su
biblioteca de Gumroad. Para avisarnos, responde al correo de tu compra.</p>"""


def fecha_boe(idb: str) -> dt.date:
    req = urllib.request.Request(f"https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/{idb}/metadatos",
                                 headers={"Accept": "application/json", "User-Agent": "LeyClara/1.0"})
    f = json.load(urllib.request.urlopen(req, timeout=60))["data"][0]["fecha_actualizacion"][:8]
    return dt.date(int(f[:4]), int(f[4:6]), int(f[6:8]))


def main() -> int:
    hoy = dt.date.today()
    filas, cambiadas = [], []
    for slug, nombre, ids, fecha_pack in LEYES_BOE:
        pack = dt.datetime.strptime(fecha_pack, "%d/%m/%Y").date()
        boe = max(fecha_boe(i) for i in ids)
        al_dia = boe <= pack
        if not al_dia:
            cambiadas.append(nombre)
        estado = ("✔ Al día" if al_dia else
                  f"⚠ El BOE publicó un cambio el {boe:%d/%m/%Y}: estamos actualizando el pack")
        enlaces = " · ".join(f'<a href="https://www.boe.es/buscar/act.php?id={i}" rel="noopener">{i}</a>' for i in ids)
        filas.append(f'<tr><td><a href="../test/{slug}/">{e(nombre)}</a></td><td>{fecha_pack}</td>'
                     f'<td class="{"ok" if al_dia else "aviso"}">{estado}</td><td>{enlaces}</td></tr>')
    resumen = (f"✔ Las {len(LEYES_BOE)} leyes de los packs están al día con el BOE." if not cambiadas else
               f"⚠ {len(cambiadas)} ley(es) con cambios recientes en el BOE: " + ", ".join(cambiadas) + ".")
    ruta = "actualizaciones/"
    h = [cabecera_html("Actualizaciones de los packs y erratas | LeyClara",
                       "Comprobación semanal automática contra el BOE de las leyes de los packs de LeyClara: versión en la "
                       "que se basa cada pack, cambios publicados y erratas corregidas.", ruta,
                       "<style>table{width:100%;border-collapse:collapse;font-size:.93rem;margin:12px 0 24px}"
                       "th,td{border-bottom:1px solid var(--borde);padding:9px 8px;text-align:left;vertical-align:top}"
                       ".tabla{overflow-x:auto}td.ok{color:var(--ok);font-weight:700}td.aviso{color:var(--mal);font-weight:700}"
                       ".resumen-boe{font-weight:700;font-size:1.05rem;background:var(--claro);border-left:4px solid var(--ok);"
                       "padding:12px 14px;border-radius:8px}</style>")]
    h.append(f"""<section class="cabecera"><div class="envoltorio">
  <h1>Actualizaciones y erratas</h1>
  <p class="intro">Las leyes cambian, y un temario desactualizado cuesta puntos. Cada semana comprobamos de forma automática, con la API oficial de datos abiertos del BOE, si se ha publicado alguna modificación de las leyes de nuestros packs.</p>
</div></section>
<main class="envoltorio">
  <p class="resumen-boe">{e(resumen)}<br><small>Última comprobación: {hoy:%d/%m/%Y}.</small></p>
  <div class="tabla"><table>
    <thead><tr><th>Ley</th><th>Versión del BOE del pack</th><th>Estado</th><th>Texto oficial</th></tr></thead>
    <tbody>{"".join(filas)}</tbody>
  </table></div>
  <h2>Si una ley cambia</h2>
  <p>Revisamos la reforma, actualizamos el pack (ley explicada, esquema, test y fichas) y lo subimos de nuevo. Quien ya lo compró lo encuentra actualizado en su biblioteca de Gumroad, sin pagar nada más.</p>
  <h2>Erratas</h2>
  <p>Erratas comunicadas hasta ahora: ninguna. Si encuentras una, responde al correo de tu compra y la corregimos; la anotaremos aquí.</p>
  {QUIEN}
</main>
""")
    h.append(PIE + CONTADOR + "\n</body>\n</html>\n")
    (WEB / ruta).mkdir(exist_ok=True)
    (WEB / ruta / "index.html").write_text("\n".join(h), encoding="utf-8")
    print(resumen)
    return 1 if cambiadas else 0


if __name__ == "__main__":
    sys.exit(main())
