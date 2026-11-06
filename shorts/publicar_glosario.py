"""Publica una sola vez el Short del glosario (generar_short_glosario.py) en el canal de LeyClara.

Tarea de Teo con OK de Sergio (oficina, mzoztca2pzp2e9ro0x4k). Guarda el id en glosario_short.json
para no publicarlo dos veces. Uso: python publicar_glosario.py [--prueba]
"""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ESTADO = BASE / "glosario_short.json"
VIDEO = BASE / "salidas" / "glosario_01.mp4"
TITULO = "3 términos de Administración que caen en oposiciones #oposiciones #shorts"
DESCRIPCION = (
    "Silencio administrativo (art. 24 Ley 39/2015), plazos en días hábiles (art. 30 Ley 39/2015) "
    "y avocación (art. 10 Ley 40/2015), en una frase cada uno.\n\n"
    "📘 Los 15 términos con su artículo, gratis: https://c4rr0.github.io/leyclara/glosario/?g=yt\n"
    "✅ Test gratis de cada ley: https://c4rr0.github.io/leyclara/test/?g=yt\n\n"
    "#oposiciones #administrativo #auxiliaradministrativo #ley39 #ley40"
)


def main() -> int:
    prueba = "--prueba" in sys.argv
    if ESTADO.exists():
        print("Ya publicado:", json.loads(ESTADO.read_text(encoding="utf-8")))
        return 0
    subprocess.run([sys.executable, str(BASE / "generar_short_glosario.py"), str(VIDEO)], check=True, cwd=BASE)
    if prueba or not (BASE / "token_leyclara.json").exists():
        print("Prueba o sin token: vídeo generado, no se sube.")
        return 0
    from publicar_short import subir
    vid = subir(str(VIDEO), TITULO, DESCRIPCION)
    ESTADO.write_text(json.dumps({"id": vid, "url": f"https://youtube.com/shorts/{vid}"}, ensure_ascii=False), encoding="utf-8")
    print("PUBLICADO_GLOSARIO=" + vid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
