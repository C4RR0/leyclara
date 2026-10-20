"""Estado en YouTube de los vídeos largos publicados (publicados.json): subida, procesado, motivo de rechazo y
privacidad. Lo usa el workflow video_largo.yml para saber si un vídeo se ha quedado bloqueado (p. ej. por durar
más de 15 minutos en un canal sin verificar por teléfono)."""
import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

AQUI = Path(__file__).resolve().parent
TOKEN = AQUI.parent / "shorts" / "token_leyclara.json"

yt = build("youtube", "v3", credentials=Credentials.from_authorized_user_file(str(TOKEN)))
hechos = json.loads((AQUI / "publicados.json").read_text(encoding="utf-8"))
r = yt.videos().list(part="status,processingDetails,contentDetails", id=",".join(hechos.values())).execute()
for v in r.get("items", []):
    s, p = v["status"], v.get("processingDetails", {})
    print(f"{v['id']}: subida={s.get('uploadStatus')} rechazo={s.get('rejectionReason', '-')} "
          f"fallo={s.get('failureReason', '-')} privacidad={s.get('privacyStatus')} "
          f"procesado={p.get('processingStatus', '-')} duración={v['contentDetails'].get('duration')}")
ch = yt.channels().list(part="status", mine=True).execute()["items"][0]["status"]
print(f"Canal: longUploadsStatus={ch.get('longUploadsStatus')}")
