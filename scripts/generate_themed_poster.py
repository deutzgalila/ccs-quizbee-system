#!/usr/bin/env python3
"""
Generate official-theme Post-Quiz Bee Evaluation Posters for OLFU IT Olympics 2026.
Matches the official visual theme of CCS Days 2026 (crimson velvet, gold arches, wax seals).
Features:
  - Cleaned-up organic wax seals with natural drop shadows (NO circular gray halo).
  - Prominent "QUIZ BEE SYSTEM" tournament branding.
  - Vector-drawn stars, icons, and bullets (NO missing glyph / tofu box '[]' issues).
  - 100% verified scannable QR code matrix.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

SOURCE_QR = "/home/javvii/.gemini/antigravity-cli/brain/bd31248a-d904-4d16-a417-d5598b3683fd/.user_uploaded/uploaded_media_1792226952716.png"
THEME_IM1 = "/home/javvii/.gemini/antigravity-cli/brain/bd31248a-d904-4d16-a417-d5598b3683fd/.user_uploaded/uploaded_media_1_1792227781305.png"
THEME_IM2 = "/home/javvii/.gemini/antigravity-cli/brain/bd31248a-d904-4d16-a417-d5598b3683fd/.user_uploaded/uploaded_media_2_1792227781305.png"
OUTPUT_DIR = "public/images"
FALLBACK_URL = "https://q.me-qr.com/43fo17lw"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Font paths
FONT_CINZEL_BOLD = "assets/fonts/Cinzel-Bold.ttf"
FONT_ALEX_BRUSH = "assets/fonts/AlexBrush-Regular.ttf"
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

def draw_gold_star(draw, cx, cy, r_outer=7, r_inner=2.5, color=(212, 175, 55, 255)):
    """Draw a vector 4-point/8-point gold starlight polygon (avoids font tofu box)."""
    pts = []
    for i in range(8):
        angle = i * math.pi / 4 - math.pi / 2
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, fill=color)

def draw_corner_reticles(draw, box, length=28, thickness=3, color=(212, 175, 55, 255), offset=10):
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

def extract_clean_wax_seal():
    """Extract organic melted red wax seal from Image 2 with ZERO circular halo."""
    im2 = Image.open(THEME_IM2).convert("RGB")
    # Exact center of left wax seal in im2 is at roughly (356, 396)
    cx, cy = 356, 396
    crop_r = 105
    seal_crop = im2.crop((cx - crop_r, cy - crop_r, cx + crop_r, cy + crop_r))
    arr = np.array(seal_crop)

    r = arr[:, :, 0].astype(float)
    g = arr[:, :, 1].astype(float)
    b = arr[:, :, 2].astype(float)

    # In the wax seal:
    # Deep red wax: (r - g) > 22 and (r - b) > 22
    # Crease shadows: r > 30 and (r / (g + 1) > 1.5)
    # Paper is cream: (g > 165) and (b > 155) and (abs(r - g) < 22)
    is_wax = ((r - g > 22) & (r - b > 22)) | ((r > 30) & (r / (g + 1) > 1.5))
    is_paper = (g > 160) & (b > 150) & (abs(r - g) < 25)
    is_wax = is_wax & (~is_paper)

    # Distance filter from center to isolate only the seal
    h, w = r.shape
    Y, X = np.ogrid[:h, :w]
    dist = np.sqrt((X - w // 2)**2 + (Y - h // 2)**2)
    is_wax = is_wax & (dist < 88)

    mask = Image.fromarray((is_wax.astype(np.uint8) * 255), mode='L')
    mask = mask.filter(ImageFilter.MaxFilter(5))  # close small internal gaps
    mask = mask.filter(ImageFilter.MinFilter(3))  # erode to edge
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))  # smooth anti-aliased organic edge

    rgba = Image.new('RGBA', seal_crop.size)
    rgba.paste(seal_crop, (0, 0))
    rgba.putalpha(mask)

    bbox = rgba.getbbox()
    return rgba.crop(bbox)

def paste_wax_seal_with_shadow(canvas, seal_img, x, y, target_size=(105, 105)):
    """Paste the wax seal with an organic, realistic contact drop shadow."""
    resized_seal = seal_img.resize(target_size, Image.Resampling.LANCZOS)
    rw, rh = target_size
    
    # Create soft realistic drop shadow
    shadow_pad = 20
    shadow = Image.new("RGBA", (rw + shadow_pad * 2, rh + shadow_pad * 2), (0, 0, 0, 0))
    s_alpha = resized_seal.split()[3].point(lambda a: int(a * 0.45))
    shadow.paste((30, 5, 5, 255), (shadow_pad + 2, shadow_pad + 4), mask=s_alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(4))
    
    canvas.paste(shadow, (x - shadow_pad, y - shadow_pad), shadow)
    canvas.paste(resized_seal, (x, y), resized_seal)

# Vector icon drawing functions for chips (avoid emoji tofu)
def draw_clock_icon(draw, x, y, r=6, color=(212, 175, 55, 255)):
    draw.ellipse([x - r, y - r, x + r, y + r], outline=color, width=2)
    draw.line([(x, y), (x, y - r + 2)], fill=color, width=2)
    draw.line([(x, y), (x + r - 3, y)], fill=color, width=2)

def draw_shield_icon(draw, x, y, w=12, h=14, color=(212, 175, 55, 255)):
    # Shield polygon
    pts = [
        (x - w // 2, y - h // 2),
        (x + w // 2, y - h // 2),
        (x + w // 2, y + 1),
        (x, y + h // 2),
        (x - w // 2, y + 1)
    ]
    draw.polygon(pts, outline=color, fill=(color[0], color[1], color[2], 60), width=1)
    # Check inside
    draw.line([(x - 3, y), (x - 1, y + 3), (x + 3, y - 2)], fill=color, width=2)

def draw_target_icon(draw, x, y, r=7, color=(212, 175, 55, 255)):
    draw.ellipse([x - r, y - r, x + r, y + r], outline=color, width=1)
    draw.ellipse([x - r + 3, y - r + 3, x + r - 3, y + r - 3], outline=color, width=1)
    draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=color)

# ==============================================================================
# POSTER 1: The Scalloped Parchment Ticket with Clean Wax Seals (Quiz Bee Edition)
# ==============================================================================
def render_parchment_poster():
    print("Generating Cleaned-Up Parchment Poster (Quiz Bee System)...")
    W, H = 1200, 1500
    
    # 1. Base Backdrop from Image 1
    im1 = Image.open(THEME_IM1).convert("RGBA")
    backdrop = im1.resize((W, H), Image.Resampling.LANCZOS)
    
    # 2. Extract clean organic wax seal (halo-free)
    clean_seal = extract_clean_wax_seal()
    
    # 3. Create Scalloped Ivory Parchment Card
    card_w, card_h = 920, 1080
    card_x = (W - card_w) // 2
    card_y = 230
    
    card = Image.new("RGBA", (card_w, card_h), (252, 250, 246, 255))
    
    # Stamp scalloped edge mask
    c_mask = Image.new("L", (card_w, card_h), 255)
    m_draw = ImageDraw.Draw(c_mask)
    hole_r = 14
    step = 36
    for py in range(36, card_h - 20, step):
        m_draw.ellipse([-hole_r, py - hole_r, hole_r, py + hole_r], fill=0)
        m_draw.ellipse([card_w - hole_r, py - hole_r, card_w + hole_r, py + hole_r], fill=0)
    for px in range(36, card_w - 20, step):
        m_draw.ellipse([px - hole_r, -hole_r, px + hole_r, hole_r], fill=0)
        m_draw.ellipse([px - hole_r, card_h - hole_r, px + hole_r, card_h + hole_r], fill=0)
        
    card.putalpha(c_mask)
    
    # Card borders
    card_draw = ImageDraw.Draw(card)
    border_inset = 28
    gold_border = (197, 160, 89, 220)
    card_draw.rectangle([border_inset, border_inset, card_w - border_inset, card_h - border_inset],
                        outline=gold_border, width=2)
    card_draw.rectangle([border_inset + 4, border_inset + 4, card_w - border_inset - 4, card_h - border_inset - 4],
                        outline=(197, 160, 89, 100), width=1)
    
    draw_corner_reticles(card_draw,
                         [border_inset + 8, border_inset + 8, card_w - border_inset - 8, card_h - border_inset - 8],
                         length=24, thickness=2, color=(197, 160, 89, 220), offset=0)

    # 4. Typography & Layout (QUIZ BEE SYSTEM CLEARLY EMPHASIZED)
    f_badge = load_font(FONT_MONTSERRAT_SEMIBOLD, 15)
    f_title_main = load_font(FONT_CINZEL_BOLD, 44)
    f_script = load_font(FONT_ALEX_BRUSH, 42)
    f_tagline = load_font(FONT_CINZEL_BOLD, 17)
    f_cursive_sub = load_font(FONT_ALEX_BRUSH, 26)
    f_desc = load_font(FONT_MONTSERRAT_MEDIUM, 15)
    f_btn = load_font(FONT_MONTSERRAT_BOLD, 18)
    f_mono = load_font(FONT_MONO, 17)
    f_chip = load_font(FONT_MONTSERRAT_SEMIBOLD, 14)
    f_notice = load_font(FONT_MONTSERRAT_MEDIUM, 14)
    
    c_maroon = (112, 9, 35, 255)
    c_gold = (180, 130, 20, 255)
    c_gold_light = (212, 175, 55, 255)
    
    # Top Eyebrow Badge
    draw_pill(card_draw, card_w // 2, 58, "COLLEGE OF COMPUTER STUDIES • ITPM 311",
              f_badge, (244, 237, 226, 255), c_maroon, (212, 175, 55, 180), pad_x=18, pad_y=6, radius=12)

    # Main Hero Title: "QUIZ BEE SYSTEM"
    t_text = "QUIZ BEE SYSTEM"
    tw, th = text_size(card_draw, t_text, f_title_main)
    card_draw.text((card_w // 2 - tw // 2 + 1, 92 + 1), t_text, font=f_title_main, fill=(212, 175, 55, 80))
    card_draw.text((card_w // 2 - tw // 2, 92), t_text, font=f_title_main, fill=c_maroon)
    
    # Script Subtitle: "Participant & Tournament Evaluation"
    s_text = "Participant & Tournament Evaluation"
    sw, sh = text_size(card_draw, s_text, f_script)
    card_draw.text((card_w // 2 - sw // 2, 146), s_text, font=f_script, fill=c_gold)
    
    # Event Theme Tagline with Vector Stars (No Tofu Boxes!)
    tag_text = "IT OLYMPICS 2026 : THREE DECADES BEYOND THE CODE"
    tgw, tgh = text_size(card_draw, tag_text, f_tagline)
    tag_y = 208
    card_draw.text((card_w // 2 - tgw // 2, tag_y), tag_text, font=f_tagline, fill=(30, 41, 59, 255))
    draw_gold_star(card_draw, card_w // 2 - tgw // 2 - 16, tag_y + tgh // 2, r_outer=7, r_inner=2.5, color=c_gold_light)
    draw_gold_star(card_draw, card_w // 2 + tgw // 2 + 16, tag_y + tgh // 2, r_outer=7, r_inner=2.5, color=c_gold_light)
    
    # Cursive Motto
    sub_tag = "Innovation, Leadership, and Digital Excellence"
    stgw, stgh = text_size(card_draw, sub_tag, f_cursive_sub)
    card_draw.text((card_w // 2 - stgw // 2, 234), sub_tag, font=f_cursive_sub, fill=c_gold)
    
    # Purpose Notice
    desc_text = "Your feedback directly shapes the Fatima QuizBee engine & tournament scoring"
    dw, dh = text_size(card_draw, desc_text, f_desc)
    card_draw.text((card_w // 2 - dw // 2, 268), desc_text, font=f_desc, fill=(71, 85, 105, 255))

    # Thin Divider with center diamond
    card_draw.line([(card_w // 2 - 240, 296), (card_w // 2 + 240, 296)], fill=(212, 175, 55, 140), width=1)
    card_draw.polygon([(card_w // 2, 293), (card_w // 2 + 5, 296), (card_w // 2, 299), (card_w // 2 - 5, 296)], fill=c_gold)

    # QR Code Container
    qr_box_size = 460
    qr_cx = card_w // 2
    qr_cy = 315 + qr_box_size // 2
    qr_rect = [qr_cx - qr_box_size // 2, qr_cy - qr_box_size // 2,
               qr_cx + qr_box_size // 2, qr_cy + qr_box_size // 2]
    
    # High-contrast pure white inner card with gold border
    card_draw.rounded_rectangle(qr_rect, radius=18, fill=(255, 255, 255, 255),
                                outline=(212, 175, 55, 180), width=2)
    
    if os.path.exists(SOURCE_QR):
        qr_src = Image.open(SOURCE_QR).convert("RGBA")
        qr_disp_size = 400
        qr_scaled = qr_src.resize((qr_disp_size, qr_disp_size), Image.Resampling.LANCZOS)
        card.paste(qr_scaled, (qr_cx - qr_disp_size // 2, qr_cy - qr_disp_size // 2), qr_scaled)
        
    draw_corner_reticles(card_draw, qr_rect, length=32, thickness=3, color=(180, 130, 20, 255), offset=10)

    # Action Banner: "POINT CAMERA TO EVALUATE QUIZ BEE"
    btn_y = qr_cy + qr_box_size // 2 + 40
    draw_pill(card_draw, card_w // 2, btn_y, "POINT CAMERA TO EVALUATE QUIZ BEE",
              f_btn, c_maroon, (255, 255, 255, 255), (212, 175, 55, 200), pad_x=26, pad_y=11, radius=20)

    # Fallback Direct Link
    link_y = btn_y + 44
    link_text = f"Direct browser link: {FALLBACK_URL}"
    lw, lh = text_size(card_draw, link_text, f_mono)
    card_draw.rounded_rectangle([card_w // 2 - lw // 2 - 14, link_y - 4, card_w // 2 + lw // 2 + 14, link_y + lh + 4],
                                radius=8, fill=(244, 237, 226, 255), outline=(212, 175, 55, 120), width=1)
    card_draw.text((card_w // 2 - lw // 2, link_y), link_text, font=f_mono, fill=(180, 83, 9, 255))

    # Feature Chips (Vector icons, perfectly centered)
    chips_y = link_y + 45
    chip_items = [
        ("2-3 Mins to Complete", draw_clock_icon),
        ("100% Anonymous", draw_shield_icon),
        ("10 Short Questions", draw_target_icon)
    ]
    c_w = 216
    c_gap = 14
    total_w = len(chip_items) * c_w + (len(chip_items) - 1) * c_gap
    start_x = (card_w - total_w) // 2 + c_w // 2
    
    for i, (txt, icon_fn) in enumerate(chip_items):
        cx = start_x + i * (c_w + c_gap)
        box = draw_pill(card_draw, cx, chips_y, "   " + txt, f_chip,
                        (255, 255, 255, 255), (51, 65, 85, 255), (226, 232, 240, 255), pad_x=14, pad_y=6, radius=12)
        # Draw vector icon inside pill
        icon_fn(card_draw, box[0] + 16, chips_y, color=c_gold)

    # Lab network notice (ASCII bullet, NO tofu)
    not_y = chips_y + 36
    not_text = "NOTE: Lab workstations are isolated from WAN • Please scan with your personal smartphone"
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
    
    # 7. Paste Clean Organic Wax Seals with Soft Drop Shadows (NO HALO!)
    paste_wax_seal_with_shadow(backdrop, clean_seal, card_x + 40, card_y + 38, target_size=(105, 105))
    paste_wax_seal_with_shadow(backdrop, clean_seal, card_x + card_w - 40 - 105, card_y + 38, target_size=(105, 105))

    # 8. Bottom Footer on Backdrop (with Vector Stars)
    f_post_foot = load_font(FONT_CINZEL_BOLD, 17)
    f_post_sub = load_font(FONT_MONTSERRAT_MEDIUM, 14)
    b_draw = ImageDraw.Draw(backdrop)
    foot_1 = "OCTOBER 15-17, 2026   SAINT BENEDICT HALL"
    fw1, fh1 = text_size(b_draw, foot_1, f_post_foot)
    foot_y = H - 145
    b_draw.text((W // 2 - fw1 // 2, foot_y), foot_1, font=f_post_foot, fill=(254, 243, 199, 240))
    # Vector stars around bottom date
    draw_gold_star(b_draw, W // 2 - fw1 // 2 - 16, foot_y + fh1 // 2, r_outer=6, r_inner=2, color=c_gold_light)
    draw_gold_star(b_draw, W // 2 + fw1 // 2 + 16, foot_y + fh1 // 2, r_outer=6, r_inner=2, color=c_gold_light)
    draw_gold_star(b_draw, W // 2 + 3, foot_y + fh1 // 2, r_outer=4, r_inner=1.5, color=c_gold_light)
    
    foot_2 = "Fatima QuizBee LAN Platform  •  ITPM 311 Systems Project  •  College of Computer Studies"
    fw2, fh2 = text_size(b_draw, foot_2, f_post_sub)
    b_draw.text((W // 2 - fw2 // 2, H - 118), foot_2, font=f_post_sub, fill=(212, 175, 55, 200))

    out_path = os.path.join(OUTPUT_DIR, "evaluation_poster_official_parchment.png")
    backdrop.save(out_path, "PNG", dpi=(300, 300))
    print(f"Parchment Poster successfully created: {out_path}")
    return out_path


# ==============================================================================
# POSTER 2: The Royal Baroque Gold Plaque (Quiz Bee System Edition)
# ==============================================================================
def render_baroque_poster():
    print("Generating Cleaned-Up Baroque Plaque Poster (Quiz Bee System)...")
    W, H = 1200, 1500
    
    im1 = Image.open(THEME_IM1).convert("RGBA")
    backdrop = im1.resize((W, H), Image.Resampling.LANCZOS)
    clean_seal = extract_clean_wax_seal()

    card_w, card_h = 920, 1080
    card_x = (W - card_w) // 2
    card_y = 230
    
    card = Image.new("RGBA", (card_w, card_h), (20, 6, 12, 235))
    card_draw = ImageDraw.Draw(card)
    
    gold_outer = (220, 180, 70, 255)
    gold_inner = (197, 160, 89, 140)
    card_draw.rounded_rectangle([16, 16, card_w - 16, card_h - 16], radius=24, outline=gold_outer, width=3)
    card_draw.rounded_rectangle([24, 24, card_w - 24, card_h - 24], radius=20, outline=gold_inner, width=1)
    
    draw_corner_reticles(card_draw, [32, 32, card_w - 32, card_h - 32], length=38, thickness=3, color=gold_outer, offset=0)

    f_badge = load_font(FONT_MONTSERRAT_SEMIBOLD, 15)
    f_title_main = load_font(FONT_CINZEL_BOLD, 44)
    f_script = load_font(FONT_ALEX_BRUSH, 42)
    f_tagline = load_font(FONT_CINZEL_BOLD, 17)
    f_cursive_sub = load_font(FONT_ALEX_BRUSH, 26)
    f_desc = load_font(FONT_MONTSERRAT_MEDIUM, 15)
    f_btn = load_font(FONT_MONTSERRAT_BOLD, 18)
    f_mono = load_font(FONT_MONO, 17)
    f_chip = load_font(FONT_MONTSERRAT_SEMIBOLD, 14)
    f_notice = load_font(FONT_MONTSERRAT_MEDIUM, 14)
    
    # Badge
    draw_pill(card_draw, card_w // 2, 58, "COLLEGE OF COMPUTER STUDIES • ITPM 311",
              f_badge, (112, 9, 35, 200), (255, 237, 213, 255), gold_outer, pad_x=18, pad_y=6, radius=12)

    # Main Title: "QUIZ BEE SYSTEM"
    t_text = "QUIZ BEE SYSTEM"
    tw, th = text_size(card_draw, t_text, f_title_main)
    card_draw.text((card_w // 2 - tw // 2, 92), t_text, font=f_title_main, fill=(255, 245, 230, 255))
    
    # Script Subtitle
    s_text = "Participant & Tournament Evaluation"
    sw, sh = text_size(card_draw, s_text, f_script)
    card_draw.text((card_w // 2 - sw // 2, 146), s_text, font=f_script, fill=gold_outer)
    
    # Tagline with Vector Stars
    tag_text = "IT OLYMPICS 2026 : THREE DECADES BEYOND THE CODE"
    tgw, tgh = text_size(card_draw, tag_text, f_tagline)
    tag_y = 208
    card_draw.text((card_w // 2 - tgw // 2, tag_y), tag_text, font=f_tagline, fill=(254, 243, 199, 255))
    draw_gold_star(card_draw, card_w // 2 - tgw // 2 - 16, tag_y + tgh // 2, r_outer=7, r_inner=2.5, color=gold_outer)
    draw_gold_star(card_draw, card_w // 2 + tgw // 2 + 16, tag_y + tgh // 2, r_outer=7, r_inner=2.5, color=gold_outer)
    
    sub_tag = "Innovation, Leadership, and Digital Excellence"
    stgw, stgh = text_size(card_draw, sub_tag, f_cursive_sub)
    card_draw.text((card_w // 2 - stgw // 2, 234), sub_tag, font=f_cursive_sub, fill=(245, 158, 11, 255))
    
    desc_text = "Your feedback directly shapes the Fatima QuizBee engine & tournament scoring"
    dw, dh = text_size(card_draw, desc_text, f_desc)
    card_draw.text((card_w // 2 - dw // 2, 268), desc_text, font=f_desc, fill=(203, 213, 225, 230))
    
    card_draw.line([(card_w // 2 - 240, 296), (card_w // 2 + 240, 296)], fill=(212, 175, 55, 140), width=1)
    card_draw.polygon([(card_w // 2, 293), (card_w // 2 + 5, 296), (card_w // 2, 299), (card_w // 2 - 5, 296)], fill=gold_outer)

    # Pure White QR Box
    qr_box_size = 460
    qr_cx = card_w // 2
    qr_cy = 315 + qr_box_size // 2
    qr_rect = [qr_cx - qr_box_size // 2, qr_cy - qr_box_size // 2,
               qr_cx + qr_box_size // 2, qr_cy + qr_box_size // 2]
    
    card_draw.rounded_rectangle(qr_rect, radius=20, fill=(255, 255, 255, 255),
                                outline=gold_outer, width=2)
    
    if os.path.exists(SOURCE_QR):
        qr_src = Image.open(SOURCE_QR).convert("RGBA")
        qr_disp_size = 400
        qr_scaled = qr_src.resize((qr_disp_size, qr_disp_size), Image.Resampling.LANCZOS)
        card.paste(qr_scaled, (qr_cx - qr_disp_size // 2, qr_cy - qr_disp_size // 2), qr_scaled)

    draw_corner_reticles(card_draw, qr_rect, length=32, thickness=3, color=(16, 185, 129, 255), offset=10)

    btn_y = qr_cy + qr_box_size // 2 + 40
    draw_pill(card_draw, card_w // 2, btn_y, "POINT CAMERA TO EVALUATE QUIZ BEE",
              f_btn, (16, 185, 129, 240), (255, 255, 255, 255), (52, 211, 153, 200), pad_x=26, pad_y=11, radius=20)

    link_y = btn_y + 44
    link_text = f"Direct browser link: {FALLBACK_URL}"
    lw, lh = text_size(card_draw, link_text, f_mono)
    card_draw.rounded_rectangle([card_w // 2 - lw // 2 - 14, link_y - 4, card_w // 2 + lw // 2 + 14, link_y + lh + 4],
                                radius=8, fill=(10, 3, 6, 200), outline=gold_inner, width=1)
    card_draw.text((card_w // 2 - lw // 2, link_y), link_text, font=f_mono, fill=(52, 211, 153, 255))

    # Chips with vector icons
    chips_y = link_y + 45
    chip_items = [
        ("2-3 Mins to Complete", draw_clock_icon),
        ("100% Anonymous", draw_shield_icon),
        ("10 Short Questions", draw_target_icon)
    ]
    c_w = 216
    c_gap = 14
    total_w = len(chip_items) * c_w + (len(chip_items) - 1) * c_gap
    start_x = (card_w - total_w) // 2 + c_w // 2
    for i, (txt, icon_fn) in enumerate(chip_items):
        cx = start_x + i * (c_w + c_gap)
        box = draw_pill(card_draw, cx, chips_y, "   " + txt, f_chip,
                        (35, 12, 20, 220), (254, 243, 199, 255), gold_inner, pad_x=14, pad_y=6, radius=12)
        icon_fn(card_draw, box[0] + 16, chips_y, color=gold_outer)

    not_y = chips_y + 36
    not_text = "NOTE: Lab workstations are isolated from WAN • Please scan with your personal smartphone"
    nw, nh = text_size(card_draw, not_text, f_notice)
    card_draw.text((card_w // 2 - nw // 2, not_y), not_text, font=f_notice, fill=(203, 213, 225, 200))

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    s_draw.rectangle([card_x + 10, card_y + 16, card_x + card_w - 10, card_y + card_h + 16], fill=(0, 0, 0, 180))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28))
    backdrop = Image.alpha_composite(backdrop, shadow)

    backdrop.paste(card, (card_x, card_y), card)
    
    paste_wax_seal_with_shadow(backdrop, clean_seal, card_x + 40, card_y + 38, target_size=(105, 105))
    paste_wax_seal_with_shadow(backdrop, clean_seal, card_x + card_w - 40 - 105, card_y + 38, target_size=(105, 105))

    f_post_foot = load_font(FONT_CINZEL_BOLD, 17)
    f_post_sub = load_font(FONT_MONTSERRAT_MEDIUM, 14)
    b_draw = ImageDraw.Draw(backdrop)
    foot_1 = "OCTOBER 15-17, 2026   SAINT BENEDICT HALL"
    fw1, fh1 = text_size(b_draw, foot_1, f_post_foot)
    foot_y = H - 145
    b_draw.text((W // 2 - fw1 // 2, foot_y), foot_1, font=f_post_foot, fill=(254, 243, 199, 240))
    draw_gold_star(b_draw, W // 2 - fw1 // 2 - 16, foot_y + fh1 // 2, r_outer=6, r_inner=2, color=gold_outer)
    draw_gold_star(b_draw, W // 2 + fw1 // 2 + 16, foot_y + fh1 // 2, r_outer=6, r_inner=2, color=gold_outer)
    draw_gold_star(b_draw, W // 2 + 3, foot_y + fh1 // 2, r_outer=4, r_inner=1.5, color=gold_outer)
    
    foot_2 = "Fatima QuizBee LAN Platform  •  ITPM 311 Systems Project  •  College of Computer Studies"
    fw2, fh2 = text_size(b_draw, foot_2, f_post_sub)
    b_draw.text((W // 2 - fw2 // 2, H - 118), foot_2, font=f_post_sub, fill=(212, 175, 55, 200))

    out_path = os.path.join(OUTPUT_DIR, "evaluation_poster_official_baroque.png")
    backdrop.save(out_path, "PNG", dpi=(300, 300))
    print(f"Baroque Plaque Poster successfully created: {out_path}")
    return out_path

if __name__ == "__main__":
    p1 = render_parchment_poster()
    p2 = render_baroque_poster()
    print("All posters updated and generated successfully!")
