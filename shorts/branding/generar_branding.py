"""Imágenes del canal de YouTube LeyClara: avatar (800x800), banner (2560x1440) y marca de agua (150x150).

Uso: python generar_branding.py   (deja avatar.png, banner.png y marca_agua.png en esta carpeta)
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
AZUL, AZUL_OSCURO, NOCHE, ACENTO, OK, BLANCO, GRIS = (
    "#1f4e79", "#0f2a44", "#0a1d30", "#ffd400", "#1e7d4f", "#ffffff", "#9fb3c8")
NEGRITA = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
           "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
NORMAL = ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def fuente(tam, negrita=True):
    for f in (NEGRITA if negrita else NORMAL):
        if Path(f).exists():
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default(tam)


def degradado(ancho, alto, arriba, abajo):
    a = Image.new("RGB", (1, 2))
    a.putpixel((0, 0), Image.new("RGB", (1, 1), arriba).getpixel((0, 0)))
    a.putpixel((0, 1), Image.new("RGB", (1, 1), abajo).getpixel((0, 0)))
    return a.resize((ancho, alto), Image.BILINEAR)


def check(d, cx, cy, tam, color, grosor):
    """Marca de verificación dibujada (no depende de que la fuente tenga el glifo)."""
    puntos = [(cx - tam * 0.45, cy), (cx - tam * 0.12, cy + tam * 0.33), (cx + tam * 0.5, cy - tam * 0.38)]
    d.line(puntos, fill=color, width=grosor, joint="curve")


def icono(tam):
    """Casilla amarilla con check sobre fondo azul («test acertado») y «LeyClara» debajo."""
    im = degradado(tam, tam, AZUL, AZUL_OSCURO)
    d = ImageDraw.Draw(im)
    lado = tam * 0.40
    x0, y0 = tam / 2 - lado / 2, tam * 0.15
    d.rounded_rectangle((x0, y0, x0 + lado, y0 + lado), radius=tam * 0.07, fill=ACENTO)
    check(d, tam / 2, y0 + lado / 2, lado * 0.8, NOCHE, int(tam * 0.05))
    f = fuente(int(tam * 0.15))
    w1, w2 = d.textlength("Ley", font=f), d.textlength("Clara", font=f)
    x = (tam - w1 - w2) / 2
    d.text((x, tam * 0.80), "Ley", font=f, fill=BLANCO, anchor="ls")
    d.text((x + w1, tam * 0.80), "Clara", font=f, fill=ACENTO, anchor="ls")
    return im


def avatar():
    im = icono(800)
    im.save(AQUI / "avatar.png")


def marca_agua():
    im = Image.new("RGB", (150, 150), AZUL_OSCURO)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((28, 22, 122, 116), radius=14, fill=ACENTO)
    check(d, 75, 69, 76, NOCHE, 11)
    im.save(AQUI / "marca_agua.png")


def banner():
    W, H = 2560, 1440
    im = degradado(W, H, NOCHE, AZUL).convert("RGBA")
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dc = ImageDraw.Draw(capa)
    # Fondo: líneas de «hoja de examen» y artículos tenues, lejos del centro
    for y in range(0, H, 64):
        dc.line((0, y, W, y), fill=(255, 255, 255, 12), width=2)
    f_tenue = fuente(46, False)
    for x, y, t in [(120, 90, "Art. 9.1"), (700, 170, "Art. 22.1"), (1900, 120, "Art. 31"),
                    (2300, 300, "Art. 4"), (180, 1180, "Art. 16.3"), (900, 1290, "Art. 2.4"),
                    (1650, 1230, "Art. 14"), (2250, 1150, "Art. 3"), (1350, 70, "Art. 10")]:
        dc.text((x, y), t, font=f_tenue, fill=(255, 255, 255, 30))
    im = Image.alpha_composite(im, capa)
    d = ImageDraw.Draw(im)

    # Zona segura (todas las pantallas): 1546x423 centrada
    cx, cy = W // 2, H // 2
    f_marca = fuente(150)
    w1, w2 = d.textlength("Ley", font=f_marca), d.textlength("Clara", font=f_marca)
    x = cx - (w1 + w2) / 2
    d.text((x, cy - 70), "Ley", font=f_marca, fill=BLANCO, anchor="ls")
    d.text((x + w1, cy - 70), "Clara", font=f_marca, fill=ACENTO, anchor="ls")
    d.text((cx, cy - 5), "Una pregunta de examen cada día", font=fuente(62), fill=BLANCO, anchor="mm")
    d.text((cx, cy + 70), "Legislación sanitaria para las OPE · con el artículo de cada respuesta",
           font=fuente(40, False), fill=GRIS, anchor="mm")

    # Fuera de la zona segura (solo escritorio/TV): tarjeta de pregunta a la derecha y leyes a la izquierda
    tx, ty = cx + 830, cy - 230
    d.rounded_rectangle((tx, ty, tx + 420, ty + 460), radius=30, fill=AZUL_OSCURO, outline=ACENTO, width=4)
    d.text((tx + 30, ty + 30), "PREGUNTA DE EXAMEN", font=fuente(30), fill=ACENTO)
    for i, (letra, ok) in enumerate([("A", False), ("B", True), ("C", False), ("D", False)]):
        y = ty + 95 + i * 88
        d.rounded_rectangle((tx + 30, y, tx + 390, y + 70), radius=16, fill=OK if ok else AZUL)
        d.text((tx + 55, y + 35), letra, font=fuente(36), fill=ACENTO if not ok else BLANCO, anchor="lm")
        d.rounded_rectangle((tx + 105, y + 26, tx + (330 if ok else 290), y + 44), radius=9,
                            fill="#d9e6f2" if ok else "#5a7a9a")
        if ok:
            check(d, tx + 360, y + 35, 40, BLANCO, 7)

    leyes = ["Estatuto Marco", "Ley 41/2002", "Ley General de Sanidad", "Prevención de riesgos",
             "Igualdad", "Protección de datos"]
    f_ley = fuente(34)
    lx, ly = cx - 1250, cy - 250
    for i, ley in enumerate(leyes):
        y = ly + i * 84
        w = d.textlength(ley, font=f_ley) + 60
        d.rounded_rectangle((lx, y, lx + w, y + 62), radius=31, fill="#1d3f62", outline="#b39a1a", width=3)
        d.text((lx + 30, y + 31), ley, font=f_ley, fill=BLANCO, anchor="lm")

    # Franja inferior dentro de la zona segura
    d.rounded_rectangle((cx - 330, cy + 125, cx + 330, cy + 185), radius=30, fill=ACENTO)
    d.text((cx, cy + 155), "NUEVA PREGUNTA CADA DÍA · 19:00", font=fuente(34), fill=NOCHE, anchor="mm")
    im.convert("RGB").save(AQUI / "banner.png")


if __name__ == "__main__":
    avatar()
    marca_agua()
    banner()
    print("avatar.png, marca_agua.png y banner.png generados en", AQUI)
