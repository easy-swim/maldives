#!/usr/bin/env python3
"""v4 데이터 생성 — 공개용 공홈 실측 DB + 98곳 한줄평 + 49장 전경 사진 매핑 → data_v4.json

소스(이 파일들만 사용):
  - data_full_backup.json   : 98곳 공홈 예약엔진 4박 실측가(비치/워터 × 2월/7월, USD)
  - data.json               : 공개용 태그·성향·식사·풀·어른전용 표기, 2월/7월 대체 기준월 메모
  - ../maldives-98-one-liners.json : 98곳 리뷰 한줄평(good/bad/line) + 구글맵 평점
  - ../blog/resorts-image-map.md   : 1~49위 공홈 전경 사진 파일명(assets/resorts/)
  - assets/resorts/         : 실제 이미지 파일 존재 여부 확인

금액은 '4박 실측 범위(최저~최고)'만 담는다. 객실 타입별 정확한 금액과 세금 포함 총액은
이 파일에 넣지 않는다(59,000원 패키지 범위).

    python3 make_data_v4.py
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
WORK = BASE.parent
IMG_DIR = BASE / "assets" / "resorts"

# 1~49위(콘텐츠 발행 순위) → data id. 근거: work/blog/resorts-image-map.md 표의 순위·이름
RANK_ID = {
    1: ("벨리간두", 12, "01-veligandu.jpg"),
    2: ("NH 하보다", 14, "02-havodda.jpg"),
    3: ("오젠 라이프 마두", 13, "03-ozen-lifemadu.jpg"),
    4: ("힐튼 아밍기리", 42, "04-hilton-amingiri.jpg"),
    5: ("럭스 사우스 아리아톨", 27, "05-lux-south-ari-atoll-crop.jpg"),
    6: ("마푸시바루", 5, "06-maafushivaru.jpg"),
    7: ("선시암 올후벨리", 19, "07-olhuveli.jpg"),
    8: ("밀라이두", 15, "08-milaidhoo.jpg"),
    9: ("아야다", 17, "09-ayada.jpg"),
    10: ("아난타라 키하바", 20, "10-anantara-kihavah.jpg"),
    11: ("후라왈리", 18, "11-hurawalhi.jpg"),
    12: ("인터컨티넨탈", 43, "12-intercontinental.jpg"),
    13: ("헤리턴스 아라", 53, "13-heritance-aarah.jpg"),
    14: ("릴리비치", 33, "14-lily-beach.jpg"),
    15: ("센타라 컬렉션 마차푸시", 47, "15-centara-machchafushi.jpg"),
    16: ("콘래드", 48, "16-conrad.jpg"),
    17: ("코라코라", 28, "17-cora-cora.jpg"),
    18: ("니바 디갈리", 45, "18-dhigali.jpg"),
    19: ("빌라멘두", 6, "19-vilamendhoo.jpg"),
    20: ("두짓 D2", 36, "20-dusitd2.jpg"),
    21: ("시루펜푸시", 44, "21-sirrufenfushi.jpg"),
    22: ("더 레지던스 디구라", 21, "22-residence-dhigurah.jpg"),
    23: ("아바니 플러스 파레스", 16, "23-avani-fares.jpg"),
    24: ("오블루 상겔리", 50, "24-sangeli.jpg"),
    25: ("에메랄드 몰디브", 96, "25-emerald.jpg"),
    26: ("니야마", 52, "26-niyama.jpg"),
    27: ("센타라 미라지", 54, "27-centara-mirage.jpg"),
    28: ("월도프 아스토리아", 46, "28-waldorf.jpg"),
    29: ("파크 하얏트 하다하", 11, "29-parkhyatt-hadahaa.jpg"),
    30: ("소네바자니", 51, "30-sonevajani.jpg"),
    31: ("하드락", 70, "31-hardrock.jpg"),
    32: ("앙사나 벨라바루", 9, "32-velavaru.jpg"),
    33: ("에메랄드 파루푸시", 97, "33-faarufushi.jpg"),
    34: ("오블루 헬렝겔리", 56, "34-helengeli.jpg"),
    35: ("바루 바이 앳모스피어", 23, "35-varu.jpg"),
    36: ("코코보두히티", 7, "36-cocoboduhithi.jpg"),
    37: ("반얀트리", 64, "37-vabbinfaru.jpg"),
    38: ("두짓타니", 39, "38-dusitthani.jpg"),
    39: ("팔루마푸시", 22, "39-falhumaafushi.jpg"),
    40: ("리츠칼튼", 61, "40-ritzcarlton.jpg"),
    41: ("파티나", 60, "41-patina.jpg"),
    42: ("쿠라마티", 63, "42-kuramathi.jpg"),
    43: ("오젠 리저브 볼리푸시", 31, "43-ozen-reserve-bolifushi.jpg"),
    44: ("알릴라 코타이파루", 30, "44-alila-kothaifaru.jpg"),
    45: ("길리랑칸푸시", 35, "45-gili-lankanfushi.jpg"),
    46: ("바카루", 62, "46-vakkaru.jpg"),
    47: ("발리오니", 49, "47-baglioni.jpg"),
    48: ("쿠다 빌링길리", 4, "48-kuda-villingili.jpg"),
    49: ("할시온 프라이빗 아일스", 32, "49-halcyon.jpg"),
}

REASON = {
    "blocked": "공홈이 자동 조회를 막아 요금을 못 봤어요",
    "no-engine": "공홈에 온라인 예약엔진이 없어요",
    "closed": "휴장·개보수 또는 2027년 예약 미오픈",
    "soldout": "조회 기간(2027-02-21~25·07-18~22)에 판매 객실 없음",
    "unknown": "공홈에서 요금을 확인하지 못했어요",
}

# 이름·브랜드가 바뀐 곳 (2026-11 조회 시점 표기 기준, 이름 안의 '구 ' 표기와 notes 근거)
RENAMED = {45, 47, 57, 32, 41}  # 니바 디갈리 · 더 센타라 컬렉션 · 멜리아 웨일 라군 · 할시온 · 모벤픽


def main() -> None:
    full = json.loads((BASE / "data_full_backup.json").read_text(encoding="utf-8"))
    pub = {r["id"]: r for r in json.loads((BASE / "data.json").read_text(encoding="utf-8"))}
    ones = {r["id"]: r for r in json.loads((WORK / "maldives-98-one-liners.json").read_text(encoding="utf-8"))}
    assert len(full) == 98 and len(pub) == 98 and len(ones) == 98

    img_by_id, rank_by_id = {}, {}
    for rank, (label, rid, fname) in RANK_ID.items():
        path = IMG_DIR / fname
        if not path.exists():
            raise SystemExit(f"[FAIL] 사진 없음: {path}")
        img_by_id[rid] = f"assets/resorts/web/{fname}"
        rank_by_id[rid] = (rank, label)

    out = []
    for r in full:
        rid = r["id"]
        p = r.get("prices") or {}
        def total(k):
            return (p.get(k) or {}).get("total")
        feb = [v for v in (total("febBeach"), total("febWater")) if v]
        jul = [v for v in (total("julBeach"), total("julWater")) if v]
        one = ones[rid]
        nm = re.match(r"^(.*?)\s*\((.*)\)$", r["name"])
        ko, en = (nm.group(1), nm.group(2)) if nm else (r["name"], "")
        pubrow = pub[rid]

        tax = "inc" if r.get("taxIncluded") else ("unknown" if r.get("taxUnknown") else "excl")
        froms = [v for v in (feb + jul)]
        item = {
            "id": rid,
            "ko": ko,
            "en": en,
            "atoll": r["atoll"],
            "type": r["type"],
            "transfer": r["transfer"],
            "transferKind": r.get("transferKind") or r["transfer"],
            "meal": r.get("meal"),
            "pool": r.get("pool"),
            "adult": r.get("adult"),
            "big": r.get("big"),
            "tags": r.get("tags") or [],
            "pros": (r.get("pros") or [])[:4],
            "cons": (r.get("cons") or [])[:3],
            "line": one.get("line") or "",
            "good": one.get("kw_good") or "",
            "bad": one.get("kw_bad") or "",
            "gm": one.get("gm_rating"),
            "gmCount": one.get("gm_count"),
            "feb": [min(feb), max(feb)] if feb else None,
            "jul": [min(jul), max(jul)] if jul else None,
            "from": min(froms) if froms else None,
            "tax": tax,
            "greenIncluded": bool(r.get("greenIncluded")),
            "monthNote": pubrow.get("monthNote") or [],
            "reasonCode": r.get("reason"),
            "reason": REASON.get(r.get("reason") or "", "") or None,
            "url": r.get("url") or "",
            "img": img_by_id.get(rid),
            "rank": rank_by_id.get(rid, (None, None))[0],
        }
        item["hasWater"] = bool(total("febWater") or total("julWater"))

        # 구간 분류 — 4박 실측 시작가 기준
        sec = []
        f = item["from"]
        if f is not None:
            if f < 2500:
                sec.append("value")
            elif f < 5000:
                sec.append("main")
            else:
                sec.append("lux")
        if "신상" in item["tags"] or "모던" in item["tags"] or rid in RENAMED or "구 " in ko:
            sec.append("hot")
        item["sec"] = sec
        out.append(item)

    priced = [x for x in out if x["from"] is not None]
    both = [x for x in out if x["feb"] and x["jul"]]
    # 같은 객실(비치↔비치, 워터↔워터)로 2월·7월을 맞춰 비교한 쌍
    pairs = []
    for r in full:
        p = r.get("prices") or {}
        for a, b in (("febBeach", "julBeach"), ("febWater", "julWater")):
            x = (p.get(a) or {}).get("total")
            y = (p.get(b) or {}).get("total")
            if x and y:
                pairs.append(y / x)
    pairs.sort()
    med = pairs[len(pairs) // 2]
    meta = {
        "total": len(out),
        "priced": len(priced),
        "bothMonths": len(both),
        "withPhoto": sum(1 for x in out if x["img"]),
        "sections": {k: sum(1 for x in out if k in x["sec"]) for k in ("value", "main", "lux", "hot")},
        "pairCount": len(pairs),
        "pairMedianDiscount": round((1 - med) * 100),
        "pairCheaperShare": round(100 * sum(1 for q in pairs if q < 1) / len(pairs)),
        "pairBigDiscountShare": round(100 * sum(1 for q in pairs if q < 0.8) / len(pairs)),
        "febCheapest": (min(priced, key=lambda x: x["from"])["ko"], min(x["from"] for x in priced)),
        "febMax": max((x["feb"][1] for x in out if x["feb"]), default=None),
        "checked": "2026-11-19~24",
        "stays": "2027-02-21~25 · 2027-07-18~22",
    }
    (BASE / "data_v4.json").write_text(json.dumps({"meta": meta, "resorts": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("OK data_v4.json", json.dumps(meta, ensure_ascii=False))
    print("누락:", [(x["id"], x["ko"]) for x in out if x["from"] is None])


if __name__ == "__main__":
    main()
