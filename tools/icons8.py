"""Coloured 16x16 pixel icons: each drawn with 2-4 tone ramps, then auto dark outline + top-left highlight.
Always used at integer scale (x1 or x2 in low-res) so pixels stay square."""
import math
from PIL import Image, ImageDraw

OUT = (14, 12, 22, 255)
def C(*v): return tuple(v) + (255,)
STEEL = [C(70, 78, 96), C(120, 130, 150), C(176, 186, 204), C(232, 238, 246)]
WOOD = [C(86, 52, 32), C(132, 84, 48), C(178, 122, 70)]
RED = [C(120, 24, 30), C(196, 44, 44), C(240, 96, 80)]
GRN = [C(24, 90, 50), C(52, 160, 80), C(130, 222, 120)]
BLU = [C(24, 54, 120), C(52, 120, 210), C(120, 196, 250)]
GOLDR = [C(130, 80, 20), C(214, 150, 40), C(250, 214, 100)]
PAPER = [C(170, 140, 96), C(222, 200, 152), C(248, 236, 204)]
SKIN = [C(150, 90, 60), C(214, 150, 108), C(244, 196, 156)]
TEAL = [C(20, 100, 96), C(40, 180, 160), C(140, 240, 220)]
PURP = [C(60, 30, 100), C(120, 70, 190), C(190, 150, 250)]

