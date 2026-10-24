"""
Aviso puntual en el canal de Telegram t.me/leyclara_avisos (novedades de la web, PDF gratis…).
El texto va en avisos/<nombre>.txt; se publica una sola vez (queda anotado en avisos/publicados.json).

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
    texto = (AVISOS / f"{nombre}.txt").read_text(encoding="utf-8").strip()
    print(texto)
    hechos = json.loads(HECHOS.read_text(encoding="utf-8")) if HECHOS.exists() else []
    if prueba:
        return
    if nombre in hechos:
        print(f"El aviso «{nombre}» ya se publicó: no se repite.")
        return
    resp = telegram("sendMessage", {"text": texto})
    hechos.append(nombre)
    HECHOS.write_text(json.dumps(hechos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Publicado (mensaje {resp['message_id']})")


if __name__ == "__main__":
    main(sys.argv[1], "--prueba" in sys.argv)
