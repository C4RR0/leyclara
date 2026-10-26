"""Fin de los precios de lanzamiento (anunciado en la web: hasta el 31/10/2026). Ejecutar el 1/11/2026, una sola vez.

Web: sueltos 6,90 → 9,90 €, Ley 55/2003 8,90 → 12,90 €, pack completo 24,90 → 34,90 €, pack Administración
17,90 → 24,90 €; quita el aviso de lanzamiento de la portada y de los tests, regenera tests, resúmenes y las 15 muestras PDF.

Uso (desde web/):  python subir_precios.py  &&  git add -A && git commit && git push
DESPUÉS, A MANO EN GUMROAD (el precio de Gumroad es SIN IVA; Gumroad suma el 4 % de publicación electrónica):
  sueltos 9,52 (también los 4 de Administración) · Ley 55/2003 12,40 · pack completo 33,56 ·
  paquete pack-administracion 23,94  (la Ley 53/1984 sigue a 0 €+).
  Comprobar en cada página pública que sale 9,90 / 12,90 / 34,90 / 24,90 € con IVA.
"""
import re
import subprocess
import sys
from pathlib import Path

WEB = Path(__file__).resolve().parent


def cambiar(ruta: Path, cambios: list[tuple[str, str, int]]) -> str:
    """Aplica (patrón, sustituto, nº de apariciones esperadas) y devuelve el texto nuevo; si alguna no cuadra, para."""
    texto = ruta.read_text(encoding="utf-8")
    for patron, nuevo, esperadas in cambios:
        texto, n = re.subn(patron, nuevo, texto)
        if n != esperadas:
            sys.exit(f"{ruta.name}: «{patron}» aparece {n} veces y se esperaban {esperadas}. No se ha cambiado nada.")
    return texto


def main() -> None:
    tests = cambiar(WEB / "generar_tests.py", [
        (r'"6,90", (\d+)\)', r'"9,90", \1)', 14),   # 10 de sanidad + 4 de Administración (26/10)
        (r'"8,90", 95\)', '"12,90", 95)', 1),
        (r"Las 12 leyes · 24,90 €", "Las 12 leyes · 34,90 €", 1),
        (r'PACK_ADMIN = "17,90"', 'PACK_ADMIN = "24,90"', 1),
        (r'LANZAMIENTO = "Precios de lanzamiento hasta el 31 de octubre\."', 'LANZAMIENTO = ""', 1),
    ])
    portada = cambiar(WEB / "index.html", [
        (r'(?m)^    <p class="aviso-lanzamiento">🏷️ .*\n', "", 1),
        (r'<div class="precio">6,90 €<small>9,90 €</small></div>', '<div class="precio">9,90 €</div>', 9),
        (r'<div class="precio">8,90 €<small>12,90 €</small></div>', '<div class="precio">12,90 €</div>', 1),
        (r'<div class="precio">24,90 €<small>77,90 €</small></div>', '<div class="precio">34,90 €<small>111,90 €</small></div>', 1),
        (r'<div class="precio">Gratis<small>6,90 €</small></div>', '<div class="precio">Gratis<small>9,90 €</small></div>', 1),
        (r"ahorras un 68 %", "ahorras un 69 %", 1),
    ])
    (WEB / "generar_tests.py").write_text(tests, encoding="utf-8")   # solo se escribe si los dos ficheros cuadran
    (WEB / "index.html").write_text(portada, encoding="utf-8")
    subprocess.run([sys.executable, "generar_tests.py"], cwd=WEB, check=True)
    subprocess.run([sys.executable, "actualizar_muestras.py", "noviembre"], cwd=WEB.parent, check=True)
    restos = [p for p in WEB.rglob("*.html") if re.search(r"12 leyes · 24,90|17,90 €|6,90 €|8,90 €|lanzamiento hasta", p.read_text(encoding="utf-8"))]
    print("OK. Páginas que aún mencionan precios antiguos:", restos or "ninguna")


if __name__ == "__main__":
    main()
