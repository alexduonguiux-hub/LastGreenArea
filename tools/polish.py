import sys, colorsys, json; sys.path.insert(0, '.')
import numpy as np
from PIL import Image
import lpc

B_CHARS = {
    'Dương': ('male', [('body/body.json', 'amber', 'body'), ('head/heads/human/heads_human_male.json', 'amber', 'body'),
                       ('legs/pants/legs_pants.json', 'navy', 'cloth'), ('feet/boots/feet_boots_basic.json', 'brown', 'cloth'),
                       ('torso/shirts/longsleeve/torso_clothes_longsleeve2_vneck.json', 'forest', 'cloth'), ('hair/short/hair_bedhead.json', 'black', 'hair')]),
    'Hùng': ('muscular', [('body/body.json', 'bronze', 'body'), ('head/heads/human/heads_human_male.json', 'bronze', 'body'),
                          ('legs/pants/legs_pants.json', 'tan', 'cloth'), ('feet/boots/feet_boots_basic.json', 'black', 'cloth'),
                          ('torso/shirts/sleeveless/torso_clothes_sleeveless2.json', 'charcoal', 'cloth'), ('hair/bald/hair_buzzcut.json', 'black', 'hair'),
                          ('headwear/coverings/bandana/hat_bandana.json', 'blue', 'cloth')]),
    'Ny': ('female', [('body/body.json', 'light', 'body'), ('head/heads/human/heads_human_female.json', 'light', 'body'),
                      ('legs/leggings/legs_leggings.json', 'charcoal', 'cloth'), ('feet/shoes/feet_shoes_basic.json', 'white', 'cloth'),
                      ('torso/shirts/longsleeve/torso_clothes_longsleeve2_buttoned.json', 'white', 'cloth'), ('hair/long/hair_bangslong.json', 'dark_brown', 'hair')]),
    'Sơn': ('male', [('body/body.json', 'amber', 'body'), ('head/heads/human/heads_human_male_gaunt.json', 'amber', 'body'),
                     ('legs/pants/legs_pants.json', 'charcoal', 'cloth'), ('feet/shoes/feet_shoes_basic.json', 'gray', 'cloth'),
                     ('torso/shirts/longsleeve/torso_clothes_longsleeve2_polo.json', 'teal', 'cloth'), ('hair/bob/hair_bob_side_part.json', 'black', 'hair'),
                     ('headwear/accessories/glasses/facial_glasses.json', None, None), ('torso/backpack/backpack.json', None, None)]),
}
for n, v in B_CHARS.items(): lpc.CHARS['B_' + n] = v

def polish(im):
    """Pixel-art finishing pass: hue-shifted ramps (cool shadows, warm highlights), coloured outlines (sel-out), warm rim light."""
    A = np.array(im.convert('RGBA')).astype(np.float32) / 255.0
    rgb, a = A[..., :3], A[..., 3]
    out = rgb.copy()
    H, W = a.shape
    for y in range(H):
        for x in range(W):
            if a[y, x] == 0: continue
            r, g, b = rgb[y, x]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            lum = 0.3 * r + 0.59 * g + 0.11 * b
            if lum < 0.45:   # shadows lean toward blue-violet, a little more saturated
                k = (0.45 - lum) / 0.45
                h = (h + (((0.70 - h + 0.5) % 1) - 0.5) * 0.16 * k) % 1; s = min(1, s + 0.12 * k)
            else:            # highlights lean warm
                k = (lum - 0.45) / 0.55
                h = (h + (((0.11 - h + 0.5) % 1) - 0.5) * 0.10 * k) % 1; v = min(1, v + 0.05 * k)
            s = min(1, s * 1.06)
            out[y, x] = colorsys.hsv_to_rgb(h, s, v)
    solid = a > 0
    edge_r = solid & ~np.pad(solid, ((0, 0), (0, 1)))[:, 1:]
    edge_t = solid & ~np.pad(solid, ((1, 0), (0, 0)))[:-1, :]
    rim = (edge_r | edge_t)
    lum = out @ np.array([0.3, 0.59, 0.11])
    rim_m = rim & (lum > 0.12)
    out[rim_m] = out[rim_m] * 0.7 + np.array([1.0, 0.86, 0.62]) * 0.3
    dark = solid & (lum < 0.1)
    out[dark] = out[dark] * 0.5 + np.array([0.10, 0.06, 0.12]) * 0.5
    res = np.dstack([out, a]); return Image.fromarray((res * 255).clip(0, 255).astype(np.uint8))

def walk_strip(key, row=2, cols=range(1, 9), fn=None):
    s = lpc.sheet(key, 'walk'); out = Image.new('RGBA', (64 * len(cols), 64), (0, 0, 0, 0))
    for i, c in enumerate(cols):
        f = s.crop((c * 64, row * 64, c * 64 + 64, row * 64 + 64))
        out.alpha_composite(fn(f) if fn else f, (i * 64, 0))
    return out

if __name__ == '__main__':
    names = ['Dương', 'Hùng', 'Ny', 'Sơn']
    rows = []
    for variant in ('A', 'B', 'C'):
        for n in names:
            key = n if variant == 'A' else 'B_' + n
            rows.append(((variant, n), walk_strip(key, fn=polish if variant == 'C' else None)))
    sheet = Image.new('RGBA', (512, 64 * len(rows)), (0, 0, 0, 0))
    for i, (_, s) in enumerate(rows): sheet.alpha_composite(s, (0, i * 64))
    sheet.save('/mnt/user-data/outputs/artifacts/c82b9169-ee10-4565-aca3-4592040c933d/polish_sheet.png', optimize=True)
    json.dump([k for k, _ in rows], open('polish_meta.json', 'w'), ensure_ascii=False)
    chk = Image.new('RGBA', (64 * 12, 64 * 4), (50, 66, 52, 255))
    for i, ((v, n), s) in enumerate(rows):
        col = 'ABC'.index(v); r = names.index(n)
        chk.alpha_composite(s.crop((0, 0, 64, 64)), (col * 256, r * 64)); chk.alpha_composite(s.crop((64 * 3, 0, 64 * 4, 64)), (col * 256 + 64, r * 64))
    chk.resize((chk.width * 2, chk.height * 2), Image.NEAREST).save('/tmp/polish.png'); print('ok')
