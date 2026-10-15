"""Descripción, palabras clave, idioma, banner y marca de agua del canal de YouTube LeyClara.
La foto de perfil no se puede poner por la API: se sube en Studio (branding/avatar.png).

Uso: python configurar_canal.py   (necesita token_leyclara.json en esta carpeta)
"""
import json
from pathlib import Path

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE = Path(__file__).resolve().parent
CRLF = "\r\n"

cred = Credentials.from_authorized_user_file(str(BASE / "token_leyclara.json"))
if not cred.valid:
    cred.refresh(Request())
yt = build("youtube", "v3", credentials=cred)
ch = yt.channels().list(part="brandingSettings,snippet", mine=True).execute()["items"][0]
print("Canal:", ch["snippet"]["title"])

b = ch["brandingSettings"]
b["channel"]["description"] = (
    "Una pregunta de examen cada día para preparar la legislación sanitaria de las OPE "
    "(SAS, SERMAS, Sacyl, SESCAM, Osakidetza, SERGAS…): TCAE, celador, enfermería, técnicos y más.\n\n"
    "Cada Short es una pregunta tipo test real de las leyes que más caen: Estatuto Marco (Ley 55/2003), "
    "autonomía del paciente (Ley 41/2002), Ley General de Sanidad, prevención de riesgos laborales, "
    "igualdad y protección de datos. Piensa tu respuesta antes de la cuenta atrás y comprueba el artículo exacto.\n\n"
    "Tests gratis con el artículo de cada respuesta: https://c4rr0.github.io/leyclara/?g=yt\n\n"
    "Material de estudio independiente elaborado a partir del BOE. No oficial ni vinculado a ninguna administración.")
b["channel"]["keywords"] = ('oposiciones "test oposiciones" "ope sanidad" tcae celador enfermeria '
                            '"estatuto marco" "ley 41/2002" "legislacion sanitaria" "temario comun" '
                            'SAS SERMAS Sacyl SESCAM Osakidetza')
b["channel"]["defaultLanguage"] = "es"
b["channel"]["country"] = "ES"
subida = yt.channelBanners().insert(
    media_body=MediaFileUpload(str(BASE / "branding" / "banner.png"), mimetype="image/png")).execute()
b.setdefault("image", {})["bannerExternalUrl"] = subida["url"]
yt.channels().update(part="brandingSettings", body={"id": ch["id"], "brandingSettings": b}).execute()
print("Descripción, palabras clave, idioma y banner puestos")

# watermarks.set con la librería falla al leer la respuesta vacía: se hace a mano, multipart.
meta = {"timing": {"type": "offsetFromEnd", "offsetMs": 15000},
        "position": {"type": "corner", "cornerPosition": "topRight"}}
img = (BASE / "branding" / "marca_agua.png").read_bytes()
frontera = "frontera_marca_agua"
cuerpo = (f"--{frontera}{CRLF}Content-Type: application/json; charset=UTF-8{CRLF}{CRLF}"
          f"{json.dumps(meta)}{CRLF}--{frontera}{CRLF}Content-Type: image/png{CRLF}{CRLF}").encode() \
    + img + f"{CRLF}--{frontera}--".encode()
r = requests.post("https://www.googleapis.com/upload/youtube/v3/watermarks/set",
                  params={"channelId": ch["id"], "uploadType": "multipart"}, data=cuerpo,
                  headers={"Authorization": f"Bearer {cred.token}",
                           "Content-Type": f"multipart/related; boundary={frontera}"}, timeout=60)
print("watermarks.set ->", r.status_code, r.text[:300])
