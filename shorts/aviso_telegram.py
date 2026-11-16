"""
Aviso puntual en el canal de Telegram t.me/leyclara_avisos (novedades de la web, PDF gratis…).
El texto va en avisos/<nombre>.txt y/o una encuesta en avisos/<nombre>.json (campos de sendPoll); se publica una sola vez (queda anotado en avisos/publicados.json).

Uso:
    python aviso_telegram.py que-cambio-2026            publica (necesita TELEGRAM_BOT_TOKEN)
    python aviso_telegram.py que-cambio-2026 --prueba   solo enseña el texto
"""
import json
import sys
from pathlib import Path

from quiz_telegram import telegram

AVISOS = Path(__file__).resolve().parent / "avisos"
HECHOS = AVISOS / "publicados.json"


def main(nombre: str, prueba: bool) -> None:
    txt, enc = AVISOS / f"{nombre}.txt", AVISOS / f"{nombre}.json"
    texto = txt.read_text(encoding="utf-8").strip() if txt.exists() else ""
    encuesta = json.loads(enc.read_text(encoding="utf-8")) if enc.exists() else None  # sendPoll (16/11)
    print(texto)
    if encuesta:
        print(json.dumps(encuesta, ensure_ascii=False, indent=1))
    hechos = json.loads(HECHOS.read_text(encoding="utf-8")) if HECHOS.exists() else []
    if prueba:
        return
    if nombre in hechos:
        print(f"El aviso «{nombre}» ya se publicó: no se repite.")
        return
    if texto:
        resp = telegram("sendMessage", {"text": texto})
    if encuesta:
        resp = telegram("sendPoll", encuesta)
    hechos.append(nombre)
    HECHOS.write_text(json.dumps(hechos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Publicado (mensaje {resp['message_id']})")


if __name__ == "__main__":
    main(sys.argv[1], "--prueba" in sys.argv)
