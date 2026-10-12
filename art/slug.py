"""Chuyển tên tiếng Việt thành id ASCII ổn định: "Đi xuống" -> "di-xuong", "Biến Thể" -> "bien-the"."""
import re
import unicodedata

_D = {'đ': 'd', 'Đ': 'd'}


def slug(s: str) -> str:
    s = ''.join(_D.get(c, c) for c in s)
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return s
