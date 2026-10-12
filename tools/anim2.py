import sys, json; sys.path.insert(0, '.')
import lpc
from PIL import Image, ImageDraw
MAIN = ('Dương', 'Hùng', 'Ny', 'Sơn')
_CACHE = {}
STYLE = {'v': 'C'}
def fr(name, anim, row, col):
    key = (STYLE['v'], name, anim, row, col)
    if key in _CACHE: return _CACHE[key].copy()
    if STYLE['v'] == 'C':
        import polish
        src = 'B_' + name if name in MAIN else name
        s = lpc.sheet(src, anim)
        if s is None: s = lpc.sheet(name, anim)
        f = polish.polish(s.crop((col * 64, row * 64, col * 64 + 64, row * 64 + 64)))
    else:
        s = lpc.sheet(name, anim); f = s.crop((col * 64, row * 64, col * 64 + 64, row * 64 + 64))
    _CACHE[key] = f
    return f.copy()
def cell(): return Image.new('RGBA', (64, 64), (0, 0, 0, 0))

def door(c, x, state=0, shake=0):
    d = ImageDraw.Draw(c)
    if state < 2:
        x += shake
        d.rectangle((x, 18, x + 12, 56), fill=(110, 78, 48, 255), outline=(50, 34, 20, 255))
        for yy in range(24, 56, 8): d.line([(x + 1, yy), (x + 11, yy)], fill=(80, 56, 34, 255))
        d.point((x + 3, 38), fill=(220, 190, 110, 255))
        if state == 1: d.line([(x + 4, 20), (x + 8, 34), (x + 5, 46)], fill=(30, 20, 12, 255))
    else:
        d.polygon([(x + 2, 56), (x + 14, 50), (x + 22, 56), (x + 10, 60)], fill=(110, 78, 48, 255), outline=(50, 34, 20, 255))
        for p in ((x - 2, 52), (x + 20, 46), (x + 24, 58)): d.rectangle((p[0], p[1], p[0] + 3, p[1] + 1), fill=(90, 62, 38, 255))

def lock(c, x, y, opened=False):
    d = ImageDraw.Draw(c)
    if opened: d.arc((x - 1, y - 8, x + 6, y), 180, 360, fill=(200, 200, 190, 255)); d.line([(x + 6, y - 4), (x + 6, y - 9)], fill=(200, 200, 190, 255))
    else: d.arc((x, y - 6, x + 6, y + 1), 180, 360, fill=(200, 200, 190, 255))
    d.rectangle((x - 1, y - 2, x + 7, y + 5), fill=(214, 176, 70, 255), outline=(90, 70, 20, 255))

def break_door(who='Hùng'):
    out = []
    for i in range(4):
        c = cell(); door(c, 46); c.alpha_composite(fr(who, 'walk', 3, 1 + i * 2), (-14 + i * 4, 0)); out.append(c)
    c = cell(); door(c, 46, 0, 1); c.alpha_composite(fr(who, 'thrust', 3, 5), (2, 0)); out.append(c)
    c = cell(); door(c, 46, 1, -1); c.alpha_composite(fr(who, 'thrust', 3, 6), (3, 0)); out.append(c)
    c = cell(); door(c, 46, 1, 1); c.alpha_composite(fr(who, 'thrust', 3, 5), (4, 0)); out.append(c)
    for i in range(3):
        c = cell(); door(c, 44, 2); c.alpha_composite(fr(who, 'idle', 3, i % 2), (6, 0)); out.append(c)
    return out

def choke(who='Hùng'):
    out = []
    for i in range(3):
        c = cell(); c.alpha_composite(fr('Biến Thể', 'walk', 3, 0), (10, 0)); c.alpha_composite(fr(who, 'walk', 3, 1 + i * 2), (-22 + i * 5, 0)); out.append(c)
    for i in range(4):
        c = cell(); z = fr('Biến Thể', 'hurt', 0, min(i, 1)); c.alpha_composite(z, (10, 0))
        c.alpha_composite(fr(who, 'thrust', 3, 4 + (i % 2)), (-4, 0)); out.append(c)
    from knock import lying
    L = lying('Biến Thể')
    for i in range(3):
        c = cell(); d = ImageDraw.Draw(c); d.ellipse((24, 55, 24 + L.width, 60), fill=(0, 0, 0, 80)); c.alpha_composite(L, (24, 58 - L.height)); c.alpha_composite(fr(who, 'idle', 3, i % 2), (-6, 0)); out.append(c)
    return out

