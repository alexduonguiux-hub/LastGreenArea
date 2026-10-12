"""UI kit v5 — authentic pixel UI drawn at native 800x450 (×2 on screen).
Direction from the user's reference: chunky 2px pixel borders with stepped corners, several 'materials'
(navy glass, parchment, metal slot with corner brackets, wood window, neon ability frames),
segmented bars, 3D keycap buttons, list rows with a highlight strip, pixel font."""
import math
from PIL import Image, ImageDraw, ImageFont

FD = '/usr/share/fonts/truetype/dejavu/'
PF = {('b', 9): ImageFont.truetype(FD + 'DejaVuSans-Bold.ttf', 9), ('b', 10): ImageFont.truetype(FD + 'DejaVuSans-Bold.ttf', 10),
      ('b', 13): ImageFont.truetype(FD + 'DejaVuSans-Bold.ttf', 13), ('r', 9): ImageFont.truetype(FD + 'DejaVuSans.ttf', 9),
      ('b', 8): ImageFont.truetype(FD + 'DejaVuSans-Bold.ttf', 8)}

# palette (close in spirit to the reference, tuned to the forest scene)
NAVY = (29, 42, 74); NAVY2 = (40, 58, 98); NAVY_HI = (88, 152, 214); NAVY_LO = (14, 20, 38); CYAN = (110, 210, 240)
PARCH = (242, 230, 204); PARCH2 = (226, 208, 172); ORANGE = (196, 120, 58); ORANGE_LO = (120, 66, 30); INKD = (52, 40, 32)
STEEL = (138, 146, 164); STEEL2 = (98, 106, 124); STEEL_HI = (196, 204, 220); STEEL_LO = (40, 44, 56); SLOT = (52, 58, 72)
WOOD = (92, 58, 46); WOOD2 = (120, 80, 60); WOOD_LO = (46, 28, 22)
WHITE = (240, 240, 232); GREY = (160, 166, 180); RED = (226, 70, 60); GOLD = (244, 196, 80); GREEN = (90, 220, 120)
NEON = {'green': ((40, 200, 110), (14, 60, 40)), 'blue': ((60, 150, 240), (16, 40, 80)), 'purple': ((150, 90, 240), (40, 20, 80)), 'gold': ((244, 196, 80), (70, 50, 16)), 'red': ((230, 80, 60), (70, 20, 16))}

TQ = []   # text queue: drawn after the ×2 upscale so Vietnamese diacritics stay correct (aliased, still pixel-crisp)
HF = {}
def text(d, xy, s, size=9, w='b', fill=WHITE, anchor='la', shadow=None):
    TQ.append((xy, s, size, w, fill, anchor, shadow))

def flush_text(big, k=2):
    d = ImageDraw.Draw(big); d.fontmode = '1'
    for (x, y), s, size, w, fill, anchor, shadow in TQ:
        key = (w, size)
        if key not in HF: HF[key] = ImageFont.truetype(FD + ('DejaVuSans-Bold.ttf' if w == 'b' else 'DejaVuSans.ttf'), int(size * k * 0.95))
        f = HF[key]
        if shadow: d.text((x * k + 2, y * k + 2), s, font=f, fill=shadow, anchor=anchor)
        d.text((x * k, y * k), s, font=f, fill=fill, anchor=anchor)
    TQ.clear(); return big

def tw(s, size=9, w='b'): return PF[(w, size)].getlength(s)

def stepped(d, x0, y0, x1, y1, fill):
    d.rectangle((x0 + 2, y0, x1 - 2, y1), fill=fill); d.rectangle((x0, y0 + 2, x1, y1 - 2), fill=fill)
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=fill)

def border(d, x0, y0, x1, y1, col, inset=0):
    x0 += inset; y0 += inset; x1 -= inset; y1 -= inset
    d.line([(x0 + 2, y0), (x1 - 2, y0)], fill=col); d.line([(x0 + 2, y1), (x1 - 2, y1)], fill=col)
    d.line([(x0, y0 + 2), (x0, y1 - 2)], fill=col); d.line([(x1, y0 + 2), (x1, y1 - 2)], fill=col)
    d.point((x0 + 1, y0 + 1), fill=col); d.point((x1 - 1, y0 + 1), fill=col); d.point((x0 + 1, y1 - 1), fill=col); d.point((x1 - 1, y1 - 1), fill=col)

def shadow(d, x0, y0, x1, y1): stepped(d, x0 + 2, y0 + 2, x1 + 2, y1 + 2, (0, 0, 0, 120))

