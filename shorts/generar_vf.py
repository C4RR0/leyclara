"""Genera el Short semanal «¿Verdadero o falso?» (1080x1920) a partir de shorts/verdadero_falso.md.

Estructura: afirmación (la voz la lee) -> cuenta atrás 3-2-1 -> VERDADERO/FALSO con su artículo -> cierre.
Reutiliza fuentes, cuenta atrás y voz de generar_short_test.py.

Uso:
    python generar_vf.py <n_afirmacion> [salida.mp4]
    python generar_vf.py --lista        (enumera las afirmaciones del banco)
Imprime un JSON con titulo, descripcion (con la explicación para el comentario fijado) y ruta del vídeo.
"""
import asyncio
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

import generar_short_test as g

BANCO = Path(__file__).parent / "verdadero_falso.md"
# cabecera del banco -> (nombre corto, subtítulo, slug del test en la web)
LEYES = [("Ley 41/2002", "Autonomía del paciente", "ley-41-2002"),
         ("Ley 55/2003", "Estatuto Marco", "ley-55-2003"),
         ("Ley 14/1986", "General de Sanidad", "ley-14-1986"),
         ("Ley 31/1995", "Prevención de riesgos laborales", "ley-31-1995"),
         ("Ley 44/2003", "Ordenación de las profesiones sanitarias", "ley-44-2003"),
         ("Constitución", "Constitución Española de 1978", "constitucion-espanola"),
         ("TREBEP", "Estatuto Básico del Empleado Público", "trebep"),
         ("Ley 40/2015", "Régimen jurídico del sector público", "ley-40-2015")]


def leer_banco() -> dict:
    """{n: {afirmacion, verdad(bool), articulo, explicacion, ley:(nombre, sub, slug)}}"""
    ley, banco = LEYES[0], {}
    for linea in BANCO.read_text(encoding="utf-8").splitlines():
        if linea.startswith("## "):
            ley = next((l for l in LEYES if l[0].lower() in linea.lower()), ley)
            continue
        m = re.match(r"^(\d+)\. «(.+?)» · (VERDADERO|FALSO)[^·]*· ([^·]+?)(?: · (.*))?$", linea.strip())
        if m:
            n, afirm, vf, art, expl = m.groups()
            banco[int(n)] = {"afirmacion": afirm, "verdad": vf == "VERDADERO", "articulo": art.strip(),
                             "explicacion": (expl or "").strip(), "ley": ley}
    return banco


