"""Anuncia en el canal de Telegram (@leyclara_avisos) los vídeos largos de publicados.json que aún no estén en
anunciados.json: enlace del vídeo + test gratis de la web. Solo vídeos largos (los Shorts salen 3 al día y, con el
quiz diario, serían demasiados mensajes). Lo ejecuta video_largo.yml después de subir; Teo lo vigila desde el panel.

Uso: TELEGRAM_BOT_TOKEN=… python videos_largos/anunciar_telegram.py [--prueba]
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "shorts"))
from quiz_telegram import telegram  # noqa: E402

PUBLICADOS, ANUNCIADOS = AQUI / "publicados.json", AQUI / "anunciados.json"
WEB = "https://c4rr0.github.io/leyclara"
# texto de cada vídeo: qué es y a qué test gratis de la web lleva
TEXTOS = {
    "estatuto_marco_parte1": ("🎬 Nuevo vídeo: Test del Estatuto Marco (Ley 55/2003), parte 1",
                              "25 preguntas de examen con 6 segundos para pensar y la respuesta con su artículo. "
                              "Ideal para repasar en el coche o paseando.", "test/ley-55-2003/"),
    "estatuto_marco_parte2": ("🎬 Nuevo vídeo: Test del Estatuto Marco (Ley 55/2003), parte 2",
                              "25 preguntas más (de la 26 a la 50), con la respuesta y el artículo de cada una.",
                              "test/ley-55-2003/"),
}


def main() -> int:
    prueba = "--prueba" in sys.argv
    publicados = json.loads(PUBLICADOS.read_text(encoding="utf-8")) if PUBLICADOS.exists() else {}
    anunciados = json.loads(ANUNCIADOS.read_text(encoding="utf-8")) if ANUNCIADOS.exists() else {}
    for nombre, vid in publicados.items():
        if nombre in anunciados:
            continue
        titulo, texto, test = TEXTOS.get(nombre, (f"🎬 Nuevo vídeo de LeyClara: {nombre.replace('_', ' ')}", "", "test/"))
        mensaje = (f"<b>{titulo}</b>\n\n{texto}\n\n▶️ https://youtu.be/{vid}\n\n"
                   f"📝 ¿Prefieres hacerlo por escrito y ver tu nota? Test gratis por temas: {WEB}/{test}?g=tg-canal")
        if prueba:
            print(mensaje, "\n---")
            continue
        telegram("sendMessage", {"text": mensaje, "parse_mode": "HTML"})
        anunciados[nombre] = vid
        ANUNCIADOS.write_text(json.dumps(anunciados, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"Anunciado en Telegram: {nombre}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
