"""Thành phần UI v10 vẽ bằng code (port tools/locked.py: frame, title, slot, card, tabs, choice, bar, scrollbar).

Mỗi thành phần là một ảnh nhỏ + metadata 9-slice (top, right, bottom, left) và outset (phần vẽ ra ngoài hộp:
vạch thước, bóng). Game dùng qua CSS border-image (src/ui/v10.css sinh từ build) hoặc Phaser NineSlice.
Chỉ dùng màu trong palette.UI; art/check.py chặn màu lạ.
"""
from PIL import Image, ImageDraw

from palette import UI

Spec = dict  # {'img': Image, 'slice': (t, r, b, l) | None, 'outset': int, 'kind': 'nine' | 'sprite' | 'tile'}


def _new(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def _c(name, a=255):
    r, g, b = UI[name]
    return (r, g, b, a)


def brackets(d, x0, y0, x1, y1, col, L=3):
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.line([(cx, cy), (cx + sx * L, cy)], fill=col)
        d.line([(cx, cy), (cx, cy + sy * L)], fill=col)


def panel() -> Spec:
    """Khung: bóng lệch, viền tối, nền có vạch quét, viền teal hai góc, vạch cyan, thước đo, 3 LED."""
    M = 4  # lề ngoài cho thước và bóng
    w, h = 64 + M * 2, 40 + M * 2
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = M, M, M + 63, M + 39
    d.rectangle((x0 + 2, y0 + 2, x1 + 2, y1 + 2), fill=_c('black', 120))
    d.rectangle((x0, y0, x1, y1), fill=_c('shadow'))
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=_c('panel'))
    for y in range(y0 + 3, y1 - 1, 2):
        d.line([(x0 + 2, y), (x1 - 2, y)], fill=_c('scan'))
    d.line([(x0 + 1, y0 + 1), (x1 - 4, y0 + 1)], fill=_c('edge'))
    d.line([(x0 + 1, y0 + 1), (x0 + 1, y1 - 4)], fill=_c('edge'))
    d.line([(x1 - 1, y0 + 4), (x1 - 1, y1 - 1)], fill=_c('edge'))
    d.line([(x0 + 4, y1 - 1), (x1 - 1, y1 - 1)], fill=_c('edge'))
    d.line([(x1 - 4, y0 + 1), (x1 - 1, y0 + 4)], fill=_c('tick'))
    d.line([(x0 + 1, y1 - 4), (x0 + 4, y1 - 1)], fill=_c('tick'))
    # thước: dải trên trái + dải trái trên, chấm dưới trái + dải trái dưới (chỉ trong góc để 9-slice lặp được)
    d.line([(x0 + 2, y0 - 2), (x0 + 2 + 20, y0 - 2)], fill=_c('tick'))
    for k in range(0, 20, 2):
        d.point((x0 + 2 + k, y0 - 3), fill=_c('tick'))
    d.line([(x0 - 2, y0 + 2), (x0 - 2, y0 + 12)], fill=_c('tick'))
    for k in range(0, 16, 2):
        d.point((x0 + 4 + k, y1 + 2), fill=_c('tick'))
    d.line([(x0 - 2, y1 - 8), (x0 - 2, y1)], fill=_c('tick'))
    for k, c in enumerate(('bad', 'warn', 'ok')):
        d.rectangle((x1 - 22 + k * 6, y0 + 4, x1 - 19 + k * 6, y0 + 6), fill=_c(c))
    d.point((x1 - 4, y1 - 4), fill=_c('dim'))
    # slice: trên 14 (thước + LED), phải 28 (LED), dưới 10 (chấm + bóng), trái 10 (thước); giữa 2 hàng vạch quét lặp
    return {'img': im, 'slice': (M + 10, M + 26, M + 6, M + 6), 'outset': M, 'kind': 'nine'}


def button(state: str) -> Spec:
    w, h = 24, 16
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    fill = {'normal': 'tab_off', 'hover': 'btn_hover', 'pressed': 'mag', 'disabled': 'scan'}[state]
    edge = {'normal': 'edge', 'hover': 'edge_hi', 'pressed': 'mag_hi', 'disabled': 'bracket_dim'}[state]
    d.rectangle((0, 0, w - 1, h - 1), fill=_c(fill), outline=_c(edge))
    if state == 'pressed':
        d.line([(1, 1), (w - 2, 1)], fill=_c('mag_hi'))
    else:
        d.line([(1, h - 2), (w - 2, h - 2)], fill=_c('shadow'))
    return {'img': im, 'slice': (3, 3, 3, 3), 'outset': 0, 'kind': 'nine'}