def navy(d, x0, y0, x1, y1, glow=True):
    shadow(d, x0, y0, x1, y1); stepped(d, x0, y0, x1, y1, NAVY + (240,))
    hgt = max(1, y1 - y0)
    for y in range(y0 + 3, y1 - 2):
        t = (y - y0) / hgt
        c = tuple(int(a + (b - a) * t) for a, b in zip((38, 54, 92), (22, 32, 58)))
        d.line([(x0 + 3, y), (x1 - 3, y)], fill=c + (242,))
    if glow and (x1 - x0) > 60 and hgt > 40:
        for k in range(0, 6):
            d.point((x0 + 5 + k * 2, y0 + 4 + k), fill=(160, 210, 240, 90)); d.point((x0 + 6 + k * 2, y0 + 4 + k), fill=(160, 210, 240, 60))
    border(d, x0, y0, x1, y1, NAVY_LO); border(d, x0, y0, x1, y1, NAVY_HI, 1); border(d, x0, y0, x1, y1, (32, 46, 80), 2)
    d.line([(x0 + 3, y0 + 1), (x0 + 12, y0 + 1)], fill=CYAN); d.point((x1 - 3, y1 - 1), fill=CYAN)

def _h(x, y): return ((x * 73856093) ^ (y * 19349663)) & 1023

def parchment(d, x0, y0, x1, y1, dogear=True):
    shadow(d, x0, y0, x1, y1); stepped(d, x0, y0, x1, y1, PARCH)
    # paper grain + slightly burnt inner edge
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2):
            h = _h(x, y)
            if h < 26: d.point((x, y), fill=(232, 218, 188))
            elif h < 32: d.point((x, y), fill=(250, 242, 222))
    d.rectangle((x0 + 2, y0 + 2, x1 - 2, y0 + 2), fill=(250, 244, 228))
    d.line([(x0 + 3, y1 - 2), (x1 - 3, y1 - 2)], fill=PARCH2); d.line([(x1 - 2, y0 + 3), (x1 - 2, y1 - 3)], fill=PARCH2)
    d.line([(x0 + 2, y0 + 3), (x0 + 2, y1 - 3)], fill=(236, 222, 194))
    border(d, x0, y0, x1, y1, ORANGE_LO); border(d, x0, y0, x1, y1, ORANGE, 1)
    if dogear and (x1 - x0) > 60 and (y1 - y0) > 30:
        d.polygon([(x1 - 7, y1), (x1, y1 - 7), (x1, y1)], fill=(0, 0, 0, 0))
        d.polygon([(x1 - 7, y1 - 1), (x1 - 1, y1 - 7), (x1 - 7, y1 - 7)], fill=PARCH2)
        d.line([(x1 - 7, y1 - 1), (x1 - 1, y1 - 7)], fill=ORANGE_LO); d.line([(x1 - 7, y1 - 7), (x1 - 7, y1 - 1)], fill=ORANGE)

def metal(d, x0, y0, x1, y1, brackets=True, fill=SLOT, sel=None):
    shadow(d, x0, y0, x1, y1); stepped(d, x0, y0, x1, y1, STEEL)
    border(d, x0, y0, x1, y1, STEEL_LO)
    d.line([(x0 + 2, y0 + 1), (x1 - 2, y0 + 1)], fill=STEEL_HI); d.line([(x0 + 1, y0 + 2), (x0 + 1, y1 - 2)], fill=STEEL_HI)
    d.line([(x0 + 2, y1 - 1), (x1 - 2, y1 - 1)], fill=STEEL2); d.line([(x1 - 1, y0 + 2), (x1 - 1, y1 - 2)], fill=STEEL2)
    for y in range(y0 + 2, y1 - 1, 3): d.line([(x0 + 2, y), (x0 + 2, y)], fill=STEEL_HI)
    d.rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), fill=fill); d.rectangle((x0 + 3, y0 + 3, x1 - 3, y0 + 3), fill=STEEL_LO)
    d.line([(x0 + 3, y0 + 4), (x0 + 3, y1 - 3)], fill=tuple(max(0, c - 14) for c in fill[:3]))
    if brackets:
        c = sel or STEEL_HI; L = 4
        for (cx, cy, sx, sy) in ((x0 - 1, y0 - 1, 1, 1), (x1 + 1, y0 - 1, -1, 1), (x0 - 1, y1 + 1, 1, -1), (x1 + 1, y1 + 1, -1, -1)):
            d.line([(cx, cy), (cx + sx * L, cy)], fill=c, width=2); d.line([(cx, cy), (cx, cy + sy * L)], fill=c, width=2)

