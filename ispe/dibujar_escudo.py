#!/usr/bin/env python3
"""Dibuja el escudo de ISPE (favicon.svg de internetseguroparaempresas.com) a 1024 px con PIL.

ImageMagick no renderiza los trazos del SVG, así que se reproducen a mano sus trazados
(lienzo 32x32 → escala 32): fondo redondeado #0A0F14, escudo con borde rojo #E63946 y
marca de verificación blanca #F4F7F6. Resultado: escudo-1024.png.
"""
from PIL import Image, ImageDraw

K = 32  # 32 unidades del SVG × 32 = 1024 px
SS = 4  # sobremuestreo para bordes suaves


def bezier(p0, p1, p2, p3, n=40):
    """Puntos de una curva Bézier cúbica (las curvas laterales del escudo)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t ** 2; d = t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def main():
    s = K * SS
    img = Image.new("RGBA", (32 * s, 32 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Fondo: rect 32x32 con esquinas rx=6
    d.rounded_rectangle([0, 0, 32 * s - 1, 32 * s - 1], radius=6 * s, fill=(10, 15, 20, 255))
    # Escudo: M16 5 l8 3 v6 c0 5 -3.4 9.2 -8 11 c-4.6 -1.8 -8 -6 -8 -11 V8 z
    pts = [(16, 5), (24, 8), (24, 14)]
    pts += bezier((24, 14), (24, 19), (20.6, 23.2), (16, 25))[1:]
    pts += bezier((16, 25), (11.4, 23.2), (8, 19), (8, 14))[1:]
    pts += [(8, 8), (16, 5)]
    d.line([(x * s, y * s) for x, y in pts], fill=(230, 57, 70, 255), width=int(1.6 * s), joint="curve")
    # Marca: M12 16 l3 3 5 -6 (trazo 1.8, extremos redondeados)
    chk = [(12 * s, 16 * s), (15 * s, 19 * s), (20 * s, 13 * s)]
    w = int(1.8 * s)
    d.line(chk, fill=(244, 247, 246, 255), width=w, joint="curve")
    for x, y in (chk[0], chk[-1]):
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=(244, 247, 246, 255))
    img.resize((1024, 1024), Image.LANCZOS).save("escudo-1024.png")


if __name__ == "__main__":
    main()