def finish(im):
    """Add 1px dark outline around opaque pixels and nothing else (icons drawn inside 1px margin)."""
    W, H = im.size; px = im.load(); out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); po = out.load()
    for y in range(H):
        for x in range(W):
            if px[x, y][3] == 0 and any(0 <= x + dx < W and 0 <= y + dy < H and px[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                po[x, y] = OUT
    out.alpha_composite(im); return out

def new(): im = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

def ic_play():
    im, d = new(); d.polygon([(4, 2), (13, 8), (4, 14)], fill=GRN[1]); d.polygon([(4, 2), (13, 8), (8, 8), (4, 5)], fill=GRN[2]); d.line([(4, 13), (12, 9)], fill=GRN[0]); return finish(im)
def ic_restart():
    im, d = new(); d.arc((2, 2, 13, 13), 60, 360, fill=GOLDR[1], width=3); d.arc((2, 2, 13, 13), 200, 300, fill=GOLDR[2], width=1)
    d.polygon([(9, 1), (14, 4), (9, 7)], fill=GOLDR[2]); return finish(im)
def ic_book():
    im, d = new(); d.rectangle((2, 3, 13, 13), fill=RED[1]); d.rectangle((2, 3, 4, 13), fill=RED[0]); d.rectangle((5, 4, 13, 12), fill=PAPER[2])
    d.rectangle((5, 12, 13, 13), fill=PAPER[1]); [d.line([(7, y), (12, y)], fill=PAPER[0]) for y in (6, 8, 10)]; d.rectangle((10, 2, 11, 7), fill=GOLDR[1]); return finish(im)
def ic_gear():
    im, d = new()
    for a in range(8):
        t = a * math.pi / 4; x, y = 7.5 + 5.5 * math.cos(t), 7.5 + 5.5 * math.sin(t); d.rectangle((x - 1, y - 1, x + 1, y + 1), fill=STEEL[1])
    d.ellipse((3, 3, 12, 12), fill=STEEL[1]); d.ellipse((3, 3, 10, 10), fill=STEEL[2]); d.ellipse((6, 6, 9, 9), fill=STEEL[0]); d.point((5, 4), fill=STEEL[3]); return finish(im)
def ic_quit():
    im, d = new(); d.rectangle((7, 1, 14, 14), fill=WOOD[1]); d.rectangle((8, 2, 13, 13), fill=WOOD[0]); d.rectangle((8, 2, 9, 13), fill=C(30, 18, 12))
    d.rectangle((1, 7, 8, 9), fill=RED[1]); d.polygon([(6, 4), (10, 8), (6, 12)], fill=RED[2]); return finish(im)
def ic_grid():
    im, d = new()
    for (a, b, r) in ((2, 2, BLU), (9, 2, GRN), (2, 9, GOLDR), (9, 9, RED)): d.rectangle((a, b, a + 4, b + 4), fill=r[1]); d.rectangle((a, b, a + 4, b), fill=r[2])
    return finish(im)
def ic_climb():
    im, d = new(); d.rectangle((3, 1, 4, 14), fill=WOOD[1]); d.rectangle((11, 1, 12, 14), fill=WOOD[1]); d.line([(3, 1), (3, 14)], fill=WOOD[2])
    for y in (3, 7, 11): d.rectangle((5, y, 10, y + 1), fill=WOOD[2]); d.line([(5, y + 1), (10, y + 1)], fill=WOOD[0])
    return finish(im)
def ic_knife():
    im, d = new(); d.polygon([(4, 11), (12, 2), (14, 2), (14, 4), (6, 13)], fill=STEEL[2]); d.line([(5, 11), (13, 3)], fill=STEEL[3]); d.line([(6, 12), (14, 4)], fill=STEEL[1])
    d.rectangle((3, 10, 6, 11), fill=GOLDR[1]); d.polygon([(1, 13), (3, 11), (5, 13), (3, 15)], fill=WOOD[1]); d.point((2, 13), fill=WOOD[2]); return finish(im)
def ic_stone():
    im, d = new(); d.ellipse((2, 4, 13, 13), fill=STEEL[1]); d.ellipse((3, 5, 10, 10), fill=STEEL[2]); d.point((5, 6), fill=STEEL[3]); d.point((6, 6), fill=STEEL[3]); d.arc((2, 4, 13, 13), 20, 160, fill=STEEL[0]); return finish(im)
def ic_throw():
    im, d = new()
    for k in range(9): d.point((1 + k, 13 - int(9 * math.sin(k / 9 * math.pi * 0.85))), fill=GOLDR[2] if k % 2 else GOLDR[1])
    d.ellipse((9, 2, 14, 7), fill=STEEL[1]); d.ellipse((9, 2, 12, 5), fill=STEEL[2]); return finish(im)
def ic_map():
    im, d = new(); d.polygon([(1, 3), (5, 1), (10, 3), (14, 1), (14, 12), (10, 14), (5, 12), (1, 14)], fill=PAPER[1])
    d.polygon([(5, 1), (10, 3), (10, 14), (5, 12)], fill=PAPER[2]); d.line([(2, 9), (6, 7), (9, 9), (13, 6)], fill=BLU[1]); d.point((11, 5), fill=RED[1]); d.point((11, 4), fill=RED[2]); return finish(im)
def ic_pick():
    im, d = new(); d.ellipse((1, 8, 7, 14), fill=GOLDR[1]); d.ellipse((3, 10, 5, 12), fill=C(40, 30, 20)); d.line([(6, 9), (13, 2)], fill=STEEL[2], width=2); d.line([(11, 2), (14, 5)], fill=STEEL[2]); return finish(im)
def ic_drone():
    im, d = new()
    for (a, b) in ((1, 1), (10, 1), (1, 10), (10, 10)): d.ellipse((a, b, a + 4, b + 4), fill=STEEL[2]); d.point((a + 2, b + 2), fill=STEEL[0])
    d.line([(4, 4), (11, 11)], fill=STEEL[1]); d.line([(11, 4), (4, 11)], fill=STEEL[1]); d.rectangle((5, 5, 10, 10), fill=TEAL[1]); d.rectangle((6, 6, 8, 7), fill=TEAL[2]); d.point((9, 9), fill=RED[2]); return finish(im)
def ic_trap():
    im, d = new(); d.rectangle((1, 11, 14, 13), fill=STEEL[1]); d.line([(1, 11), (14, 11)], fill=STEEL[2])
    for k in range(1, 13, 3): d.polygon([(k, 11), (k + 1, 5), (k + 2, 11)], fill=STEEL[2])
    d.point((7, 13), fill=RED[2]); return finish(im)
def ic_wrench():
    im, d = new(); d.line([(3, 13), (10, 6)], fill=STEEL[1], width=3); d.line([(3, 12), (9, 6)], fill=STEEL[2]); d.ellipse((8, 1, 14, 7), fill=STEEL[2]); d.rectangle((10, 1, 12, 4), fill=(0, 0, 0, 0)); return finish(im)
def ic_pistol():
    im, d = new(); d.rectangle((1, 4, 13, 7), fill=STEEL[1]); d.line([(1, 4), (13, 4)], fill=STEEL[3]); d.rectangle((8, 7, 11, 13), fill=WOOD[1]); d.line([(8, 7), (8, 13)], fill=WOOD[2])
    d.rectangle((6, 8, 7, 9), fill=STEEL[0]); return finish(im)
def ic_bandage():
    im, d = new(); d.rectangle((1, 5, 14, 10), fill=PAPER[2]); d.rectangle((1, 9, 14, 10), fill=PAPER[1]); d.rectangle((5, 5, 10, 10), fill=RED[1]); d.rectangle((7, 6, 8, 9), fill=C(255, 255, 255)); d.rectangle((6, 7, 9, 8), fill=C(255, 255, 255)); return finish(im)
def ic_eye():
    im, d = new(); d.ellipse((1, 4, 14, 12), fill=C(236, 240, 244)); d.ellipse((5, 4, 10, 11), fill=TEAL[1]); d.ellipse((6, 6, 9, 9), fill=C(20, 30, 40)); d.point((7, 6), fill=C(255, 255, 255)); return finish(im)
def ic_heart():
    im, d = new(); d.ellipse((1, 2, 8, 9), fill=RED[1]); d.ellipse((7, 2, 14, 9), fill=RED[1]); d.polygon([(1, 6), (14, 6), (7, 14)], fill=RED[1]); d.ellipse((3, 3, 6, 6), fill=RED[2]); return finish(im)
def ic_clock():
    im, d = new(); d.ellipse((1, 1, 14, 14), fill=GOLDR[1]); d.ellipse((3, 3, 12, 12), fill=PAPER[2]); d.line([(7, 4), (7, 8), (10, 10)], fill=C(40, 30, 20)); return finish(im)
def ic_trophy():
    im, d = new(); d.rectangle((4, 2, 11, 8), fill=GOLDR[1]); d.rectangle((4, 2, 6, 8), fill=GOLDR[2]); d.arc((1, 2, 6, 8), 90, 270, fill=GOLDR[1]); d.arc((9, 2, 14, 8), 270, 90, fill=GOLDR[1])
    d.rectangle((7, 9, 8, 11), fill=GOLDR[0]); d.rectangle((4, 12, 11, 14), fill=WOOD[1]); return finish(im)
def ic_star():
    im, d = new(); pts = [(7.5 + (7 if i % 2 == 0 else 3) * math.cos(-math.pi / 2 + i * math.pi / 5), 8 + (7 if i % 2 == 0 else 3) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
    d.polygon(pts, fill=GOLDR[1]); d.polygon([(7.5, 1), (9, 6), (6, 6)], fill=GOLDR[2]); return finish(im)
def ic_figure(pose, col):
    im, d = new(); body = col
    if pose == 'stand': d.ellipse((6, 1, 9, 4), fill=SKIN[1]); d.rectangle((6, 5, 9, 10), fill=body[1]); d.rectangle((6, 11, 7, 14), fill=C(40, 44, 70)); d.rectangle((8, 11, 9, 14), fill=C(40, 44, 70)); d.rectangle((5, 5, 5, 9), fill=body[0]); d.rectangle((10, 5, 10, 9), fill=body[2])
    elif pose == 'crouch': d.ellipse((5, 4, 8, 7), fill=SKIN[1]); d.polygon([(5, 8), (10, 8), (11, 12), (5, 12)], fill=body[1]); d.rectangle((4, 12, 11, 14), fill=C(40, 44, 70)); d.point((10, 9), fill=body[2])
    else: d.ellipse((1, 8, 4, 11), fill=SKIN[1]); d.rectangle((5, 9, 11, 12), fill=body[1]); d.rectangle((11, 10, 14, 12), fill=C(40, 44, 70)); d.line([(5, 9), (11, 9)], fill=body[2])
    return finish(im)

ICONS = {'play': ic_play, 'restart': ic_restart, 'book': ic_book, 'gear': ic_gear, 'quit': ic_quit, 'grid': ic_grid, 'climb': ic_climb, 'knife': ic_knife,
         'stone': ic_stone, 'throw': ic_throw, 'map': ic_map, 'pick': ic_pick, 'drone': ic_drone, 'trap': ic_trap, 'wrench': ic_wrench, 'pistol': ic_pistol,
         'bandage': ic_bandage, 'eye': ic_eye, 'heart': ic_heart, 'clock': ic_clock, 'trophy': ic_trophy, 'star': ic_star,
         'stand': lambda: ic_figure('stand', GRN), 'crouch': lambda: ic_figure('crouch', GRN), 'crawl': lambda: ic_figure('crawl', GRN)}
_cache = {}
def icon(name, k=1):
    if (name, k) not in _cache:
        im = ICONS[name](); _cache[(name, k)] = im.resize((16 * k, 16 * k), Image.NEAREST) if k > 1 else im
    return _cache[(name, k)].copy()
