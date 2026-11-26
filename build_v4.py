#!/usr/bin/env python3
"""v4 사이트 빌드 — template_v4.html + data_v4.json → index.html

    python3 make_data_v4.py && python3 build_v4.py

빌드 전 검사:
  - 리조트 98곳 · 요금 확보 87곳
  - 데이터에 </script 문자열 없음
  - OG 메타태그·노션 CTA·여행사 9곳·3분 진단 자리 유지
  - 입금 계좌번호(숫자-숫자-숫자) 노출 없음
  - 남의 브랜드 용어(입학시험·교재실·캠퍼스)·내부 호칭(피클·라뷰) 없음
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
TPL = BASE / "template_v4.html"
DATA = BASE / "data_v4.json"
OUT = BASE / "index.html"

FORBIDDEN = ["입학시험", "교재실", "캠퍼스", "몰디브대학", "피클", "라뷰"]
REQUIRED = [
    "og:image",
    "assets/og-cover.png",
    "https://app.notion.com/p/1-1-424ad1a95078812b999cc5a134099124",
    "https://docs.google.com/forms/d/e/1FAIpQLSfBbRKPUfFeXjRlNFHVqY-H5gHcgKblJUALwyOMBn5VUtnkIw/viewform",
    "이지스윔 몰디브 노트",
    "__MALDIVES_DATA__",
]


def main() -> None:
    raw = json.loads(DATA.read_text(encoding="utf-8"))
    resorts = raw["resorts"]
    if len(resorts) != 98:
        raise SystemExit(f"[FAIL] 리조트는 98곳이어야 합니다 (현재 {len(resorts)})")
    priced = sum(1 for r in resorts if r.get("feb") or r.get("jul"))
    if priced < 80:
        raise SystemExit(f"[FAIL] 요금 확보 리조트가 너무 적습니다 ({priced}곳)")

    html = TPL.read_text(encoding="utf-8")
    for token in REQUIRED:
        if token not in html:
            raise SystemExit(f"[FAIL] 템플릿에 필수 항목이 없습니다: {token}")

    payload = json.dumps(raw, ensure_ascii=False, separators=(",", ":"))
    if "</script" in payload.lower():
        raise SystemExit("[FAIL] 데이터에 </script 문자열이 있습니다")
    html = html.replace("__MALDIVES_DATA__", payload)

    for bad in FORBIDDEN:
        if bad in html:
            raise SystemExit(f"[FAIL] 금지 문구가 남아 있습니다: {bad}")

    # 공개 페이지에 입금 계좌번호 형태(숫자 3~6-2~6-2~8)가 없어야 한다
    acct = re.findall(r"\b\d{3,6}-\d{2,8}-\d{4,8}\b", html)
    if acct:
        raise SystemExit(f"[FAIL] 계좌번호로 보이는 문자열: {acct[:3]}")

    OUT.write_text(html, encoding="utf-8")
    print(f"OK index.html {len(html):,}자 · 리조트 {len(resorts)}곳 · 요금 확보 {priced}곳")
    print(f"   사진 {sum(1 for r in resorts if r.get('img'))}장 · 레일 "
          f"실속 {raw['meta']['sections']['value']} / 메인 {raw['meta']['sections']['main']} / "
          f"럭셔리 {raw['meta']['sections']['lux']} / 화제 {raw['meta']['sections']['hot']}")


if __name__ == "__main__":
    main()
