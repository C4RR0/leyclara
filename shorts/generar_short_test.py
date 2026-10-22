"""Genera un Short vertical (1080x1920) de «pregunta tipo test» a partir de las muestras gratis.

Estructura: pregunta + 4 opciones (voz las lee) -> cuenta atrás 3-2-1 -> respuesta correcta
resaltada con su artículo -> cierre con llamada a la acción.

Uso:
    python generar_short_test.py <carpeta_pack> <n_pregunta_muestra> [salida.mp4]
    p. ej.: python generar_short_test.py ../ley41 7
Imprime un JSON con titulo, descripcion y ruta del vídeo.
"""
import asyncio
import json
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

import edge_tts
from edge_tts import communicate as _edge_communicate
from edge_tts.constants import TRUSTED_CLIENT_TOKEN
from PIL import Image, ImageDraw, ImageFont

# Desde el 10/10/2026 Microsoft movió la síntesis a api.msedgeservices.com y edge-tts 7.2.8
# sigue con la URL vieja (403). Mismo apaño que en CanalIA-CienciaEspacio/scripts/generar_audio.py.
_edge_communicate.WSS_URL = ("wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1"
                             f"?Ocp-Apim-Subscription-Key={TRUSTED_CLIENT_TOKEN}")

ANCHO, ALTO = 1080, 1920
AZUL, AZUL_OSCURO, ACENTO, OK = "#1f4e79", "#0f2a44", "#ffd400", "#1e7d4f"
BLANCO, GRIS = "#ffffff", "#9fb3c8"
VOZ = "es-ES-AlvaroNeural"
WEB = "c4rr0.github.io/leyclara"
SLUGS = {"ley14": "ley-14-1986", "ley16": "ley-16-2003", "ley31": "ley-31-1995", "ley41": "ley-41-2002",
         "ley44": "ley-44-2003", "ley55": "ley-55-2003", "lo3_2007": "lo-3-2007", "lo3_2018": "lo-3-2018",
         "ley2_1998_and": "ley-2-1998-andalucia", "and_igualdad": "leyes-12-13-2007-andalucia",
         "ley53": "ley-53-1984"}

NOMBRES = {
    "ley14": ("Ley 14/1986", "General de Sanidad"),
    "ley16": ("Ley 16/2003", "Cohesión y calidad del SNS"),
    "ley31": ("Ley 31/1995", "Prevención de riesgos laborales"),
    "ley41": ("Ley 41/2002", "Autonomía del paciente"),
    "ley44": ("Ley 44/2003", "Ordenación de las profesiones sanitarias"),
    "ley55": ("Ley 55/2003", "Estatuto Marco"),
    "lo3_2007": ("LO 3/2007", "Igualdad efectiva de mujeres y hombres"),
    "lo3_2018": ("LO 3/2018", "Protección de datos"),
    "ley2_1998_and": ("Ley 2/1998", "Salud de Andalucía"),
    "and_igualdad": ("Leyes 12 y 13/2007", "Igualdad y violencia de género"),
    "ley53": ("Ley 53/1984", "Incompatibilidades"),
}

AMBITO = {"ley2_1998_and": "la OPE del Servicio Andaluz de Salud (SAS)",
          "and_igualdad": "la OPE del Servicio Andaluz de Salud (SAS)"}
ETIQUETAS = {"ley2_1998_and": " #sas #opesas", "and_igualdad": " #sas #opesas"}

def con_articulo(ref: str) -> str:
    """«el art. 5», «la DF 2.ª», «la Ley 12/2007…», «los arts. 3 y 4»."""
    primera = ref.split()[0] if ref else ""
    if primera in ("Arts.", "arts."):
        art = "los"
    elif primera in ("Leyes",):
        art = "las"
    elif primera in ("DA", "DF", "DT", "DD", "Disposición", "Exposición", "LO", "Ley"):
        art = "la"
    else:
        art = "el"
    return f"{art} {ref}"


FUENTES_NEGRITA = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FUENTES_NORMAL = ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def fuente(tam: int, negrita: bool = True) -> ImageFont.FreeTypeFont:
    for f in (FUENTES_NEGRITA if negrita else FUENTES_NORMAL):
        if Path(f).exists():
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default(tam)


def leer_pregunta(carpeta: Path, n: int) -> dict:
    est = (carpeta / "muestra" / "estudio.md").read_text(encoding="utf-8")
    test = est.split("## Preguntas tipo test")[1]
    preg_txt, sol_txt = test.split("### Soluciones")
    bloque = re.search(rf"(?ms)^{n}\. (.*?)(?=^\d+\. |\Z)", preg_txt).group(1).strip().splitlines()
    enunciado = bloque[0].strip()
    opciones = [re.sub(r"^[a-d]\)\s*", "", x).strip() for x in bloque[1:5]]
    sol = re.search(rf"(?m)^{n}\. ([a-d])\) (.*)$", sol_txt)
    letra, explicacion = sol.group(1), sol.group(2).strip()
    articulo = explicacion.split(":")[0].strip() if ":" in explicacion else ""
    return {"enunciado": enunciado, "opciones": opciones, "correcta": "abcd".index(letra),
            "explicacion": explicacion, "articulo": articulo}


