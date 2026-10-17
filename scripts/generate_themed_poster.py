#!/usr/bin/env python3
"""
Generate official-theme Post-Quiz Bee Evaluation Posters for OLFU IT Olympics 2026.
Matches the official visual theme of CCS Days 2026 (crimson velvet, gold arches, wax seals).
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SOURCE_QR = "/home/javvii/.gemini/antigravity-cli/brain/bd31248a-d904-4d16-a417-d5598b3683fd/.user_uploaded/uploaded_media_1792226952716.png"
THEME_IM1 = "/home/javvii/.gemini/antigravity-cli/brain/bd31248a-d904-4d16-a417-d5598b3683fd/.user_uploaded/uploaded_media_1_1792227781305.png"
THEME_IM2 = "/home/javvii/.gemini/antigravity-cli/brain/bd31248a-d904-4d16-a417-d5598b3683fd/.user_uploaded/uploaded_media_2_1792227781305.png"
OUTPUT_DIR = "public/images"
FALLBACK_URL = "https://q.me-qr.com/43fo17lw"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Font paths
FONT_CINZEL_BOLD = "assets/fonts/Cinzel-Bold.ttf"
FONT_CINZEL_DEC = "assets/fonts/CinzelDecorative-Bold.ttf"
FONT_PLAYFAIR_BOLD = "assets/fonts/PlayfairDisplay-Bold.ttf"
FONT_ALEX_BRUSH = "assets/fonts/AlexBrush-Regular.ttf"
FONT_GREAT_VIBES = "assets/fonts/GreatVibes-Regular.ttf"
FONT_MONTSERRAT_BOLD = "/usr/share/fonts/TTF/Montserrat-Bold.ttf"
FONT_MONTSERRAT_SEMIBOLD = "/usr/share/fonts/TTF/Montserrat-SemiBold.ttf"
FONT_MONTSERRAT_MEDIUM = "/usr/share/fonts/TTF/Montserrat-Medium.ttf"
FONT_MONO = "/usr/share/fonts/TTF/JetBrainsMonoNLNerdFont-Medium.ttf"

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception as e:
        print(f"Font load error ({path}):", e)
        return ImageFont.load_default()

def text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def draw_corner_reticles(draw, box, length=32, thickness=4, color=(212, 175, 55, 255), offset=12):
    """Draw elegant gold corner viewfinder brackets."""
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
    draw.line([(x2, y1), (x2, y1 + length)], fill=color, width=thickness)
    # Bottom-Left
    draw.line([(x1, y2), (x1 + length, y2)], fill=color, width=thickness)
    draw.line([(x1, y2), (x1, y2 - length)], fill=color, width=thickness)
    # Bottom-Right
    draw.line([(x2, y2), (x2 - length, y2)], fill=color, width=thickness)
    draw.line([(x2, y2), (x2, y2 - length)], fill=color, width=thickness)

def draw_pill(draw, x, y, text, font, bg_color, text_color, border_color=None, pad_x=20, pad_y=8, radius=16):
    tw, th = text_size(draw, text, font)
    w = tw + pad_x * 2
    h = th + pad_y * 2
    box = [x - w // 2, y - h // 2, x + w // 2, y + h // 2]
    draw.rounded_rectangle(box, radius=radius, fill=bg_color, outline=border_color, width=1 if border_color else 0)
    draw.text((x - tw // 2, y - th // 2 - 2), text, font=font, fill=text_color)
    return box

# ==============================================================================
# POSTER 1: The Royal Scalloped Parchment Ticket with Red Wax Seals (Image 2 style)
# ==============================================================================
def render_parchment_poster():
    print("Generating Parchment Poster (Official Theme)...")
    # Base canvas dimensions: 1200 x 1500 (4:5 vertical poster)
    W, H = 1200, 1500
    
    # 1. Prepare Base Backdrop from Image 1
    im1 = Image.open(THEME_IM1).convert("RGBA")
    backdrop = im1.resize((W, H), Image.Resampling.LANCZOS)
    
    # 2. Extract Red Wax Seal from Image 2
    im2 = Image.open(THEME_IM2).convert("RGBA")
    # Left wax seal is at (230, 270, 480, 520) in im2
    raw_seal = im2.crop((230, 270, 480, 520))
    sw, sh = raw_seal.size
    seal_mask = Image.new("L", (sw, sh), 0)
    s_draw = ImageDraw.Draw(seal_mask)
    s_draw.ellipse([10, 10, sw - 10, sh - 10], fill=255)
    seal_mask = seal_mask.filter(ImageFilter.GaussianBlur(3))
    raw_seal.putalpha(seal_mask)
    seal_img = raw_seal.resize((120, 120), Image.Resampling.LANCZOS)
    
    # 3. Create Scalloped Ivory Parchment Card
    card_w, card_h = 920, 1080
    card_x = (W - card_w) // 2
    card_y = 230
    
    # Card surface
    card = Image.new("RGBA", (card_w, card_h), (252, 250, 246, 255))
    c_draw = ImageDraw.Draw(card)
    
    # Stamp scalloped mask
    c_mask = Image.new("L", (card_w, card_h), 255)
    m_draw = ImageDraw.Draw(c_mask)
    hole_r = 14
    step = 36
    # Left and right scalloped edges
    for py in range(36, card_h - 20, step):
        m_draw.ellipse([-hole_r, py - hole_r, hole_r, py + hole_r], fill=0)
        m_draw.ellipse([card_w - hole_r, py - hole_r, card_w + hole_r, py + hole_r], fill=0)
    # Top and bottom scalloped edges
    for px in range(36, card_w - 20, step):
        m_draw.ellipse([px - hole_r, -hole_r, px + hole_r, hole_r], fill=0)
        m_draw.ellipse([px - hole_r, card_h - hole_r, px + hole_r, card_h + hole_r], fill=0)
        
    card.putalpha(c_mask)
    
    # Draw ornate inner hairline border inside card
    card_draw = ImageDraw.Draw(card)
    border_inset = 28
    gold_border = (197, 160, 89, 220)
    card_draw.rectangle([border_inset, border_inset, card_w - border_inset, card_h - border_inset],
                        outline=gold_border, width=2)
    card_draw.rectangle([border_inset + 4, border_inset + 4, card_w - border_inset - 4, card_h - border_inset - 4],
                        outline=(197, 160, 89, 100), width=1)
    
    # Corner ornaments on card
    draw_corner_reticles(card_draw,
                         [border_inset + 8, border_inset + 8, card_w - border_inset - 8, card_h - border_inset - 8],
                         length=24, thickness=2, color=(197, 160, 89, 220), offset=0)

    # 4. Content inside Parchment Card
    # Fonts
    f_badge = load_font(FONT_MONTSERRAT_SEMIBOLD, 15)
    f_title_main = load_font(FONT_CINZEL_BOLD, 42)
    f_script = load_font(FONT_ALEX_BRUSH, 48)
    f_tagline = load_font(FONT_CINZEL_BOLD, 19)
    f_cursive_sub = load_font(FONT_ALEX_BRUSH, 28)
    f_btn = load_font(FONT_MONTSERRAT_BOLD, 18)
    f_mono = load_font(FONT_MONO, 17)
    f_chip = load_font(FONT_MONTSERRAT_SEMIBOLD, 15)
    f_notice = load_font(FONT_MONTSERRAT_MEDIUM, 14)
    
    # Colors
    c_maroon = (112, 9, 35, 255)
    c_gold = (180, 130, 20, 255)
    c_gold_light = (212, 175, 55, 255)
    c_slate = (71, 85, 105, 255)
    
    # Badge: "COLLEGE OF COMPUTER STUDIES • ITPM 311"
    draw_pill(card_draw, card_w // 2, 60, "COLLEGE OF COMPUTER STUDIES • ITPM 311",
              f_badge, (244, 237, 226, 255), c_maroon, (212, 175, 55, 180), pad_x=18, pad_y=6, radius=12)

    # Title: "IT OLYMPICS 2026"
    t_text = "IT OLYMPICS 2026"
    tw, th = text_size(card_draw, t_text, f_title_main)
    # Subtle drop shadow for title
    card_draw.text((card_w // 2 - tw // 2 + 1, 95 + 1), t_text, font=f_title_main, fill=(212, 175, 55, 80))
    card_draw.text((card_w // 2 - tw // 2, 95), t_text, font=f_title_main, fill=c_maroon)
    
    # Script subtitle: "Participant Evaluation"
    s_text = "Participant Evaluation"
    sw, sh = text_size(card_draw, s_text, f_script)
    card_draw.text((card_w // 2 - sw // 2, 150), s_text, font=f_script, fill=c_gold)
    
    # Tagline: "THREE DECADES BEYOND THE CODE"
    tag_text = "✦  THREE DECADES BEYOND THE CODE  ✦"
    tgw, tgh = text_size(card_draw, tag_text, f_tagline)
    card_draw.text((card_w // 2 - tgw // 2, 218), tag_text, font=f_tagline, fill=(30, 41, 59, 255))
    
    sub_tag = "Innovation, Leadership, and Digital Excellence"
    stgw, stgh = text_size(card_draw, sub_tag, f_cursive_sub)
    card_draw.text((card_w // 2 - stgw // 2, 248), sub_tag, font=f_cursive_sub, fill=c_gold)
    
    # Thin divider
    card_draw.line([(card_w // 2 - 240, 290), (card_w // 2 + 240, 290)], fill=(212, 175, 55, 140), width=1)
    card_draw.polygon([(card_w // 2, 287), (card_w // 2 + 5, 290), (card_w // 2, 293), (card_w // 2 - 5, 290)], fill=c_gold)

    # QR Code Container
    qr_box_size = 470
    qr_cx = card_w // 2
    qr_cy = 315 + qr_box_size // 2
    qr_rect = [qr_cx - qr_box_size // 2, qr_cy - qr_box_size // 2,
               qr_cx + qr_box_size // 2, qr_cy + qr_box_size // 2]
    
    # High-contrast pure white inner card with gold border
    card_draw.rounded_rectangle(qr_rect, radius=18, fill=(255, 255, 255, 255),
                                outline=(212, 175, 55, 180), width=2)
    
    # Paste pristine QR code
    if os.path.exists(SOURCE_QR):
        qr_src = Image.open(SOURCE_QR).convert("RGBA")
        qr_disp_size = 410
        qr_scaled = qr_src.resize((qr_disp_size, qr_disp_size), Image.Resampling.LANCZOS)
        card.paste(qr_scaled, (qr_cx - qr_disp_size // 2, qr_cy - qr_disp_size // 2), qr_scaled)
        
    # Corner brackets around QR
    draw_corner_reticles(card_draw, qr_rect, length=32, thickness=3, color=(180, 130, 20, 255), offset=10)

    # Action Banner: "SCAN WITH YOUR PHONE CAMERA"
    btn_y = qr_cy + qr_box_size // 2 + 42
    draw_pill(card_draw, card_w // 2, btn_y, "POINT CAMERA TO SCAN",
              f_btn, c_maroon, (255, 255, 255, 255), (212, 175, 55, 200), pad_x=26, pad_y=11, radius=20)

    # Fallback Direct Link
    link_y = btn_y + 44
    link_text = f"Direct browser link: {FALLBACK_URL}"
    lw, lh = text_size(card_draw, link_text, f_mono)
    card_draw.rounded_rectangle([card_w // 2 - lw // 2 - 14, link_y - 4, card_w // 2 + lw // 2 + 14, link_y + lh + 4],
                                radius=8, fill=(244, 237, 226, 255), outline=(212, 175, 55, 120), width=1)
    card_draw.text((card_w // 2 - lw // 2, link_y), link_text, font=f_mono, fill=(180, 83, 9, 255))

    # Feature Chips (⚡ 2-3 Mins | 🔒 100% Anonymous | 🎯 10 Questions)
    chips_y = link_y + 45
    chips = ["⚡ 2-3 Minutes", "🔒 100% Anonymous", "🎯 10 Quick Questions"]
    c_w = 210
    c_gap = 14
    total_w = len(chips) * c_w + (len(chips) - 1) * c_gap
    start_x = (card_w - total_w) // 2 + c_w // 2
    for i, chip_txt in enumerate(chips):
        cx = start_x + i * (c_w + c_gap)
        draw_pill(card_draw, cx, chips_y, chip_txt, f_chip,
                  (255, 255, 255, 255), (51, 65, 85, 255), (226, 232, 240, 255), pad_x=14, pad_y=6, radius=12)

    # Lab network notice
    not_y = chips_y + 36
    not_text = "※ Lab workstations are isolated from WAN • Please scan with your personal smartphone"
    nw, nh = text_size(card_draw, not_text, f_notice)
    card_draw.text((card_w // 2 - nw // 2, not_y), not_text, font=f_notice, fill=(100, 116, 139, 255))

    # 5. Composite Card Drop Shadow onto Backdrop
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rectangle([card_x + 10, card_y + 16, card_x + card_w - 10, card_y + card_h + 16], fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    
    backdrop = Image.alpha_composite(backdrop, shadow)
    
    # 6. Paste Parchment Card onto Backdrop
    backdrop.paste(card, (card_x, card_y), card)
    
    # 7. Paste Wax Seals on Upper Left and Upper Right of Card
    backdrop.paste(seal_img, (card_x + 36, card_y + 36), seal_img)
    backdrop.paste(seal_img, (card_x + card_w - 36 - 120, card_y + 36), seal_img)

    # 8. Bottom Footer on Backdrop
    f_post_foot = load_font(FONT_CINZEL_BOLD, 17)
    f_post_sub = load_font(FONT_MONTSERRAT_MEDIUM, 14)
    b_draw = ImageDraw.Draw(backdrop)
    foot_1 = "OCTOBER 15-17, 2026  ✦  SAINT BENEDICT HALL"
    fw1, fh1 = text_size(b_draw, foot_1, f_post_foot)
    b_draw.text((W // 2 - fw1 // 2, H - 145), foot_1, font=f_post_foot, fill=(254, 243, 199, 240))
    
    foot_2 = "Fatima QuizBee Engine  •  ITPM 311 Project Integration  •  Our Lady of Fatima University"
    fw2, fh2 = text_size(b_draw, foot_2, f_post_sub)
    b_draw.text((W // 2 - fw2 // 2, H - 118), foot_2, font=f_post_sub, fill=(212, 175, 55, 200))

    # 9. Save Final Standalone Poster
    out_path = os.path.join(OUTPUT_DIR, "evaluation_poster_official_parchment.png")
    backdrop.save(out_path, "PNG", dpi=(300, 300))
    print(f"Parchment Poster successfully created: {out_path}")
    return out_path


# ==============================================================================
# POSTER 2: The Royal Baroque Gold Plaque on Crimson Velvet (Image 1 style)
# ==============================================================================
def render_baroque_poster():
    print("Generating Baroque Plaque Poster (Official Theme)...")
    W, H = 1200, 1500
    
    # Base Backdrop from Image 1
    im1 = Image.open(THEME_IM1).convert("RGBA")
    backdrop = im1.resize((W, H), Image.Resampling.LANCZOS)
    
    # Wax seal
    im2 = Image.open(THEME_IM2).convert("RGBA")
    raw_seal = im2.crop((230, 270, 480, 520))
    sw, sh = raw_seal.size
    seal_mask = Image.new("L", (sw, sh), 0)
    s_draw = ImageDraw.Draw(seal_mask)
    s_draw.ellipse([10, 10, sw - 10, sh - 10], fill=255)
    seal_mask = seal_mask.filter(ImageFilter.GaussianBlur(3))
    raw_seal.putalpha(seal_mask)
    seal_img = raw_seal.resize((110, 110), Image.Resampling.LANCZOS)

    # Frosted Obsidian / Crimson Plaque
    card_w, card_h = 920, 1080
    card_x = (W - card_w) // 2
    card_y = 230
    
    card = Image.new("RGBA", (card_w, card_h), (20, 6, 12, 235))
    card_draw = ImageDraw.Draw(card)
    
    # Double Gold Foil Border
    gold_outer = (220, 180, 70, 255)
    gold_inner = (197, 160, 89, 140)
    card_draw.rounded_rectangle([16, 16, card_w - 16, card_h - 16], radius=24, outline=gold_outer, width=3)
    card_draw.rounded_rectangle([24, 24, card_w - 24, card_h - 24], radius=20, outline=gold_inner, width=1)
    
    # Viewfinder Corner reticles
    draw_corner_reticles(card_draw, [32, 32, card_w - 32, card_h - 32], length=38, thickness=3, color=gold_outer, offset=0)

    # Fonts
    f_badge = load_font(FONT_MONTSERRAT_SEMIBOLD, 15)
    f_title_main = load_font(FONT_CINZEL_BOLD, 42)
    f_script = load_font(FONT_ALEX_BRUSH, 48)
    f_tagline = load_font(FONT_CINZEL_BOLD, 19)
    f_cursive_sub = load_font(FONT_ALEX_BRUSH, 28)
    f_btn = load_font(FONT_MONTSERRAT_BOLD, 18)
    f_mono = load_font(FONT_MONO, 17)
    f_chip = load_font(FONT_MONTSERRAT_SEMIBOLD, 15)
    f_notice = load_font(FONT_MONTSERRAT_MEDIUM, 14)
    
    # Text
    draw_pill(card_draw, card_w // 2, 60, "COLLEGE OF COMPUTER STUDIES • ITPM 311",
              f_badge, (112, 9, 35, 200), (255, 237, 213, 255), gold_outer, pad_x=18, pad_y=6, radius=12)

    t_text = "IT OLYMPICS 2026"
    tw, th = text_size(card_draw, t_text, f_title_main)
    card_draw.text((card_w // 2 - tw // 2, 95), t_text, font=f_title_main, fill=(255, 245, 230, 255))
    
    s_text = "Participant Evaluation"
    sw, sh = text_size(card_draw, s_text, f_script)
    card_draw.text((card_w // 2 - sw // 2, 150), s_text, font=f_script, fill=gold_outer)
    
    tag_text = "✦  THREE DECADES BEYOND THE CODE  ✦"
    tgw, tgh = text_size(card_draw, tag_text, f_tagline)
    card_draw.text((card_w // 2 - tgw // 2, 218), tag_text, font=f_tagline, fill=(254, 243, 199, 255))
    
    sub_tag = "Innovation, Leadership, and Digital Excellence"
    stgw, stgh = text_size(card_draw, sub_tag, f_cursive_sub)
    card_draw.text((card_w // 2 - stgw // 2, 248), sub_tag, font=f_cursive_sub, fill=(245, 158, 11, 255))
    
    # Divider
    card_draw.line([(card_w // 2 - 240, 290), (card_w // 2 + 240, 290)], fill=(212, 175, 55, 140), width=1)

    # Pure White QR Box
    qr_box_size = 470
    qr_cx = card_w // 2
    qr_cy = 315 + qr_box_size // 2
    qr_rect = [qr_cx - qr_box_size // 2, qr_cy - qr_box_size // 2,
               qr_cx + qr_box_size // 2, qr_cy + qr_box_size // 2]
    
    card_draw.rounded_rectangle(qr_rect, radius=20, fill=(255, 255, 255, 255),
                                outline=gold_outer, width=2)
    
    if os.path.exists(SOURCE_QR):
        qr_src = Image.open(SOURCE_QR).convert("RGBA")
        qr_disp_size = 410
        qr_scaled = qr_src.resize((qr_disp_size, qr_disp_size), Image.Resampling.LANCZOS)
        card.paste(qr_scaled, (qr_cx - qr_disp_size // 2, qr_cy - qr_disp_size // 2), qr_scaled)

    draw_corner_reticles(card_draw, qr_rect, length=32, thickness=3, color=(16, 185, 129, 255), offset=10)

    # Action Button
    btn_y = qr_cy + qr_box_size // 2 + 42
    draw_pill(card_draw, card_w // 2, btn_y, "POINT CAMERA TO SCAN",
              f_btn, (16, 185, 129, 240), (255, 255, 255, 255), (52, 211, 153, 200), pad_x=26, pad_y=11, radius=20)

    # Direct Link Box
    link_y = btn_y + 44
    link_text = f"Direct browser link: {FALLBACK_URL}"
    lw, lh = text_size(card_draw, link_text, f_mono)
    card_draw.rounded_rectangle([card_w // 2 - lw // 2 - 14, link_y - 4, card_w // 2 + lw // 2 + 14, link_y + lh + 4],
                                radius=8, fill=(10, 3, 6, 200), outline=gold_inner, width=1)
    card_draw.text((card_w // 2 - lw // 2, link_y), link_text, font=f_mono, fill=(52, 211, 153, 255))

    # Chips
    chips_y = link_y + 45
    chips = ["⚡ 2-3 Minutes", "🔒 100% Anonymous", "🎯 10 Quick Questions"]
    c_w = 210
    c_gap = 14
    total_w = len(chips) * c_w + (len(chips) - 1) * c_gap
    start_x = (card_w - total_w) // 2 + c_w // 2
    for i, chip_txt in enumerate(chips):
        cx = start_x + i * (c_w + c_gap)
        draw_pill(card_draw, cx, chips_y, chip_txt, f_chip,
                  (35, 12, 20, 220), (254, 243, 199, 255), gold_inner, pad_x=14, pad_y=6, radius=12)

    # Notice
    not_y = chips_y + 36
    not_text = "※ Lab workstations are isolated from WAN • Please scan with your personal smartphone"
    nw, nh = text_size(card_draw, not_text, f_notice)
    card_draw.text((card_w // 2 - nw // 2, not_y), not_text, font=f_notice, fill=(203, 213, 225, 200))

    # Composite Shadow
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rectangle([card_x + 10, card_y + 16, card_x + card_w - 10, card_y + card_h + 16], fill=(0, 0, 0, 180))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    backdrop = Image.alpha_composite(backdrop, shadow)

    # Paste Card
    backdrop.paste(card, (card_x, card_y), card)
    
    # Wax Seals
    backdrop.paste(seal_img, (card_x + 36, card_y + 36), seal_img)
    backdrop.paste(seal_img, (card_x + card_w - 36 - 110, card_y + 36), seal_img)

    # Bottom Footer on Backdrop
    f_post_foot = load_font(FONT_CINZEL_BOLD, 17)
    f_post_sub = load_font(FONT_MONTSERRAT_MEDIUM, 14)
    b_draw = ImageDraw.Draw(backdrop)
    foot_1 = "OCTOBER 15-17, 2026  ✦  SAINT BENEDICT HALL"
    fw1, fh1 = text_size(b_draw, foot_1, f_post_foot)
    b_draw.text((W // 2 - fw1 // 2, H - 145), foot_1, font=f_post_foot, fill=(254, 243, 199, 240))
    
    foot_2 = "Fatima QuizBee Engine  •  ITPM 311 Project Integration  •  Our Lady of Fatima University"
    fw2, fh2 = text_size(b_draw, foot_2, f_post_sub)
    b_draw.text((W // 2 - fw2 // 2, H - 118), foot_2, font=f_post_sub, fill=(212, 175, 55, 200))

    out_path = os.path.join(OUTPUT_DIR, "evaluation_poster_official_baroque.png")
    backdrop.save(out_path, "PNG", dpi=(300, 300))
    print(f"Baroque Plaque Poster successfully created: {out_path}")
    return out_path

if __name__ == "__main__":
    p1 = render_parchment_poster()
    p2 = render_baroque_poster()
    print("All posters generated!")
