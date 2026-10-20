"""Sube al canal de YouTube de LeyClara los vídeos largos montados por montar_video_test.py (salida/<nombre>.mp4,
con su _descripcion.txt y _miniatura.jpg) que aún no estén en publicados.json. Nunca sube dos veces el mismo.

Necesita ../shorts/token_leyclara.json (lo escribe el workflow video_largo.yml desde el secret).
Uso: python videos_largos/subir_video_largo.py estatuto_marco_50
"""
import json
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

AQUI = Path(__file__).resolve().parent
TOKEN = AQUI.parent / "shorts" / "token_leyclara.json"
PUBLICADOS = AQUI / "publicados.json"
TITULOS = {"estatuto_marco_50": "Test del Estatuto Marco (Ley 55/2003): 50 preguntas de examen con solución | Oposiciones sanidad"}


def main(nombre: str) -> int:
    hechos = json.loads(PUBLICADOS.read_text(encoding="utf-8")) if PUBLICADOS.exists() else {}
    if nombre in hechos:
        print(f"{nombre} ya está publicado: https://youtu.be/{hechos[nombre]}")
        return 0
    salida = AQUI / "salida"
    yt = build("youtube", "v3", credentials=Credentials.from_authorized_user_file(str(TOKEN)))
    body = {"snippet": {"title": TITULOS.get(nombre, nombre.replace("_", " "))[:100],
                        "description": (salida / f"{nombre}_descripcion.txt").read_text(encoding="utf-8")[:5000],
                        "categoryId": "27",  # Educación
                        "tags": ["oposiciones", "test oposiciones", "estatuto marco", "ley 55/2003", "ope sanidad",
                                 "tcae", "celador", "enfermeria", "legislacion sanitaria", "temario comun"],
                        "defaultLanguage": "es", "defaultAudioLanguage": "es"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}
    resp = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(
        str(salida / f"{nombre}.mp4"), mimetype="video/mp4", resumable=True, chunksize=8 * 1024 * 1024)).execute()
    vid = resp["id"]
    hechos[nombre] = vid
    PUBLICADOS.write_text(json.dumps(hechos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"PUBLICADO=https://youtu.be/{vid}")
    try:  # las miniaturas propias exigen el canal verificado por teléfono: si falla, el vídeo queda con la automática
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(salida / f"{nombre}_miniatura.jpg"),
                                                                     mimetype="image/jpeg")).execute()
        print("Miniatura puesta")
    except Exception as e:  # noqa: BLE001
        print(f"::warning::Miniatura no puesta ({type(e).__name__}: {str(e)[:200]})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
