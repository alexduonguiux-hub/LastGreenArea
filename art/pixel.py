"""Ma trận ký tự <-> ảnh.

Một asset nhỏ (vũ khí, item, mảnh UI) được viết dưới dạng khối chữ, mỗi ký tự là một màu
trong bảng màu. Ký tự đặc biệt đánh dấu điểm neo và vẫn được tô màu:

    PAL = {'.': None, 'k': (16,14,20), 'g': (52,56,64)}
    MARK = {'G': ('grip', 'g'), 'M': ('muzzle', 'k')}   # G vẽ bằng màu 'g', ghi vị trí 'grip'
    img, marks = parse('''
    ..kkkkkkkkkkkkkkk.
    Mkkggggggggggggkk.
    ..kkkkkkkggggkkk..
    ........kkGgk.....
    ''', PAL, MARK)
    marks == {'grip': (10, 3), 'muzzle': (0, 1)}

`to_text` làm ngược lại để chuyển sprite có sẵn thành ma trận (dùng khi port vũ khí cũ ở A3).
"""
from PIL import Image

Palette = dict  # ký tự -> RGB | RGBA | None
Markers = dict  # ký tự -> (tên neo, ký tự màu)


def _rgba(c):
    if c is None:
        return (0, 0, 0, 0)
    return tuple(c) if len(c) == 4 else (c[0], c[1], c[2], 255)


def parse(text: str, palette: Palette, markers: Markers | None = None):
    """Trả về (Image RGBA, {tên neo: (x, y)}). Dòng trống đầu/cuối bị bỏ; dòng ngắn được đệm trong suốt."""
    markers = markers or {}
    lines = [ln.rstrip('\n') for ln in text.strip('\n').split('\n')]
    lines = [ln for ln in lines if ln.strip() != '' or True]
    w = max(len(ln) for ln in lines)
    h = len(lines)
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = img.load()
    marks = {}
    for y, ln in enumerate(lines):
        for x, ch in enumerate(ln):
            if ch == ' ':
                ch = '.'
            if ch in markers:
                name, colch = markers[ch]
                marks[name] = (x, y)
                ch = colch
            if ch not in palette:
                raise KeyError(f'ký tự {ch!r} tại ({x},{y}) không có trong bảng màu')
            px[x, y] = _rgba(palette[ch])
    return img, marks


def to_text(img: Image.Image, palette: Palette, marks: dict | None = None, markers: Markers | None = None) -> str:
    """Ảnh -> ma trận ký tự. Màu không có trong bảng → ValueError (để bảng màu luôn đầy đủ)."""
    inv = {}
    for ch, c in palette.items():
        inv.setdefault(_rgba(c), ch)
    pos = {}
    if marks and markers:
        name2ch = {name: ch for ch, (name, _) in markers.items()}
        for name, (x, y) in marks.items():
            if name in name2ch:
                pos[(x, y)] = name2ch[name]
    img = img.convert('RGBA')
    px = img.load()
    out = []
    for y in range(img.height):
        row = []
        for x in range(img.width):
            c = px[x, y]
            if c[3] == 0:
                c = (0, 0, 0, 0)
            if (x, y) in pos:
                row.append(pos[(x, y)])
                continue
            if c not in inv:
                raise ValueError(f'màu {c} tại ({x},{y}) không có trong bảng màu')
            row.append(inv[c])
        out.append(''.join(row))
    return '\n'.join(out)


def auto_palette(img: Image.Image, alphabet: str = 'abcdefghijklmnopqrstuvwxyz0123456789') -> Palette:
    """Sinh bảng màu tạm từ ảnh (màu phổ biến trước). Dùng khi port sprite cũ, sau đó đặt tên lại."""
    img = img.convert('RGBA')
    counts = {}
    for c in img.getdata():
        if c[3] == 0:
            continue
        counts[c] = counts.get(c, 0) + 1
    pal = {'.': None}
    for i, (c, _) in enumerate(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))):
        if i >= len(alphabet):
            raise ValueError('ảnh có quá nhiều màu cho bảng chữ cái')
        pal[alphabet[i]] = c
    return pal
