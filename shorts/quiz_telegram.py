"""
Publica un quiz diario (encuesta en modo cuestionario) en el canal de Telegram t.me/leyclara_avisos.
Los domingos, «Test del domingo»: un mensaje de cabecera y 5 preguntas seguidas (20/10, idea votada en la oficina).

Saca las preguntas de las muestras (preguntas/<ley>/muestra/estudio.md), alternando leyes, y guarda por
dónde va en quiz_estado.json. Se salta las preguntas que no caben en los límites de Telegram.

Uso:
    python quiz_telegram.py            publica la siguiente (necesita TELEGRAM_BOT_TOKEN)
    python quiz_telegram.py --prueba   solo enseña cuál publicaría
    python quiz_telegram.py --prueba --domingo   igual, como si fuera domingo
El bot tiene que ser administrador del canal con permiso para publicar.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from generar_short_test import NOMBRES, leer_pregunta

AQUI = Path(__file__).resolve().parent
ESTADO = AQUI / "quiz_estado.json"
CANAL = "@leyclara_avisos"
# orden de rotación: primero las leyes comunes a todas las OPE
LEYES = ["ley55", "ley41", "ley14", "ley31", "ley44", "lo3_2018", "ley16", "lo3_2007", "ley53",
         "ley2_1998_and", "and_igualdad"]
POR_LEY = 20
# límites de la API de Telegram para encuestas
MAX_PREGUNTA, MAX_OPCION, MAX_EXPLICACION = 300, 100, 200
DOMINGO = 5  # preguntas del test del domingo
CABECERA_DOMINGO = ("🧠 Test del domingo: 5 preguntas de leyes distintas del temario común. "
                    "Responde sin mirar y cuenta tus aciertos. Más tests gratis: https://c4rr0.github.io/leyclara/test/?g=tg-canal")


def candidatas():
    """Todas las preguntas en orden de publicación: la 1 de cada ley, luego la 2 de cada ley…"""
    for n in range(1, POR_LEY + 1):
        for clave in LEYES:
            yield clave, n


def preparar(clave: str, n: int) -> dict | None:
    q = leer_pregunta(AQUI / "preguntas" / clave, n)
    ley, tema = NOMBRES[clave]
    pregunta = f"{ley} ({tema}): {q['enunciado']}"
    if len(pregunta) > MAX_PREGUNTA:
        pregunta = q["enunciado"]
    explicacion = q["explicacion"]
    if len(explicacion) > MAX_EXPLICACION:
        explicacion = explicacion[:MAX_EXPLICACION - 1].rsplit(" ", 1)[0] + "…"
    opciones = [o.rstrip(".") for o in q["opciones"]]
    if len(pregunta) > MAX_PREGUNTA or any(len(o) > MAX_OPCION for o in opciones):
        return None
    return {"question": pregunta, "options": [{"text": o} for o in opciones], "type": "quiz",
            "correct_option_id": q["correcta"], "explanation": explicacion, "is_anonymous": True}


def telegram(metodo: str, datos: dict) -> dict:
    # strip(): al pegar el secret en GitHub se coló un salto de línea y la URL salía inválida
    token = os.environ["TELEGRAM_BOT_TOKEN"].strip()
    pet = urllib.request.Request(f"https://api.telegram.org/bot{token}/{metodo}",
                                 data=json.dumps({"chat_id": CANAL, **datos}).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(pet, timeout=30) as r:
        resp = json.load(r)
    if not resp.get("ok"):
        sys.exit(f"Telegram respondió: {resp}")
    return resp["result"]


def siguiente(estado: dict, lista: list, usadas: set):
    """La siguiente pregunta que cabe en Telegram y no es de una ley ya usada hoy."""
    for _ in range(len(lista)):
        i = estado["siguiente"] % len(lista)
        clave, n = lista[i]
        estado["siguiente"] = i + 1
        if clave in usadas:
            continue
        quiz = preparar(clave, n)
        if quiz:
            return clave, n, quiz
        print(f"Saltada {clave}:{n} (no cabe en los límites de Telegram)")
    sys.exit("No queda ninguna pregunta que quepa en Telegram")


def main(prueba: bool) -> None:
    estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {"siguiente": 0, "publicadas": []}
    # Lo lanzan dos workflows (el Short de la tarde y, de reserva, el schedule propio): uno al día como mucho.
    hoy = datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
    if not prueba and estado.get("ultimo_dia") == hoy:
        print(f"Ya hay quiz publicado hoy ({hoy}): no se publica otro.")
        return
    lista = list(candidatas())
    domingo = "--domingo" in sys.argv or datetime.now(ZoneInfo("Europe/Madrid")).weekday() == 6
    usadas, quizzes = set(), []
    for _ in range(DOMINGO if domingo else 1):
        clave, n, quiz = siguiente(estado, lista, usadas)
        usadas.add(clave)
        quizzes.append((clave, n, quiz))
    if domingo:
        print(CABECERA_DOMINGO)
    for clave, n, quiz in quizzes:
        print(json.dumps(quiz, ensure_ascii=False, indent=1))
    if prueba:
        return
    if domingo:
        telegram("sendMessage", {"text": CABECERA_DOMINGO, "disable_web_page_preview": True})
    for clave, n, quiz in quizzes:
        resp = telegram("sendPoll", quiz)
        estado["publicadas"].append(f"{clave}:{n}")
        estado["ultimo_dia"] = hoy
        # se guarda tras cada una: si falla a mitad, no se repiten las ya publicadas
        ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Publicada {clave}:{n} (mensaje {resp['message_id']})")


if __name__ == "__main__":
    main("--prueba" in sys.argv)
