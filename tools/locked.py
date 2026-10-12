"""LOCKED UI STYLE — 'UI v10 · Cyberpunk nhà máy' (chốt). Colours sampled from the approved board.
Rules: dark slate panels with scanlines, thin teal outline, cyan ruler ticks top-left/bottom-left, R/Y/G LEDs top-right,
magenta parallelogram title tab, teal corner-bracket slots, magenta brackets + dotted cap for the selected item,
segmented bars, parallelogram tabs (active = magenta)."""
import sys; sys.path.insert(0, '/home/claude/gen')
import cyber, ui9, hud9
from ui5 import text, tw

BG = (8, 10, 16); GRID = (14, 18, 28); PANEL = (18, 22, 32); SCAN = (16, 20, 30); EDGE = (24, 96, 120); TICK = (62, 236, 255)
MAG = (110, 20, 74); MAG_HI = (255, 58, 168); MAG_LO = (56, 16, 44); SLOT = (22, 28, 40); INK = (216, 244, 255); DIM = (120, 150, 176)
LED = ((240, 70, 80), (240, 200, 60), (80, 220, 120))

def background(im):
    from PIL import ImageDraw
    d = ImageDraw.Draw(im); d.rectangle((0, 0, im.width, im.height), fill=BG)
    for x in range(0, im.width, 16): d.line([(x, 0), (x, im.height)], fill=GRID)
    for y in range(0, im.height, 16): d.line([(0, y), (im.width, y)], fill=GRID)

def frame(d, x0, y0, x1, y1, fill=None):
    d.rectangle((x0 + 2, y0 + 2, x1 + 2, y1 + 2), fill=(0, 0, 0, 120))
    d.rectangle((x0, y0, x1, y1), fill=(4, 6, 10)); d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=fill or PANEL)
    for y in range(y0 + 3, y1 - 1, 2): d.line([(x0 + 2, y), (x1 - 2, y)], fill=SCAN)
    d.line([(x0 + 1, y0 + 1), (x1 - 4, y0 + 1)], fill=EDGE); d.line([(x0 + 1, y0 + 1), (x0 + 1, y1 - 4)], fill=EDGE)
    d.line([(x1 - 1, y0 + 4), (x1 - 1, y1 - 1)], fill=EDGE); d.line([(x0 + 4, y1 - 1), (x1 - 1, y1 - 1)], fill=EDGE)
    d.line([(x1 - 4, y0 + 1), (x1 - 1, y0 + 4)], fill=TICK); d.line([(x0 + 1, y1 - 4), (x0 + 4, y1 - 1)], fill=TICK)
    # ruler ticks (top-left run + bottom-left run)
    L = min(70, (x1 - x0) // 3)
    d.line([(x0 + 2, y0 - 2), (x0 + 2 + L, y0 - 2)], fill=TICK)
    for k in range(0, L, 2): d.point((x0 + 2 + k, y0 - 3), fill=TICK)
    d.line([(x0 - 2, y0 + 2), (x0 - 2, y0 + 16)], fill=TICK)
    for k in range(0, 30, 2): d.point((x0 + 4 + k, y1 + 2), fill=TICK)
    d.line([(x0 - 2, y1 - 10), (x0 - 2, y1)], fill=TICK)
    for k, c in enumerate(LED): d.rectangle((x1 - 22 + k * 6, y0 + 4, x1 - 19 + k * 6, y0 + 6), fill=c)
    d.point((x1 - 4, y1 - 4), fill=DIM)
    return (x0 + 6, y0 + 8, x1 - 6, y1 - 6)

def title(d, cx, y, s, w=None):
    s = s.upper(); w = max(w or 0, int(tw(s, 10)) + 34); x0, x1 = int(cx - w / 2), int(cx + w / 2)
    d.polygon([(x0 + 6, y - 8), (x1 + 2, y - 8), (x1 - 4, y + 8), (x0, y + 8)], fill=MAG_LO)
    d.polygon([(x0 + 5, y - 9), (x1, y - 9), (x1 - 6, y + 7), (x0 - 1, y + 7)], fill=MAG)
    d.polygon([(x0 + 5, y - 9), (x0 + 9, y - 9), (x0 + 3, y + 7), (x0 - 1, y + 7)], fill=MAG_HI)
    d.line([(x0 + 9, y - 9), (x1, y - 9)], fill=(170, 40, 120))
    text(d, (cx + 2.5, y - 8), s, 10, 'b', INK, 'ma', shadow=(30, 6, 22))

def brackets(d, x0, y0, x1, y1, c, L=3):
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx, cy), (cx + sx * L, cy)], fill=c); d.line([(cx, cy), (cx, cy + sy * L)], fill=c)