def _parallelogram(w, h, fill, top=None, left_stripe=None, shadow=None):
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    s = 4  # độ nghiêng
    if shadow:
        d.polygon([(s + 1, 1), (w - 1, 1), (w - 1 - s, h - 1), (1, h - 1)], fill=_c(shadow))
    d.polygon([(s, 0), (w - 2, 0), (w - 2 - s, h - 2), (0, h - 2)], fill=_c(fill))
    if left_stripe:
        d.polygon([(s, 0), (s + 3, 0), (3, h - 2), (0, h - 2)], fill=_c(left_stripe))
    if top:
        d.line([(s + (4 if left_stripe else 0), 0), (w - 2, 0)], fill=_c(top))
    return im


def tab(state: str) -> Spec:
    im = _parallelogram(28, 16, 'mag' if state == 'active' else 'tab_off', top='mag_hi' if state == 'active' else None)
    return {'img': im, 'slice': (2, 8, 2, 8), 'outset': 0, 'kind': 'nine'}


def title() -> Spec:
    im = _parallelogram(32, 18, 'mag', top='mag_line', left_stripe='mag_hi', shadow='mag_lo')
    return {'img': im, 'slice': (3, 9, 3, 9), 'outset': 0, 'kind': 'nine'}


def slot(selected: bool) -> Spec:
    M = 2
    w, h = 24 + M * 2, 24 + M * 2
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = M, M, M + 23, M + 23
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=_c('slot'))
    brackets(d, x0, y0, x1, y1, _c('mag_hi') if selected else _c('edge'))
    if selected:
        for x in range(x0, x1 + 1, 2):
            d.point((x, y0 - 2), fill=_c('mag_hi'))
    return {'img': im, 'slice': (M + 5, M + 5, M + 5, M + 5), 'outset': M, 'kind': 'nine'}


def card(selected: bool) -> Spec:
    w, h = 32, 24
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=_c('card_sel') if selected else _c('slot'))
    if selected:
        for y in range(1, h - 1, 2):
            d.line([(1, y), (w - 2, y)], fill=_c('card_stripe'))
        d.rectangle((0, 0, 1, h - 1), fill=_c('mag_hi'))
        brackets(d, 0, 0, w - 1, h - 1, _c('mag_hi'), 4)
    else:
        brackets(d, 0, 0, w - 1, h - 1, _c('bracket_dim'), 3)
    return {'img': im, 'slice': (6, 6, 6, 6), 'outset': 0, 'kind': 'nine'}


def choice(selected: bool) -> Spec:
    w, h = 28, 16
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=_c('choice_sel') if selected else _c('choice'))
    if selected:
        d.rectangle((0, 0, 1, h - 1), fill=_c('mag_hi'))
        d.line([(2, 0), (w - 1, 0)], fill=_c('mag_hi'))
        d.polygon([(w - 8, 4), (w - 3, 8), (w - 8, 12)], fill=_c('ink'))
    return {'img': im, 'slice': (2, 10, 2, 4), 'outset': 0, 'kind': 'nine'}


def seg(color: str | None) -> Spec:
    """Một ô của thanh phân đoạn: 4 px ô + 1 px khoảng trống (lặp theo chiều ngang)."""
    im = _new(5, 5)
    d = ImageDraw.Draw(im)
    if color:
        d.rectangle((0, 0, 3, 4), fill=_c(color))
        d.line([(0, 0), (3, 0)], fill=_c(color + '_hi'))
    else:
        d.rectangle((0, 0, 3, 4), fill=_c('bar_off'))
    return {'img': im, 'slice': None, 'outset': 0, 'kind': 'tile'}


def scroll_track() -> Spec:
    im = _new(5, 4)
    ImageDraw.Draw(im).line([(2, 0), (2, 3)], fill=_c('track'))
    return {'img': im, 'slice': None, 'outset': 0, 'kind': 'tile'}


def scroll_thumb() -> Spec:
    im = _new(5, 18)
    ImageDraw.Draw(im).rectangle((0, 0, 4, 17), fill=_c('tick'))
    return {'img': im, 'slice': (2, 0, 2, 0), 'outset': 0, 'kind': 'nine'}


