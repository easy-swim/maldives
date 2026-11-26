# 몰디브 리조트 98곳 — 2월·7월 4박 실측가 카드 비교 (무료 공개판 v4)

영업 중인 몰디브 리조트 98곳을 각 리조트 공식 홈페이지 예약엔진에서 직접 조회해 정리한 비교 페이지입니다.

- 사이트: https://easy-swim.github.io/maldives/
- 조회 조건: 성인 2인 1실 · USD · 2027-02-21~25(2월) / 2027-07-18~22(7월) 각 4박
- 데이터 기준일: 2026-11-19~24 (98곳 전수 조회 · 87곳 요금 확보 · 82곳은 2월·7월 둘 다)
- 무료 공개 범위: 카테고리별 카드(실속·메인·럭셔리·리노베이션), **2월·7월 4박 실측 범위**, 단점 한 줄, 공홈 전경 사진 49장, 1~12월 시즌 가이드, 이동수단 3종, 숨은 비용 3가지, 98곳 검색·필터·상세 모달, 최대 3곳 비교함, **3분 진단**(여덟 질문 → 여행사 요청서), 국내 여행사 9곳 링크
- 별도 제공(59,000원 패키지): 찜 3곳 + 추천 5곳(총 8곳)의 **객실별 정확한 금액·세금 포함 총액·두 분 날짜 기준 공홈·아고다 비교** + 1:1 줌 컨설팅

## 구조 (v4, 2026-11-27)

| 파일 | 역할 |
| --- | --- |
| `template_v4.html` | 화면 템플릿(HTML+CSS+JS 단일 파일). 데이터 자리에 `__MALDIVES_DATA__` 자리표시자 |
| `make_data_v4.py` | `data_full_backup.json` + `data.json` + `../maldives-98-one-liners.json` + 사진 매핑 → `data_v4.json` |
| `data_v4.json` | v4 공개용 데이터(98곳). 4박 실측은 **범위(min~max)만** 담고 객실별 정확 금액은 넣지 않음 |
| `build_v4.py` | `template_v4.html` + `data_v4.json` → `index.html` (금지 문구·계좌번호·필수 링크 검사 포함) |
| `index.html` | 배포본(외부 라이브러리 없이 동작하는 단일 파일, 데이터 내장) |
| `assets/resorts/*.jpg` | 1~49위 공홈 전경 원본(블로그 임베드용) |
| `assets/resorts/web/*.jpg` | 사이트 카드용 900px·품질 78 리사이즈본(사이트는 이쪽만 참조) |
| `make_og_cover.py` | 카톡·스레드·DM 공유 미리보기 카드 → `assets/og-cover.png` (1200×630) |

## 빌드·배포

    cd work/maldives-site
    python3 make_data_v4.py     # 원본 데이터 → data_v4.json
    python3 build_v4.py         # 템플릿 + 데이터 → index.html
    git add -A && git commit -m "..." && git push origin main
    # GitHub Pages는 gh-pages 브랜치를 서빙한다(index.html·assets 포함해 함께 push)

공유 카드 문구는 `template_v4.html` `<head>`의 `og:*`·`twitter:*` 태그에서 고칩니다. `og:image`는 절대 주소
`https://easy-swim.github.io/maldives/assets/og-cover.png` 그대로 둡니다(카톡이 그림을 읽으려면 절대 주소여야 함).

## 공개 범위 원칙

- 무료 페이지에는 **4박 실측 범위**(가장 낮은 객실~가장 높은 객실)까지만 싣습니다. 객실 타입별 정확한 금액,
  세금 포함 총액, 두 분 날짜 기준 재조회는 59,000원 패키지의 범위입니다.
- 입금 계좌번호·예금주는 공개 페이지에 넣지 않습니다(신청서 안내).
- 남의 사이트 브랜드 용어(입학시험·교재실·캠퍼스 등)는 쓰지 않습니다. `build_v4.py`가 검사합니다.

## 이전 버전

- v3(`template_v3.html`·`data.json`·`build_v3.py`·`make_template_v3.py`, 2026-11-26): 사이드바형 대시보드 · 1박 예산 구간만 공개
- v2(`build_v2.py`·`free_app.js`): 이력 보관용, 배포에 쓰지 않음
- `assets/detail/card-01~05.png`: 노션 상세페이지용 카드 이미지

요금은 프로모션·재고·환율에 따라 달라집니다. 예약 전 공홈에서 다시 확인하세요.

공홈 조회·정리: 이지스윔(@easyswim__)
