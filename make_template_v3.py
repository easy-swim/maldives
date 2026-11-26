#!/usr/bin/env python3
"""클로드 아티팩트(design-ref/claude/artifact_original.html)를 v3 템플릿으로 정리한다.

- 문구 일관성 수정(라뷰/이지의 → 이지스윔, 조회 기간 2026-11-19~24, 피클 언급 제거, 3분 진단)
- 데이터 스크립트를 __MALDIVES_DATA__ 자리표시자로 바꿔 data.json 한 곳에서만 관리
출력: template_v3.html  (index.html은 build_v3.py가 만든다)
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SRC = BASE / "design-ref" / "claude" / "artifact_original.html"
OUT = BASE / "template_v3.html"

html = SRC.read_text(encoding="utf-8")

REPL = [
    # 표지/브랜드
    ("<title>이지스윔 몰디브 노트</title>",
     "<title>몰디브 리조트 98곳 예산대·3분 진단 비교 | 이지스윔</title>", 1),
    ("<span>이지스윔<small>데이터 2026-11-24 · USD</small></span>",
     "<span>이지스윔<small>데이터 2026-11-19~24 · USD</small></span>", 1),
    ('<div class="eyebrow">이지의 몰디브 자료</div>',
     '<div class="eyebrow">이지스윔 몰디브 노트</div>', 1),
    # 조회 기간 통일 (2026-11-19~24)
    ("2027년 2월·7월 슬롯을 2026년 11월 24일에 조회한 기록입니다",
     "2027년 2월·7월 슬롯을 2026년 11월 19~24일에 조회한 기록입니다", 1),
    ("2026-11-19~11-24에 각 리조트 <b>공식 홈페이지의 예약엔진</b>",
     "2026-11-19~24에 각 리조트 <b>공식 홈페이지의 예약엔진</b>", 1),
    ("데이터 기준 2026-11-24 · 통화 USD",
     "데이터 기준 2026-11-19~24 · 통화 USD", 1),
    ("(2026-11-24 공홈 조회 · 이지스윔)",
     "(2026-11-19~24 공홈 조회 · 이지스윔)", 1),
    ("2026-11-19~11-24에 각 리조트 공식 홈페이지의 예약엔진",
     "2026-11-19~24에 각 리조트 공식 홈페이지의 예약엔진", 1),
    ("(2026-11-21~24 공식 홈페이지 직접 조회)",
     "(2026-11-19~24 공식 홈페이지 직접 조회)", 1),
    ("조회 시점(2026-11-21~24)", "조회 시점(2026-11-19~24)", 1),
    ("2026년 11월 21~24일 기준", "2026년 11월 19~24일 기준", 1),
    # 3분 진단 표기 통일 (죽은 '여행 기준' 화면 문구 포함)
    ('<div class="note-inline"><b>질문 5문항 뼈대</b>',
     '<div class="note-inline"><b>3분 진단 구성</b>', 1),
    ("'<b>여행 기준</b> 탭에서 다섯 질문에 답하면 조건에 맞는 후보 3곳을 추려 드려요. 기준이 흐리면 후보가 30곳 넘게 남습니다.'",
     "'<b>3분 진단</b> 탭에서 여덟 개를 누르면 여행사에 보낼 요청서가 만들어지고, 리조트 찾기 필터도 함께 맞춰져요. 기준이 흐리면 후보가 30곳 넘게 남습니다.'", 1),
    # 내부 호칭 정리
    ("피클이 쓴 10분 기준표의 순서를 따랐습니다",
     "이지스윔이 정리한 10분 기준표의 순서를 따랐습니다", 1),
    ("(피클 노션 상세페이지 ①~⑧ 순서 그대로)", "(상세페이지 ①~⑧ 순서 그대로)", 1),
    ("(피클 최종본: 4단계)", "(4단계)", 1),
]

for old, new, want in REPL:
    n = html.count(old)
    if n != want:
        sys.exit(f"[FAIL] {n}회 발견(기대 {want}): {old[:60]}")
    html = html.replace(old, new)

# 가이드 문구를 원본 데이터에서 고쳤으므로 런타임 치환 핵( fixG + MutationObserver ) 제거
FIXG = """    /* 가이드 1단계 문구: 없어진 '여행 기준 탭'을 3분 진단으로 안내 */
    var gl = $('#guideList');
    if (gl) {
      var fixG = function () {
        var s = '<b>여행 기준</b> 탭에서 다섯 질문에 답하면 조건에 맞는 후보 3곳을 추려 드려요.';
        if (gl.innerHTML.indexOf(s) > -1) gl.innerHTML = gl.innerHTML.split(s).join('<b>3분 진단</b> 탭에서 여덟 개를 누르면 여행사에 보낼 요청서가 만들어지고, 리조트 찾기 필터도 함께 맞춰져요.');
      };
      fixG(); new MutationObserver(fixG).observe(gl, { childList: true, subtree: true });
    }

"""
if FIXG not in html:
    sys.exit("[FAIL] fixG 블록을 찾지 못했습니다")
html = html.replace(FIXG, "")

# 데이터: 한 곳(data.json)에서만 관리
m = re.search(r'<script id="data" type="application/json">.*?</script>', html, re.S)
if not m:
    sys.exit("[FAIL] 데이터 스크립트를 찾지 못했습니다")
html = html[:m.start()] + '<script id="data" type="application/json">__MALDIVES_DATA__</script>' + html[m.end():]

for bad in ["라뷰", "이지의 몰디브", "피클"]:
    if bad in html:
        sys.exit(f"[FAIL] 금지 문구 남음: {bad}")

OUT.write_text(html, encoding="utf-8")
print(f"OK template_v3.html {len(html):,}자")