def wood_window(d, x0, y0, x1, y1, title=None):
    shadow(d, x0, y0, x1, y1); stepped(d, x0, y0, x1, y1, WOOD)
    for y in range(y0 + 3, y1 - 2):
        for x in range(x0 + 3, x1 - 2, 1):
            v = (math.sin(y * 0.9 + math.sin(x * 0.05 + y * 0.3) * 2.2) + 1) / 2
            if v > 0.86: d.point((x, y), fill=(104, 68, 52))
            elif v < 0.08: d.point((x, y), fill=(80, 50, 38))
    border(d, x0, y0, x1, y1, WOOD_LO); border(d, x0, y0, x1, y1, WOOD2, 1)
    d.line([(x0 + 3, y0 + 2), (x1 - 3, y0 + 2)], fill=(146, 100, 74))
    if title:
        pw = int(tw(title, 10)) + 26
        px0 = x0 + 8; px1 = px0 + pw
        stepped(d, px0, y0 - 6, px1, y0 + 10, PARCH); border(d, px0, y0 - 6, px1, y0 + 10, ORANGE_LO); border(d, px0, y0 - 6, px1, y0 + 10, ORANGE, 1)
        for nx in (px0 + 4, px1 - 4): d.rectangle((nx - 1, y0 + 1, nx, y0 + 2), fill=(90, 90, 96)); d.point((nx - 1, y0 + 1), fill=(200, 200, 210))
        text(d, (px0 + 13, y0 - 4), title, 10, 'b', INKD)

def neon(d, x0, y0, x1, y1, color='blue', active=False):
    hi, lo = NEON[color]
    shadow(d, x0, y0, x1, y1)
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=(18, 24, 40, 245))
    d.rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), fill=lo + (255,) if active else (24, 32, 52, 255))
    # angled corners + bright edge
    pts = [(x0 + 4, y0), (x1 - 1, y0), (x1, y0 + 1), (x1, y1 - 4), (x1 - 4, y1), (x0 + 1, y1), (x0, y1 - 1), (x0, y0 + 4)]
    d.line(pts + [pts[0]], fill=hi, width=1)
    d.line([(x0 + 2, y0 + 2), (x0 + 6, y0 + 2)], fill=hi); d.line([(x1 - 2, y1 - 2), (x1 - 6, y1 - 2)], fill=hi)
    if active:
        for x in range(x0 - 2, x1 + 3):
            for y in (y0 - 2, y1 + 2):
                if (x + y) % 2 == 0: d.point((x, y), fill=hi + (150,))
        for y in range(y0 - 1, y1 + 2):
            for x in (x0 - 2, x1 + 2):
                if (x + y) % 2 == 0: d.point((x, y), fill=hi + (150,))
        d.line([(x0 + 4, y0 - 1), (x1 - 2, y0 - 1)], fill=tuple(min(255, c + 60) for c in hi))
    for (cx, cy) in ((x0 + 1, y1 - 1), (x1 - 1, y0 + 1)): d.point((cx, cy), fill=tuple(min(255, c + 80) for c in hi))

def keycap(d, cx, cy, s, w=None):
    w = w or max(12, int(tw(s, 9)) + 6); h = 12; x0 = int(cx - w / 2); y0 = int(cy - h / 2)
    d.rectangle((x0, y0 + 1, x0 + w, y0 + h + 1), fill=(34, 36, 46)); stepped(d, x0, y0, x0 + w, y0 + h, (204, 210, 224))
    d.rectangle((x0 + 1, y0 + h - 2, x0 + w - 1, y0 + h - 1), fill=(150, 156, 172)); d.line([(x0 + 2, y0 + 1), (x0 + w - 2, y0 + 1)], fill=(240, 244, 252))
    border(d, x0, y0, x0 + w, y0 + h, (34, 36, 46))
    text(d, (x0 + w / 2 + 0.5, y0 + 5), s, 9, 'b', (34, 36, 46), 'mm')

def seg_bar(d, x, y, n, full, col, w=6, h=4, gap=1, empty=(40, 46, 60)):
    for i in range(n):
        xx = x + i * (w + gap); c = col if i < full else empty
        d.rectangle((xx, y, xx + w - 1, y + h - 1), fill=c); d.line([(xx, y), (xx + w - 1, y)], fill=tuple(min(255, v + 50) for v in c))

def pill_bar(d, x, y, w, frac, col, h=6):
    stepped(d, x, y, x + w, y + h, (20, 24, 36)); border(d, x, y, x + w, y + h, (10, 12, 20))
    fw = int((w - 4) * frac)
    if fw > 0: d.rectangle((x + 2, y + 2, x + 2 + fw, y + h - 2), fill=col); d.line([(x + 2, y + 2), (x + 2 + fw, y + 2)], fill=tuple(min(255, v + 60) for v in col))

def heart(d, x, y, full=True):
    pix = ['.##.##.', '#######', '#######', '.#####.', '..###..', '...#...']
    for j, row in enumerate(pix):
        for i, ch in enumerate(row):
            if ch == '#': d.point((x + i, y + j), fill=(RED if full else (70, 40, 50)))
    if full: d.point((x + 1, y + 1), fill=(255, 190, 180))

