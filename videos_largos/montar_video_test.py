"""Monta el vídeo largo horizontal (1920x1080) de un guion de test (guion_*.md de generar_guion_test.py):
intro, y por cada pregunta: enunciado y 4 opciones (la voz las lee), 6 s de cuenta atrás, respuesta con su artículo;
cierre con la web y Telegram. Escribe también la miniatura y la descripción con capítulos reales cada 10 preguntas.
No publica nada: subirlo necesita el OK de Sergio.

Uso (desde la raíz del repo): python videos_largos/montar_video_test.py videos_largos/guion_estatuto_marco_50.md
En el repo de la web lo lanza el workflow video_largo.yml al subir un guion nuevo.
"""
import asyncio
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
# en el repo de la web (leyclara) los Shorts están en ../shorts; en negocio, en ../web/shorts
sys.path.insert(0, str(AQUI.parent / "shorts" if (AQUI.parent / "shorts").exists() else AQUI.parent / "web" / "shorts"))
from generar_short_test import (ACENTO, AZUL, AZUL_OSCURO, BLANCO, GRIS, OK, WEB, caja_redondeada,  # noqa: E402
                                con_articulo, duracion, envolver, fuente, tts)

ANCHO, ALTO = 1920, 1080
PAUSA = 6  # segundos para pensar, como dice la intro
LEY = ("Ley 55/2003", "Estatuto Marco", "ley-55-2003")
TELEGRAM = "t.me/leyclara_avisos"


def leer_guion(ruta: Path):
    t = ruta.read_text(encoding="utf-8")
    intro = re.search(r"## Intro.*?\n«(.+?)»", t, re.S).group(1)
    cierre = re.search(r"## Cierre.*?\n«(.+?)»", t, re.S).group(1)
    preguntas = []
    for bloque in re.findall(r"(?ms)^### Pregunta \d+\n(.*?)(?=^### |^## )", t):
        lineas = [l.strip() for l in bloque.strip().splitlines() if l.strip()]
        enunciado = re.sub(r"^\d+\.\s*", "", lineas[0])
        opciones = [re.sub(r"^[a-d]\)\s*", "", l) for l in lineas[1:5]]
        letra, ref = re.match(r"\*\*Respuesta:\*\* ([a-d])\) ([^:]+):", lineas[5]).groups()
        preguntas.append({"enunciado": enunciado, "opciones": opciones, "correcta": "abcd".index(letra),
                          "articulo": ref.strip()})
    return intro, cierre, preguntas


