import sys, json, random; sys.path.insert(0, '.')
import lpc
from PIL import Image, ImageDraw
from anim2 import fr, strip

def grass(c, seed):
    d = ImageDraw.Draw(c); rng = random.Random(seed)
    for x in range(0, 64, 2):
        h = rng.randint(2, 5); col = rng.choice([(58, 104, 52, 255), (74, 128, 60, 255), (46, 86, 44, 255)])
        d.line([(x, 63), (x + rng.choice((-1, 0, 1)), 63 - h)], fill=col)

COL = {
    'Dương': dict(top=(62, 98, 50), sleeve=(62, 98, 50), skin=(232, 172, 128), pants=(46, 66, 128), shoes=(106, 70, 40)),
    'Hùng': dict(top=(52, 52, 56), sleeve=(176, 118, 80), skin=(176, 118, 80), pants=(178, 152, 102), shoes=(30, 28, 26)),
    'Ny': dict(top=(236, 232, 224), sleeve=(236, 232, 224), skin=(246, 204, 172), pants=(52, 52, 60), shoes=(240, 238, 230)),
    'Sơn': dict(top=(30, 140, 170), sleeve=(30, 140, 170), skin=(232, 172, 128), pants=(42, 44, 50), shoes=(110, 116, 124), pack=(32, 38, 42)),
    'Biến Thể': dict(top=(112, 112, 118), sleeve=(112, 112, 118), skin=(204, 198, 168), pants=(196, 196, 190), shoes=(150, 120, 100)),
}
def _shade(c, k): return tuple(max(0, min(255, int(v * k))) for v in c) + (255,)

def crawl(name, zombie=False, neck=36):
    """Hand-built 3/4 prone crawl: real LPC head in profile + drawn body lying chest-down,
    arms reaching forward along the ground and knees pushing, alternating over 8 frames."""
    c_ = COL[name]; out = []
    side = fr(name, 'walk', 1, 0)
    head = side.crop((0, 0, 64, neck)); head = head.crop(head.getbbox())
    for i in range(8):
        ph = i / 8 * 2 * 3.14159
        import math
        s_ = math.sin(ph)
        body = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(body)
        G = 57
        # far limbs (darker, behind)
        def limb(pts, col, w): d.line(pts, fill=col, width=w, joint='curve')
        t1 = (s_ + 1) / 2; t2 = 1 - t1          # 0 = leg straight back, 1 = knee pulled forward
        def leg(t):
            knee = (51 - 7 * t, 54 + 1 * t); foot = (60 - 7 * t, 55 - 2 * t); return knee, foot
        def arm(t):                              # 1 = reaching forward, 0 = pulled back under the chest
            elbow = (27 - 9 * t, 55 - 1 * t); hand = (24 - 13 * t, 56 - 1 * t); return elbow, hand
        kb, fb = leg(t2); eb, hb = arm(t1)
        limb([(41, 52), kb, fb], _shade(c_['pants'], 0.75), 4); d.rectangle((fb[0] - 1, fb[1] - 1, fb[0] + 2, fb[1] + 1), fill=_shade(c_['shoes'], 0.75))
        limb([(24, 50), eb, hb], _shade(c_['sleeve'], 0.75), 4); d.rectangle((hb[0] - 2, hb[1] - 1, hb[0], hb[1] + 1), fill=_shade(c_['skin'], 0.8))
        ka, fa = leg(t1); ea, ha = arm(t2)
        # torso + hips
        d.rounded_rectangle((20, 46, 40, 55), 4, fill=c_['top'] + (255,))
        if 'pack' in c_: d.rounded_rectangle((25, 42, 37, 49), 2, fill=c_['pack'] + (255,))
        d.rounded_rectangle((36, 47, 45, 55), 3, fill=c_['pants'] + (255,))
        # near limbs
        limb([(41, 53), ka, fa], c_['pants'] + (255,), 4); d.rectangle((fa[0] - 1, fa[1] - 1, fa[0] + 2, fa[1] + 1), fill=c_['shoes'] + (255,))
        limb([(24, 51), ea, ha], c_['sleeve'] + (255,), 4); d.rectangle((ha[0] - 2, ha[1] - 1, ha[0], ha[1] + 1), fill=c_['skin'] + (255,))
        # shading + outline
        px = body.load(); W, H = body.size
        sol = [[px[x, y][3] > 0 for x in range(W)] for y in range(H)]
        sh = body.copy(); ps = sh.load()
        for y in range(H):
            for x in range(W):
                if not sol[y][x]: continue
                r, g, b, a = px[x, y]
                if y + 1 < H and not sol[y + 1][x]: ps[x, y] = _shade((r, g, b), 0.72)
                elif y - 1 >= 0 and not sol[y - 1][x]: ps[x, y] = _shade((r, g, b), 1.15)
        cell = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); pc = cell.load()
        for y in range(H):
            for x in range(W):
                if not sol[y][x] and any(0 <= x + dx < W and 0 <= y + dy < H and sol[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    pc[x, y] = (24, 18, 16, 255)
        cell.alpha_composite(sh)
        # head in profile resting on the shoulders, chin slightly up
        cell.alpha_composite(head, (22 - head.width + 8, 50 - head.height + (1 if i % 4 in (1, 2) else 0)))
        final = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); dd = ImageDraw.Draw(final)
        dd.ellipse((8, G - 2, 62, G + 2), fill=(0, 0, 0, 80))
        final.alpha_composite(cell, (2 - (i // 3), 0))
        import polish
        final = polish.polish(final) if name in ('Dương', 'Hùng', 'Ny', 'Sơn') else final
        grass(final, 7)
        out.append(final)
    return out

if __name__ == '__main__':
    rows = {n: crawl(n) for n in ('Dương', 'Hùng', 'Ny', 'Sơn', 'Biến Thể')}
    chk = Image.new('RGBA', (512, 320), (40, 60, 44, 255))
    for k, (n, fs) in enumerate(rows.items()):
        chk.alpha_composite(strip(fs), (0, k * 64))
    chk.resize((1024, 640), Image.NEAREST).save('/tmp/crawl.png')
    print('ok')
