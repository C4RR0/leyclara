"""
«¿Verdadero o falso?» del día en el canal de Telegram t.me/leyclara_avisos (tarea de Teo en la oficina, OK de Sergio el
3/11/2026): cada día una afirmación de verdadero_falso.md y, en el mismo mensaje, la respuesta de la del día anterior.

Del 4 al 10/11/2026 van las 7 del Estatuto Marco (Ley 55/2003) para llevar gente al test durante la prueba del pack a 3 €
(generar_tests.py, PRUEBA). Cuando se acaban las de LEY, publica una última respuesta y se para solo.
Lo lanza el Short de las 15:00 (short_diario.yml); uno al día como mucho. Estado en vf_estado.json.

Uso:
    python vf_telegram.py            publica el de hoy (necesita TELEGRAM_BOT_TOKEN)
    python vf_telegram.py --prueba   solo enseña lo que publicaría
"""
import json
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
from generar_vf import leer_banco  # noqa: E402
from quiz_telegram import telegram  # noqa: E402

ESTADO = AQUI / "vf_estado.json"
LEY = "ley-55-2003"
WEB = "https://c4rr0.github.io/leyclara/test/"
PACK = "https://carrosphere.gumroad.com/l/ley-55-2003"
FIN_PRUEBA = date(2026, 11, 10)  # último día del pack a 3 €


def afirmaciones():
    banco = leer_banco()
    return [(n, banco[n]) for n in sorted(banco) if banco[n]["ley"][2] == LEY]


def respuesta(a):
    vf = "VERDADERO ✅" if a["verdad"] else "FALSO ❌"
    expl = f" {a['explicacion']}" if a["explicacion"] else ""
    return f"🔎 Respuesta de ayer: «{a['afirmacion']}»\n→ {vf} ({a['articulo']}).{expl}"


def texto(hoy, ayer, dia):
    partes = [respuesta(ayer)] if ayer else []
    if hoy:
        slug = hoy["ley"][2]
        partes.append(f"🤔 ¿Verdadero o falso? · {hoy['ley'][0]} ({hoy['ley'][1]})\n\n«{hoy['afirmacion']}»\n\n"
                      f"Piénsalo: mañana te doy la respuesta con su artículo.\n"
                      f"👉 Test gratis de 20 preguntas: {WEB}{slug}/?g=tg-vf")
    if dia <= FIN_PRUEBA:
        partes.append(f"🏷️ Solo hasta el 10/11: el pack del Estatuto Marco por 3 € (antes 8,90 €) → {PACK}")
    return "\n\n".join(partes)


def main(prueba: bool) -> None:
    estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else {"siguiente": 0, "publicados": []}
    ahora = datetime.now(ZoneInfo("Europe/Madrid")).date()
    if not prueba and estado.get("ultimo_dia") == ahora.isoformat():
        print(f"Ya hay verdadero o falso hoy ({ahora}): no se publica otro.")
        return
    lista = afirmaciones()
    i = estado["siguiente"]
    if i > len(lista):
        print("Serie terminada: no se publica nada.")
        return
    hoy = lista[i][1] if i < len(lista) else None
    ayer = lista[i - 1][1] if i > 0 else None
    mensaje = texto(hoy, ayer, ahora)
    print(mensaje)
    if prueba:
        return
    resp = telegram("sendMessage", {"text": mensaje, "disable_web_page_preview": True})
    estado.update(siguiente=i + 1, ultimo_dia=ahora.isoformat())
    estado["publicados"].append(lista[i][0] if hoy else "fin")
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Publicado (mensaje {resp['message_id']})")


if __name__ == "__main__":
    main("--prueba" in sys.argv)