def lienzo(k=None, total=None):
    im = Image.new("RGB", (ANCHO, ALTO), AZUL_OSCURO)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, ANCHO, 120), fill=AZUL)
    d.text((60, 60), "LeyClara · TEST DE OPOSICIONES", font=fuente(44), fill=ACENTO, anchor="lm")
    d.text((ANCHO - 60, 60), f"{LEY[0]} · {LEY[1]}", font=fuente(38, False), fill=BLANCO, anchor="rm")
    if k:
        d.rectangle((0, ALTO - 14, ANCHO * k // total, ALTO), fill=ACENTO)  # barra de progreso
    return im, d


def pantalla_pregunta(q, k, total, modo, cuenta=0):
    """modo: 'pregunta', 'cuenta' o 'respuesta'."""
    im, d = lienzo(k, total)
    d.text((80, 175), f"PREGUNTA {k} DE {total}", font=fuente(40), fill=ACENTO, anchor="lm")
    # el tamaño baja hasta que enunciado + opciones caben encima de la franja inferior
    for tam in range(58, 33, -2):
        f_p, f_o = fuente(tam), fuente(tam - 8, False)
        lp = envolver(d, q["enunciado"], f_p, ANCHO - 160)
        lo = [envolver(d, op, f_o, ANCHO - 330) for op in q["opciones"]]
        alto = len(lp) * (tam + 14) + 40 + sum(len(l) * (tam + 4) + 44 for l in lo) + 3 * 18
        if 230 + alto <= ALTO - 150:
            break
    y = 225
    for l in lp:
        d.text((80, y), l, font=f_p, fill=BLANCO)
        y += tam + 14
    y += 40
    for i, lin in enumerate(lo):
        h = len(lin) * (tam + 4) + 44
        fondo, borde, color = AZUL, None, BLANCO
        if modo == "respuesta":
            fondo, borde, color = (OK, ACENTO, BLANCO) if i == q["correcta"] else ("#1a3654", None, GRIS)
        caja_redondeada(d, (80, y, ANCHO - 80, y + h), fondo, radio=24, borde=borde)
        d.text((125, y + 20), "ABCD"[i], font=fuente(tam), fill=ACENTO if color == BLANCO else GRIS)
        yy = y + 22
        for l in lin:
            d.text((220, yy), l, font=f_o, fill=color)
            yy += tam + 4
        y += h + 18
    pie = ALTO - 85
    if modo == "cuenta":
        d.ellipse((ANCHO // 2 - 60, pie - 60, ANCHO // 2 + 60, pie + 60), fill=ACENTO)
        d.text((ANCHO // 2, pie), str(cuenta), font=fuente(84), fill=AZUL_OSCURO, anchor="mm")
    elif modo == "respuesta":
        d.text((ANCHO // 2, pie), f"Lo dice {con_articulo(q['articulo'])}", font=fuente(48), fill=ACENTO, anchor="mm")
    else:
        d.text((ANCHO // 2, pie), "¿Cuál es la correcta? Pausa si necesitas pensar", font=fuente(44), fill=ACENTO,
               anchor="mm")
    return im


def pantalla_texto(lineas):
    im, d = lienzo()
    y = (ALTO - sum(t + 30 for _, t, _ in lineas)) // 2 + 60
    for texto, tam, color in lineas:
        d.text((ANCHO // 2, y), texto, font=fuente(tam, tam >= 60), fill=color, anchor="mm")
        y += tam + 30
    return im


def a_wav(origen: Path, destino: Path, relleno=0.0):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(origen), "-af", f"apad=pad_dur={relleno}",
                    "-ar", "24000", "-ac", "1", str(destino)], check=True)


def main():
    guion = Path(sys.argv[1])
    intro, cierre, preguntas = leer_guion(guion)
    total = len(preguntas)
    salida = AQUI / "salida"
    salida.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="video_largo_"))
    tic = tmp / "tic.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"aevalsrc='0.3*sin(2*PI*880*t)*lt(mod(t,1),0.1)':s=24000:d={PAUSA}", "-ac", "1", str(tic)],
                   check=True)

    escenas, audios = [], []  # (png, duración) y wavs en el mismo orden

    def escena(nombre, imagen, texto=None, wav=None, relleno=0.6, dur=None):
        png = tmp / f"{nombre}.png"
        imagen.save(png)
        if texto is not None:
            mp3 = tmp / f"{nombre}.mp3"
            asyncio.run(tts(texto, mp3))
            wav = tmp / f"{nombre}.wav"
            a_wav(mp3, wav, relleno)
            dur = duracion(wav)
        escenas.append((png, dur))
        audios.append(wav)

    escena("intro", pantalla_texto([("Test del Estatuto Marco", 96, ACENTO), (f"{total} preguntas de examen", 68, BLANCO),
                                    ("Ley 55/2003 · con el artículo de cada respuesta", 44, GRIS),
                                    (f"Tienes {PAUSA} segundos para pensar cada una", 44, GRIS)]), intro, relleno=1.0)
    capitulos = []
    for k, q in enumerate(preguntas, 1):
        if k % 10 == 1:
            capitulos.append((sum(e[1] for e in escenas), f"Preguntas {k}-{min(k + 9, total)}"))
        print(f"Pregunta {k}/{total}", flush=True)
        escena(f"p{k}", pantalla_pregunta(q, k, total, "pregunta"),
               f"Pregunta {k}. {q['enunciado']} " + " ".join(f"{'ABCD'[i]}: {o}." for i, o in enumerate(q["opciones"])),
               relleno=0.3)
        for c in range(PAUSA, 0, -1):  # el tic de 6 s va entero con la primera pantalla de la cuenta
            escena(f"p{k}c{c}", pantalla_pregunta(q, k, total, "cuenta", c), wav=tic if c == PAUSA else None, dur=1.0)
        letra = "ABCD"[q["correcta"]]
        escena(f"p{k}r", pantalla_pregunta(q, k, total, "respuesta"),
               f"La correcta es la {letra}: {q['opciones'][q['correcta']]}. Lo dice {con_articulo(q['articulo'])}.",
               relleno=1.2)
    capitulos.append((sum(e[1] for e in escenas), "Resultado y test completo"))
    escena("cierre", pantalla_texto([("¿Cuántas has acertado?", 96, ACENTO), ("Cuéntalo en los comentarios", 60, BLANCO),
                                     ("", 20, BLANCO), ("Tests gratis con el artículo de cada respuesta:", 46, GRIS),
                                     (WEB, 60, ACENTO), ("Un test cada día por Telegram:", 46, GRIS),
                                     (TELEGRAM, 60, ACENTO)]), cierre, relleno=4.0)

    lista = [f"file '{p.as_posix()}'\nduration {d:.3f}" for p, d in escenas] + [f"file '{escenas[-1][0].as_posix()}'"]
    (tmp / "imagenes.txt").write_text("\n".join(lista), encoding="utf-8")
    (tmp / "audios.txt").write_text("\n".join(f"file '{a.as_posix()}'" for a in audios if a), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "audios.txt"),
                    str(tmp / "audio.wav")], check=True)
    video = salida / f"{guion.stem.replace('guion_', '')}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "imagenes.txt"),
                    "-i", str(tmp / "audio.wav"), "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", str(video)], check=True)

    mini = pantalla_texto([("TEST", 150, ACENTO), ("ESTATUTO MARCO", 120, BLANCO), (f"{total} preguntas de examen", 80, ACENTO),
                           ("Ley 55/2003 · con solución", 56, GRIS)])
    mini.resize((1280, 720)).save(salida / f"{video.stem}_miniatura.jpg", quality=90)
    mmss = lambda s: f"{int(s) // 60}:{int(s) % 60:02d}"  # noqa: E731
    descripcion = "\n".join([
        f"{total} preguntas tipo test de la Ley 55/2003, del Estatuto Marco del personal estatutario de los servicios de "
        "salud, para las OPE de sanidad (SAS, SERMAS, Sacyl, SERGAS, SESCAM, Osakidetza…): TCAE, celador, enfermería, "
        f"técnicos y administrativos. Tras cada pregunta tienes {PAUSA} segundos y luego la respuesta con su artículo.", "",
        "El proyecto de nuevo Estatuto Marco caducó al disolverse las Cortes (6/10/2026): la Ley 55/2003 sigue vigente.", "",
        f"Test gratis del Estatuto Marco por temas: https://{WEB}/test/{LEY[2]}/?g=yt",
        f"Un test cada día por Telegram: https://{TELEGRAM}", "",
        "Capítulos:", "0:00 Intro"] + [f"{mmss(s)} {t}" for s, t in capitulos] + [
        "", "#oposiciones #estatutomarco #opesanidad #tcae #celador #enfermeria"])
    (salida / f"{video.stem}_descripcion.txt").write_text(descripcion + "\n", encoding="utf-8")
    print(f"Vídeo: {video} ({mmss(duracion(video))})")
    print(descripcion)


if __name__ == "__main__":
    main()
