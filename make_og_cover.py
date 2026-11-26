#!/usr/bin/env python3
"""OG 공유 카드 커버 생성 — assets/og-cover.png (1200×630)

카톡·스레드·DM 미리보기 카드용. 사이트 히어로(크림 종이 + 민트 바다, 산호섬) 톤을
그대로 옮겨 그린다. 3배 크기로 그린 뒤 LANCZOS로 줄여 선·글자를 매끄럽게 만든다.

    python3 make_og_cover.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 630
S = 3  # 슈퍼샘플링 배율
CW, CH = W * S, H * S

BASE = Path(__file__).resolve().parent
OUT = BASE / "assets" / "og-cover.png"

FONT = "/usr/share/fonts/pickle-hwp/NotoSansCJKkr-Regular.otf"

PAPER = (248, 247, 243)
INK = (24, 62, 64)
INK2 = (35, 95, 86)
MUTED = (95, 127, 117)
PILL_BORDER = (184, 207, 195)


# ---------------------------------------------------------------- helpers
def font(size, weight=0.0):
    """size는 최종 픽셀 기준. weight는 가짜 굵기(스트로크) 두께."""
    return ImageFont.truetype(FONT, max(1, round(size * S))), weight * S


def text(draw, xy, s, size, color, weight=0.0, anchor="la"):
    f, st = font(size, weight)
    pos = (xy[0] * S, xy[1] * S)
    draw.text(pos, s, font=f, fill=color, anchor=anchor,
              stroke_width=max(0, round(st)), stroke_fill=color)
    return draw.textbbox(pos, s, font=f, anchor=anchor, stroke_width=max(0, round(st)))


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def layer(size):
    return Image.new("RGBA", (int(size[0] * S), int(size[1] * S)), (0, 0, 0, 0))


def place(base, lay, cx, cy, angle=0):
    """레이어 중심을 (cx,cy)에 두고 angle만큼 돌려 합성 (화면 밖은 잘라냄)."""
    if angle:
        lay = lay.rotate(angle, resample=Image.BICUBIC, expand=True)
    x = int(cx * S - lay.width / 2)
    y = int(cy * S - lay.height / 2)
    # 베이스 밖으로 나간 부분 잘라내기
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1 = lay.width - max(0, x + lay.width - CW)
    sy1 = lay.height - max(0, y + lay.height - CH)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    base.alpha_composite(lay.crop((sx0, sy0, sx1, sy1)), (max(0, x), max(0, y)))


# ---------------------------------------------------------------- 바다
def ocean_layer():
    """오른쪽 민트 바다 — 방사형 번짐 여러 겹을 겹쳐 부드럽게."""
    lay = Image.new("RGB", (CW, CH), PAPER)
    px = lay.load()
    # (cx, cy, 반지름, 중심색, 세기, 감쇠지수)
    washes = [
        (1020, 340, 560, (92, 176, 161), 1.00, 1.08),
        (1250, 505, 520, (128, 198, 183), 0.92, 1.45),
        (990, 120, 420, (136, 202, 188), 0.85, 1.60),
        (1270, 650, 390, (150, 209, 195), 0.80, 1.90),
    ]
    for cx, cy, r, col, amt, pw in washes:
        cx, cy, r = cx * S, cy * S, r * S
        x0, x1 = max(0, int(cx - r)), min(CW - 1, int(cx + r))
        y0, y1 = max(0, int(cy - r)), min(CH - 1, int(cy + r))
        for y in range(y0, y1 + 1):
            dy = (y - cy) / r
            dy2 = dy * dy
            for x in range(x0, x1 + 1):
                dx = (x - cx) / r
                d2 = dx * dx + dy2
                if d2 >= 1:
                    continue
                a = (1 - d2 ** 0.5) ** pw * amt
                px[x, y] = lerp(px[x, y], col, min(1.0, a))
    return lay.filter(ImageFilter.GaussianBlur(6 * S))


# ---------------------------------------------------------------- 섬 그림
ICX, ICY = 992, 352          # 섬 중심 (최종 좌표)
ISLAND_W, ISLAND_H = 168, 108
TILT = -28


def draw_ripples(base):
    for w_, h_, alpha in [(300, 205, 165), (405, 278, 130), (515, 355, 95)]:
        lay = layer((w_, h_))
        d = ImageDraw.Draw(lay)
        pad = 12
        d.ellipse([pad * S, pad * S, (w_ - pad) * S, (h_ - pad) * S],
                  outline=(250, 254, 251, alpha), width=max(1, round(1.5 * S)))
        place(base, lay, ICX, ICY, TILT)


def draw_jetty(base):
    """섬 오른쪽에서 바다로 뻗는 작은 부두 (섬 테두리에 붙어 시작)."""
    lay = layer((W, H))
    d = ImageDraw.Draw(lay)
    x0, y0 = ICX + 54, ICY + 62
    x1, y1 = x0 + 96, y0 - 56
    d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=(198, 185, 150, 255), width=round(3.0 * S))
    for i in range(4):
        t = 0.3 + i * 0.23
        px_ = (x0 + (x1 - x0) * t) * S
        py_ = (y0 + (y1 - y0) * t) * S
        r = 5.2 * S
        d.rectangle([px_ - r, py_ - r, px_ + r, py_ + r], fill=(182, 167, 131, 255))
    place(base, lay, W / 2, H / 2, 0)


def draw_island(base):
    # 물빛 후광 (box-shadow 두 겹)
    for grow, col, blur in [(58, (176, 224, 207, 60), 14), (30, (158, 215, 197, 95), 9)]:
        lay = layer((ISLAND_W + grow + 90, ISLAND_H + grow + 90))
        d = ImageDraw.Draw(lay)
        w_, h_ = ISLAND_W + grow, ISLAND_H + grow
        cx, cy = lay.width / 2, lay.height / 2
        d.ellipse([cx - w_ * S / 2, cy - h_ * S / 2, cx + w_ * S / 2, cy + h_ * S / 2], fill=col)
        place(base, lay.filter(ImageFilter.GaussianBlur(blur * S / 3)), ICX, ICY, TILT)

    lay = layer((ISLAND_W + 30, ISLAND_H + 30))
    d = ImageDraw.Draw(lay)
    cx, cy = lay.width / 2, lay.height / 2

    def ell(w_, h_, fill):
        d.ellipse([cx - w_ * S / 2, cy - h_ * S / 2, cx + w_ * S / 2, cy + h_ * S / 2], fill=fill)

    ell(ISLAND_W, ISLAND_H, (244, 239, 212, 255))            # 모래 테두리
    ell(ISLAND_W - 26, ISLAND_H - 26, (232, 225, 183, 255))  # 얕은 모래
    ell(ISLAND_W - 46, ISLAND_H - 46, (140, 172, 141, 255))  # 섬 가장자리
    ell(ISLAND_W - 62, ISLAND_H - 62, (103, 147, 120, 255))  # 숲
    place(base, lay, ICX, ICY, TILT)

    # ✳ 표식
    lay = layer((80, 80))
    d = ImageDraw.Draw(lay)
    cx, cy, r = lay.width / 2, lay.height / 2, 21 * S
    for ang in (0, 45, 90, 135):
        a = math.radians(ang)
        d.line([(cx - r * math.cos(a), cy - r * math.sin(a)),
                (cx + r * math.cos(a), cy + r * math.sin(a))],
               fill=(246, 251, 239, 255), width=round(2.6 * S))
    d.ellipse([cx - 5.5 * S, cy - 5.5 * S, cx + 5.5 * S, cy + 5.5 * S], fill=(246, 251, 239, 255))
    place(base, lay, ICX, ICY, TILT)


# ---------------------------------------------------------------- 좌측 카피
def draw_copy(img):
    d = ImageDraw.Draw(img)
    lx, ly, lw = 64, 56, 40

    # 웨이브 로고 (파비콘과 같은 결)
    d.rounded_rectangle([lx * S, ly * S, (lx + lw) * S, (ly + lw) * S], radius=12 * S, fill=(230, 242, 235))
    for i, yy in enumerate((ly + 15.5, ly + 25)):
        pts = [((lx + 9 + t / 24 * 22) * S,
                (yy - 2.4 * math.sin(t / 24 * 2 * math.pi * 1.5)) * S) for t in range(25)]
        d.line(pts, fill=(45, 122, 110, 255 if i == 0 else 150), width=round((2.5 - i * 0.3) * S), joint="curve")

    text(d, (lx + lw + 16, ly + 2), "이지스윔 몰디브 노트", 17, INK, weight=0.7)
    text(d, (lx + lw + 16, ly + 26), "MALDIVES  FIELD  NOTES  ·  98 RESORTS", 9.5, (110, 140, 130))

    # 필
    top, ph = 170, 30
    f, _ = font(11.5)
    pill_txt = "무료 · 가입 없이"
    pw = d.textlength(pill_txt, font=f) / S + 42
    d.rounded_rectangle([lx * S, top * S, (lx + pw) * S, (top + ph) * S], radius=15 * S,
                        outline=PILL_BORDER + (255,), width=round(1.3 * S))
    text(d, (lx + pw / 2, top + ph / 2 + 0.5), pill_txt, 11.5, INK2, anchor="mm")

    # 헤드라인
    text(d, (lx, 220), "우리 둘의 몰디브 취향,", 46, INK, weight=0.3)
    text(d, (lx - 3, 284), "3분 진단", 84, INK2, weight=1.4)

    # 구분선 + 설명
    d.line([(lx * S, 424 * S), ((lx + 54) * S, 424 * S)], fill=(104, 141, 127, 255), width=round(1.6 * S))
    text(d, (lx, 446), "영업 중인 리조트 98곳 공홈 직접 조회", 21.5, MUTED)
    text(d, (lx, 480), "가입·결제 없이 예산대 · 라군 · 수중환경 비교", 21.5, MUTED)
    text(d, (lx, 514), "여행사 요청서까지 무료로", 21.5, MUTED)

    # 우하단 지도 라벨
    text(d, (W - 54, H - 66), "YOUR OWN OCEAN", 11.5, (88, 139, 123), anchor="ra")
    text(d, (W - 54, H - 48), "00° 41' N · 73° 10' E", 9.5, (105, 149, 135), anchor="ra")


def main():
    img = ocean_layer().convert("RGBA")
    draw_ripples(img)
    draw_jetty(img)
    draw_island(img)
    draw_copy(img)

    out = img.convert("RGB").resize((W, H), Image.LANCZOS)
    out.save(OUT, "PNG", optimize=True)
    print(f"OK {OUT} {out.size} · {OUT.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
