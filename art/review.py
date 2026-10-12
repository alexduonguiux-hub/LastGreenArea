"""Sinh bản review đứng độc lập: python3 art/review.py  (hoặc npm run art:review)

Gộp viewer/gallery + atlas.js + ảnh (base64) thành MỘT file mở trực tiếp trên bất kỳ máy nào:
  prototype/atlas_review.html    ma trận atlas (kỹ thuật: ô, id, neo)
  prototype/gallery_review.html  gallery hoạt ảnh + sân thử tương tác
Với --artifact <thư mục>: xuất thêm bản không có khung <html>/<head>/<body> để đăng làm trang web (artifact).
"""
import base64
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

ROOT = build.ROOT
PROTO = ROOT / 'prototype'
PAGES = {
    'atlas_viewer.html': ('atlas_review.html', 'Ma trận atlas Vùng Xanh'),
    'gallery.html': ('gallery_review.html', 'Gallery Vùng Xanh'),
}


def embed_images():
    imgs = {}
    for name in build.PAGES:
        data = (build.OUT_IMG / name).read_bytes()
        imgs[name] = 'data:image/png;base64,' + base64.b64encode(data).decode('ascii')
    bg = (ROOT / 'assets' / 'maps' / 'level1_bridge_bg.png').read_bytes()
    imgs['bg'] = 'data:image/png;base64,' + base64.b64encode(bg).decode('ascii')
    return imgs


def standalone(src: Path, title: str, js: str) -> str:
    html = src.read_text(encoding='utf-8')
    tag = '<script src="../public/data/atlas.js"></script>'
    assert tag in html, f'không tìm thấy thẻ atlas.js trong {src.name}'
    html = html.replace(tag, '<script>\n' + js + '</script>')
    html = re.sub(r"im\.src = '\.\./public/assets/' \+ t\.image;", 'im.src = window.ATLAS_IMG[t.image];', html)
    html = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html, count=1)
    return html


def artifact_body(html: str) -> str:
    """Bỏ khung tài liệu: trang artifact được bọc sẵn <html>/<head>/<body> khi đăng."""
    html = re.sub(r'<!doctype html>\s*', '', html, flags=re.I)
    html = re.sub(r'</?html[^>]*>|</?head>|</?body>', '', html)
    html = re.sub(r'<meta [^>]*>\s*', '', html)
    return html.strip() + '\n'


def main():
    out_art = None
    if '--artifact' in sys.argv:
        out_art = Path(sys.argv[sys.argv.index('--artifact') + 1])
        out_art.mkdir(parents=True, exist_ok=True)
    js = (build.OUT_DATA / 'atlas.js').read_text(encoding='utf-8')
    js += 'window.ATLAS_IMG=' + repr(embed_images()).replace("'", '"') + ';\n'
    for src_name, (out_name, title) in PAGES.items():
        html = standalone(PROTO / src_name, title, js)
        out = PROTO / out_name
        out.write_text(html, encoding='utf-8')
        print(f'{out.relative_to(ROOT)}: {out.stat().st_size // 1024} KB')
        if out_art:
            (out_art / out_name).write_text(artifact_body(html), encoding='utf-8')
            print(f'  artifact: {out_art / out_name}')


if __name__ == '__main__':
    main()
