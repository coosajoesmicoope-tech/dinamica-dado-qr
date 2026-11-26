#!/usr/bin/env python3
"""
Genera Códigos QR transparentes con el LOGO OFICIAL en el centro:
"COOSAJO R.L. es MICOOPE - La magia de Compartir"
- Fondo 100% transparente
- Error Correction HIGH (soporta hasta 30% de cobertura sin perder legibilidad)
- Badge central con borde neón protegiendo el logo
- Plantilla imprimible en alta resolución para las 6 caras del dado
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.append(os.path.dirname(__file__))
from qrcodegen import QrCode, QrSegment


def draw_diamond_star(draw, cx, cy, size, fill):
    points = [
        (cx, cy - size),
        (cx + size * 0.25, cy - size * 0.25),
        (cx + size, cy),
        (cx + size * 0.25, cy + size * 0.25),
        (cx, cy + size),
        (cx - size * 0.25, cy + size * 0.25),
        (cx - size, cy),
        (cx - size * 0.25, cy - size * 0.25),
    ]
    draw.polygon(points, fill=fill)


def get_cropped_logo(base_dir):
    logo_path = os.path.join(base_dir, "logo_coosajo.png")
    if not os.path.exists(logo_path):
        return None
    raw = Image.open(logo_path)
    bbox = raw.getbbox()
    if bbox:
        return raw.crop(bbox)
    return raw


def generate_qr_with_logo(
    text: str,
    label: str,
    output_path: str,
    logo_img=None,
    dark_color=(0, 56, 175, 255),
    accent_color=(0, 210, 35, 255),
    img_size=1024,
    show_label=True,
    white_theme=False,
):
    # Usar minversion=4 y HIGH ECC para tener densidad suficiente y tolerar el logo
    segs = QrSegment.make_segments(text)
    qr = QrCode.encode_segments(segs, QrCode.Ecc.HIGH, minversion=4)
    modules_count = qr.size

    img = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = int(img_size * 0.08)
    qr_draw_size = img_size - 2 * margin - (int(img_size * 0.12) if show_label else 0)
    module_size = qr_draw_size / modules_count

    def is_finder(r, c):
        return (r < 7 and c < 7) or (r < 7 and c >= modules_count - 7) or (r >= modules_count - 7 and c < 7)

    # Dibujar módulos
    for r in range(modules_count):
        for c in range(modules_count):
            if qr.get_module(c, r):
                x = margin + c * module_size
                y = margin + r * module_size

                if white_theme:
                    color = (255, 255, 255, 255)
                elif is_finder(r, c):
                    color = accent_color if (r in (2, 3, 4) and c in (2, 3, 4)) or \
                                            (r in (2, 3, 4) and c in (modules_count - 5, modules_count - 4, modules_count - 3)) or \
                                            (r in (modules_count - 5, modules_count - 4, modules_count - 3) and c in (2, 3, 4)) else dark_color
                else:
                    ratio = (r + c) / (modules_count * 2)
                    color = accent_color if ratio > 0.82 else dark_color

                pad = module_size * 0.08
                draw.rounded_rectangle(
                    [x + pad, y + pad, x + module_size - pad, y + module_size - pad],
                    radius=module_size * 0.28,
                    fill=color,
                )

    # Estrellas de 4 puntas decorativas
    star_size = margin * 0.38
    star_color = (255, 255, 255, 255) if white_theme else accent_color
    draw_diamond_star(draw, margin * 0.5, margin * 0.5, star_size, (255, 255, 255, 240))
    draw_diamond_star(draw, img_size - margin * 0.5, margin * 0.5, star_size, star_color)
    draw_diamond_star(draw, margin * 0.5, margin + qr_draw_size + margin * 0.4, star_size, star_color)
    draw_diamond_star(draw, img_size - margin * 0.5, margin + qr_draw_size + margin * 0.4, star_size, (255, 255, 255, 240))

    # INSERTAR LOGO EN EL CENTRO
    if logo_img:
        # Calcular dimensiones del badge central
        badge_w = int(qr_draw_size * 0.36)
        badge_h = int(badge_w / (logo_img.width / logo_img.height)) + 24
        badge_x = margin + (qr_draw_size - badge_w) // 2
        badge_y = margin + (qr_draw_size - badge_h) // 2

        # Fondo del badge (Azul oscuro o blanco)
        badge_bg = (1, 16, 52, 255) if not white_theme else (1, 18, 55, 255)
        badge_border = accent_color if not white_theme else (255, 255, 255, 255)

        draw.rounded_rectangle(
            [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
            radius=16,
            fill=badge_bg,
            outline=badge_border,
            width=3,
        )

        # Ajustar logo adentro con padding
        pad = 10
        inner_w = badge_w - pad * 2
        inner_h = badge_h - pad * 2
        ratio = logo_img.width / logo_img.height

        tw = inner_w
        th = int(tw / ratio)
        if th > inner_h:
            th = inner_h
            tw = int(th * ratio)

        logo_resized = logo_img.resize((tw, th), Image.LANCZOS)
        lx = badge_x + (badge_w - tw) // 2
        ly = badge_y + (badge_h - th) // 2
        img.paste(logo_resized, (lx, ly), logo_resized)

    # Etiqueta de texto abajo
    if show_label and label:
        text_y = margin + qr_draw_size + int(img_size * 0.02)
        font_size = int(img_size * 0.052)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_x = (img_size - text_w) / 2

        pill_pad_x = 28
        pill_pad_y = 12
        pill_rect = [
            text_x - pill_pad_x,
            text_y - pill_pad_y,
            text_x + text_w + pill_pad_x,
            text_y + (bbox[3] - bbox[1]) + pill_pad_y,
        ]

        pill_bg = (2, 20, 75, 230) if not white_theme else (255, 255, 255, 230)
        text_color = (0, 240, 60, 255) if not white_theme else (0, 40, 140, 255)

        draw.rounded_rectangle(pill_rect, radius=18, fill=pill_bg, outline=accent_color if not white_theme else dark_color, width=3)
        draw.text((text_x, text_y), label, fill=text_color, font=font)

    img.save(output_path, "PNG")
    print(f"✓ Creado QR con logo: {output_path}")
    return img


def generate_printable_sheet_with_logo(assets_dir, base_dir, logo_img):
    sheet_w, sheet_h = 2480, 3508
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    bg_path = os.path.join(base_dir, "fondo_estilo.jpg")
    base_bg = Image.open(bg_path).convert("RGBA")

    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 60)
        sub_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 32)
        face_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 36)
    except Exception:
        title_font = sub_font = face_font = ImageFont.load_default()

    # Encabezado con el Logo Corporativo
    if logo_img:
        logo_head_w = 480
        logo_head_h = int(logo_head_w / (logo_img.width / logo_img.height))
        # Fondo azul detrás del logo en el encabezado
        draw.rounded_rectangle([(sheet_w - logo_head_w) // 2 - 20, 40, (sheet_w + logo_head_w) // 2 + 20, 40 + logo_head_h + 20], radius=16, fill=(1, 20, 65, 255), outline=(0, 230, 38, 255), width=3)
        head_logo = logo_img.resize((logo_head_w, logo_head_h), Image.LANCZOS)
        sheet.paste(head_logo, ((sheet_w - logo_head_w) // 2, 50), head_logo)

    draw.text((sheet_w // 2 - 460, 260), "PLANTILLA PARA DADO INTERACTIVO", fill=(0, 40, 140, 255), font=title_font)
    draw.text((sheet_w // 2 - 470, 335), "Recorta los 6 cuadrados y pégalos en las 6 caras de tu dado.", fill=(60, 80, 110, 255), font=sub_font)

    caras = [
        ("CARA 1: ¡PREMIO!", "qr_1_premio.png", (255, 204, 0)),
        ("CARA 2: PROMOCIONAL", "qr_3_promocional.png", (0, 230, 38)),
        ("CARA 3: GRACIAS", "qr_2_gracias_por_participar.png", (255, 255, 255)),
        ("CARA 4: GRACIAS", "qr_2_gracias_por_participar.png", (255, 255, 255)),
        ("CARA 5: GRACIAS", "qr_2_gracias_por_participar.png", (255, 255, 255)),
        ("CARA 6: GRACIAS", "qr_2_gracias_por_participar.png", (255, 255, 255)),
    ]

    card_size = 640
    cols = 2
    start_x = (sheet_w - (card_size * 2 + 160)) // 2
    start_y = 420

    for i, (titulo, qr_file, border_color) in enumerate(caras):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_size + 160)
        y = start_y + row * (card_size + 120)

        face_bg = base_bg.resize((card_size, card_size), Image.LANCZOS)
        sheet.paste(face_bg, (x, y))

        draw.rectangle([x, y, x + card_size, y + card_size], outline=(0, 230, 38, 255), width=5)
        draw.rectangle([x + 20, y + 16, x + card_size - 20, y + 75], fill=(0, 20, 70, 230))
        draw.text((x + 40, y + 24), titulo, fill=border_color, font=face_font)

        qr_white_file = qr_file.replace(".png", "_blanco.png")
        qr_img = Image.open(os.path.join(assets_dir, qr_white_file)).resize((card_size - 90, card_size - 90), Image.LANCZOS)
        sheet.paste(qr_img, (x + 45, y + 70), qr_img)

    sheet_out = os.path.join(assets_dir, "plantilla_imprimible_dado_6_caras.png")
    sheet.convert("RGB").save(sheet_out, quality=95)
    print(f"✓ Hoja imprimible con logo creada: {sheet_out}")


def main():
    base_dir = os.path.dirname(__file__)
    assets_dir = os.path.join(base_dir, "codigos_qr_generados")
    os.makedirs(assets_dir, exist_ok=True)

    logo_img = get_cropped_logo(base_dir)

    items = [
        ("PREMIO", "1. PREMIO", "qr_1_premio"),
        ("GRACIAS POR PARTICIPAR", "GRACIAS POR PARTICIPAR", "qr_2_gracias_por_participar"),
        ("PROMOCIONAL", "3. PROMOCIONAL", "qr_3_promocional"),
        ("https://coosajo.com/dinamica", "ESCANEA PARA JUGAR", "qr_maestro_dinamica"),
    ]

    print("--- Regenerando Códigos QR con el Logo de COOSAJO / MICOOPE ---")
    for text, label, filename in items:
        # Versión color con logo
        png_path = os.path.join(assets_dir, f"{filename}.png")
        generate_qr_with_logo(text, label, png_path, logo_img=logo_img, show_label=True)

        # Versión blanca con logo
        png_white_path = os.path.join(assets_dir, f"{filename}_blanco.png")
        generate_qr_with_logo(text, label, png_white_path, logo_img=logo_img, show_label=True, white_theme=True)

    generate_printable_sheet_with_logo(assets_dir, base_dir, logo_img)
    print("\n¡Todos los códigos QR y la plantilla del dado tienen el logo integrado!")


if __name__ == "__main__":
    main()