def list_row(d, x0, y0, x1, label, sel=False, style='navy'):
    if style == 'navy':
        stepped(d, x0, y0, x1, y0 + 14, NAVY2 if sel else NAVY); border(d, x0, y0, x1, y0 + 14, NAVY_HI if sel else (56, 84, 130))
        if sel:
            d.rectangle((x0 + 2, y0 + 2, x0 + 3, y0 + 12), fill=CYAN)
            for x in range(x0 + 4, min(x1 - 2, x0 + 40)): 
                if x % 2 == 0: d.point((x, y0 + 2), fill=(110, 210, 240, 90))
            d.polygon([(x1 - 8, y0 + 4), (x1 - 4, y0 + 7), (x1 - 8, y0 + 10)], fill=CYAN)
        text(d, (x0 + 8, y0 + 3), label, 9, 'b', WHITE if sel else GREY, shadow=(10, 14, 26) if sel else None)
    else:
        stepped(d, x0, y0, x1, y0 + 14, PARCH); border(d, x0, y0, x1, y0 + 14, PARCH2)
        text(d, (x0 + 8, y0 + 3), label, 9, 'b', ORANGE if not sel else INKD)

def checkbox(d, x, y, on=True):
    stepped(d, x, y, x + 9, y + 9, WOOD2 if on else SLOT); border(d, x, y, x + 9, y + 9, WOOD_LO)
    if on: d.line([(x + 2, y + 5), (x + 4, y + 7), (x + 7, y + 2)], fill=PARCH, width=1)

def pixel_icon(name, col=WHITE):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = col + (255,)
    L = lambda pts: d.line(pts, fill=c)
    if name == 'climb': L([(4, 1), (4, 14)]); L([(11, 1), (11, 14)]); [L([(4, y), (11, y)]) for y in (4, 8, 12)]
    elif name == 'knife': L([(3, 13), (10, 6)]); L([(10, 6), (13, 2)]); L([(11, 7), (14, 3)]); d.rectangle((2, 12, 4, 14), fill=(140, 96, 60, 255))
    elif name == 'throw': [d.point((2 + k, 13 - int(10 * math.sin(k / 10 * math.pi * 0.8))), fill=c) for k in range(11)]; d.ellipse((11, 2, 14, 5), fill=(150, 154, 140, 255))
    elif name == 'map': d.polygon([(1, 3), (5, 1), (10, 3), (14, 1), (14, 12), (10, 14), (5, 12), (1, 14)], fill=(226, 208, 160, 255)); L([(5, 1), (5, 12)]); L([(10, 3), (10, 14)]); d.point((7, 7), fill=(226, 70, 60, 255))
    elif name == 'stand': d.ellipse((6, 1, 9, 4), fill=c); L([(7, 5), (7, 10)]); L([(8, 5), (8, 10)]); L([(4, 7), (11, 7)]); L([(7, 10), (5, 15)]); L([(8, 10), (10, 15)])
    elif name == 'crouch': d.ellipse((5, 4, 8, 7), fill=c); L([(7, 8), (9, 11)]); L([(9, 11), (6, 13)]); L([(6, 13), (6, 15)]); L([(9, 11), (12, 14)]); L([(7, 9), (4, 11)])
    elif name == 'crawl': d.ellipse((1, 8, 4, 11), fill=c); L([(5, 11), (12, 11)]); L([(5, 12), (12, 12)]); L([(12, 12), (15, 10)]); L([(6, 12), (4, 14)])
    elif name == 'pistol': d.rectangle((1, 4, 12, 7), fill=(90, 96, 108, 255)); d.rectangle((8, 7, 11, 13), fill=(70, 74, 84, 255)); L([(1, 4), (12, 4)])
    elif name == 'stone': d.ellipse((3, 5, 12, 13), fill=(150, 154, 140, 255)); d.point((6, 7), fill=(210, 214, 200, 255))
    elif name == 'bandage': d.rectangle((2, 5, 13, 10), fill=(236, 230, 214, 255)); d.rectangle((6, 5, 9, 10), fill=(220, 70, 60, 255))
    elif name == 'eye': d.ellipse((1, 4, 14, 11), outline=c); d.ellipse((6, 6, 9, 9), fill=c)
    elif name == 'drone': [d.ellipse((a, b, a + 4, b + 4), outline=c) for a, b in ((1, 1), (10, 1), (1, 10), (10, 10))]; d.rectangle((5, 5, 10, 10), fill=c)
    elif name == 'clock': d.ellipse((1, 1, 14, 14), outline=c); L([(7, 4), (7, 8)]); L([(7, 8), (10, 10)])
    elif name == 'play': d.polygon([(4, 2), (13, 8), (4, 14)], fill=c)
    elif name == 'sun': d.ellipse((5, 5, 10, 10), fill=(244, 196, 80, 255))
    return im
