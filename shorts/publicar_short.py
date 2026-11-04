"""Publica en YouTube el siguiente Short de «pregunta tipo test» de la cola (cola.json).

Necesita token_leyclara.json (OAuth del canal, lo crea el workflow desde el secret
YOUTUBE_TOKEN_LEYCLARA_JSON). Con --prueba solo genera el vídeo, sin subirlo ni tocar la cola.

Uso: python publicar_short.py [--prueba] [--vf]

Los domingos por la tarde publica el Short semanal «¿Verdadero o falso?» (generar_vf.py) en lugar del test.
"""
import json
import sys
from pathlib import Path

from generar_short_test import generar

BASE = Path(__file__).resolve().parent
COLA = BASE / "cola.json"
TOKEN = BASE / "token_leyclara.json"


def subir(video: str, titulo: str, descripcion: str) -> str:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    creds = Credentials.from_authorized_user_file(str(TOKEN))
    yt = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {"title": titulo, "description": descripcion, "categoryId": "27",  # Educación
                    "tags": ["oposiciones", "test oposiciones", "ope sanidad", "tcae", "celador",
                             "enfermeria", "legislacion sanitaria"],
                    "defaultLanguage": "es", "defaultAudioLanguage": "es"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    resp = yt.videos().insert(part="snippet,status", body=body,
                              media_body=MediaFileUpload(video, mimetype="video/mp4")).execute()
    return resp["id"]


VF_ESTADO = BASE / "vf_short.json"


def es_turno_vf() -> bool:
    """Domingo, publicación de la tarde (12-18 h Madrid): toca el Short semanal «¿Verdadero o falso?»."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    ahora = datetime.now(ZoneInfo("Europe/Madrid"))
    return ahora.weekday() == 6 and 12 <= ahora.hour < 18 or "--vf" in sys.argv


def publicar_vf(prueba: bool) -> int:
    """Short semanal V/F (tarea de Teo). Estado propio en vf_short.json; salta las afirmaciones usadas en Telegram."""
    from generar_vf import leer_banco, generar as generar_vf
    from datetime import date
    estado = json.loads(VF_ESTADO.read_text(encoding="utf-8")) if VF_ESTADO.exists() else {"publicados": []}
    hoy = date.today().isoformat()
    if any(p["fecha"] == hoy for p in estado["publicados"]) and not prueba:
        print("El V/F de hoy ya está publicado.")
        return 0
    tg = BASE / "vf_estado.json"
    usados = set(json.loads(tg.read_text(encoding="utf-8")).get("publicados", [])) if tg.exists() else set()
    usados |= {p["n"] for p in estado["publicados"]}
    libres = [n for n in sorted(leer_banco()) if n not in usados]
    if not libres:
        print("No quedan afirmaciones V/F: se publica la pregunta tipo test normal.")
        return -1
    n = libres[0]
    info = generar_vf(n, BASE / "salidas" / f"vf_{n}.mp4")
    print(json.dumps(info, ensure_ascii=False, indent=1))
    if prueba or not TOKEN.exists():
        print("Prueba o sin token: vídeo V/F generado, no se sube.")
        return 0
    vid = subir(info["video"], info["titulo"], info["descripcion"])
    estado["publicados"].append({"n": n, "fecha": hoy, "video": vid})
    VF_ESTADO.write_text(json.dumps(estado, indent=0, ensure_ascii=False), encoding="utf-8")
    print(f"PUBLICADO=https://youtu.be/{vid}")
    return 0


def main() -> int:
    prueba = "--prueba" in sys.argv
    if es_turno_vf():
        r = publicar_vf(prueba)
        if r >= 0:
            return r
    estado = json.loads(COLA.read_text(encoding="utf-8"))
    i = estado["siguiente"]
    if i >= len(estado["cola"]):
        print("Cola vacía: no quedan preguntas.")
        return 0
    ley, n = estado["cola"][i].split(":")
    info = generar(BASE / "preguntas" / ley, int(n), BASE / "salidas" / f"{ley}_{n}.mp4")
    print(json.dumps(info, ensure_ascii=False, indent=1))
    if prueba:
        print("Prueba: vídeo generado, no se sube.")
        return 0
    if not TOKEN.exists():
        print("Sin token_leyclara.json: canal no configurado, no se sube.")
        return 0
    vid = subir(info["video"], info["titulo"], info["descripcion"])
    estado["publicados"].append({"pregunta": estado["cola"][i], "video": vid})
    estado["siguiente"] = i + 1
    COLA.write_text(json.dumps(estado, indent=0, ensure_ascii=False), encoding="utf-8")
    print(f"PUBLICADO=https://youtu.be/{vid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
