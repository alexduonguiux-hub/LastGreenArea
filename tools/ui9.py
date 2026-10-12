"""UI option 9 — cosy RPG style from the user's reference: navy frames with corner rivets, cream parchment fill,
navy title pill with stars, teal selection, colour bars, navy item slots, tabs, ribbons, notification pills."""
import math
from PIL import Image, ImageDraw
from ui5 import text, tw, flush_text

NV0, NV1, NV2, NV3 = (24, 30, 52), (40, 50, 82), (60, 74, 112), (110, 128, 168)
CR0, CR1, CR2 = (232, 214, 176), (244, 232, 206), (252, 245, 228)
TEAL0, TEAL1, TEAL2 = (40, 110, 104), (84, 172, 156), (170, 226, 208)
ORANGE = (240, 122, 82); HPC = (96, 200, 162); MPC = (240, 168, 64); REDC = (232, 98, 80); BLUEC = (80, 140, 214); PURPC = (150, 110, 210)
INK = (46, 42, 54); INK2 = (110, 100, 90); WHITE = (246, 244, 236); GOLD = (244, 196, 70)

def frame(d, x0, y0, x1, y1, fill=CR1):
    d.rectangle((x0 + 3, y0 + 3, x1 + 3, y1 + 3), fill=(0, 0, 0, 70))
    d.rectangle((x0 + 1, y0, x1 - 1, y1), fill=NV0); d.rectangle((x0, y0 + 1, x1, y1 - 1), fill=NV0)
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=NV1)
    d.line([(x0 + 2, y0 + 1), (x1 - 2, y0 + 1)], fill=NV3); d.line([(x0 + 2, y1 - 1), (x1 - 2, y1 - 1)], fill=NV0)
    d.rectangle((x0 + 3, y0 + 3, x1 - 3, y1 - 3), fill=NV0)
    d.rectangle((x0 + 4, y0 + 4, x1 - 4, y1 - 4), fill=fill)
    d.line([(x0 + 5, y0 + 5), (x1 - 5, y0 + 5)], fill=CR2 if fill == CR1 else tuple(min(255, c + 20) for c in fill))
    d.line([(x0 + 5, y1 - 5), (x1 - 5, y1 - 5)], fill=CR0 if fill == CR1 else tuple(max(0, c - 16) for c in fill))
    for (cx, cy) in ((x0 + 2, y0 + 2), (x1 - 2, y0 + 2), (x0 + 2, y1 - 2), (x1 - 2, y1 - 2)):
        d.point((cx, cy), fill=(196, 150, 120))
    return (x0 + 6, y0 + 6, x1 - 6, y1 - 6)

def title(d, cx, y, s, w=None):
    w = w or int(tw(s, 10) * 1.0) + 40; x0, x1 = int(cx - w / 2), int(cx + w / 2)
    d.rectangle((x0 + 1, y - 7, x1 - 1, y + 7), fill=NV0); d.rectangle((x0, y - 6, x1, y + 6), fill=NV0)
    d.rectangle((x0 + 2, y - 5, x1 - 2, y + 5), fill=NV1); d.line([(x0 + 3, y - 5), (x1 - 3, y - 5)], fill=NV3)
    for sx in (x0 + 8, x1 - 8): star(d, sx, y, 3, (220, 208, 180))
    text(d, (cx + 0.5, y - 6), s, 10, 'b', WHITE, 'ma')

def star(d, cx, cy, r, col):
    pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.cos(-math.pi / 2 + i * math.pi / 5), cy + (r if i % 2 == 0 else r * 0.45) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    d.polygon(pts, fill=col)

def card(d, x0, y0, x1, y1, sel=False):
    d.rectangle((x0, y0, x1, y1), fill=NV0)
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=((150, 214, 192) if CR1[0] > 150 else (40, 112, 104)) if sel else CR2)
    d.line([(x0 + 1, y1 - 1), (x1 - 1, y1 - 1)], fill=TEAL1 if sel else CR0)
    if sel: d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), outline=TEAL0)

def bar(d, x, y, w, frac, col, h=4, label=None):
    if label: text(d, (x - 1, y - 3), label, 8, 'b', INK2, 'ra')
    d.rectangle((x, y, x + w, y + h), fill=NV0); d.rectangle((x + 1, y + 1, x + w - 1, y + h - 1), fill=(58, 64, 88))
    fw = int((w - 2) * frac)
    if fw > 0: d.rectangle((x + 1, y + 1, x + fw, y + h - 1), fill=col); d.line([(x + 1, y + 1), (x + fw, y + 1)], fill=tuple(min(255, c + 50) for c in col))

