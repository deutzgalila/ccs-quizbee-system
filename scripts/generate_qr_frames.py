#!/usr/bin/env python3
"""
Generate modern, minimal, elegant frames for the Post-Quiz Bee Evaluation QR Code.
Outputs:
  - public/images/evaluation_qr_standee_dark.png  (1200x1700 portrait)
  - public/images/evaluation_qr_standee_light.png (1200x1700 portrait)
  - public/images/evaluation_qr_stage_dark.png    (1920x1080 widescreen)
  - public/images/evaluation_qr_stage_light.png   (1920x1080 widescreen)
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SOURCE_QR_PATH = "/home/javvii/.gemini/antigravity-cli/brain/bd31248a-d904-4d16-a417-d5598b3683fd/.user_uploaded/uploaded_media_1792226952716.png"
CCS_LOGO_PATH = "public/logo/ccs-logo.png"
OUTPUT_DIR = "public/images"
FALLBACK_URL = "https://q.me-qr.com/43fo17lw"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Typography paths
FONT_BOLD = "/usr/share/fonts/TTF/Montserrat-Bold.ttf"
FONT_SEMIBOLD = "/usr/share/fonts/TTF/Montserrat-SemiBold.ttf"
FONT_MEDIUM = "/usr/share/fonts/TTF/Montserrat-Medium.ttf"
FONT_REGULAR = "/usr/share/fonts/TTF/Montserrat-Regular.ttf"
FONT_MONO = "/usr/share/fonts/TTF/JetBrainsMonoNLNerdFont-Medium.ttf"

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def draw_corner_reticles(draw, box, length=32, thickness=4, color=(16, 185, 129, 255), offset=14):
    """Draw high-tech minimal camera viewfinder corner brackets."""
    x1, y1, x2, y2 = box
    x1 -= offset
    y1 -= offset
    x2 += offset
    y2 += offset
    
    # Top-Left
    draw.line([(x1, y1), (x1 + length, y1)], fill=color, width=thickness)
    draw.line([(x1, y1), (x1, y1 + length)], fill=color, width=thickness)
    
    # Top-Right
    draw.line([(x2, y1), (x2 - length, y1)], fill=color, width=thickness)
    draw.line([(x2, y1), (x2 - length, y1 + length)], fill=color, width=thickness)
    # Correct top-right vertical line
    draw.line([(x2, y1), (x2, y1 + length)], fill=color, width=thickness)
    
    # Bottom-Left
    draw.line([(x1, y2), (x1 + length, y2)], fill=color, width=thickness)
    draw.line([(x1, y2), (x1, y2 - length)], fill=color, width=thickness)
    
    # Bottom-Right
    draw.line([(x2, y2), (x2 - length, y2)], fill=color, width=thickness)
    draw.line([(x2, y2), (x2, y2 - length)], fill=color, width=thickness)

def create_radial_glow(width, height, center_x, center_y, radius, color):
    """Create a soft radial ambient light aura."""
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    r_color = color[:3]
    max_alpha = color[3] if len(color) > 3 else 255
    
    steps = 30
    for i in range(steps, 0, -1):
        step_radius = radius * (i / steps)
        alpha = int(max_alpha * (1 - (i / steps)) ** 1.8)
        bbox = [center_x - step_radius, center_y - step_radius, center_x + step_radius, center_y + step_radius]
        draw.ellipse(bbox, fill=(*r_color, alpha))
        
    return glow.filter(ImageFilter.GaussianBlur(radius // 5))

def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def draw_pill(draw, x, y, text, font, bg_color, text_color, border_color=None, pad_x=24, pad_y=10, radius=20):
    tw, th = text_size(draw, text, font)
    w = tw + pad_x * 2
    h = th + pad_y * 2
    box = [x - w // 2, y - h // 2, x + w // 2, y + h // 2]
    draw.rounded_rectangle(box, radius=radius, fill=bg_color, outline=border_color, width=1 if border_color else 0)
    draw.text((x - tw // 2, y - th // 2 - 2), text, font=font, fill=text_color)
    return box

# ==========================================
# 1. Vertical Standee (1200 x 1700)
# ==========================================
def render_standee(dark_mode=True):
    W, H = 1200, 1700
    canvas = Image.new("RGBA", (W, H), (11, 15, 25, 255) if dark_mode else (248, 250, 252, 255))
    
    # Ambient glows for dark mode
    if dark_mode:
        glow_maroon = create_radial_glow(W, H, 200, 200, 450, (136, 19, 55, 60))
        glow_emerald = create_radial_glow(W, H, 600, 880, 500, (16, 185, 129, 45))
        canvas = Image.alpha_composite(canvas, glow_maroon)
        canvas = Image.alpha_composite(canvas, glow_emerald)
        
        # Subtle grid dots or lines
        grid_draw = ImageDraw.Draw(canvas)
        dot_color = (255, 255, 255, 12)
        for gx in range(40, W, 40):
            for gy in range(40, H, 40):
                grid_draw.point((gx, gy), fill=dot_color)

    draw = ImageDraw.Draw(canvas)

    # Theme colors
    text_primary = (248, 250, 252, 255) if dark_mode else (15, 23, 42, 255)
    text_secondary = (148, 163, 184, 255) if dark_mode else (100, 116, 139, 255)
    text_accent = (52, 211, 153, 255) if dark_mode else (5, 150, 105, 255)
    card_bg = (20, 27, 45, 230) if dark_mode else (255, 255, 255, 255)
    card_border = (45, 58, 86, 255) if dark_mode else (226, 232, 240, 255)
    reticle_color = (16, 185, 129, 255) if dark_mode else (5, 150, 105, 255)
    pill_bg = (136, 19, 55, 220) if dark_mode else (253, 242, 248, 255)
    pill_border = (244, 63, 94, 180) if dark_mode else (244, 114, 182, 180)
    pill_text = (255, 228, 230, 255) if dark_mode else (159, 18, 57, 255)

    # Fonts
    font_badge = load_font(FONT_SEMIBOLD, 20)
    font_title = load_font(FONT_BOLD, 46)
    font_subtitle = load_font(FONT_MEDIUM, 22)
    font_btn = load_font(FONT_BOLD, 20)
    font_mono = load_font(FONT_MONO, 19)
    font_chip = load_font(FONT_SEMIBOLD, 18)
    font_footer = load_font(FONT_MEDIUM, 18)
    font_footer_sub = load_font(FONT_REGULAR, 15)

    # 1. Header Section
    header_y = 110
    
    # Optional CCS Logo badge
    if os.path.exists(CCS_LOGO_PATH):
        try:
            logo = Image.open(CCS_LOGO_PATH).convert("RGBA")
            logo = logo.resize((64, 64), Image.Resampling.LANCZOS)
            canvas.paste(logo, (W // 2 - 280, header_y - 20), logo)
        except Exception as e:
            print("Logo load error:", e)

    draw_pill(draw, W // 2 + 30, header_y + 12, "OLFU COLLEGE OF COMPUTER STUDIES • IT OLYMPICS 2026",
              font_badge, pill_bg, pill_text, pill_border, pad_x=22, pad_y=8, radius=18)

    # Title
    title_text = "POST-QUIZ BEE EVALUATION"
    tw, th = text_size(draw, title_text, font_title)
    draw.text((W // 2 - tw // 2, header_y + 65), title_text, font=font_title, fill=text_primary)

    # Subtitle
    sub_text = "Help us elevate the platform — your feedback shapes the next integration"
    sw, sh = text_size(draw, sub_text, font_subtitle)
    draw.text((W // 2 - sw // 2, header_y + 128), sub_text, font=font_subtitle, fill=text_secondary)

    # 2. Hero QR Card Container
    card_w, card_h = 760, 890
    card_x1 = (W - card_w) // 2
    card_y1 = header_y + 185
    card_x2 = card_x1 + card_w
    card_y2 = card_y1 + card_h

    # Card background with rounded corners
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=28, fill=card_bg, outline=card_border, width=2)

    # Pristine White QR inner canvas (generous quiet zone)
    qr_canvas_size = 600
    qr_cx = W // 2
    qr_cy = card_y1 + 40 + qr_canvas_size // 2
    qr_box = [qr_cx - qr_canvas_size // 2, qr_cy - qr_canvas_size // 2,
              qr_cx + qr_canvas_size // 2, qr_cy + qr_canvas_size // 2]
    
    draw.rounded_rectangle(qr_box, radius=24, fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)

    # Paste Source QR Code
    if os.path.exists(SOURCE_QR_PATH):
        qr_img = Image.open(SOURCE_QR_PATH).convert("RGBA")
        qr_size = 520
        qr_scaled = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        canvas.paste(qr_scaled, (qr_cx - qr_size // 2, qr_cy - qr_size // 2), qr_scaled)

    # Draw sleek viewfinder corner reticles around the QR box
    draw_corner_reticles(draw, qr_box, length=38, thickness=4, color=reticle_color, offset=14)

    # "POINT CAMERA TO SCAN" Action Pill
    btn_y = card_y1 + 700
    btn_bg = (16, 185, 129, 230) if dark_mode else (15, 23, 42, 240)
    btn_text_color = (255, 255, 255, 255)
    draw_pill(draw, W // 2, btn_y, "SCAN WITH YOUR PHONE CAMERA", font_btn, btn_bg, btn_text_color, pad_x=28, pad_y=12, radius=22)

    # Fallback Direct Link
    link_y = btn_y + 55
    link_text = f"Direct link: {FALLBACK_URL}"
    lw, lh = text_size(draw, link_text, font_mono)
    # Subtle link box
    draw.rounded_rectangle([W // 2 - lw // 2 - 16, link_y - 4, W // 2 + lw // 2 + 16, link_y + lh + 4],
                           radius=8, fill=(15, 23, 42, 160) if dark_mode else (241, 245, 249, 255))
    draw.text((W // 2 - lw // 2, link_y), link_text, font=font_mono, fill=text_accent)

    # 3. Highlights Row (3 Badges)
    chips_y = card_y2 + 65
    chips = [
        "2-3 Mins to Complete",
        "100% Anonymous",
        "10 Short Questions"
    ]
    chip_w_est = 260
    gap = 24
    total_chips_w = len(chips) * chip_w_est + (len(chips) - 1) * gap
    start_cx = (W - total_chips_w) // 2 + chip_w_est // 2

    chip_bg = (24, 33, 54, 200) if dark_mode else (255, 255, 255, 255)
    chip_border = (45, 58, 86, 200) if dark_mode else (226, 232, 240, 255)
    chip_text_col = text_primary

    for idx, c_text in enumerate(chips):
        cx = start_cx + idx * (chip_w_est + gap)
        draw_pill(draw, cx, chips_y, c_text, font_chip, chip_bg, chip_text_col, chip_border, pad_x=20, pad_y=10, radius=16)

    # 4. Footer Section
    divider_y = H - 150
    draw.line([(W // 2 - 400, divider_y), (W // 2 + 400, divider_y)],
              fill=(45, 58, 86, 120) if dark_mode else (226, 232, 240, 255), width=1)

    foot_text = "FATIMA QUIZBEE ENGINE • ITPM 311 PROJECT INTEGRATION"
    fw, fh = text_size(draw, foot_text, font_footer)
    draw.text((W // 2 - fw // 2, divider_y + 24), foot_text, font=font_footer, fill=text_secondary)

    foot_sub = "Our Lady of Fatima University — College of Computer Studies"
    fsw, fsh = text_size(draw, foot_sub, font_footer_sub)
    draw.text((W // 2 - fsw // 2, divider_y + 54), foot_sub, font=font_footer_sub, fill=(100, 116, 139, 200))

    # Save
    filename = "evaluation_qr_standee_dark.png" if dark_mode else "evaluation_qr_standee_light.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    canvas.save(filepath, "PNG", dpi=(300, 300))
    print(f"Saved: {filepath}")
    return filepath


# ==========================================
# 2. Widescreen Stage Projector (1920 x 1080)
# ==========================================
def render_stage(dark_mode=True):
    W, H = 1920, 1080
    canvas = Image.new("RGBA", (W, H), (10, 14, 26, 255) if dark_mode else (248, 250, 252, 255))
    
    # Ambient glows for dark mode
    if dark_mode:
        glow_maroon = create_radial_glow(W, H, 300, 300, 600, (136, 19, 55, 55))
        glow_emerald = create_radial_glow(W, H, 1450, 540, 600, (16, 185, 129, 50))
        canvas = Image.alpha_composite(canvas, glow_maroon)
        canvas = Image.alpha_composite(canvas, glow_emerald)
        
        # Subtle grid dots
        grid_draw = ImageDraw.Draw(canvas)
        dot_color = (255, 255, 255, 10)
        for gx in range(40, W, 40):
            for gy in range(40, H, 40):
                grid_draw.point((gx, gy), fill=dot_color)

    draw = ImageDraw.Draw(canvas)

    # Theme colors
    text_primary = (248, 250, 252, 255) if dark_mode else (15, 23, 42, 255)
    text_secondary = (148, 163, 184, 255) if dark_mode else (100, 116, 139, 255)
    text_accent = (52, 211, 153, 255) if dark_mode else (5, 150, 105, 255)
    card_bg = (20, 27, 45, 230) if dark_mode else (255, 255, 255, 255)
    card_border = (45, 58, 86, 255) if dark_mode else (226, 232, 240, 255)
    reticle_color = (16, 185, 129, 255) if dark_mode else (5, 150, 105, 255)
    pill_bg = (136, 19, 55, 220) if dark_mode else (253, 242, 248, 255)
    pill_border = (244, 63, 94, 180) if dark_mode else (244, 114, 182, 180)
    pill_text = (255, 228, 230, 255) if dark_mode else (159, 18, 57, 255)

    # Fonts
    font_badge = load_font(FONT_SEMIBOLD, 18)
    font_hero = load_font(FONT_BOLD, 52)
    font_hero_sub = load_font(FONT_MEDIUM, 24)
    font_bullet_title = load_font(FONT_BOLD, 20)
    font_bullet_desc = load_font(FONT_REGULAR, 18)
    font_btn = load_font(FONT_BOLD, 20)
    font_mono = load_font(FONT_MONO, 18)
    font_notice = load_font(FONT_MEDIUM, 16)
    font_footer = load_font(FONT_MEDIUM, 17)

    # Left Column Layout (X: 130 to 1020)
    col_x = 130
    top_y = 120

    # Badge Row
    if os.path.exists(CCS_LOGO_PATH):
        try:
            logo = Image.open(CCS_LOGO_PATH).convert("RGBA")
            logo = logo.resize((52, 52), Image.Resampling.LANCZOS)
            canvas.paste(logo, (col_x, top_y - 12), logo)
        except Exception as e:
            print("Logo error:", e)

    draw_pill(draw, col_x + 320, top_y + 14, "OLFU IT OLYMPICS 2026 • OFFICIAL EVALUATION",
              font_badge, pill_bg, pill_text, pill_border, pad_x=20, pad_y=8, radius=16)

    # Main Hero Title
    hero_title = "Participant Evaluation"
    draw.text((col_x, top_y + 65), hero_title, font=font_hero, fill=text_primary)

    # Hero Subtitle
    hero_sub = "Help us elevate the platform — your feedback shapes the next integration."
    draw.text((col_x, top_y + 140), hero_sub, font=font_hero_sub, fill=text_secondary)

    # Bullet / Value props
    bullets = [
        ("⚡ Quick & Anonymous", "Takes only 2-3 minutes. All responses are 100% confidential."),
        ("🎯 Real-Time Experience", "Rate interface clarity, countdown pacing, and buzzer responsiveness."),
        ("💡 Suggest Enhancements", "Directly guide the development roadmap for IT Olympics 2027.")
    ]

    bullet_start_y = top_y + 220
    for i, (b_title, b_desc) in enumerate(bullets):
        by = bullet_start_y + i * 82
        # Bullet indicator box
        draw.rounded_rectangle([col_x, by, col_x + 36, by + 36], radius=10,
                               fill=(16, 185, 129, 40) if dark_mode else (241, 245, 249, 255),
                               outline=reticle_color, width=1)
        # Checkmark
        draw.line([(col_x + 10, by + 18), (col_x + 16, by + 24), (col_x + 26, by + 12)],
                  fill=reticle_color, width=3)
        # Text
        draw.text((col_x + 52, by + 1), b_title, font=font_bullet_title, fill=text_primary)
        draw.text((col_x + 52, by + 27), b_desc, font=font_bullet_desc, fill=text_secondary)

    # Workstation isolate notice & fallback link
    notice_box_y = bullet_start_y + 275
    nb_w, nb_h = 760, 115
    draw.rounded_rectangle([col_x, notice_box_y, col_x + nb_w, notice_box_y + nb_h],
                           radius=16,
                           fill=(18, 25, 41, 200) if dark_mode else (241, 245, 249, 255),
                           outline=(45, 58, 86, 180) if dark_mode else (226, 232, 240, 255), width=1)

    notice_icon_text = "🔒 Lab Network Isolation Notice:"
    draw.text((col_x + 24, notice_box_y + 18), notice_icon_text, font=font_notice, fill=(251, 191, 36, 255))
    notice_sub = "Lab workstations are isolated from WAN. Please scan using your mobile phone camera."
    draw.text((col_x + 24, notice_box_y + 44), notice_sub, font=font_notice, fill=text_secondary)
    
    direct_link_text = f"Direct browser link: {FALLBACK_URL}"
    draw.text((col_x + 24, notice_box_y + 74), direct_link_text, font=font_mono, fill=text_accent)

    # Right Column: Framed QR Card (X: 1150 to 1770)
    card_w, card_h = 620, 770
    card_x1 = 1170
    card_y1 = 120
    card_x2 = card_x1 + card_w
    card_y2 = card_y1 + card_h

    # Card backdrop
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=28, fill=card_bg, outline=card_border, width=2)

    # Pristine white QR box
    qr_canvas_size = 500
    qr_cx = card_x1 + card_w // 2
    qr_cy = card_y1 + 40 + qr_canvas_size // 2
    qr_box = [qr_cx - qr_canvas_size // 2, qr_cy - qr_canvas_size // 2,
              qr_cx + qr_canvas_size // 2, qr_cy + qr_canvas_size // 2]
    draw.rounded_rectangle(qr_box, radius=22, fill=(255, 255, 255, 255), outline=(226, 232, 240, 255), width=2)

    # Paste QR
    if os.path.exists(SOURCE_QR_PATH):
        qr_img = Image.open(SOURCE_QR_PATH).convert("RGBA")
        qr_size = 430
        qr_scaled = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        canvas.paste(qr_scaled, (qr_cx - qr_size // 2, qr_cy - qr_size // 2), qr_scaled)

    # Viewfinder reticles
    draw_corner_reticles(draw, qr_box, length=34, thickness=4, color=reticle_color, offset=14)

    # Card bottom button
    btn_y = card_y1 + 610
    btn_bg = (16, 185, 129, 230) if dark_mode else (15, 23, 42, 240)
    draw_pill(draw, qr_cx, btn_y, "POINT CAMERA TO SCAN", font_btn, btn_bg, (255, 255, 255, 255), pad_x=28, pad_y=12, radius=20)

    # Status tag under button
    tag_text = "● Ready to Scan • No App Required"
    tw, th = text_size(draw, tag_text, font_notice)
    draw.text((qr_cx - tw // 2, btn_y + 46), tag_text, font=font_notice, fill=text_secondary)

    # Bottom Full-width Footer Bar
    bar_y = H - 75
    draw.line([(100, bar_y), (W - 100, bar_y)], fill=(45, 58, 86, 120) if dark_mode else (226, 232, 240, 255), width=1)
    
    foot_left = "Fatima QuizBee Engine • ITPM 311 Project Integration"
    draw.text((120, bar_y + 24), foot_left, font=font_footer, fill=text_secondary)

    foot_right = "Our Lady of Fatima University — College of Computer Studies"
    rw, rh = text_size(draw, foot_right, font_footer)
    draw.text((W - 120 - rw, bar_y + 24), foot_right, font=font_footer, fill=text_secondary)

    # Save
    filename = "evaluation_qr_stage_dark.png" if dark_mode else "evaluation_qr_stage_light.png"
    filepath = os.path.join(OUTPUT_DIR, filename)
    canvas.save(filepath, "PNG", dpi=(300, 300))
    print(f"Saved: {filepath}")
    return filepath

if __name__ == "__main__":
    print("Generating framed QR assets...")
    f1 = render_standee(dark_mode=True)
    f2 = render_standee(dark_mode=False)
    f3 = render_stage(dark_mode=True)
    f4 = render_stage(dark_mode=False)
    print("All framed QR assets generated successfully!")
