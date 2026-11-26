#!/usr/bin/env python3
"""카톡·스레드 미리보기 예상도 (실제 앱 렌더가 아닌 재현 이미지) — shots/og-preview-kakao-mock.png"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
S = 3
F = "/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf"
W, H = 720, 520


def font(sz, w=0):
    return ImageFont.truetype(F, sz * S), w * S


def txt(d, xy, s, sz, color, w=0, anchor="la"):
    f, st = font(sz, w)
    d.text((xy[0] * S, xy[1] * S), s, font=f, fill=color, anchor=anchor,
           stroke_width=int(st), stroke_fill=color)


img = Image.new("RGB", (W * S, H * S), (178, 199, 190))
d = ImageDraw.Draw(img)

# 채팅방 말풍선 카드
cx, cy, cw, ch = 60, 40, 470, 430
d.rounded_rectangle([cx * S, cy * S, (cx + cw) * S, (cy + ch) * S], radius=16 * S, fill=(255, 255, 255))

# 이미지 (400x210 비율로 크롭)
cover = Image.open(BASE / "assets" / "og-cover.png").convert("RGB")
iw = cw - 28
ih = round(iw * 630 / 1200)
pic = cover.resize((iw * S, ih * S), Image.LANCZOS)
mask = Image.new("L", (iw * S, ih * S), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, iw * S, ih * S], radius=10 * S, fill=255)
img.paste(pic, ((cx + 14) * S, (cy + 14) * S), mask)

ty = cy + 14 + ih + 18
txt(d, (cx + 16, ty), "우리 둘의 몰디브 취향, 3분 진단", 17, (25, 31, 34), w=0.7)
txt(d, (cx + 16, ty + 30), "영업 중인 몰디브 리조트 98곳 공홈 직접 조회! 가입·결제 없이", 12.5, (110, 117, 122))
txt(d, (cx + 16, ty + 51), "예산대·라군·수중환경 비교하고 여행사 요청서까지 받아보세요.", 12.5, (110, 117, 122))
# 구분선 + 도메인
d.line([(cx * S, (ty + 86) * S), ((cx + cw) * S, (ty + 86) * S)], fill=(240, 240, 240), width=S)
txt(d, (cx + 16, ty + 98), "easy-swim.github.io", 11.5, (150, 155, 160))

# 설명 캡션
txt(d, (cx, cy + ch + 16), "카카오톡 링크 미리보기 예상도 (실제 앱 화면 재현)", 11, (245, 250, 248))

img.resize((W, H), Image.LANCZOS).save(BASE / "shots" / "og-preview-kakao-mock.png")
print("ok shots/og-preview-kakao-mock.png")
