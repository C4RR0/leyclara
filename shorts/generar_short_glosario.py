"""Short vertical (1080x1920) de ~20 s con 3 términos del glosario (texto en guion_glosario.md).

Uso: python generar_short_glosario.py [salida.mp4]
Reutiliza fuentes, colores y voz de generar_short_test.py. No publica nada.
"""
import asyncio
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

import generar_short_test as g

TERMINOS = [
    ("Silencio administrativo", "Artículo 24 · Ley 39/2015",
     "Si vence el plazo sin respuesta expresa, el interesado puede entender estimada su solicitud, "
     "salvo que una ley diga lo contrario."),
    ("Plazos en días hábiles", "Artículo 30 · Ley 39/2015",
     "Los plazos por días son hábiles: no cuentan sábados, domingos ni festivos, "
     "y empiezan al día siguiente de la notificación."),
    ("Avocación", "Artículo 10 · Ley 40/2015",
     "El órgano superior toma para sí un asunto de un órgano dependiente, "
     "con acuerdo motivado y sin recurso contra él."),
]
GANCHO = "3 términos de Administración que caen en oposiciones."
CIERRE = "Los 15 términos, en la web: LeyClara, Glosario."


def marco(titulo_barra: str) -> tuple:
    im = Image.new("RGB", (g.ANCHO, g.ALTO), g.AZUL_OSCURO)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, g.ANCHO, 210), fill=g.AZUL)
    d.text((g.ANCHO // 2, 80), "LeyClara · GLOSARIO", font=g.fuente(46), fill=g.ACENTO, anchor="mm")
    d.text((g.ANCHO // 2, 150), titulo_barra, font=g.fuente(38, False), fill=g.BLANCO, anchor="mm")
    return im, d


def texto_centrado(d, texto, y, tam, color, negrita=True, ancho=g.ANCHO - 140, paso=None):
    f = g.fuente(tam, negrita)
    for linea in g.envolver(d, texto, f, ancho):
        d.text((g.ANCHO // 2, y), linea, font=f, fill=color, anchor="mm")
        y += paso or int(tam * 1.3)
    return y


def f_gancho():
    im, d = marco("Oposiciones de Administración")
    texto_centrado(d, "3 términos que caen en oposiciones", 700, 78, g.ACENTO)
    texto_centrado(d, "y su artículo exacto", 960, 64, g.BLANCO)
    return im


def f_termino(i):
    nombre, art, defin = TERMINOS[i]
    im, d = marco(f"Término {i + 1} de 3")
    y = texto_centrado(d, nombre, 450, 84, g.ACENTO)
    d.text((g.ANCHO // 2, y + 20), art, font=g.fuente(46, False), fill=g.GRIS, anchor="mm")
    texto_centrado(d, defin, y + 160, 54, g.BLANCO, negrita=False, paso=76)
    return im


def f_cierre():
    im, d = marco("Los 15 términos")
    texto_centrado(d, "Los 15 términos", 640, 92, g.ACENTO)
    texto_centrado(d, "con su artículo, en la web:", 800, 54, g.BLANCO)
    texto_centrado(d, g.WEB + "/glosario/", 920, 50, g.ACENTO)
    texto_centrado(d, "(enlace en la descripción)", 1040, 44, g.GRIS, negrita=False)
    return im


def generar(salida: Path) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="short_glosario_"))
    textos = [GANCHO] + [f"{n}. {d}" for n, _, d in TERMINOS] + [CIERRE]
    escenas = [f_gancho()] + [f_termino(i) for i in range(3)] + [f_cierre()]
    lista = []
    audios = []
    for k, t in enumerate(textos):
        mp3 = tmp / f"a{k}.mp3"
        asyncio.run(g.tts(t, mp3))
        dur = g.duracion(mp3) + 0.35
        audios.append(mp3)
        png = tmp / f"f{k}.png"
        escenas[k].save(png)
        lista.append(f"file '{png.as_posix()}'\nduration {dur:.3f}")
    lista.append(f"file '{(tmp / f'f{len(textos) - 1}.png').as_posix()}'")
    (tmp / "lista.txt").write_text("\n".join(lista), encoding="utf-8")
    entradas = [x for a in audios for x in ("-i", str(a))]
    filtro = "".join(f"[{k}]apad=pad_dur=0.35[p{k}];" for k in range(len(audios))) \
        + "".join(f"[p{k}]" for k in range(len(audios))) + f"concat=n={len(audios)}:v=0:a=1[a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *entradas, "-filter_complex", filtro,
                    "-map", "[a]", "-ar", "44100", str(tmp / "audio.m4a")], check=True)
    salida.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "lista.txt"),
                    "-i", str(tmp / "audio.m4a"), "-vf", "fps=30,format=yuv420p", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-shortest",
                    str(salida)], check=True)
    return {"video": str(salida), "duracion": round(g.duracion(salida), 1), "fotogramas": str(tmp)}


if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "salidas" / "glosario.mp4"
    print(generar(out))