def fotograma(a: dict, modo: str, cuenta: int = 0) -> Image.Image:
    """modo: 'afirmacion', 'cuenta', 'respuesta' o 'cierre'."""
    if modo == "cierre":
        return g.fotograma({}, a["ley"][:2], "cierre")
    im = Image.new("RGB", (g.ANCHO, g.ALTO), g.AZUL_OSCURO)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, g.ANCHO, 210), fill=g.AZUL)
    d.text((g.ANCHO // 2, 80), "LeyClara · ¿VERDADERO O FALSO?", font=g.fuente(46), fill=g.ACENTO, anchor="mm")
    d.text((g.ANCHO // 2, 150), f"{a['ley'][0]} · {a['ley'][1]}", font=g.fuente(38, False), fill=g.BLANCO, anchor="mm")
    f = g.fuente(68)
    y = 380
    for l in g.envolver(d, "«" + a["afirmacion"] + "»", f, g.ANCHO - 140):
        d.text((70, y), l, font=f, fill=g.BLANCO)
        y += 88
    y += 90
    if modo == "cuenta":
        d.ellipse((g.ANCHO // 2 - 110, y, g.ANCHO // 2 + 110, y + 220), fill=g.ACENTO)
        d.text((g.ANCHO // 2, y + 110), str(cuenta), font=g.fuente(150), fill=g.AZUL_OSCURO, anchor="mm")
    elif modo == "respuesta":
        color = g.OK if a["verdad"] else "#b3261e"
        g.caja_redondeada(d, (120, y, g.ANCHO - 120, y + 170), color, borde=g.ACENTO)
        d.text((g.ANCHO // 2, y + 85), "VERDADERO" if a["verdad"] else "FALSO", font=g.fuente(96), fill=g.BLANCO, anchor="mm")
        rotulo = f"Lo dice {g.con_articulo(a['articulo'])}"
        tam = 54
        while tam > 34 and g.fuente(tam).getlength(rotulo) > g.ANCHO - 120:
            tam -= 2
        d.text((g.ANCHO // 2, y + 280), rotulo, font=g.fuente(tam), fill=g.ACENTO, anchor="mm")
    else:
        d.text((g.ANCHO // 2, y + 60), "¿Verdadero o falso?", font=g.fuente(60), fill=g.ACENTO, anchor="mm")
    return im


def generar(n: int, salida: Path) -> dict:
    a = leer_banco()[n]
    tmp = Path(tempfile.mkdtemp(prefix="short_vf_"))
    textos = {"preg": f"¿Verdadero o falso? {a['afirmacion']}",
              "resp": f"{'Verdadero' if a['verdad'] else 'Falso'}. Lo dice {g.con_articulo(a['articulo'])}.",
              "cierre": "¿Acertaste? Sígueme y cada semana tienes un verdadero o falso nuevo."}
    for nombre, texto in textos.items():
        asyncio.run(g.tts(texto, tmp / f"{nombre}.mp3"))
    d_preg, d_resp, d_cierre = (g.duracion(tmp / f"{x}.mp3") for x in ("preg", "resp", "cierre"))
    escenas = [("afirmacion", 0, d_preg + 0.3)] + [("cuenta", c, 1.0) for c in (3, 2, 1)] \
        + [("respuesta", 0, d_resp + 0.8), ("cierre", 0, d_cierre + 0.8)]
    lista = []
    for i, (modo, c, dur) in enumerate(escenas):
        ruta = tmp / f"f{i}.png"
        fotograma(a, modo, c).save(ruta)
        lista.append(f"file '{ruta.as_posix()}'\nduration {dur:.3f}")
    lista.append(f"file '{(tmp / f'f{len(escenas) - 1}.png').as_posix()}'")
    (tmp / "lista.txt").write_text("\n".join(lista), encoding="utf-8")
    filtro = ("[0]apad=pad_dur=0.3[a0];[1]anull[a1];[2]apad=pad_dur=0.8[a2];[3]apad=pad_dur=0.8[a3];"
              "[a0][a1][a2][a3]concat=n=4:v=0:a=1[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-i", str(tmp / "preg.mp3"), "-f", "lavfi", "-i",
                    "aevalsrc='0.35*sin(2*PI*880*t)*lt(mod(t,1),0.12)':s=24000:d=3",
                    "-i", str(tmp / "resp.mp3"), "-i", str(tmp / "cierre.mp3"),
                    "-filter_complex", filtro, "-map", "[a]", "-ar", "44100", str(tmp / "audio.m4a")], check=True)
    salida.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"),
                    "-i", str(tmp / "audio.m4a"), "-vf", "fps=30,format=yuv420p", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    str(salida)], check=True)
    corto = a["afirmacion"] if len(a["afirmacion"]) <= 70 else a["afirmacion"][:67].rsplit(" ", 1)[0] + "…"
    titulo = f"¿Verdadero o falso? {corto} #oposiciones"[:100]
    expl = f" {a['explicacion']}" if a["explicacion"] else ""
    descripcion = (f"Afirmación de {a['ley'][0]} ({a['ley'][1]}), comprobada contra el texto del BOE.\n\n"
                   f"Respuesta: {'VERDADERO' if a['verdad'] else 'FALSO'} ({a['articulo']}).{expl}\n\n"
                   f"Haz el test completo gratis, con el artículo de cada respuesta: https://{g.WEB}/test/{a['ley'][2]}/?g=yt\n\n"
                   "Avisos gratis por Telegram cuando cambie una ley de tu temario: https://t.me/leyclara_avisos\n\n"
                   "#oposiciones #opesanidad #legislacionsanitaria")
    return {"titulo": titulo, "descripcion": descripcion, "video": str(salida),
            "duracion": round(sum(e[2] for e in escenas), 1)}


if __name__ == "__main__":
    if sys.argv[1] == "--lista":
        for k, v in leer_banco().items():
            print(k, "V" if v["verdad"] else "F", v["ley"][0], v["afirmacion"][:70])
        sys.exit()
    n = int(sys.argv[1])
    salida = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent / "salidas" / f"vf_{n}.mp4"
    print(json.dumps(generar(n, salida), ensure_ascii=False, indent=1))
