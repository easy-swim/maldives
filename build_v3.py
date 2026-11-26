#!/usr/bin/env python3
"""v3 사이트 빌드 — template_v3.html + data.json → index.html

data.json(98곳, 1박 예산 구간까지만 담긴 공개용 데이터)을 템플릿의 __MALDIVES_DATA__ 자리에 넣는다.
정확한 금액·총액은 data.json에 없으므로 무료 사이트로 새어 나가지 않는다.

    python3 build_v3.py
"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
TPL = BASE / "template_v3.html"
DATA = BASE / "data.json"
OUT = BASE / "index.html"


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) != 98:
        raise SystemExit(f"[FAIL] data.json은 98곳 목록이어야 합니다 (현재 {len(data) if isinstance(data, list) else type(data)})")

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    if "</script" in payload.lower():
        raise SystemExit("[FAIL] 데이터에 </script 문자열이 있어 그대로 넣을 수 없습니다")

    html = TPL.read_text(encoding="utf-8")
    if "__MALDIVES_DATA__" not in html:
        raise SystemExit("[FAIL] template_v3.html에 __MALDIVES_DATA__ 자리표시자가 없습니다")

    html = html.replace("__MALDIVES_DATA__", payload)
    OUT.write_text(html, encoding="utf-8")
    print(f"OK index.html {len(html):,}자 · 리조트 {len(data)}곳")


if __name__ == "__main__":
    main()
