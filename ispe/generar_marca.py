#!/usr/bin/env python3
"""Genera los iconos y logos de «ISPE Soporte» para el cliente RustDesk personalizado.

Parte del escudo de internetseguroparaempresas.com (escudo-1024.png, renderizado desde favicon.svg)
y deja en ./salida/ todo lo que el código de RustDesk espera encontrar:
  - icon.png / icon.svg          → flutter/assets (icono dentro de la app y de la bandeja del sistema)
  - logo.png, logo_light.png,
    logo_dark.png (máx. 300x60)  → flutter/assets (cabecera de la ventana principal)
  - app_icon.ico / icon.ico      → icono del .exe, accesos directos e instalador MSI
  - 32x32 / 64x64 / 128x128 /
    128x128@2x.png / icon.png    → carpeta res/ (otros empaquetados)
"""
import os
import shutil

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
SAL = os.path.join(BASE, "salida")
FUENTE_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FUENTE_N = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
ROJO = (230, 57, 70, 255)  # #E63946, el rojo del escudo de la web


def icono_cuadrado():
    """Escudo a 1024 px: es la base de todos los PNG e ICO."""
    return Image.open(os.path.join(BASE, "escudo-1024.png")).convert("RGBA")


def logo(color_texto, color_sub):
    """Logo horizontal 300x60 (lo máximo que admite RustDesk): escudo + «ISPE Soporte» + lema.

    Se dibuja a 4x (1200x240) y se reduce para que el texto salga suave.
    """
    k = 4
    img = Image.new("RGBA", (300 * k, 60 * k), (0, 0, 0, 0))
    esc = icono_cuadrado().resize((56 * k, 56 * k), Image.LANCZOS)
    img.paste(esc, (2 * k, 2 * k), esc)
    d = ImageDraw.Draw(img)
    # Línea principal: «ISPE» en rojo de marca y «Soporte» en el color del tema
    f1 = ImageFont.truetype(FUENTE_B, 26 * k)
    x = 66 * k
    d.text((x, 4 * k), "ISPE", font=f1, fill=ROJO)
    x += d.textlength("ISPE ", font=f1)
    d.text((x, 4 * k), "Soporte", font=f1, fill=color_texto)
    # Lema debajo
    f2 = ImageFont.truetype(FUENTE_N, 11 * k)
    d.text((66 * k, 38 * k), "Internet Seguro para Empresas", font=f2, fill=color_sub)
    return img.resize((300, 60), Image.LANCZOS)


def main():
    os.makedirs(SAL, exist_ok=True)
    ic = icono_cuadrado()

    # PNG de distintos tamaños (assets de Flutter y carpeta res/)
    ic.resize((256, 256), Image.LANCZOS).save(os.path.join(SAL, "icon.png"))
    for n in (32, 64, 128):
        ic.resize((n, n), Image.LANCZOS).save(os.path.join(SAL, f"{n}x{n}.png"))
    ic.resize((256, 256), Image.LANCZOS).save(os.path.join(SAL, "128x128@2x.png"))

    # ICO multitamaño para el ejecutable, accesos directos y MSI
    ic.save(os.path.join(SAL, "app_icon.ico"),
            sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    shutil.copy(os.path.join(SAL, "app_icon.ico"), os.path.join(SAL, "icon.ico"))

    # SVG original (Flutter lo usa si falta el PNG)
    shutil.copy(os.path.join(BASE, "escudo.svg"), os.path.join(SAL, "icon.svg"))

    # Logos para tema claro y oscuro (+ logo.png por defecto = versión clara)
    logo((10, 15, 20, 255), (90, 100, 110, 255)).save(os.path.join(SAL, "logo_light.png"))
    logo((244, 247, 246, 255), (170, 180, 190, 255)).save(os.path.join(SAL, "logo_dark.png"))
    shutil.copy(os.path.join(SAL, "logo_light.png"), os.path.join(SAL, "logo.png"))
    print("Generado en", SAL, sorted(os.listdir(SAL)))


if __name__ == "__main__":
    main()
