import json, os
from PIL import Image

L = '/home/claude/lpc'
def J(p): return json.load(open(f'{L}/{p}'))
PALS = {'hair': J('palette_definitions/hair/hair_ulpc.json') | J('palette_definitions/hair/hair_lpcr.json'),
        'body': J('palette_definitions/body/body_ulpc.json'), 'cloth': J('palette_definitions/cloth/cloth_ulpc.json')}
BASE = {'hair': 'orange', 'body': 'light', 'cloth': 'white'}

def hx(c): c = c.lstrip('#'); return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

def recolor(im, material, target):
    if not material or not target: return im
    srcpal = J('palette_definitions/hair/hair_ulpc.json')[BASE[material]] if material == 'hair' else PALS[material][BASE[material]]
    src = [hx(c) for c in srcpal]
    dst = [hx(c) for c in PALS[material][target]]
    mp = {s: d for s, d in zip(src, dst)}
    im = im.convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in mp: px[x, y] = mp[(r, g, b)] + (a,)
    return im

def layer(defpath, bodytype, anim, color=None, material=None):
    d = J('sheet_definitions/' + defpath)
    out = []
    for k, v in d.items():
        if not k.startswith('layer_'): continue
        p = v.get(bodytype) or v.get('male')
        if not p: continue
        f = f'{L}/spritesheets/{p}{anim}.png'
        if not os.path.exists(f):
            dd = f'{L}/spritesheets/{p}{anim}'
            if os.path.isdir(dd):
                cands = sorted(x for x in os.listdir(dd) if x.endswith('.png'))
                pick = [x for x in cands if color and x.startswith(color)] or cands
                if not pick: continue
                f = f'{dd}/{pick[0]}'
            else: continue
        if material and str(material).startswith('tint'):
            im = Image.open(f).convert('RGBA'); tc = tuple(int(material[5 + i * 2:7 + i * 2], 16) for i in range(3))
            import numpy as _np
            A = _np.array(im).astype(_np.float32); Lm = A[..., :3].mean(axis=2, keepdims=True) / 255
            A[..., :3] = _np.array(tc) * (0.35 + 0.9 * Lm); im = Image.fromarray(A.clip(0, 255).astype(_np.uint8))
        else:
            mat = material or (d.get('recolors') or {}).get('material') if isinstance(d.get('recolors'), dict) else material
            im = recolor(Image.open(f), mat, color)
        out.append((v.get('zPos', 0), im))
    return out

def compose(parts, bodytype, anim):
    layers = []
    for defpath, color, mat in parts:
        layers += layer(defpath, bodytype, anim, color, mat)
    if not layers: return None
    W = max(im.width for _, im in layers); H = max(im.height for _, im in layers)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for z, im in sorted(layers, key=lambda t: t[0]):
        out.alpha_composite(im.convert('RGBA'), (0, 0))
    return out

CHARS = {
    'Dương': ('male', [('body/body.json', 'amber', 'body'), ('head/heads/human/heads_human_male.json', 'amber', 'body'),
                       ('legs/pants/legs_pants.json', 'navy', 'cloth'), ('feet/boots/feet_boots_basic.json', 'brown', 'cloth'),
                       ('torso/shirts/longsleeve/torso_clothes_longsleeve2_cardigan.json', 'forest', 'cloth'), ('hair/short/hair_bedhead.json', 'black', 'hair')]),
    'Hùng': ('muscular', [('body/body.json', 'olive', 'body'), ('head/heads/human/heads_human_male.json', 'olive', 'body'),
                          ('legs/pants/legs_pants.json', 'tan', 'cloth'), ('feet/shoes/feet_shoes_basic.json', 'black', 'cloth'),
                          ('torso/shirts/sleeveless/torso_clothes_sleeveless2.json', 'charcoal', 'cloth'), ('hair/bald/hair_buzzcut.json', 'black', 'hair')]),
    'Ny': ('female', [('body/body.json', 'light', 'body'), ('head/heads/human/heads_human_female.json', 'light', 'body'),
                      ('legs/leggings/legs_leggings.json', 'black', 'cloth'), ('feet/shoes/feet_shoes_basic.json', 'white', 'cloth'),
                      ('torso/shirts/longsleeve/torso_clothes_longsleeve2.json', 'white', 'cloth'), ('hair/long/hair_bangslong.json', 'dark_brown', 'hair')]),
    'Sơn': ('male', [('body/body.json', 'amber', 'body'), ('head/heads/human/heads_human_male_gaunt.json', 'amber', 'body'),
                     ('legs/pants/legs_pants.json', 'charcoal', 'cloth'), ('feet/shoes/feet_shoes_basic.json', 'gray', 'cloth'),
                     ('torso/shirts/longsleeve/torso_clothes_longsleeve2.json', 'bluegray', 'cloth'), ('hair/bob/hair_bob_side_part.json', 'black', 'hair'),
                     ('torso/backpack/backpack.json', None, None)]),
    'Biến Thể': ('male', [('body/special/body_zombie.json', None, None), ('head/heads/undead/heads_zombie.json', 'zombie', 'body'),
                          ('legs/pants/legs_pants.json', 'slate', 'cloth'), ('torso/shirts/shortsleeve/torso_clothes_tshirt.json', 'gray', 'cloth')]),
}

def sheet(name, anim):
    bt, parts = CHARS[name]
    return compose(parts, bt, anim)

if __name__ == '__main__':
    os.makedirs('/home/claude/gen/lpc_out', exist_ok=True)
    row = Image.new('RGBA', (64 * 5 * 3, 64 * 2), (60, 70, 60, 255))
    for i, n in enumerate(CHARS):
        for j, anim in enumerate(('idle', 'walk', 'sit')):
            s = sheet(n, anim)
            if s is None: continue
            # frame 0 of "down" row (row index 2) and "up" row (0)
            fr = s.crop((0, 128, 64, 192)); row.alpha_composite(fr, ((i * 3 + j) * 64, 0))
            fr = s.crop((0, 0, 64, 64)); row.alpha_composite(fr, ((i * 3 + j) * 64, 64))
    row.resize((row.width * 2, row.height * 2), Image.NEAREST).save('/home/claude/gen/lpc_out/test.png')
    print('ok')
