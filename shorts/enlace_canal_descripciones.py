"""Añade el enlace del canal de avisos de Telegram a la descripción de los Shorts ya publicados que no lo tengan.

Lo ejecuta el workflow del Short diario después de publicar; si todos lo tienen ya, no hace nada.
Usa token_leyclara.json, igual que publicar_short.py.
"""
import json
from pathlib import Path

from publicar_short import COLA, TOKEN

LINEA = "Avisos gratis por Telegram cuando cambie una ley de tu temario: https://t.me/leyclara_avisos"


def main() -> None:
    if not TOKEN.exists():
        print("Sin token_leyclara.json: no se toca nada.")
        return
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    yt = build("youtube", "v3", credentials=Credentials.from_authorized_user_file(str(TOKEN)))
    ids = [p["video"] for p in json.loads(COLA.read_text(encoding="utf-8"))["publicados"]]
    cambiados = 0
    for i in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet", id=",".join(ids[i:i + 50])).execute().get("items", []):
            sn = v["snippet"]
            if "t.me/leyclara_avisos" in sn["description"]:
                continue
            # justo antes de los hashtags, como en los Shorts nuevos
            partes = sn["description"].rsplit("\n\n#", 1)
            sn["description"] = (f"{partes[0]}\n\n{LINEA}\n\n#{partes[1]}" if len(partes) == 2
                                 else f"{sn['description']}\n\n{LINEA}")
            body = {"id": v["id"], "snippet": {k: sn[k] for k in ("title", "description", "categoryId", "tags",
                                                               "defaultLanguage", "defaultAudioLanguage") if k in sn}}
            yt.videos().update(part="snippet", body=body).execute()
            cambiados += 1
            print(f"Enlace añadido a {v['id']}")
    print(f"{cambiados} descripciones actualizadas")


if __name__ == "__main__":
    main()
