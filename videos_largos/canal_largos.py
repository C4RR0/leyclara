"""Sale con código 1 (y un aviso en el run) si el canal de LeyClara aún no puede subir vídeos de más de 15 minutos
(longUploadsStatus distinto de «allowed»): así el workflow no sube un vídeo largo que YouTube eliminaría al momento,
como pasó el 20/10. Se activa verificando el canal por SMS en youtube.com/verify."""
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = Path(__file__).resolve().parent.parent / "shorts" / "token_leyclara.json"
yt = build("youtube", "v3", credentials=Credentials.from_authorized_user_file(str(TOKEN)))
estado = yt.channels().list(part="status", mine=True).execute()["items"][0]["status"].get("longUploadsStatus")
if estado != "allowed":
    print(f"::warning::Canal sin vídeos largos activados (longUploadsStatus={estado}): verificarlo en youtube.com/verify. No se sube nada.")
    sys.exit(1)
print("::notice::Canal con vídeos largos activados")
