"""Sinh src/ui/v10.css từ bảng màu và bộ thành phần: biến CSS token, lớp 9-slice (border-image), sprite, tile.

Đơn vị: 1 px game = var(--px) px CSS (JS đặt --px = bề rộng lớp UI / 800 khi đổi cỡ cửa sổ). Ảnh đặt tại
src/ui/sprites/<tên>.png (cắt từ atlas nên pixel giống hệt), Vite bundle khi build.
"""
from palette import UI, hexs


def _px(n):
    return f'calc(var(--px) * {n})'


def css(components: dict) -> str:
    out = ['/* FILE SINH bởi art/ui/css.py (npm run art). Không sửa tay. */', ':root {']
    for k, v in UI.items():
        out.append(f'  --{k.replace("_", "-")}: {hexs(v)};')
    out.append('  --px: 2px;')
    out.append('}')
    out.append('.v10 { image-rendering: pixelated; }')
    for name, spec in components.items():
        im = spec['img']
        url = f'url(./sprites/{name}.png)'
        cls = f'.v10-{name}'
        if spec['kind'] == 'nine':
            t, r, b, l = spec['slice']
            o = spec['outset']
            out.append(
                f'{cls} {{ border-style: solid; border-width: {_px(t)} {_px(r)} {_px(b)} {_px(l)}; '
                f'border-image: {url} {t} {r} {b} {l} fill / {_px(t)} {_px(r)} {_px(b)} {_px(l)} / {_px(o)} repeat; '
                f'image-rendering: pixelated; box-sizing: border-box; }}'
            )
        elif spec['kind'] == 'tile':
            out.append(
                f'{cls} {{ background: {url} repeat-x; background-size: {_px(im.width)} {_px(im.height)}; '
                f'height: {_px(im.height)}; image-rendering: pixelated; display: inline-block; }}'
            )
        else:
            out.append(
                f'{cls} {{ background: {url} no-repeat; background-size: {_px(im.width)} {_px(im.height)}; '
                f'width: {_px(im.width)}; height: {_px(im.height)}; image-rendering: pixelated; display: inline-block; }}'
            )
    return '\n'.join(out) + '\n'
