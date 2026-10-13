"""Thành phần UI v11 "đá và gỗ" vẽ bằng code (khung phiến đá, thẻ tiêu đề ván gỗ, ô lõm, thanh phân đoạn, thanh cuộn).

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
    """Phiến đá: bóng dưới, viền đá tối, thân đá, cạnh sáng trên-trái, cạnh tối dưới-phải, đinh tán 4 góc."""
    M = 3  # lề ngoài cho bóng
    w, h = 48 + M * 2, 32 + M * 2
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = M, M, M + 47, M + 31
    d.rectangle((x0 + 1, y0 + 2, x1 + 2, y1 + 2), fill=_c('shadow', 150))
    d.rectangle((x0, y0, x1, y1), fill=_c('edge'))
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=_c('panel'))
    d.line([(x0 + 1, y0 + 1), (x1 - 2, y0 + 1)], fill=_c('tick'))
    d.line([(x0 + 1, y0 + 1), (x0 + 1, y1 - 2)], fill=_c('tick'))
    d.line([(x0 + 2, y1 - 1), (x1 - 1, y1 - 1)], fill=_c('scan'))
    d.line([(x1 - 1, y0 + 2), (x1 - 1, y1 - 1)], fill=_c('scan'))
    for cx, cy in ((x0 + 3, y0 + 3), (x1 - 4, y0 + 3), (x0 + 3, y1 - 4), (x1 - 4, y1 - 4)):
        d.rectangle((cx, cy, cx + 1, cy + 1), fill=_c('edge'))
        d.point((cx, cy), fill=_c('tick'))
    # vân đá thưa ở giữa (lặp được)
    for (px_, py_) in ((14, 12), (30, 20), (22, 26), (38, 10)):
        d.point((x0 + px_, y0 + py_), fill=_c('scan'))
    return {'img': im, 'slice': (M + 7, M + 7, M + 7, M + 7), 'outset': M, 'kind': 'nine'}


def _plank(w, h, fill='mag', top='mag_line', bottom='mag_lo', nails=True):
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=_c(bottom))
    d.rectangle((1, 1, w - 2, h - 2), fill=_c(fill))
    d.line([(1, 1), (w - 2, 1)], fill=_c(top))
    d.line([(1, 1), (1, h - 2)], fill=_c(top))
    if nails:
        for (nx, ny) in ((3, 3), (w - 4, 3), (3, h - 4), (w - 4, h - 4)):
            d.point((nx, ny), fill=_c('mag_lo'))
            d.point((nx + 1, ny), fill=_c('mag_line'))
    return im


def button(state: str) -> Spec:
    w, h = 24, 16
    if state == 'pressed':
        im = _plank(w, h, nails=False)
    else:
        im = _new(w, h)
        d = ImageDraw.Draw(im)
        fill = {'normal': 'tab_off', 'hover': 'btn_hover', 'disabled': 'scan'}[state]
        d.rectangle((0, 0, w - 1, h - 1), fill=_c(fill), outline=_c('edge'))
        d.line([(1, 1), (w - 2, 1)], fill=_c('tick'))
        d.line([(1, h - 2), (w - 2, h - 2)], fill=_c('shadow'))
    return {'img': im, 'slice': (3, 3, 3, 3), 'outset': 0, 'kind': 'nine'}


def tab(state: str) -> Spec:
    if state == 'active':
        im = _plank(28, 16, nails=False)
    else:
        im = _new(28, 16)
        d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 27, 15), fill=_c('tab_off'), outline=_c('edge'))
        d.line([(1, 15), (26, 15)], fill=_c('shadow'))
    return {'img': im, 'slice': (3, 4, 3, 4), 'outset': 0, 'kind': 'nine'}


def title() -> Spec:
    """Ván gỗ treo: nền gỗ, cạnh sáng trên-trái, bóng dưới, đinh ở hai đầu."""
    return {'img': _plank(32, 16), 'slice': (3, 6, 3, 6), 'outset': 0, 'kind': 'nine'}


def slot(selected: bool) -> Spec:
    """Ô lõm vào đá; đang chọn: viền hổ phách."""
    M = 2
    w, h = 24 + M * 2, 24 + M * 2
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = M, M, M + 23, M + 23
    d.rectangle((x0, y0, x1, y1), fill=_c('edge'))
    d.rectangle((x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=_c('slot'))
    d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=_c('shadow'))
    d.line([(x0 + 1, y0 + 1), (x0 + 1, y1 - 1)], fill=_c('shadow'))
    if selected:
        d.rectangle((x0 - 1, y0 - 1, x1 + 1, y1 + 1), outline=_c('mag_hi'))
    return {'img': im, 'slice': (M + 5, M + 5, M + 5, M + 5), 'outset': M, 'kind': 'nine'}


def card(selected: bool) -> Spec:
    w, h = 32, 24
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    if selected:
        d.rectangle((0, 0, w - 1, h - 1), fill=_c('card_sel'), outline=_c('mag_hi'))
        d.line([(1, 1), (w - 2, 1)], fill=_c('warn_hi'))
    else:
        d.rectangle((0, 0, w - 1, h - 1), fill=_c('tab_off'), outline=_c('edge'))
        d.line([(1, h - 2), (w - 2, h - 2)], fill=_c('shadow'))
    return {'img': im, 'slice': (6, 6, 6, 6), 'outset': 0, 'kind': 'nine'}


def choice(selected: bool) -> Spec:
    w, h = 28, 16
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=_c('choice_sel') if selected else _c('choice'), outline=_c('edge') if not selected else _c('mag_hi'))
    if selected:
        d.rectangle((1, 1, 2, h - 2), fill=_c('mag_hi'))
        d.polygon([(w - 8, 4), (w - 3, 8), (w - 8, 12)], fill=_c('paper'))
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
    """Phím: mẩu gỗ nhỏ, chữ màu giấy."""
    return {'img': _plank(12, 12, nails=False), 'slice': (3, 3, 4, 3), 'outset': 0, 'kind': 'nine'}


def toggle(on: bool) -> Spec:
    w, h = 24, 12
    im = _new(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), fill=_c('slot'), outline=_c('edge'))
    if on:
        d.rectangle((12, 1, w - 2, h - 2), fill=_c('mag_hi'))
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

# icon nhỏ cho HUD (moodboard v10): hình người theo tư thế (xanh lá), đá, cuộn nhiệm vụ, vật phẩm, đồng hồ
GLYPH_DUNG = """
..kkk..
..kwk..
..kkk..
.kkwkk.
kwkwkwk
kkkwkkk
..kwk..
..kkk..
..kwk..
.kwkwk.
.kk.kk.
"""
GLYPH_CHAY = """
....kkk..
....kwk..
.kkkkkk..
kwwkwwk..
kkkkwwkk.
...kwwkwk
..kkwkkk.
.kwkkwk..
kwk..kwk.
kk....kk.
"""
GLYPH_KHOM = """
.....kkk.
.....kwk.
..kkkkkk.
.kwwwwwk.
.kwwwwkkk
.kwwwwkwk
kkwkkkkk.
kwk.kwk..
kkk.kkk..
"""
GLYPH_BO = """
.........kkk
kkkkkkkkkkwk
kwwwwwwwwwwk
kkkkkkkkkkkk
"""
GLYPH_ROCK = """
...kkkk..
..kwwwwk.
.kwwwwwwk
kwwwwkwwk
kwwwwwwwk
.kwwwwwk.
..kkkkk..
"""
GLYPH_QUEST = """
kkkkkkk
kwwwwwk
kwkkkwk
kwwwwwk
kwkkkwk
kwwwwwk
kkkkkkk
"""
GLYPH_ITEM = """
.kkkkk.
kwkwkwk
kkkkkkk
kwwwwwk
kwwkwwk
kwwwwwk
kkkkkkk
"""
GLYPH_CLOCK = """
.kkkkk.
kwwwwwk
kwwkwwk
kwwkwwk
kwwwkwk
kwwwwwk
.kkkkk.
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
    d.line([(0, 0), (8, 8)], fill=_c('mag_hi'))
    d.line([(8, 0), (0, 8)], fill=_c('mag_hi'))
    return {'img': im, 'slice': None, 'outset': 0, 'kind': 'sprite'}


def all_components() -> dict[str, Spec]:
    out = {
        'panel': panel(),
        'title': title(),
        'keycap': keycap(),
        'scroll-track': scroll_track(),
        'scroll-thumb': scroll_thumb(),
        'cursor': glyph(CURSOR, 'paper'),
        'target': target(),
        'marker-q': glyph(GLYPH_Q, 'warn'),
        'marker-x': glyph(GLYPH_X, 'bad'),
        'check-on': check(True),
        'check-off': check(False),
        'toggle-on': toggle(True),
        'toggle-off': toggle(False),
        'icon-dung': glyph(GLYPH_DUNG, 'ok'),
        'icon-chay': glyph(GLYPH_CHAY, 'ok'),
        'icon-khom': glyph(GLYPH_KHOM, 'ok'),
        'icon-bo': glyph(GLYPH_BO, 'ok'),
        'icon-rock': glyph(GLYPH_ROCK, 'tick'),
        'icon-quest': glyph(GLYPH_QUEST, 'warn'),
        'icon-item': glyph(GLYPH_ITEM, 'ok'),
        'icon-clock': glyph(GLYPH_CLOCK, 'warn'),
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
