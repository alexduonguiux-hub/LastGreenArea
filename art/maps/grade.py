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