def slot(d, x0, y0, s=22, sel=False):
    d.rectangle((x0 + 1, y0 + 1, x0 + s - 1, y0 + s - 1), fill=SLOT)
    brackets(d, x0, y0, x0 + s, y0 + s, MAG_HI if sel else EDGE)
    if sel:
        for x in range(x0, x0 + s + 1, 2): d.point((x, y0 - 2), fill=MAG_HI)

def card(d, x0, y0, x1, y1, sel=False):
    d.rectangle((x0, y0, x1, y1), fill=(58, 14, 42) if sel else SLOT)
    if sel:
        for y in range(y0 + 1, y1, 2): d.line([(x0 + 1, y), (x1 - 1, y)], fill=(70, 18, 52))
        d.rectangle((x0, y0, x0 + 1, y1), fill=MAG_HI); brackets(d, x0, y0, x1, y1, MAG_HI, 4)
    else: brackets(d, x0, y0, x1, y1, (40, 56, 76), 3)

def tabs(d, x0, y0, labels, active, w=None):
    x = x0
    for i, s in enumerate(labels):
        ww = w or int(tw(s, 9)) + 18; act = i == active
        d.polygon([(x + 4, y0), (x + ww + 2, y0), (x + ww - 2, y0 + 14), (x, y0 + 14)], fill=MAG if act else (30, 38, 54))
        if act: d.line([(x + 4, y0), (x + ww + 2, y0)], fill=MAG_HI)
        text(d, (x + ww / 2 + 1.5, y0 + 3), s, 9, 'b', INK if act else DIM, 'ma')
        x += ww + 3
    return x

def choice(d, x0, y0, x1, s, sel=False, mark='›'):
    d.rectangle((x0, y0, x1, y0 + 15), fill=(70, 16, 52) if sel else (24, 30, 44))
    if sel:
        d.rectangle((x0, y0, x0 + 1, y0 + 15), fill=MAG_HI); d.line([(x0 + 2, y0), (x1, y0)], fill=MAG_HI)
        d.polygon([(x1 - 8, y0 + 4), (x1 - 3, y0 + 8), (x1 - 8, y0 + 12)], fill=INK)
    text(d, (x0 + 18, y0 + 3), s, 9, 'b', INK)

def bar(d, x, y, w, frac, col, h=4, label=None):
    if label: text(d, (x - 1, y - 3), label, 8, 'b', DIM, 'ra')
    n = max(4, w // 5); on = int(round(n * frac))
    for i in range(n):
        xx = x + i * (w / n); d.rectangle((xx, y, xx + w / n - 2, y + h), fill=col if i < on else (30, 36, 52))
        if i < on: d.line([(xx, y), (xx + w / n - 2, y)], fill=tuple(min(255, v + 60) for v in col))

def scrollbar(d, x, y0, y1, pos=0.2):
    d.line([(x + 4, y0), (x + 4, y1)], fill=(30, 40, 58)); ty = int(y0 + 2 + (y1 - y0 - 22) * pos); d.rectangle((x + 2, ty, x + 6, ty + 18), fill=TICK)

for name in ('frame', 'title', 'slot', 'card', 'tabs', 'choice', 'bar', 'scrollbar'):
    for m in (cyber, ui9, hud9): setattr(m, name, globals()[name])
cyber.CY = TICK; cyber.CY2 = EDGE; cyber.MG = MAG_HI; cyber.G3 = (60, 76, 100)
