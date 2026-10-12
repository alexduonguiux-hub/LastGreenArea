"""Cyber-factory skin over the dark option-9 layout.
Frames: chamfered corners, gunmetal bevel, cyan neon inner edge, hazard-stripe tab, LED dots, rivets, scanlines,
circuit traces. Title: angled plate with magenta notch. Bars: segmented with glow. Selection: cyan glow."""
import sys, math, random, pickle; sys.path.insert(0, '/home/claude/gen')
import dark9, ui9, hud9
from PIL import Image, ImageDraw
from ui5 import text, tw

CY = (60, 230, 240); CY2 = (30, 120, 140); MG = (240, 60, 170); MG2 = (120, 24, 90); HZ = (240, 196, 40)
G0, G1, G2, G3 = (10, 12, 20), (26, 30, 44), (44, 50, 70), (84, 94, 124)
FILL = (16, 20, 34); FILL2 = (24, 30, 50)
ui9.CR0, ui9.CR1, ui9.CR2 = (12, 14, 24), FILL, FILL2
for m in (ui9, hud9): m.INK, m.INK2 = (226, 236, 244), (120, 150, 176)
ui9.TEAL1 = CY; ui9.TEAL2 = (180, 250, 255); ui9.TEAL0 = CY2; ui9.HPC = (70, 230, 160); ui9.ORANGE = MG
hud9.ORANGE = MG

def chamfer(x0, y0, x1, y1, c):
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]