def keycap() -> Spec:
    w, h = 12, 12
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=_c('tab_off'), outline=_c('edge'))
    d.line([(1, h - 2), (w - 2, h - 2)], fill=_c('scan'))
    d.line([(1, h - 3), (w - 2, h - 3)], fill=_c('scan'))
    return {'img': im, 'slice': (3, 3, 4, 3), 'outset': 0, 'kind': 'nine'}


def toggle(on: bool) -> Spec:
    w, h = 24, 12
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=_c('slot'), outline=_c('edge'))
    if on:
        d.rectangle((12, 1, w - 2, h - 2), fill=_c('tick'))
    else:
        d.rectangle((1, 1, 11, h - 2), fill=_c('dim'))
    return {'img': im, 'slice': None, 'outset': 0, 'kind': 'sprite'}


def led(color: str) -> Spec:
    im = _new(4, 3)
    ImageDraw.Draw(im).rectangle((0, 0, 3, 2), fill=_c(color))
    return {'img': im, 'slice': None, 'outset': 0, 'kind': 'sprite'}


GLYPH_Q = """
.kkkkk.
kkwwwkk
kwwkkwk
kkkkwwk
..kwwk.
..kwkk.
..kkk..
..kwwk.
..kwwk.
..kkkk.
"""
GLYPH_X = """
.kkkk.
.kwwk.
.kwwk.
.kwwk.
.kwwk.
.kwwk.
.kkkk.
.kkkk.
.kwwk.
.kkkk.
"""
GLYPH_CHECK = """
.....k.
....kwk
...kwk.
k.kwk..
kwwk...
.kk....
"""
CURSOR = """
k..........
kk.........
kwk........
kwwk.......
kwwwk......
kwwwwk.....
kwwwwwk....
kwwwkkkk...
kwkwwk.....
kk.kwwk....
....kk.....
"""


def glyph(text: str, color: str) -> Spec:
    rows = [r for r in text.strip('\n').split('\n')]
    w = max(len(r) for r in rows)
    im = _new(w, len(rows))
    px = im.load()
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == 'k':
                px[x, y] = _c('black')
            elif ch == 'w':
                px[x, y] = _c(color)
    return {'img': im, 'slice': None, 'outset': 0, 'kind': 'sprite'}


def check(on: bool) -> Spec:
    im = _new(7, 7)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 6, 6), fill=_c('slot'), outline=_c('edge'))
    if on:
        g = glyph(GLYPH_CHECK, 'ok')['img']
        im.alpha_composite(g, (0, 1))
    return {'img': im, 'slice': None, 'outset': 0, 'kind': 'sprite'}


def target() -> Spec:
    im = _new(9, 9)
    d = ImageDraw.Draw(im)
    d.line([(0, 0), (8, 8)], fill=_c('tick'))
    d.line([(8, 0), (0, 8)], fill=_c('tick'))
    return {'img': im, 'slice': None, 'outset': 0, 'kind': 'sprite'}


def all_components() -> dict[str, Spec]:
    out = {
        'panel': panel(),
        'title': title(),
        'keycap': keycap(),
        'scroll-track': scroll_track(),
        'scroll-thumb': scroll_thumb(),
        'cursor': glyph(CURSOR, 'ink'),
        'target': target(),
        'marker-q': glyph(GLYPH_Q, 'warn'),
        'marker-x': glyph(GLYPH_X, 'bad'),
        'check-on': check(True),
        'check-off': check(False),
        'toggle-on': toggle(True),
        'toggle-off': toggle(False),
    }
    for st in ('normal', 'hover', 'pressed', 'disabled'):
        out[f'button-{st}'] = button(st)
    for st in ('normal', 'active'):
        out[f'tab-{st}'] = tab(st)
    out['slot'] = slot(False)
    out['slot-sel'] = slot(True)
    out['card'] = card(False)
    out['card-sel'] = card(True)
    out['choice'] = choice(False)
    out['choice-sel'] = choice(True)
    for c in ('bad', 'warn', 'ok', 'tick', 'speed'):
        out[f'seg-{c}'] = seg(c)
    out['seg-off'] = seg(None)
    for c in ('bad', 'warn', 'ok'):
        out[f'led-{c}'] = led(c)
    return out
