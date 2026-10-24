"""
Encuesta de los viernes en el canal de Telegram t.me/leyclara_avisos: «¿Qué ley quieres practicar el domingo?»
(idea de Teo votada por Sergio en la oficina, 23/10). El resultado orienta el Test del domingo y el siguiente pack.

Es una encuesta normal (no cuestionario) con 10 opciones, el máximo de Telegram. La lanza el Short de la mañana
los viernes; una al día como mucho (guarda el día en encuesta_estado.json).

Uso:
    python encuesta_viernes.py            publica la encuesta (necesita TELEGRAM_BOT_TOKEN)
    python encuesta_viernes.py --prueba   solo la enseña
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from quiz_telegram import telegram

ESTADO = Path(__file__).resolve().parent / "encuesta_estado.json"
VIERNES = 4
ENCUESTA = {
    "question": "¿Qué ley quieres practicar en el Test del domingo?",
    "options": ["Ley 55/2003 (Estatuto Marco)", "Ley 41/2002 (autonomía del paciente)", "Ley 14/1986 (General de Sanidad)",
                "Ley 44/2003 (profesiones sanitarias)", "Ley 16/2003 (cohesión y calidad)", "Ley 31/1995 (riesgos laborales)",
                "LO 3/2007 (igualdad)", "LO 3/2018 (datos y derechos digitales)", "Constitución Española",
                "Otra: dímela por aquí"],
    "is_anonymous": True,
}


def main(prueba: bool) -> None:
    estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {"publicadas": []}
    ahora = datetime.now(ZoneInfo("Europe/Madrid"))
    hoy = ahora.date().isoformat()
    print(json.dumps(ENCUESTA, ensure_ascii=False, indent=1))
    if prueba:
        return
    if ahora.weekday() != VIERNES:
        print(f"Hoy no es viernes ({hoy}): no se publica.")
        return
    if estado.get("ultimo_dia") == hoy:
        print(f"Ya hay encuesta publicada hoy ({hoy}): no se publica otra.")
        return
    resp = telegram("sendPoll", ENCUESTA)
    estado["ultimo_dia"] = hoy
    estado["publicadas"].append({"dia": hoy, "mensaje": resp["message_id"]})
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Publicada la encuesta (mensaje {resp['message_id']})")


if __name__ == "__main__":
    main("--prueba" in sys.argv)
