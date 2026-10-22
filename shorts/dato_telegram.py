"""
«Dato del día» en el canal de Telegram t.me/leyclara_avisos (idea de Teo votada por Sergio en la oficina, 21/10):
un mensaje corto con una duda clave de una ley y el enlace a su test gratis (?g=tg-dato para medir los clics).

Saca los datos de las preguntas frecuentes de la web (../faq_leyes.py, comprobadas contra el BOE), alternando
leyes, y guarda por dónde va en dato_estado.json. Lo lanza el Short de la mañana; uno al día como mucho.

Uso:
    python dato_telegram.py            publica el siguiente (necesita TELEGRAM_BOT_TOKEN)
    python dato_telegram.py --prueba   solo enseña cuál publicaría
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
from faq_leyes import FAQ  # noqa: E402
from generar_tests import TODAS, de  # noqa: E402
from quiz_telegram import telegram  # noqa: E402

ESTADO = AQUI / "dato_estado.json"
WEB = "https://c4rr0.github.io/leyclara/test/"


def candidatas():
    """La 1.ª duda de cada ley (primero las sanitarias, luego las de Administración), luego la 2.ª…"""
    for n in range(3):
        for ley in TODAS:
            if ley[1] in FAQ and n < len(FAQ[ley[1]]):
                yield ley, n


def texto(ley, n):
    slug, corto = ley[1], ley[2]
    pregunta, respuesta = FAQ[slug][n]
    return (f"📌 Dato del día · {corto}\n\n{pregunta}\n{respuesta}\n\n"
            f"👉 ¿Te lo sabías? Test gratis {de(corto)}: {WEB}{slug}/?g=tg-dato")


def main(prueba: bool) -> None:
    estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {"siguiente": 0, "publicados": []}
    hoy = datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
    if not prueba and estado.get("ultimo_dia") == hoy:
        print(f"Ya hay dato publicado hoy ({hoy}): no se publica otro.")
        return
    lista = list(candidatas())
    i = estado["siguiente"] % len(lista)
    ley, n = lista[i]
    mensaje = texto(ley, n)
    print(mensaje)
    if prueba:
        return
    resp = telegram("sendMessage", {"text": mensaje, "disable_web_page_preview": True})
    estado.update(siguiente=i + 1, ultimo_dia=hoy)
    estado["publicados"].append(f"{ley[1]}:{n}")
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Publicado {ley[1]}:{n} (mensaje {resp['message_id']})")


if __name__ == "__main__":
    main("--prueba" in sys.argv)
