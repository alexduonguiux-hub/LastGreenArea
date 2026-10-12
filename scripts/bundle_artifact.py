"""Đóng gói dist/ thành trang artifact: python3 scripts/bundle_artifact.py <thư mục ra>

Artifact chỉ cho script/CSS nội tuyến (hoặc CDN), nên JS và CSS của Vite được nhúng thẳng vào index.html;
ảnh, JSON, font giữ làm file kèm theo (published files). Đường dẫn font trong CSS đổi từ ./x.ttf thành assets/x.ttf.
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / 'dist'
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

html = (DIST / 'index.html').read_text(encoding='utf-8')
js = re.search(r'<script type="module" crossorigin src="\./(assets/[^"]+\.js)"></script>', html)
css = re.search(r'<link rel="stylesheet" crossorigin href="\./(assets/[^"]+\.css)">', html)
assert js and css, 'không tìm thấy thẻ script/css của Vite'
js_src = (DIST / js.group(1)).read_text(encoding='utf-8').replace('</script', '<\\/script')
css_src = (DIST / css.group(1)).read_text(encoding='utf-8').replace('url(./', 'url(assets/')
html = html.replace(js.group(0), '').replace(css.group(0), f'<style>\n{css_src}\n</style>')
html = html.replace('</body>', f'<script type="module">\n{js_src}\n</script>\n</body>')
# bỏ khung tài liệu: trang artifact được bọc sẵn
html = re.sub(r'<!doctype html>\s*', '', html, flags=re.I)
html = re.sub(r'</?html[^>]*>|</?head>|</?body>', '', html)
html = re.sub(r'<meta [^>]*>\s*', '', html)
(OUT / 'index.html').write_text(html.strip() + '\n', encoding='utf-8')

files = []
for p in DIST.rglob('*'):
    if p.is_file() and p.suffix not in ('.js', '.css', '.html'):
        rel = p.relative_to(DIST)
        dest = OUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        files.append(str(rel))
print('index.html:', (OUT / 'index.html').stat().st_size // 1024, 'KB')
print('files:', ' '.join(files))