def slot(d, x0, y0, s=22, sel=False):
    d.rectangle((x0, y0, x0 + s, y0 + s), fill=NV0); d.rectangle((x0 + 1, y0 + 1, x0 + s - 1, y0 + s - 1), fill=NV2)
    d.rectangle((x0 + 2, y0 + 2, x0 + s - 2, y0 + s - 2), fill=(52, 62, 96)); d.line([(x0 + 2, y0 + 2), (x0 + s - 2, y0 + 2)], fill=NV3)
    if sel: d.rectangle((x0 - 1, y0 - 1, x0 + s + 1, y0 + s + 1), outline=ORANGE)

def tabs(d, x0, y0, labels, active, w=None):
    x = x0
    for i, s in enumerate(labels):
        ww = w or int(tw(s, 9)) + 14; act = i == active
        d.rectangle((x, y0, x + ww, y0 + 14), fill=NV0)
        d.rectangle((x + 1, y0 + 1, x + ww - 1, y0 + 14), fill=((150, 214, 192) if CR1[0] > 150 else (40, 112, 104)) if act else NV2)
        if act: d.line([(x + 1, y0 + 1), (x + ww - 1, y0 + 1)], fill=TEAL2)
        text(d, (x + ww / 2 + 0.5, y0 + 3), s, 9, 'b', INK if act else WHITE, 'ma')
        x += ww + 2
    return x

def scrollbar(d, x, y0, y1, pos=0.2):
    d.rectangle((x, y0, x + 8, y1), fill=NV0); d.rectangle((x + 1, y0 + 1, x + 7, y1 - 1), fill=TEAL0)
    d.polygon([(x + 2, y0 + 6), (x + 6, y0 + 6), (x + 4, y0 + 3)], fill=TEAL2); d.polygon([(x + 2, y1 - 6), (x + 6, y1 - 6), (x + 4, y1 - 3)], fill=TEAL2)
    ty = int(y0 + 10 + (y1 - y0 - 34) * pos); d.rectangle((x + 2, ty, x + 6, ty + 14), fill=TEAL2)

def ribbon(d, cx, y, s, col=(TEAL0, TEAL1, TEAL2), icon=None, im=None):
    w = int(tw(s, 10)) + 56; x0, x1 = int(cx - w / 2), int(cx + w / 2)
    for sx in (-1, 1):
        ex = x0 - 10 if sx < 0 else x1 + 10; bx = x0 + 4 if sx < 0 else x1 - 4
        d.polygon([(bx, y - 4), (ex, y - 4), (ex + 5 * sx * -1, y + 3), (ex, y + 10), (bx, y + 10)], fill=col[0])
    d.rectangle((x0, y - 8, x1, y + 8), fill=NV0); d.rectangle((x0 + 1, y - 7, x1 - 1, y + 7), fill=col[1])
    d.line([(x0 + 2, y - 6), (x1 - 2, y - 6)], fill=col[2]); d.line([(x0 + 2, y + 6), (x1 - 2, y + 6)], fill=col[0])
    text(d, (cx + 9.5, y - 6), s, 10, 'b', WHITE, 'ma', shadow=NV0)
    if icon is not None and im is not None: im.alpha_composite(icon, (x0 + 5, y - 8))

def pill(d, x0, y, x1, s, icon=None, im=None):
    d.rectangle((x0 + 1, y - 9, x1 - 1, y + 9), fill=NV0); d.rectangle((x0, y - 8, x1, y + 8), fill=NV0)
    d.rectangle((x0 + 2, y - 7, x1 - 2, y + 7), fill=NV1); d.line([(x0 + 3, y - 7), (x1 - 3, y - 7)], fill=NV3)
    text(d, (x0 + 26, y - 6), s, 9, 'b', WHITE)
    if icon is not None and im is not None: im.alpha_composite(icon, (x0 - 6, y - icon.height // 2))

def choice(d, x0, y0, x1, s, sel=False, mark='›'):
    d.rectangle((x0, y0, x1, y0 + 15), fill=NV0)
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y0 + 14), fill=ORANGE if sel else NV2)
    if sel: d.line([(x0 + 2, y0 + 2), (x1 - 2, y0 + 2)], fill=(255, 180, 150))
    text(d, (x0 + 18, y0 + 3), s, 9, 'b', WHITE)

def toggle(d, x, y, on=True):
    d.rectangle((x, y, x + 22, y + 11), fill=NV0); d.rectangle((x + 1, y + 1, x + 21, y + 10), fill=TEAL1 if on else NV2)
    kx = x + 12 if on else x + 2; d.rectangle((kx, y + 2, kx + 8, y + 9), fill=CR2)
