"""Hậu kỳ "bình minh, sương" ở độ phân giải gốc (port từ tools/lpcframe.postfx).

grade(): split-tone (bóng teal, sáng hổ phách) + tương phản, dùng cho cả nền lẫn sprite môi trường để
cây đặt trong game khớp màu với nền. rays(): vệt nắng posterise + dither từ góc trên phải, chỉ cho nền.
"""
import math

import numpy as np
from PIL import Image

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.float32) / 16.0


def _rgb_alpha(im: Image.Image):
    arr = np.array(im.convert('RGBA')).astype(np.float32)
    return arr[..., :3] / 255.0, arr[..., 3:4]


def _out(rgb, alpha):
    arr = np.concatenate([np.clip(rgb, 0, 1) * 255, alpha], axis=-1)
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')


def grade(im: Image.Image) -> Image.Image:
    A, alpha = _rgb_alpha(im)
    lum = (A @ np.array([0.299, 0.587, 0.114], dtype=np.float32))[..., None]
    shadow = np.array([0.80, 0.95, 1.10])
    high = np.array([1.12, 1.00, 0.82])
    t = np.clip((lum - 0.25) / 0.5, 0, 1)
    A = A * (shadow * (1 - t) + high * t) * 1.08
    A = np.clip((A - 0.5) * 1.12 + 0.5, 0, 1)
    return _out(A, alpha)


def rays(im: Image.Image, strength: float = 0.42) -> Image.Image:
    A, alpha = _rgb_alpha(im)
    Hh, Ww = A.shape[:2]
    yy, xx = np.mgrid[0:Hh, 0:Ww].astype(np.float32)
    ang = math.radians(118)
    dx, dy = math.cos(ang), math.sin(ang)
    u = (xx - Ww) * (-dy) + yy * dx
    r = (np.sin(u / 23.0) * 0.5 + 0.5) ** 6 + (np.sin(u / 9.0 + 1.7) * 0.5 + 0.5) ** 10 * 0.5
    fall = np.clip(1.1 - (yy / Hh) * 0.9 - ((Ww - xx) / Ww) * 0.35, 0, 1)
    R = r * fall * 0.55
    B = BAYER[(yy % 4).astype(int), (xx % 4).astype(int)]
    Rq = np.floor(R * 4 + B) / 4.0
    A = A + Rq[..., None] * np.array([1.0, 0.80, 0.50]) * strength
    return _out(A, alpha)


# ---- Hệ màu Cainos (assets/tiles/cainos): ô-liu 56–66°, bão hòa vừa, dải sáng hẹp 0.2–0.65, bóng ấm -------------
def _rgb2hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1)
    mn = a.min(-1)
    d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6.0
    s = np.where(mx > 0, d / (mx + 1e-9), 0)
    return h, s, mx


def _hsv2rgb(h, s, v):
    i = np.floor(h * 6) % 6
    f = h * 6 - np.floor(h * 6)
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    sel = [i == k for k in range(6)]
    r = np.select(sel, [v, q, p, p, t, v])
    g = np.select(sel, [t, v, v, q, p, p])
    b = np.select(sel, [p, p, t, v, v, q])
    return np.stack([r, g, b], -1)


def cainos_grade(im: Image.Image, strength: float = 1.0) -> Image.Image:
    """Kéo sprite LPC về hệ màu Cainos: xanh lá → ô-liu, xanh lam → teal xám, màu da/gỗ giữ ấm, nén dải sáng."""
    A, alpha = _rgb_alpha(im)
    h, s, v = _rgb2hsv(A)
    hd = h * 360
    green = (hd > 70) & (hd < 178)   # lá thông LPC tới ~175° vẫn là xanh lá
    blue = (hd >= 178) & (hd < 270)
    warm = (hd <= 50) | (hd >= 330)
    h2 = np.where(green, (56 + (hd - 70) / 108 * 12) / 360, h)
    h2 = np.where(blue, (185 + (hd - 178) / 92 * 10) / 360, h2)
    s2 = np.where(green, np.clip(s * 0.95, 0, 0.8), np.where(blue, s * 0.55, np.where(warm, s * 0.85, s * 0.7)))
    v2 = np.where(warm, 0.18 + v * 0.52, 0.2 + v * 0.45)
    v2 = np.where(green, v2 + 0.04, v2)
    out = _hsv2rgb(h2, s2, v2) * np.array([1.03, 1.0, 0.92])
    out = A * (1 - strength) + out * strength
    return _out(out, alpha)