def frame(d, x0, y0, x1, y1, fill=None):
    fill = fill or FILL
    d.polygon(chamfer(x0 + 3, y0 + 3, x1 + 3, y1 + 3, 6), fill=(0, 0, 0, 120))
    d.polygon(chamfer(x0, y0, x1, y1, 6), fill=G0)
    d.polygon(chamfer(x0 + 1, y0 + 1, x1 - 1, y1 - 1, 6), fill=G2)
    d.line(chamfer(x0 + 1, y0 + 1, x1 - 1, y1 - 1, 6)[:3], fill=G3)
    d.polygon(chamfer(x0 + 3, y0 + 3, x1 - 3, y1 - 3, 5), fill=G0)
    d.polygon(chamfer(x0 + 4, y0 + 4, x1 - 4, y1 - 4, 4), fill=fill)
    # scanlines + faint grid
    for y in range(y0 + 6, y1 - 4, 3): d.line([(x0 + 6, y), (x1 - 6, y)], fill=tuple(max(0, c - 4) for c in fill))
    # cyan neon edge, broken in places
    pts = chamfer(x0 + 4, y0 + 4, x1 - 4, y1 - 4, 4)
    d.line([pts[7], pts[0], pts[1]], fill=CY); d.line([pts[3], pts[4], pts[5]], fill=CY2)
    d.line([(x1 - 4, y0 + 10), (x1 - 4, y0 + 22)], fill=CY)
    # hazard strip bottom-left + LEDs + rivets
    hx = x0 + 10; hy = y1 - 3
    for k in range(6):
        d.polygon([(hx + k * 6, hy), (hx + k * 6 + 3, hy - 2), (hx + k * 6 + 6, hy - 2), (hx + k * 6 + 3, hy)], fill=HZ if k % 2 == 0 else G0)
    for k, col in enumerate((MG, CY, (90, 230, 120))): d.rectangle((x1 - 18 + k * 4, y0 + 1, x1 - 17 + k * 4, y0 + 2), fill=col)
    for (rx, ry) in ((x0 + 2, y0 + 8), (x0 + 2, y1 - 8), (x1 - 2, y1 - 8)): d.point((rx, ry), fill=G3)
    # circuit trace on the left rail
    tx = x0 + 1; ty = y0 + 14
    if y1 - y0 > 60: d.line([(tx, ty), (tx, ty + 10)], fill=CY2); d.point((tx, ty + 11), fill=CY)
    # inner dot grid + corner brackets + micro tag + power conduit
    for gy in range(y0 + 12, y1 - 8, 8):
        for gx in range(x0 + 12, x1 - 8, 8): d.point((gx, gy), fill=tuple(min(255, c + 9) for c in fill))
    for (cx, cy, sx, sy) in ((x0 + 6, y0 + 6, 1, 1), (x1 - 6, y1 - 6, -1, -1)):
        d.line([(cx, cy), (cx + 5 * sx, cy)], fill=CY); d.line([(cx, cy), (cx, cy + 5 * sy)], fill=CY)
    if x1 - x0 > 120:
        _FR['n'] += 1; tag = f'SEC-{_FR["n"]:02d}'
        text(d, (x1 - 24, y1 - 5), tag, 8, 'r', CY2, 'rs')
        d.line([(x0 + 50, y1 - 1), (x1 - 60, y1 - 1)], fill=G1); d.line([(x0 + 50, y1 - 1), (x0 + 50 + (x1 - x0) // 5, y1 - 1)], fill=MG)
    return (x0 + 6, y0 + 6, x1 - 6, y1 - 6)
_FR = {'n': 0}

def title(d, cx, y, s, w=None):
    w = max(w or 0, int(tw(s.upper(), 10)) + 40); x0, x1 = int(cx - w / 2), int(cx + w / 2)
    pts = [(x0 + 7, y - 7), (x1 - 7, y - 7), (x1, y), (x1 - 7, y + 7), (x0 + 7, y + 7), (x0, y)]
    d.polygon(pts, fill=G0); d.polygon([(x0 + 8, y - 6), (x1 - 8, y - 6), (x1 - 2, y), (x1 - 8, y + 6), (x0 + 8, y + 6), (x0 + 2, y)], fill=G1)
    d.line([(x0 + 8, y - 6), (x1 - 8, y - 6)], fill=CY)
    d.polygon([(x0 + 3, y), (x0 + 8, y - 4), (x0 + 8, y + 4)], fill=MG); d.polygon([(x1 - 3, y), (x1 - 8, y - 4), (x1 - 8, y + 4)], fill=MG)
    text(d, (cx + 0.5, y - 6), s.upper(), 10, 'b', (220, 250, 255), 'ma', shadow=G0)

def card(d, x0, y0, x1, y1, sel=False):
    d.polygon(chamfer(x0, y0, x1, y1, 3), fill=G0)
    d.polygon(chamfer(x0 + 1, y0 + 1, x1 - 1, y1 - 1, 3), fill=(18, 60, 70) if sel else FILL2)
    d.line([(x0 + 3, y0 + 1), (x1 - 3, y0 + 1)], fill=CY if sel else G2)
    if sel:
        for x in range(x0 - 2, x1 + 3, 2): d.point((x, y0 - 2), fill=CY + (150,)); d.point((x, y1 + 2), fill=CY + (150,))
        d.rectangle((x0 + 1, y0 + 3, x0 + 2, y1 - 3), fill=CY)

def bar(d, x, y, w, frac, col, h=4, label=None):
    if label: text(d, (x - 1, y - 3), label, 8, 'b', (120, 150, 176), 'ra')
    n = max(4, w // 5); on = int(n * frac)
    for i in range(n):
        xx = x + i * (w / n); c = col if i < on else (34, 40, 58)
        d.rectangle((xx, y, xx + w / n - 2, y + h), fill=c)
        if i < on: d.line([(xx, y), (xx + w / n - 2, y)], fill=tuple(min(255, v + 70) for v in col))
    if on: d.line([(x, y + h + 1), (x + on * w / n - 2, y + h + 1)], fill=col + (90,))

def slot(d, x0, y0, s=22, sel=False):
    d.rectangle((x0, y0, x0 + s, y0 + s), fill=G0); d.rectangle((x0 + 1, y0 + 1, x0 + s - 1, y0 + s - 1), fill=(20, 26, 42))
    d.line([(x0 + 1, y0 + s - 1), (x0 + s - 1, y0 + s - 1)], fill=G2)
    c = CY if sel else G3; L = 3
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x0 + s, y0, -1, 1), (x0, y0 + s, 1, -1), (x0 + s, y0 + s, -1, -1)):
        d.line([(cx, cy), (cx + sx * L, cy)], fill=c); d.line([(cx, cy), (cx, cy + sy * L)], fill=c)
    if sel:
        for x in range(x0 - 2, x0 + s + 3, 2): d.point((x, y0 - 2), fill=CY + (140,)); d.point((x, y0 + s + 2), fill=CY + (140,))

def tabs(d, x0, y0, labels, active, w=None):
    x = x0
    for i, s in enumerate(labels):
        ww = w or int(tw(s, 9)) + 16; act = i == active
        d.polygon([(x + 4, y0), (x + ww, y0), (x + ww, y0 + 14), (x, y0 + 14), (x, y0 + 4)], fill=G0)
        d.polygon([(x + 5, y0 + 1), (x + ww - 1, y0 + 1), (x + ww - 1, y0 + 14), (x + 1, y0 + 14), (x + 1, y0 + 5)], fill=(18, 70, 80) if act else G1)
        if act: d.line([(x + 5, y0 + 1), (x + ww - 1, y0 + 1)], fill=CY)
        text(d, (x + ww / 2 + 1.5, y0 + 3), s, 9, 'b', (220, 250, 255) if act else (130, 150, 176), 'ma')
        x += ww + 2
    return x

def choice(d, x0, y0, x1, s, sel=False, mark='›'):
    d.polygon([(x0 + 4, y0), (x1, y0), (x1, y0 + 15), (x0, y0 + 15), (x0, y0 + 4)], fill=G0)
    if sel:
        for xx in range(x0 + 1, x1):
            t = (xx - x0) / max(1, x1 - x0); c = tuple(int(a + (b - a) * t) for a, b in zip(MG, (90, 30, 120)))
            d.line([(xx, y0 + 1 + (3 if xx < x0 + 4 else 0)), (xx, y0 + 14)], fill=c)
        d.line([(x0 + 5, y0 + 1), (x1 - 1, y0 + 1)], fill=(255, 150, 220))
    else: d.polygon([(x0 + 5, y0 + 1), (x1 - 1, y0 + 1), (x1 - 1, y0 + 14), (x0 + 1, y0 + 14), (x0 + 1, y0 + 5)], fill=G1)
    text(d, (x0 + 18, y0 + 3), s, 9, 'b', (240, 240, 250))

def scrollbar(d, x, y0, y1, pos=0.2):
    d.rectangle((x, y0, x + 8, y1), fill=G0); d.rectangle((x + 3, y0 + 2, x + 5, y1 - 2), fill=G1)
    ty = int(y0 + 4 + (y1 - y0 - 24) * pos); d.rectangle((x + 1, ty, x + 7, ty + 18), fill=CY2); d.rectangle((x + 2, ty + 1, x + 6, ty + 17), fill=CY)

def ribbon(d, cx, y, s, col=None, icon=None, im=None):
    w = int(tw(s, 10)) + 60; x0, x1 = int(cx - w / 2), int(cx + w / 2)
    d.polygon([(x0 - 10, y - 8), (x1 + 10, y - 8), (x1, y + 8), (x0, y + 8)], fill=G0)
    d.polygon([(x0 - 8, y - 7), (x1 + 8, y - 7), (x1 - 1, y + 7), (x0 + 1, y + 7)], fill=G1)
    d.line([(x0 - 8, y - 7), (x1 + 8, y - 7)], fill=MG); d.line([(x0 + 1, y + 7), (x1 - 1, y + 7)], fill=CY)
    for k in range(4): d.polygon([(x0 + 2 + k * 5, y + 6), (x0 + 5 + k * 5, y + 3), (x0 + 7 + k * 5, y + 3), (x0 + 4 + k * 5, y + 6)], fill=HZ if k % 2 == 0 else G0)
    text(d, (cx + 9.5, y - 6), s, 10, 'b', (220, 250, 255), 'ma', shadow=G0)
    if icon is not None and im is not None: im.alpha_composite(icon, (x0 + 22, y - 8))

def pill(d, x0, y, x1, s, icon=None, im=None):
    d.polygon([(x0, y - 8), (x1, y - 8), (x1 - 6, y + 8), (x0, y + 8)], fill=G0)
    d.polygon([(x0 + 1, y - 7), (x1 - 2, y - 7), (x1 - 7, y + 7), (x0 + 1, y + 7)], fill=G1)
    d.rectangle((x0 + 1, y - 7, x0 + 2, y + 7), fill=MG); d.line([(x0 + 3, y - 7), (x1 - 3, y - 7)], fill=CY2)
    text(d, (x0 + 26, y - 6), s, 9, 'b', (220, 240, 250))
    if icon is not None and im is not None: im.alpha_composite(icon, (x0 + 4, y - icon.height // 2))

def toggle(d, x, y, on=True):
    d.rectangle((x, y, x + 22, y + 11), fill=G0); d.rectangle((x + 1, y + 1, x + 21, y + 10), fill=(18, 70, 80) if on else G1)
    kx = x + 12 if on else x + 2; d.rectangle((kx, y + 2, kx + 8, y + 9), fill=CY if on else G3)

for name in ('frame', 'title', 'card', 'bar', 'slot', 'tabs', 'choice', 'scrollbar', 'ribbon', 'pill', 'toggle'):
    setattr(ui9, name, globals()[name]); setattr(hud9, name, globals()[name])

if __name__ == '__main__':
    lo = Image.open('/home/claude/gen/screens6/scene_lo.png').convert('RGBA'); squad, e1 = pickle.load(open('/home/claude/gen/screens6/scene_meta.pkl', 'rb'))
    hud9.save(hud9.gameplay(lo, squad, e1), '/home/claude/gen/screens/cyber_game.png')
    m = hud9.menus(); hud9.save(m, '/home/claude/gen/screens/cyber_menus.png')
    import armory2
    for nm in ('frame', 'title', 'card', 'bar', 'slot', 'tabs', 'choice', 'scrollbar'): setattr(armory2, nm, globals()[nm])
    hud9.save(armory2.armory(), '/home/claude/gen/screens/cyber_armory.png')
    print('ok')