def envolver(draw, texto, f, ancho_max):
    """Parte el texto en líneas que quepan en ancho_max píxeles."""
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if draw.textlength(prueba, font=f) <= ancho_max:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def caja_redondeada(draw, xy, color, radio=34, borde=None):
    draw.rounded_rectangle(xy, radius=radio, fill=color, outline=borde, width=6 if borde else 0)


def fotograma(q: dict, ley: tuple, modo: str, cuenta: int = 0) -> Image.Image:
    """modo: 'pregunta', 'cuenta', 'respuesta' o 'cierre'."""
    im = Image.new("RGB", (ANCHO, ALTO), AZUL_OSCURO)
    d = ImageDraw.Draw(im)
    # Cabecera de marca
    d.rectangle((0, 0, ANCHO, 210), fill=AZUL)
    d.text((ANCHO // 2, 80), "LeyClara · TEST DE OPOSICIONES", font=fuente(46), fill=ACENTO, anchor="mm")
    d.text((ANCHO // 2, 150), f"{ley[0]} · {ley[1]}", font=fuente(38, False), fill=BLANCO, anchor="mm")

    if modo == "cierre":
        y = 640
        for linea, tam, color in [("¿La sabías?", 92, ACENTO), ("Una pregunta nueva", 64, BLANCO),
                                  ("cada día", 64, BLANCO), ("", 40, BLANCO),
                                  ("Tests gratis con el", 50, GRIS), ("artículo de cada respuesta:", 50, GRIS),
                                  (WEB, 54, ACENTO), ("(enlace en el perfil)", 44, GRIS)]:
            d.text((ANCHO // 2, y), linea, font=fuente(tam, tam >= 64), fill=color, anchor="mm")
            y += tam + 40
        return im

    # Enunciado
    f_preg = fuente(66)
    lineas = envolver(d, q["enunciado"], f_preg, ANCHO - 140)
    d.text((70, 270), "PREGUNTA DE EXAMEN", font=fuente(40), fill=ACENTO)
    y = 340
    for l in lineas:
        d.text((70, y), l, font=f_preg, fill=BLANCO)
        y += 84
    y += 60

    # Opciones
    f_op = fuente(54, False)
    for i, op in enumerate(q["opciones"]):
        lin = envolver(d, op, f_op, ANCHO - 260)
        alto = 68 * len(lin) + 64
        fondo, borde, color_txt = AZUL, None, BLANCO
        if modo == "respuesta":
            if i == q["correcta"]:
                fondo, borde = OK, ACENTO
            else:
                fondo, color_txt = "#1a3654", GRIS
        caja_redondeada(d, (60, y, ANCHO - 60, y + alto), fondo, borde=borde)
        d.text((110, y + 30), "ABCD"[i], font=fuente(60), fill=ACENTO if modo != "respuesta" or i == q["correcta"] else GRIS)
        yy = y + 32
        for l in lin:
            d.text((190, yy), l, font=f_op, fill=color_txt)
            yy += 68
        y += alto + 28

    if modo == "cuenta":
        d.ellipse((ANCHO // 2 - 110, y + 30, ANCHO // 2 + 110, y + 250), fill=ACENTO)
        d.text((ANCHO // 2, y + 140), str(cuenta), font=fuente(150), fill=AZUL_OSCURO, anchor="mm")
    elif modo == "respuesta" and q["articulo"]:
        rotulo = f"Lo dice {con_articulo(q['articulo'].split(' (')[0])}"   # en pantalla, sin el paréntesis
        tam = 54
        while tam > 34 and fuente(tam).getlength(rotulo) > ANCHO - 120:
            tam -= 2
        d.text((ANCHO // 2, y + 70), rotulo, font=fuente(tam), fill=ACENTO, anchor="mm")
    else:
        d.text((ANCHO // 2, y + 70), "¿Cuál es la correcta?", font=fuente(54), fill=ACENTO, anchor="mm")
    return im


def para_voz(texto: str) -> str:
    """Ajusta abreviaturas para que la voz las lea bien."""
    t = texto.replace("Art.", "artículo").replace("arts.", "artículos").replace("LO ", "Ley Orgánica ")
    t = re.sub(r"(\d+)/(\d{4})", r"\1 barra \2", t)
    return t


async def tts(texto: str, ruta: Path) -> None:
    # El endpoint nuevo da 429 con ráfagas y a veces corta sin audio: reintentar con espera.
    # El 22/10 a las 19:00 falló tras ~4 min de reintentos: ahora aguanta ~13 min.
    from aiohttp import ClientResponseError
    from edge_tts.exceptions import NoAudioReceived
    esperas = [15, 30, 60, 120, 240, 300]
    for intento in range(len(esperas) + 1):
        try:
            await edge_tts.Communicate(para_voz(texto), VOZ, rate="+12%").save(str(ruta))
            return
        except (ClientResponseError, NoAudioReceived) as e:
            if (isinstance(e, ClientResponseError) and e.status != 429) or intento == len(esperas):
                raise
            await asyncio.sleep(esperas[intento])


def duracion(ruta: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(ruta)], capture_output=True, text=True).stdout
    return float(out.strip())


def generar(carpeta: Path, n: int, salida: Path) -> dict:
    clave = carpeta.resolve().name
    ley = NOMBRES[clave]
    q = leer_pregunta(carpeta, n)
    tmp = Path(tempfile.mkdtemp(prefix="short_test_"))

    texto_preg = (f"Pregunta de oposiciones. {q['enunciado']} "
                  + " ".join(f"{'ABCD'[i]}: {op}." for i, op in enumerate(q["opciones"])))
    letra = "ABCD"[q["correcta"]]
    texto_resp = (f"La correcta es la {letra}: {q['opciones'][q['correcta']]}. "
                  + (f"Lo dice {con_articulo(q['articulo'])}. " if q["articulo"] else ""))
    texto_cierre = "¿La sabías? Sígueme y cada día tienes una pregunta nueva."
    for nombre, texto in [("preg", texto_preg), ("resp", texto_resp), ("cierre", texto_cierre)]:
        asyncio.run(tts(texto, tmp / f"{nombre}.mp3"))

    d_preg, d_resp, d_cierre = (duracion(tmp / f"{x}.mp3") for x in ("preg", "resp", "cierre"))
    escenas = [("pregunta", 0, d_preg + 0.3)] + [("cuenta", c, 1.0) for c in (3, 2, 1)] \
        + [("respuesta", 0, d_resp + 0.8), ("cierre", 0, d_cierre + 0.8)]
    lista = []
    for i, (modo, c, dur) in enumerate(escenas):
        ruta = tmp / f"f{i}.png"
        fotograma(q, ley, modo, c).save(ruta)
        lista.append(f"file '{ruta.as_posix()}'\nduration {dur:.3f}")
    lista.append(f"file '{(tmp / f'f{len(escenas) - 1}.png').as_posix()}'")
    (tmp / "lista.txt").write_text("\n".join(lista), encoding="utf-8")

    # Audio: pregunta, 3 s de tic-tac (cuenta atrás), respuesta, cierre.
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

    corto = q["enunciado"] if len(q["enunciado"]) <= 70 else q["enunciado"][:67].rsplit(" ", 1)[0] + "…"
    titulo = f"{corto} | Test {ley[0]} #oposiciones"
    if len(titulo) > 100:                     # YouTube corta a 100: mejor sin hashtag que con medio
        titulo = f"{corto} | Test {ley[0]}"[:100]
    # Leyes autonómicas: solo entran en la OPE de su servicio de salud
    la = ("las " if ley[0].startswith("Leyes") else "la ") + ley[0]
    ambito = AMBITO.get(clave, "las OPE de los servicios de salud (SAS, SERMAS, Sacyl, SESCAM, Osakidetza…)")
    descripcion = (f"Pregunta tipo test de {la} ({ley[1]}), de las que caen en {ambito}.\n\n"
                   f"Respuesta: {letra}) {q['opciones'][q['correcta']]}\n{q['explicacion']}\n\n"
                   f"Haz el test completo de {la} gratis (20 preguntas, con el artículo de cada respuesta): "
                   f"https://{WEB}/test/{SLUGS[clave]}/?g=yt\n\n"
                   "Avisos gratis por Telegram cuando cambie una ley de tu temario: https://t.me/leyclara_avisos\n\n"
                   "#oposiciones #opesanidad #tcae #celador #enfermeria #legislacionsanitaria"
                   + ETIQUETAS.get(clave, ""))
    return {"titulo": titulo, "descripcion": descripcion, "video": str(salida),
            "duracion": round(sum(e[2] for e in escenas), 1)}


if __name__ == "__main__":
    carpeta = Path(sys.argv[1])
    n = int(sys.argv[2])
    salida = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).parent / "salidas" / f"{carpeta.name}_{n}.mp4"
    print(json.dumps(generar(carpeta, n, salida), ensure_ascii=False, indent=1))