def pick_lock(who='Sơn'):
    out = []
    for i in range(10):
        c = cell(); opened = i >= 8
        d = ImageDraw.Draw(c)
        if not opened: door(c, 44)
        else:
            d.rectangle((44, 18, 47, 56), fill=(110, 78, 48, 255), outline=(50, 34, 20, 255)); d.rectangle((48, 18, 56, 56), fill=(18, 14, 10, 255))
        lock(c, 46, 36, opened)
        pose = fr(who, 'spellcast', 3, 1 + (i % 2)) if not opened else fr(who, 'idle', 3, 0)
        c.alpha_composite(pose, (4, 0))
        d = ImageDraw.Draw(c)
        if not opened and i % 2 == 1: d.point((45, 38), fill=(255, 250, 200, 255)); d.point((44, 37), fill=(255, 220, 120, 255))
        d.rectangle((24, 8, 48, 11), fill=(20, 24, 22, 255), outline=(60, 66, 58, 255))
        d.rectangle((25, 9, 25 + min(22, int(22 * (i + 1) / 8)), 10), fill=(63, 217, 180, 255))
        out.append(c)
    return out

def look_around():
    out = []
    for row, mark in ((2, False), (1, False), (0, True), (3, True)):
        for k in range(2):
            c = cell(); c.alpha_composite(fr('Biến Thể', 'walk', row, 0), (0, 0))
            if mark:
                d = ImageDraw.Draw(c); d.rectangle((39, 4, 46, 13), fill=(255, 214, 92, 255), outline=(60, 40, 10, 255)); d.text((40, 3), '?', fill=(40, 26, 8, 255))
            out.append(c)
    return out

def strip(frames):
    s = Image.new('RGBA', (64 * len(frames), 64), (0, 0, 0, 0))
    for i, f in enumerate(frames): s.alpha_composite(f, (i * 64, 0))
    return s

if __name__ == '__main__':
    meta = json.load(open('anim_meta.json'))
    old = Image.open('/mnt/user-data/outputs/artifacts/c82b9169-ee10-4565-aca3-4592040c933d/anim_sheet.png')
    repl = {('Hùng', 'Phá cửa'): ('Phá cửa', break_door()), ('Hùng', 'Khóa siết'): ('Khóa siết từ sau', choke()),
            ('Sơn', 'Mở khóa'): ('Mở khóa cửa', pick_lock()), ('Biến Thể', 'Đẩy'): ('Quay đầu nghe ngóng', look_around())}
    rows = []; newmeta = []
    for i, (n, lab, cnt) in enumerate(meta):
        if (n, lab) in repl:
            lab2, frames = repl[(n, lab)]; rows.append(strip(frames)); newmeta.append((n, lab2, len(frames), 'scene'))
        else:
            rows.append(old.crop((0, i * 64, cnt * 64, i * 64 + 64))); newmeta.append((n, lab, cnt, 'loop'))
    sheet = Image.new('RGBA', (640, 64 * len(rows)), (0, 0, 0, 0))
    for i, r in enumerate(rows): sheet.alpha_composite(r, (0, i * 64))
    sheet.save('/mnt/user-data/outputs/artifacts/c82b9169-ee10-4565-aca3-4592040c933d/anim_sheet2.png', optimize=True)
    json.dump(newmeta, open('anim_meta2.json', 'w'), ensure_ascii=False)
    chk = Image.new('RGBA', (640, 64 * 4), (60, 80, 60, 255))
    for k, (key) in enumerate(repl):
        chk.alpha_composite(strip(repl[key][1]), (0, k * 64))
    chk.resize((1280, 512), Image.NEAREST).save('/tmp/anim2.png')
    print('ok')
