# -*- coding: utf-8 -*-
"""몰디브 98곳 비교 사이트 — 무료 공개판(지피티 디자인) 빌드.

무료 공개 범위: 질문형 추천(5문항) · 유형/이동수단/성향/만타·고래상어/예산 필터 ·
리조트별 특징·장단점 · 1박 예산 구간(tier)만 노출.
정확한 2월·7월 1박 달러 금액, 세금 포함 환산액, 7월 할인율은 넣지 않는다 → 59,000원 패키지 CTA.

입력: work/maldives-site/data_full_backup.json  (정확한 금액 포함 원본 · 로컬 보관 / 배포 금지)
출력: work/maldives-site/index.html  (배포본)
      work/maldives-site/data.json    (무료 공개용 — 예산 구간·성향만)
JS  : work/maldives-site/free_app.js
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
full = json.load(open(os.path.join(HERE, "data_full_backup.json"), encoding="utf-8"))

TIER_LABELS = ["$500대", "$600~800대", "$900~1,200대", "$1,300~1,900대", "$2,000~2,900대", "$3,000+"]
TIER_MAX = [600, 900, 1300, 2000, 3000]  # 구간 상한(USD, 1박 · 세금 포함 추정) / 마지막 라벨은 3,000+


def tier_idx(v):
    if not v:
        return None
    for i, hi in enumerate(TIER_MAX):
        if v < hi:
            return i
    return len(TIER_LABELS) - 1


def clean_meal(s):
    # 식사 플랜 괄호 안의 할인율 표기만 제거 (금액·할인 정보 비노출)
    s = re.sub(r"\((?:\d+~\d+%\s*할인|Save\s*\d+%|\d+%\s*할인)\)", "", s or "")
    s = re.sub(r"(?:\d+~\d+%|\d+)%\s*할인", "할인 프로모션", s)
    return s.strip()


def free_row(r):
    feb = r["est"].get("febWater") or r["est"].get("febBeach")
    jul = r["est"].get("julWater") or r["est"].get("julBeach")
    row = {k: r.get(k) for k in ("id", "name", "type", "atoll", "transfer", "transferKind", "big",
                                 "tags", "adult", "pool", "taxIncluded", "taxUnknown",
                                 "pros", "cons", "monthNote")}
    row["meal"] = clean_meal(r.get("meal"))
    row["url"] = r.get("url")
    row["tFeb"] = tier_idx(feb)
    row["tJul"] = tier_idx(jul)
    row["reason"] = (r.get("reason") or "") if not feb else ""
    return row


rows = [free_row(r) for r in full]
DATA_JSON = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))

HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>몰디브 리조트 98곳 예산대·성향 비교 | 이지스윔</title>
<meta name="description" content="영업 중인 몰디브 리조트 98곳을 공식 홈페이지 예약엔진에서 직접 조회해 정리했습니다. 바다 형태·이동수단·성향·1박 예산대로 골라 보고, 최대 3곳을 나란히 비교하세요.">
<meta name="theme-color" content="#f8f7f3">
<meta property="og:type" content="website">
<meta property="og:title" content="몰디브 리조트 98곳, 취향과 예산대로 고르기">
<meta property="og:description" content="영업 중 98곳 · 2027년 2월 성수기 / 7월 비수기 · 1박 예산대와 리조트 성향 · 최대 3곳 비교">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23e6f2eb'/%3E%3Cpath d='M10 38c6-6 10-6 16 0s10 6 16 0 10-6 16 0' stroke='%232d7a6e' stroke-width='4' fill='none' stroke-linecap='round'/%3E%3Cpath d='M10 48c6-6 10-6 16 0s10 6 16 0 10-6 16 0' stroke='%232d7a6e' stroke-width='4' fill='none' stroke-linecap='round' opacity='.55'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet">
<style>
:root{
  --paper:#f8f7f3; --surface:#fff; --ink:#183e40; --ink2:#235f56;
  --muted:#586c65; --muted2:#7a8d8a; --faint:#6f8579;
  --green:#2d7a6e; --green-d:#235f56; --mint:#e9f2eb; --mint2:#dcece7; --mint3:#eff6f3;
  --sand:#efece4; --gold:#9a8750; --line:#e4ebe6; --line2:#d6e3df; --line3:#dbe4d6;
  --r6:6px; --r9:9px; --r12:12px; --r18:18px;
  --shadow:0 5px 30px rgba(17,34,51,.10);
}
*{box-sizing:border-box;margin:0;padding:0}
html{-webkit-text-size-adjust:100%}
body{
  font-family:"Noto Sans KR",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",Arial,sans-serif;
  background:var(--paper); color:var(--ink); font-size:14px; line-height:1.5;
  -webkit-font-smoothing:antialiased; word-break:keep-all; overflow-wrap:anywhere;
}
a{color:var(--green);text-decoration:none}
button{font:inherit;color:inherit;background:none;border:0;cursor:pointer;transition:background .15s,transform .15s}
button:hover{filter:brightness(.97)}
button:disabled{opacity:.5;cursor:wait}
:is(button,a,input,select):focus-visible{outline:3px solid #61bbae;outline-offset:3px}
svg{vertical-align:middle;flex-shrink:0}
[hidden]{display:none !important}

/* ---------- shell ---------- */
.shell{display:flex;min-height:100vh}
.side{position:fixed;inset:0 auto 0 0;width:246px;background:#fff;border-right:1px solid var(--line);
  padding:34px 20px 22px;display:flex;flex-direction:column;overflow-y:auto;z-index:30}
.brand{display:flex;align-items:center;gap:12px;text-align:left;width:100%}
.brand .bi{width:43px;height:43px;border-radius:14px;background:var(--mint);color:var(--green);display:grid;place-items:center}
.brand b{display:block;font-size:23px;font-weight:800;letter-spacing:-1px;line-height:1.15}
.brand small{display:block;font-size:8px;font-weight:500;letter-spacing:1.7px;margin-top:3px;color:var(--ink)}
.space-label{font-size:10px;letter-spacing:1px;color:#8e9d96;margin:44px 12px 15px}
.side nav{display:flex;flex-direction:column;gap:5px}
.side nav button{display:flex;align-items:center;gap:12px;padding:12px 13px;border-radius:8px;
  font-size:12.5px;font-weight:500;color:#6a7d77;text-align:left;width:100%}
.side nav button.on{background:var(--mint);color:#17675e;font-weight:700}
.side nav button .cnt{margin-left:auto;font-size:10px;font-weight:600;color:#8aa79c}
.side nav button.on .cnt{color:#17675e}
.side-bottom{margin-top:auto;padding:40px 12px 0}
.side-bottom .sea{color:#8daaa0}
.side-bottom strong{display:block;font-size:17px;font-weight:500;line-height:1.7;letter-spacing:-.3px;margin-top:6px}
.side-bottom p{font-size:10px;color:var(--muted2);line-height:1.8;margin:6px 0 26px}
.host{display:flex;align-items:center;gap:10px;border-top:1px solid var(--line);padding-top:18px;font-size:10.5px;color:var(--ink)}
.host .av{width:32px;height:32px;border-radius:50%;background:#e9e7db;color:#78785c;display:grid;place-items:center;font-size:11px;flex:0 0 auto}
.host small{display:block;color:var(--muted2);font-size:9px;margin-top:3px}

.main{margin-left:246px;width:calc(100% - 246px);display:flex;flex-direction:column;min-height:100vh}
.topbar{height:77px;display:flex;align-items:center;justify-content:space-between;gap:16px;
  padding:0 44px;border-bottom:1px solid var(--line);background:rgba(255,255,255,.72);
  -webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);position:sticky;top:0;z-index:20;
  font-size:11px;color:#71847e}
.crumb{display:flex;align-items:center;gap:8px}
.crumb b{color:var(--ink);font-weight:600}
.crumb .sep{color:#b6cbc6}
.topbar .right{display:flex;align-items:center;gap:10px;white-space:nowrap}
.live{width:6px;height:6px;border-radius:50%;background:#3f9278;display:inline-block;margin-right:6px}
.avatar{width:32px;height:32px;border-radius:50%;background:#e9e7db;color:#78785c;display:grid;place-items:center;font-size:11px;margin-left:6px}

main.wrap{width:100%;max-width:1290px;margin:0 auto;padding:38px 44px 44px;flex:1}
.view{display:none}
.view.on{display:block}

/* ---------- shared ---------- */
.eyebrow{font-size:9px;letter-spacing:1.8px;color:#67877b;font-weight:600;text-transform:uppercase}
h1{font-size:29px;font-weight:600;letter-spacing:-1.2px;line-height:1.35;margin:10px 0 8px}
.lede{font-size:13px;color:var(--muted);line-height:1.85;max-width:680px}
.intro{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;margin-bottom:24px}
.intro .side-btn{flex:0 0 auto}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;border-radius:var(--r6);
  padding:12px 17px;font-size:11.5px;font-weight:500;white-space:nowrap}
.btn.primary{background:var(--green);color:#fff}
.btn.ghost{background:#fff;border:1px solid var(--line3);color:var(--ink2)}
.text-btn{display:inline-flex;align-items:center;gap:5px;font-size:10.5px;color:#7e9086}
.text-btn:hover{color:var(--green)}
.sec-head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:0 0 12px}
.sec-head h2{font-size:16.5px;font-weight:600;letter-spacing:-.4px}
.card{background:#fff;border:1px solid var(--line);border-radius:var(--r9)}

/* ---------- home: hero ---------- */
.hero{position:relative;background:var(--mint2);border-radius:var(--r12);min-height:300px;
  display:flex;overflow:hidden;isolation:isolate}
.hero-copy{position:relative;z-index:2;width:54%;padding:32px 36px 28px}
.pill{display:inline-block;border:1px solid #b8cfc3;border-radius:20px;padding:6px 10px;
  font-size:8px;letter-spacing:1.7px;color:var(--ink2);font-weight:500}
.hero h2{font-size:clamp(28px,3.1vw,38px);font-weight:500;letter-spacing:-1.6px;line-height:1.44;margin:16px 0 12px}
.hero p{font-size:11.5px;line-height:1.95;color:#5f7f75;max-width:360px}
.hero .under{display:inline-flex;align-items:center;gap:18px;border-bottom:1px solid #688d7f;
  padding:8px 0;font-size:11.5px;font-weight:500;color:var(--ink2);margin-top:18px}
.ocean{position:absolute;top:0;right:0;width:56%;height:100%;
  background:radial-gradient(at 56% 48%,#8ccfc1 12%,#aadacb 30%,#bddfd5 47%,#dcece7 70%)}
.island{position:absolute;top:29%;left:42%;width:145px;height:95px;background:#e8e1b7;
  border:10px solid #f4efd4;border-radius:48% 44% 52% 34%;transform:rotate(-28deg);
  box-shadow:0 0 0 14px rgba(156,214,195,.48),0 0 0 30px rgba(170,220,202,.33);display:grid;place-items:center}
.trees{width:100%;height:100%;border-radius:40%;background:radial-gradient(#679378,#88a98a 64%,#d1d4a5 66%);
  color:#f5faed;font-size:40px;line-height:1;display:grid;place-items:center}
.ripple{position:absolute;border:1px solid rgba(243,251,244,.66);border-radius:48%;transform:rotate(-28deg)}
.r1{width:260px;height:180px;top:17%;left:28%}
.r2{width:360px;height:260px;top:4%;left:18%}
.r3{width:460px;height:340px;top:-10%;left:7%}
.jetty{position:absolute;top:60%;left:65%;width:100px;height:4px;background:#c0b392;transform:rotate(32deg)}
.jetty:after{content:"";position:absolute;top:-8px;right:0;width:20px;height:20px;background:#b5a581;
  box-shadow:-30px 0 #b5a581,-60px 0 #b5a581}
.map-label{position:absolute;right:35px;bottom:38px;text-align:right;font-size:10px;letter-spacing:2px;color:#5a8d7d}
.map-label span{display:block;font-size:8px;letter-spacing:1px;margin-top:8px}
.art-cap{position:absolute;right:15px;bottom:10px;font-size:8px;color:#71998b}

/* ---------- home: promo / stats ---------- */
.promo{display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap;
  background:var(--sand);border-radius:var(--r9);padding:22px 26px;margin-top:20px}
.promo h2{font-size:16px;font-weight:600;letter-spacing:-.3px;margin:7px 0 5px}
.promo p{font-size:11.5px;color:#52635d;line-height:1.8}
.stats{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;background:#fff;border:1px solid var(--line);
  border-radius:var(--r9);margin-top:20px;padding:20px 0}
.stats>div{padding:0 24px;border-right:1px solid var(--line);min-width:0}
.stats>div:last-child{border-right:0}
.stats span{display:block;font-size:10.5px;color:var(--faint)}
.stats strong{display:block;font-size:22px;font-weight:600;letter-spacing:-.6px;margin:8px 0 5px}
.stats small{display:block;font-size:9.5px;line-height:1.7;color:var(--faint)}
.home-grid{display:grid;grid-template-columns:1.1fr 1fr;gap:28px;margin-top:28px}
.steps{background:#fff;border:1px solid var(--line);border-radius:var(--r9);padding:0 20px}
.steps button{display:flex;align-items:center;gap:14px;width:100%;text-align:left;padding:18px 0;border-bottom:1px solid var(--line)}
.steps button:last-child{border-bottom:0}
.steps .num{width:34px;height:34px;border-radius:50%;background:#f0f3e9;color:#718567;
  display:grid;place-items:center;font-size:11px;flex:0 0 auto}
.steps strong{display:block;font-size:12.5px;font-weight:600}
.steps p{font-size:10.5px;color:var(--faint);line-height:1.6;margin-top:5px}
.steps .chev{margin-left:auto;color:#a0afa6;font-size:15px}
.cands{display:flex;flex-direction:column;gap:10px}
.cand{display:flex;align-items:center;gap:13px;text-align:left;background:#fff;border:1px solid var(--line);
  border-radius:var(--r9);padding:12px 13px;width:100%}
.cand:hover{border-color:#c9dcd7}
.thumb{width:62px;height:62px;border-radius:7px;flex:0 0 auto;display:grid;place-items:center;color:#f5faed;
  background:radial-gradient(at 45%,#e0dbba 0 20%,#94b69a 21% 32%,#8dcbb8 33% 50%,#c7e4d5 51%)}
.thumb.t2{background:radial-gradient(at 50% 60%,#749381 0 17%,#eee4bc 18% 27%,#8fcbb9 28% 48%,#bcdfd9 49%)}
.thumb.t3{background:radial-gradient(at 60% 40%,#9ed3c4 0 18%,#e6e2c2 19% 26%,#8cc3b2 27% 52%,#d5ece4 53%)}
.cand-body{min-width:0;flex:1}
.cand small{display:block;font-size:8px;letter-spacing:1.3px;color:#8c9a8e}
.cand strong{display:block;font-size:12px;font-weight:600;margin:5px 0 3px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cand em{display:block;font-style:normal;font-size:10px;color:var(--faint)}
.cand .chev{color:#a0afa6;font-size:13px}
.banner{display:flex;align-items:center;gap:16px;background:#eff3ed;border:1px solid #e0e7da;
  border-radius:var(--r9);padding:20px 24px;margin-top:26px;flex-wrap:wrap}
.banner .txt{flex:1;min-width:200px}
.banner strong{font-size:12.5px;font-weight:600}
.banner p{font-size:10.5px;color:#869780;margin-top:5px;line-height:1.7}

/* ---------- catalog ---------- */
.catalog{background:#fff;border:1px solid var(--line2);border-radius:var(--r18);padding:clamp(16px,3vw,32px)}
.catalog h2{font-size:clamp(24px,3.2vw,36px);font-weight:500;letter-spacing:-1.6px;color:#194e47;margin:9px 0 10px;line-height:1.3}
.catalog .sub{font-size:11.5px;color:#47625d;line-height:1.85;max-width:860px}
.tools{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.field{flex:1 1 170px;min-width:140px}
.field.f2{flex:2 1 240px}
.field label{display:block;font-size:10.5px;color:#345d55;margin-bottom:6px}
input[type=search],input[type=text],input[type=number],select{
  width:100%;border:1px solid #b6cbc6;border-radius:8px;background:#fff;color:#233d36;
  padding:10px 11px;font-size:12.5px;font-family:inherit;-webkit-appearance:none;appearance:none}
select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%236f8579' stroke-width='1.4' fill='none'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 12px center;padding-right:30px}
input::placeholder{color:#9aa8a0}
.filters{display:flex;flex-wrap:wrap;gap:7px;margin-top:11px}
.filters .lbl{font-size:10px;color:#8ba198;letter-spacing:.6px;align-self:center;margin-right:2px}
.chip{border:1px solid #b6cbc6;border-radius:20px;padding:7px 13px;font-size:11.5px;color:#20584f;background:#fff}
.chip small{font-size:9.5px;opacity:.62;margin-left:4px}
.chip.on{background:var(--green-d);border-color:var(--green-d);color:#fff}
.chip.on small{opacity:.8}
.af{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.af:empty{margin:0}
.af .item{display:inline-flex;align-items:center;gap:6px;background:var(--mint);color:#17675e;
  border-radius:20px;padding:5px 10px;font-size:10.5px;font-weight:500}
.af .item button{color:#17675e;font-size:12px;line-height:1}
.count-row{display:flex;align-items:center;justify-content:space-between;gap:12px;
  border-top:1px solid #d5e3dd;margin-top:16px;padding-top:15px;font-size:11px;color:#50877c}
.count-row b{color:var(--ink);font-size:13px;font-weight:600}

.cmp-now{display:flex;align-items:center;gap:10px;flex-wrap:wrap;background:var(--mint3);
  border:1px solid #d9eee3;border-radius:10px;padding:14px 16px;margin-top:16px}
.cmp-now .names{display:flex;flex-wrap:wrap;gap:6px;flex:1;min-width:0}
.cmp-now .nm{display:inline-flex;align-items:center;gap:6px;background:#fff;border:1px solid #d5e3dd;
  border-radius:20px;padding:5px 9px;font-size:10.5px;color:#31564e}
.cmp-now .nm button{font-size:11px;color:#8ba198;line-height:1}

.grp{margin-top:22px}
.grp-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 8px;padding:0 2px 6px}
.grp-head h3{font-size:13px;font-weight:600;letter-spacing:-.2px;flex:0 0 auto;white-space:nowrap}
.grp-head span{font-size:10.5px;color:var(--muted2);flex:0 0 auto;white-space:nowrap}
.grp-head p{flex:1 0 100%;font-size:10.5px;color:var(--muted2);line-height:1.6}

.entry{position:relative;display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:14px 26px;
  padding:22px 0;border-top:1px solid var(--line);isolation:isolate}
.entry:first-of-type{border-top:0}
.entry.on h3:before{content:"✓";display:inline-block;margin-right:7px;color:var(--green);font-size:15px;vertical-align:2px}
.kicker{font-size:9.5px;letter-spacing:1px;color:#8c9a8e;text-transform:uppercase}
.entry h3{font-size:19px;font-weight:600;letter-spacing:-.5px;line-height:1.35;margin:7px 0 5px}
.entry h3 small{font-size:11.5px;font-weight:400;color:#8ba198;letter-spacing:0;margin-left:6px}
.meta{font-size:11.5px;color:#6f8579}
.badges{display:flex;flex-wrap:wrap;gap:5px;margin-top:9px}
.badge{font-size:9.5px;padding:4px 7px;border-radius:4px;background:#f1f5ef;color:#5d7364;font-weight:500}
.badge.warn{background:#f6f0df;color:#9a8750}
.badge.ok{background:#e6f1e8;color:#378064}
.badge.na{background:#f4eefb;color:#5b3f8a}
.why{margin-top:11px;font-size:11.5px;line-height:1.85;color:#5d7364}
.why .pro{color:#2f6b52}
.why .con{color:#a05a35}

.pbox{background:var(--mint3);border:1px solid #d9eee3;border-radius:10px;padding:13px 14px}
.pbox .plbl{font-size:9.5px;letter-spacing:1px;color:#5f8b7c;font-weight:600;display:block}
.pnow{display:flex;align-items:baseline;gap:7px;flex-wrap:wrap;margin:3px 0 2px}
.pnow b{font-size:26px;line-height:1.1;font-weight:600;letter-spacing:-1.1px;color:var(--green)}
.pnow span{font-size:10.5px;color:#6f8579}
.pest{font-size:10.5px;color:#5d7364;margin-top:4px}
.pest b{font-weight:600;color:var(--ink);font-size:11.5px}
.pest .q{color:var(--gold)}
.pgrid{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-top:10px}
.pgrid div{background:#fff;border:1px solid #e2efe9;border-radius:6px;padding:5px 7px}
.pgrid span{display:block;font-size:9px;color:#7a8d8a}
.pgrid b{font-size:12px;font-weight:600;color:#22383f}
.pgrid b.na{font-size:10px;color:var(--gold);font-weight:500}
.pdiff{font-size:10.5px;margin-top:8px;color:#5d7364}
.pdiff b{color:#2f6b52;font-weight:600}
.acts{display:flex;gap:6px;margin-top:10px}
.acts .cmp-btn{flex:1;border:1px solid #b6cbc6;border-radius:var(--r6);padding:10px;
  font-size:11.5px;font-weight:500;color:#20584f;background:#fff}
.acts .cmp-btn.on{background:var(--green);border-color:var(--green);color:#fff}
.acts .site{border:1px solid var(--line);border-radius:var(--r6);padding:10px 11px;font-size:11px;color:var(--muted);background:#fff}
.e-main{display:flex;flex-direction:column;min-width:0}
.memo{margin-top:auto;padding-top:14px}
.memo summary{font-size:10.5px;font-weight:600;color:#226154;cursor:pointer;list-style:none}
.memo summary::-webkit-details-marker{display:none}
.memo summary:before{content:"▸ ";color:#8ba198}
.memo[open] summary:before{content:"▾ "}
.memo .body{background:#fcfcf9;border:1px solid #eef3e8;border-radius:8px;padding:12px 14px;margin-top:8px;
  font-size:10.5px;line-height:1.9;color:#5d7364;display:grid;gap:3px}
.memo .body b{color:#41564f;font-weight:600}
.memo .body a{font-size:10px;word-break:break-all}
.empty{margin:26px 0;padding:52px 20px;text-align:center;border:1px dashed #d7e2d5;border-radius:10px;color:#829789}
.empty b{display:block;font-size:15px;font-weight:600;color:var(--ink);margin-bottom:6px}
.empty p{font-size:11.5px}

/* ---------- info card ---------- */
.info-card{background:#fff;border:1px solid var(--line);border-radius:var(--r9);padding:20px 24px;margin-top:24px;
  font-size:11.5px;color:#4b615d;line-height:1.9}
.info-card h3{font-size:12.5px;font-weight:600;color:var(--ink);margin-bottom:7px}
.info-card details{margin-top:10px;border-top:1px solid var(--line);padding-top:10px}
.info-card summary{font-size:11px;font-weight:600;color:#226154;cursor:pointer}
.info-card ul{margin:8px 0 0 16px;display:grid;gap:5px}
.info-card li{list-style:disc}

/* ---------- pick (질문형) ---------- */
.note-inline{background:#fbf7eb;border:1px solid #e9dfc4;border-radius:8px;padding:13px 16px;
  font-size:11px;color:#89764b;line-height:1.8;margin-bottom:16px}
.q-card{background:#fff;border:1px solid var(--line);border-radius:var(--r12);padding:20px 22px;margin-bottom:12px}
.q-top{display:flex;align-items:center;gap:11px}
.q-num{width:30px;height:30px;border-radius:50%;background:#f0f3e9;color:#718567;display:grid;place-items:center;
  font-size:11px;font-weight:600;flex:0 0 auto}
.q-card h2{font-size:15.5px;font-weight:600;letter-spacing:-.3px}
.q-hint{font-size:11px;color:#879587;line-height:1.75;margin:8px 0 0 41px}
.opts{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0 0 41px}
.result{background:var(--mint3);border:1px solid #d9eee3;border-radius:var(--r12);padding:20px 22px;margin-top:20px}
.result h2{font-size:16px;font-weight:600;margin-bottom:4px}
.result p.rs{font-size:11px;color:#5d7364;line-height:1.8;margin-bottom:12px}
.rcand{background:#fff;border:1px solid #d5e3dd;border-radius:10px;padding:14px 16px;margin-top:9px;
  display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.rcand .rbody{flex:1;min-width:180px}
.rcand strong{display:block;font-size:14px;font-weight:600;letter-spacing:-.3px}
.rcand small{display:block;font-size:10.5px;color:var(--faint);margin-top:4px;line-height:1.7}
.rcand .rprice{font-size:18px;font-weight:600;color:var(--green);letter-spacing:-.5px;white-space:nowrap}
.rcand .rprice small{display:block;font-size:9px;color:#7a8d8a;text-align:right;letter-spacing:0}

/* ---------- budget ---------- */
.bcard{background:#fff;border:1px solid var(--line);border-radius:var(--r12);padding:20px 22px;margin-bottom:14px}
.bgrid{display:grid;grid-template-columns:1fr 1fr;gap:14px 16px}
.bgrid label{display:block;font-size:10.5px;color:#345d55;margin-bottom:6px}
.bnote{font-size:10.5px;color:#89764b;background:#fbf7eb;border:1px solid #e9dfc4;border-radius:6px;
  padding:11px 13px;line-height:1.8;margin-bottom:14px}
.total{display:flex;align-items:baseline;gap:22px;flex-wrap:wrap;background:var(--mint3);border:1px solid #d9eee3;
  border-radius:10px;padding:16px 18px;margin-top:6px}
.total .cell span{display:block;font-size:10px;color:#5f8b7c}
.total .cell b{font-size:24px;font-weight:600;letter-spacing:-.8px;color:var(--green)}
.total .cell.small b{font-size:17px;color:var(--ink)}
.bars{margin-top:16px;display:grid;gap:10px}
.barrow{display:grid;grid-template-columns:110px minmax(0,1fr) 92px;gap:10px;align-items:center;font-size:10.5px;color:#5d7364}
.track{height:10px;border-radius:6px;background:#efece4;overflow:hidden}
.track i{display:block;height:100%;background:var(--green);border-radius:6px}
.barrow b{text-align:right;font-weight:600;color:#22383f}

/* ---------- guide ---------- */
.guide-head{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:16px}
.progress{flex:1;height:6px;border-radius:6px;background:#efece4;overflow:hidden;min-width:120px}
.progress i{display:block;height:100%;background:var(--green);width:0}
.guide-item{display:flex;gap:16px;background:#fff;border:1px solid var(--line);border-radius:var(--r12);
  padding:20px 22px;margin-bottom:12px}
.g-num{width:38px;height:38px;border-radius:50%;background:#f0f3e9;color:#718567;display:grid;place-items:center;
  font-size:12px;font-weight:600;flex:0 0 auto}
.guide-item.done .g-num{background:#d9eee3;color:#287c65}
.guide-item h2{font-size:15.5px;font-weight:600;letter-spacing:-.3px;margin:2px 0 6px}
.guide-item p{font-size:11.5px;color:#6e8777;line-height:1.85}
.g-detail{background:#f4f6ef;border-radius:6px;padding:13px 15px;font-size:11px;line-height:1.95;color:#718577;margin:11px 0}
.g-detail b{color:#41564f;font-weight:600}
.g-btn{border:1px solid #b6cbc6;border-radius:var(--r6);padding:9px 13px;font-size:11px;font-weight:500;color:#20584f;background:#fff}
.guide-item.done .g-btn{background:var(--mint);border-color:#c7e4d5;color:#287c65}

/* ---------- tray / sheet ---------- */
.tray{position:fixed;left:0;right:0;bottom:0;z-index:40;background:rgba(248,247,243,.96);
  -webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);border-top:1px solid #d5e3dd;
  box-shadow:0 -6px 24px rgba(17,34,51,.07);padding:9px 0 calc(9px + env(safe-area-inset-bottom))}
.tray .inner{max-width:1290px;margin:0 auto;padding:0 44px;display:flex;align-items:center;gap:12px}
.tray .txt{flex:1;min-width:0;font-size:10.5px;color:var(--muted)}
.tray .txt b{display:block;font-size:12px;font-weight:600;color:var(--ink);margin-bottom:1px}
.tray .names{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tray .go{flex:0 0 auto;background:var(--green);color:#fff;border-radius:var(--r6);padding:11px 15px;
  font-size:11.5px;font-weight:500;display:inline-flex;align-items:center;gap:6px}
.tray .go.off{background:#dfe7e1;color:#93a49b}
.tray .go .n{background:rgba(255,255,255,.22);border-radius:20px;padding:1px 6px;font-size:10px}

.sheet{position:fixed;inset:0;z-index:60;display:flex;align-items:center;justify-content:center;padding:20px}
.sheet .back{position:absolute;inset:0;background:rgba(23,60,59,.47);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px)}
.sheet .box{position:relative;background:var(--paper);border-radius:var(--r12);width:100%;max-width:900px;
  max-height:90vh;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 20px 100px rgba(17,34,51,.22)}
.sh-head{display:flex;align-items:center;gap:12px;padding:18px 24px;border-bottom:1px solid var(--line);
  background:#fff;position:sticky;top:0;z-index:2}
.sh-head .eyebrow{margin-bottom:2px}
.sh-head h2{font-size:17px;font-weight:600;letter-spacing:-.4px}
.sh-head .x{margin-left:auto;width:32px;height:32px;border-radius:50%;border:1px solid var(--line);
  color:var(--muted);font-size:13px;display:grid;place-items:center}
.sh-body{overflow:auto;padding:16px 20px 18px}
.sh-foot{display:flex;gap:7px;flex-wrap:wrap;padding:13px 20px calc(14px + env(safe-area-inset-bottom));
  background:#fff;border-top:1px solid var(--line)}
.sh-foot .cta{flex:1 1 240px;text-align:center;background:var(--green);color:#fff;border-radius:var(--r6);
  padding:13px;font-size:12px;font-weight:500}
.sh-foot .ghost{border:1px solid var(--line3);background:#fff;border-radius:var(--r6);padding:13px 12px;
  font-size:11px;font-weight:500;color:var(--ink2)}
.cmp-scroll{overflow:auto;background:#fff;border:1px solid var(--line2);border-radius:10px;max-height:56vh}
table.cmp{border-collapse:separate;border-spacing:0;width:100%;min-width:560px;font-size:11.5px}
table.cmp th,table.cmp td{padding:11px 12px;border-bottom:1px solid #eef4f5;text-align:left;vertical-align:top}
table.cmp thead th{position:sticky;top:0;background:#fff;font-size:12px;font-weight:600;z-index:2}
table.cmp th.rowh{position:sticky;left:0;background:#fcfcf9;font-size:10px;font-weight:500;color:#7b8e82;
  min-width:96px;white-space:nowrap;z-index:1;border-right:1px solid #eef4f5}
table.cmp thead th:first-child{z-index:3}
table.cmp .big{font-size:15px;font-weight:600;color:var(--green);letter-spacing:-.4px}
table.cmp .mut{color:#879587;font-size:10px}
table.cmp .na{color:#a88546;font-size:10.5px}
.cmp-note{font-size:10px;color:var(--muted2);line-height:1.8;margin-top:12px}
.pkg{margin-top:12px;border:1px solid #e9dfc4;background:#fbf7eb;border-radius:10px;padding:13px 15px;
  font-size:11px;line-height:1.85;color:#5a4636}
.pkg b{color:#8a4a22}

.toast{position:fixed;left:50%;bottom:calc(84px + env(safe-area-inset-bottom));transform:translateX(-50%) translateY(8px);
  background:#214f48;color:#fff;font-size:11.5px;font-weight:500;padding:10px 16px;border-radius:20px;
  opacity:0;pointer-events:none;transition:.18s;z-index:70;white-space:nowrap;box-shadow:0 5px 30px rgba(17,34,51,.20)}
.toast.on{opacity:1;transform:translateX(-50%) translateY(0)}

.foot{border-top:1px solid var(--line);margin-top:30px;padding:18px 44px 22px;display:flex;
  justify-content:space-between;gap:14px;flex-wrap:wrap;font-size:9.5px;color:#98a49a;line-height:1.9}
body{padding-bottom:86px}

/* ---------- free-tier bits ---------- */
.badge.tier{background:#e6f1e8;color:#2d7a6e;font-weight:600}
.pbox .pcta{display:block;margin-top:10px;padding-top:9px;border-top:1px dashed #cfe3da;
  font-size:10.5px;font-weight:600;color:#17675e;line-height:1.6}
.pbox .pcta span{display:block;font-weight:400;color:#7a8d8a;font-size:9.5px;margin-top:3px}
.ctabar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;background:#f2f7f0;
  border:1px solid #dbe8d9;border-radius:var(--r12);padding:16px 18px;margin-top:22px}
.ctabar .txt{flex:1;min-width:210px}
.ctabar b{font-size:12.5px;font-weight:600;letter-spacing:-.2px}
.ctabar p{font-size:10.5px;color:#6e8777;line-height:1.75;margin-top:4px}
.ctabar .btns{display:flex;gap:7px;flex-wrap:wrap}
.ctabar .btn.form{background:var(--green);color:#fff}
.ctabar .btn.chat{background:#fff;border:1px solid #b6cbc6;color:#20584f}

/* ---------- responsive ---------- */
@media (max-width:1180px){
  .side{width:212px;padding:28px 15px 20px}
  .main{margin-left:212px;width:calc(100% - 212px)}
  main.wrap{padding:30px 26px 40px}
  .topbar{padding:0 26px}
  .tray .inner{padding:0 26px}
  .foot{padding:18px 26px 22px}
  .entry{grid-template-columns:minmax(0,1fr) 270px}
  .stats>div{padding:0 16px}
  .home-grid{grid-template-columns:1fr;gap:20px}
  .hero-copy{width:60%}
  .home-grid .cands{max-width:none}
}
@media (max-width:860px){
  .shell{display:block}
  .side{position:sticky;top:0;width:100%;height:auto;border-right:0;border-bottom:1px solid var(--line);
    padding:11px 15px 7px;flex-direction:row;flex-wrap:wrap;align-items:center;gap:6px;overflow:visible;z-index:40}
  .brand{flex:1 1 auto;gap:8px}
  .brand .bi{width:31px;height:31px;border-radius:9px}
  .brand b{font-size:18px;letter-spacing:-.6px}
  .brand small{font-size:6px;letter-spacing:1.3px;margin-top:2px}
  .space-label,.side-bottom{display:none}
  .side nav{flex-direction:row;width:100%;gap:3px;overflow-x:auto;padding:6px 0 4px;order:3;scrollbar-width:none}
  .side nav::-webkit-scrollbar{display:none}
  .side nav button{white-space:nowrap;font-size:11px;padding:9px 10px;gap:6px;width:auto}
  .side nav button svg{width:14px;height:14px}
  .side nav button .cnt{display:none}
  .main{margin-left:0;width:100%}
  .topbar{display:none}
  main.wrap{padding:20px 15px 30px}
  .intro{display:block;margin-bottom:18px}
  .intro .side-btn{margin-top:14px}
  h1{font-size:22px;letter-spacing:-.8px;margin:8px 0 7px}
  .lede{font-size:12px;line-height:1.8}
  .hero{min-height:318px}
  .hero-copy{width:84%;padding:22px 20px 18px}
  .hero h2{font-size:26px;letter-spacing:-1.2px;line-height:1.45}
  .hero p{font-size:10.5px;line-height:1.85}
  .ocean{width:66%;top:118px;right:-70px;opacity:.85;height:calc(100% - 118px)}
  .island{width:100px;height:70px;top:34%;left:26%;border-width:8px}
  .trees{font-size:30px}
  .r1{width:180px;height:125px}
  .r2{width:250px;height:175px}
  .r3{width:320px;height:230px}
  .map-label{display:block;left:20px;right:auto;bottom:14px;text-align:left;font-size:8px;letter-spacing:1.4px;color:#4f8375}
  .map-label span{font-size:7px;letter-spacing:1px;margin-top:4px}
  .art-cap{display:none}
  .stats{grid-template-columns:1fr 1fr;padding:16px 0;row-gap:18px}
  .stats>div{padding:0 16px}
  .stats>div:nth-child(2){border-right:0}
  .stats strong{font-size:18px;margin:6px 0 4px}
  .stats small{font-size:9px}
  .promo{padding:18px;gap:12px}
  .promo .btn{width:100%}
  .catalog{padding:16px 14px;border-radius:var(--r12)}
  .catalog h2{font-size:25px;letter-spacing:-1.2px}
  .catalog .sub{font-size:10.5px}
  .tools{gap:8px}
  .field,.field.f2{flex:1 1 100%;min-width:0}
  .entry{grid-template-columns:1fr;gap:12px;padding:20px 0}
  .entry.on{padding:18px 12px;margin:0 -12px}
  .entry h3{font-size:17px}
  .entry h3 small{display:block;margin:3px 0 0;font-size:10.5px}
  .pnow b{font-size:25px}
  .cmp-now{padding:12px}
  .tray .inner{padding:0 15px;gap:9px}
  .tray .go{padding:10px 13px;font-size:11px}
  .sheet{padding:0;align-items:flex-end}
  .sheet .box{max-height:94vh;border-radius:14px 14px 0 0;max-width:100%}
  .sh-head{padding:14px 16px}
  .sh-body{padding:12px 12px 14px}
  .sh-foot{padding:11px 12px calc(12px + env(safe-area-inset-bottom))}
  .bgrid{grid-template-columns:1fr}
  .total{gap:14px}
  .total .cell b{font-size:21px}
  .barrow{grid-template-columns:84px minmax(0,1fr) 78px;font-size:10px}
  .guide-item{padding:16px;gap:12px}
  .g-num{width:32px;height:32px;font-size:11px}
  .q-card{padding:16px}
  .q-hint,.opts{margin-left:0}
  .rcand{padding:13px}
  .rcand .rprice{font-size:16px}
  .info-card{padding:16px 18px}
  .foot{padding:16px 15px 20px;font-size:8.5px}
  body{padding-bottom:78px}
}
</style>
</head>
<body>

<div class="shell">
  <aside class="side">
    <button class="brand" data-view="home" aria-label="홈으로">
      <span class="bi">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M3 14c1.8-2 3-2 4.8 0s3 2 4.8 0 3-2 4.8 0 3 2 4.8 0" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/>
          <path d="M3 18.5c1.8-2 3-2 4.8 0s3 2 4.8 0 3-2 4.8 0 3 2 4.8 0" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" opacity=".5"/>
          <path d="M3 9.5c1.8-2 3-2 4.8 0s3 2 4.8 0 3-2 4.8 0 3 2 4.8 0" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" opacity=".28"/>
        </svg>
      </span>
      <span><b>나의 바다</b><small>MALDIVES FIELD NOTES</small></span>
    </button>

    <div class="space-label">이지스윔의 몰디브 노트</div>
    <nav id="nav">
      <button data-view="home" class="on">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1.6" stroke="currentColor" stroke-width="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.6" stroke="currentColor" stroke-width="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.6" stroke="currentColor" stroke-width="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.6" stroke="currentColor" stroke-width="1.5"/></svg>
        홈
      </button>
      <button data-view="list">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9 4 3 6.5v13L9 17l6 2.5 6-2.5v-13L15 6.5 9 4Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M9 4v13M15 6.5v13" stroke="currentColor" stroke-width="1.5"/></svg>
        리조트 찾기 <span class="cnt" id="navCount">98</span>
      </button>
      <button data-view="pick">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5"/><path d="m15.5 8.5-2 5-5 2 2-5 5-2Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>
        여행 기준
      </button>
      <button data-view="budget">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect x="4" y="3" width="16" height="18" rx="2.2" stroke="currentColor" stroke-width="1.5"/><path d="M8 7h8M8 11h2m4 0h2M8 15h2m4 0h2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        예산 계산기
      </button>
      <button data-view="guide">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H19v16H6.5A2.5 2.5 0 0 0 4 21.5v-16Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M8 8h7M8 12h5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        가이드
      </button>
    </nav>

    <div class="side-bottom">
      <svg class="sea" width="40" height="14" viewBox="0 0 40 14" fill="none" aria-hidden="true"><path d="M1 8c3-4 5-4 8 0s5 4 8 0 5-4 8 0 5 4 8 0 4-4 6 0" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>
      <strong>함께 고르고,<br>각자의 바다로.</strong>
      <p>98곳 공홈 예약엔진을<br>직접 조회해 정리했어요.</p>
      <div class="host">
        <span class="av">이</span>
        <span>이지스윔<small>데이터 2026-11-24 · USD</small></span>
      </div>
    </div>
  </aside>

  <div class="main">
    <header class="topbar">
      <span class="crumb">나의 바다 <span class="sep">›</span> <b id="crumbNow">홈</b></span>
      <span class="right"><span><span class="live"></span>이 브라우저에 저장되는 비교함</span><span class="avatar">이</span></span>
    </header>

    <main class="wrap">

      <!-- ============ HOME ============ -->
      <section class="view on" data-view="home">
        <div class="intro">
          <div>
            <div class="eyebrow">Our journey, our ocean</div>
            <h1>어떤 바다를 꿈꾸고 있나요?</h1>
            <p class="lede">영업 중인 몰디브 리조트 98곳을 각 공식 홈페이지 예약엔진에서 직접 조회해 정리했습니다. 바다 형태·이동수단·성향과 1박 예산대를 먼저 보고, 정확한 2·7월 실측가와 세금 포함 총액은 패키지에서 확인하세요.</p>
          </div>
          <button class="btn primary side-btn" data-view="list">98곳 전체 보기</button>
        </div>

        <section class="hero">
          <div class="hero-copy">
            <span class="pill">MALDIVES FIELD NOTES</span>
            <h2>몰디브에서 눈을 뜨면,<br>어떤 바다로 갈래요?</h2>
            <p>숙소 가까이에서 만나는 산호와 물고기, 하우스리프.<br>바다 취향부터 한 끼의 식사까지,<br>막연했던 몰디브를 나만의 여행으로 바꾸는 시간.</p>
            <button class="under" data-view="list">98곳 전체 살펴보기 <span>↗</span></button>
          </div>
          <div class="ocean" aria-hidden="true">
            <div class="ripple r1"></div><div class="ripple r2"></div><div class="ripple r3"></div>
            <div class="island"><div class="trees">✳</div></div>
            <div class="jetty"></div>
            <div class="map-label">YOUR OWN OCEAN<span>00° 41' N · 73° 10' E</span></div>
            <div class="art-cap">나의 바다를 그리는 상상 지도</div>
          </div>
        </section>

        <div class="promo">
          <div>
            <div class="eyebrow">이지의 몰디브 자료</div>
            <h2>정확한 2·7월 실측가가 필요하세요?</h2>
            <p>리조트별 공홈 실측가·세금 포함 총액 계산표·7월 할인율은 59,000원 패키지에서 확인하세요. 무료 페이지는 예산대까지 보여드려요.</p>
          </div>
          <div class="btns" style="display:flex;gap:7px;flex-wrap:wrap">
            <a class="btn primary" href="https://docs.google.com/forms/d/e/1FAIpQLSfBbRKPUfFeXjRlNFHVqY-H5gHcgKblJUALwyOMBn5VUtnkIw/viewform" target="_blank" rel="noopener">패키지 신청 (구글폼) ↗</a>
            <a class="btn ghost" href="https://app.notion.com/p/1-1-424ad1a95078812b999cc5a134099124" target="_blank" rel="noopener">1:1 맞춤 상담 받기 ↗</a>
          </div>
        </div>

        <div class="stats">
          <div><span>영업 중 전수 조사</span><strong id="stTotal">98곳</strong><small>2026-11-19~24 공홈 예약엔진 직접 조회</small></div>
          <div><span>예산대 공개</span><strong id="stPriced">84곳</strong><small>세금 포함 추정 1박 기준</small></div>
          <div><span>2월 성수기 1박</span><strong id="stWater">—</strong><small>예산 구간 범위</small></div>
          <div><span>비교함</span><strong>3곳</strong><small>최대 3곳 나란히 조건 비교</small></div>
        </div>

        <div class="home-grid">
          <div>
            <div class="sec-head"><h2>차근차근, 여행 설계</h2><button class="text-btn" data-view="guide">전체 가이드 ›</button></div>
            <div class="steps">
              <button data-view="pick"><span class="num">01</span><div><strong>내가 원하는 바다 찾기</strong><p>라군·반반·수중형과 꼭 지키고 싶은 조건 3가지를 적어요.</p></div><span class="chev">›</span></button>
              <button data-view="guide"><span class="num">02</span><div><strong>하우스리프 확인하기</strong><p>공식 지도 → 다이빙센터 안내 → 최근 영상 순서로 살펴봐요.</p></div><span class="chev">›</span></button>
              <button data-view="budget"><span class="num">03</span><div><strong>같은 조건으로 총액 비교</strong><p>세금·그린택스·이동까지 넣은 2인 4박 총액을 계산해요.</p></div><span class="chev">›</span></button>
            </div>
          </div>
          <div>
            <div class="sec-head"><h2>요즘 눈에 들어온 곳</h2><button class="text-btn" data-view="list">전체 보기 ›</button></div>
            <div class="cands" id="homeCands"></div>
          </div>
        </div>

        <div class="banner">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true" style="color:#658b74"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M8 8h8M8 11.5h5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          <div class="txt"><strong>오늘 발견한 것, 비교함에 담아 두세요</strong><p>마음에 드는 리조트를 최대 3곳까지 담으면 같은 조건으로 나란히 볼 수 있어요.</p></div>
          <button class="btn ghost" id="homeCompare">비교함 열기</button>
        </div>
      </section>

      <!-- ============ LIST ============ -->
      <section class="view" data-view="list">
        <div class="intro">
          <div>
            <div class="eyebrow">Maldives field notes</div>
            <h1>리조트 98곳, 취향과 예산대로</h1>
            <p class="lede">바다 형태·이동수단·성향·1박 예산대로 좁혀 보세요. 각 리조트의 특징과 장단점을 먼저 보고, 마음에 드는 곳을 담아 나란히 비교할 수 있어요.</p>
          </div>
          <button class="btn ghost side-btn" id="resetAll">전체 초기화</button>
        </div>

        <section class="catalog">
          <div class="eyebrow">Maldives field notes</div>
          <h2>나의 바다, 전체 비교표</h2>
          <p class="sub">성인 2인 · 객실 1실 기준으로 2027년 2월·7월 슬롯을 2026년 11월 24일에 조회한 기록입니다. 무료 페이지는 <b>1박 예산 구간</b>과 리조트 특징·장단점까지만 보여드리고, 리조트별 공홈 실측 금액과 세금 포함 총액은 59,000원 패키지에서 확인하실 수 있어요.</p>

          <div class="tools">
            <div class="field f2"><label for="q">이름 · 아톨 · 이동수단</label>
              <input id="q" type="search" placeholder="예: 마차푸시, 바아, 스피드보트" autocomplete="off"></div>
            <div class="field"><label for="ftransfer">이동수단</label><select id="ftransfer"></select></div>
            <div class="field"><label for="sort">정렬</label><select id="sort">
              <option value="tFeb">2월 예산대 낮은순</option>
              <option value="tJul">7월 예산대 낮은순</option>
              <option value="name">이름순</option>
            </select></div>
          </div>

          <div class="filters" id="f-type"></div>
          <div class="filters" id="f-tags"></div>
          <div class="filters" id="f-more"></div>
          <div class="af" id="af"></div>

          <div class="count-row">
            <span>조건에 맞는 <b id="cnt">98</b>곳</span>
            <button class="text-btn" id="freset">선택 초기화</button>
          </div>

          <div class="cmp-now" id="cmpNow" hidden></div>
          <div id="list"></div>

          <div class="ctabar">
            <div class="txt"><b>정확한 2·7월 공홈 실측가와 세금 포함 총액이 필요하세요?</b>
              <p>리조트별 비치·워터 1박 금액, 세금 포함 환산표, 7월 할인율은 59,000원 패키지에 담겨 있어요.</p></div>
            <div class="btns">
              <a class="btn form" href="https://docs.google.com/forms/d/e/1FAIpQLSfBbRKPUfFeXjRlNFHVqY-H5gHcgKblJUALwyOMBn5VUtnkIw/viewform" target="_blank" rel="noopener">패키지 신청 ↗</a>
              <a class="btn chat" href="https://app.notion.com/p/1-1-424ad1a95078812b999cc5a134099124" target="_blank" rel="noopener">1:1 맞춤 상담 ↗</a>
            </div>
          </div>
        </section>

        <section class="info-card">
          <h3>이 표가 만들어진 방법</h3>
          <p>몰디브에서 지금 영업 중인 리조트 98곳을 골라, 2026-11-19~11-24에 각 리조트 <b>공식 홈페이지의 예약엔진</b>을 직접 열어 같은 조건으로 조회했습니다.</p>
          <details>
            <summary>조회 조건과 공개 범위 자세히</summary>
            <ul>
              <li><b>조회 조건</b>: 2027-02-21~25(성수기) · 2027-07-18~22(비수기) 각 4박, 성인 2인 1실, USD.</li>
              <li><b>식사 플랜</b>: 하프보드(HB) 우선, HB를 팔지 않는 리조트는 실제 판매 플랜(올인클루시브·풀보드·조식) 기준. 카드의 플랜 표기를 확인하세요.</li>
              <li><b>예산 구간</b>: 1박 표시가에 봉사료·GST·그린택스를 더해 계산한 1박 금액을 구간으로만 표기합니다. 2월은 세금 포함 1박 기준, 7월은 비수기 기준이에요.</li>
              <li><b>비공개 항목</b>: 리조트별 정확한 비치·워터 1박 달러 금액, 세금 포함 환산액, 7월 할인율은 무료 페이지에 넣지 않았요. 59,000원 패키지에 별도 정리되어 있습니다.</li>
              <li><b>대체 기준월</b>: 2월이 막힌 일부 리조트는 1월 또는 3월 날짜로 조회했고, 카드에 표시했습니다.</li>
              <li>요금은 프로모션·환율·재고에 따라 매일 바뀝니다. 예약 전 공홈에서 다시 확인하세요.</li>
            </ul>
          </details>
        </section>
      </section>

      <!-- ============ PICK ============ -->
      <section class="view" data-view="pick">
        <div class="intro">
          <div>
            <div class="eyebrow">Find your ocean</div>
            <h1>여행 기준으로 후보 3곳</h1>
            <p class="lede">다섯 가지만 정하면 98곳 중에서 조건에 맞는 곳을 추려 드려요. 결과는 검토 출발점이고, 최종 조건은 공홈·예약 담당자에게 확인하세요.</p>
          </div>
          <button class="btn primary side-btn" id="pickRun">후보 추리기</button>
        </div>
        <div class="note-inline"><b>질문 5문항 뼈대</b> · 시기 · 1박 예산대 · 바다 형태 · 이동수단 · 꼭 챙길 조건으로 추립니다. 예산은 세금 포함 1박 기준 구간으로만 겁니다(정확한 금액 표시 없음).</div>
        <div id="pickBody"></div>
        <div class="result" id="pickResult" hidden></div>
      </section>

      <!-- ============ BUDGET ============ -->
      <section class="view" data-view="budget">
        <div class="intro">
          <div>
            <div class="eyebrow">2인 4박 예산</div>
            <h1>여행 예산</h1>
            <p class="lede">같은 조건으로 비교하고, 빠진 비용까지 차근차근 확인해요. 입력 금액은 모두 2인 전체 금액입니다.</p>
          </div>
        </div>

        <div class="bcard">
          <div class="bgrid">
            <div><label for="bParty">여행 구성</label><select id="bParty">
              <option value="2" selected>커플(2인)</option><option value="3">가족·3인 이상</option></select></div>
            <div><label for="bNights">숙박 수</label><select id="bNights">
              <option value="3">3박</option><option value="4" selected>4박 · 기본</option><option value="5">5박</option></select></div>
            <div><label for="bMonth">여행 시기(월)</label><select id="bMonth">
              <option selected>아직 미정</option><option>2월</option><option>7월</option><option>1월</option><option>3월</option><option>12월</option></select></div>
            <div><label for="bCur">표시 통화</label><select id="bCur">
              <option value="krw" selected>원</option><option value="usd">USD</option></select></div>
          </div>
        </div>

        <div class="bcard">
          <h2 style="font-size:15.5px;font-weight:600;letter-spacing:-.3px;margin-bottom:6px">2인 4박 총액 계산기</h2>
          <div class="bnote">세금·봉사료가 견적에 포함됐는지 먼저 확인하세요. 포함이면 세금 칸에 0을 적어요. 금액을 모르면 비워두세요. 환율 변환 없이 표시만 바뀝니다. 리조트별 정확한 공홈 실측가는 59,000원 패키지에서 확인한 뒤 입력할 수 있어요.</div>
          <div class="bgrid">
            <div><label for="bStay">숙박 총액 (2인 4박)</label><input id="bStay" type="number" inputmode="numeric" placeholder="확인한 견적 금액 입력 · 포함 또는 비용 없음은 0"></div>
            <div><label for="bTransfer">왕복 트랜스퍼 (2인)</label><input id="bTransfer" type="number" inputmode="numeric" placeholder="확인한 금액 입력 · 포함 또는 비용 없음은 0"></div>
            <div><label for="bTax">세금·그린택스 (2인)</label><input id="bTax" type="number" inputmode="numeric" placeholder="견적에 포함이면 0"></div>
            <div><label for="bFnb">추가 식음료 (2인)</label><input id="bFnb" type="number" inputmode="numeric" placeholder="추가 식사·음료 예상"></div>
            <div><label for="bAir">항공 · 선택 (2인)</label><input id="bAir" type="number" inputmode="numeric" placeholder="항공 포함일 때만 입력"></div>
            <div><label for="bEtc">기타 (2인)</label><input id="bEtc" type="number" inputmode="numeric" placeholder="보험·팁 등"></div>
            <div><label for="bRate">환율 (1 USD = 원)</label><input id="bRate" type="number" inputmode="numeric" value="1380"></div>
            <div><label for="bAirOn">항공 포함 여부</label><select id="bAirOn"><option value="0" selected>항공 미포함</option><option value="1">항공 포함</option></select></div>
          </div>

          <div class="total" style="margin-top:16px">
            <div class="cell"><span>2인 총액</span><b id="bTotal">0원</b></div>
            <div class="cell small"><span>1인당</span><b id="bPer">0원</b></div>
            <div class="cell small"><span>1박당 · 2인</span><b id="bNight">0원</b></div>
          </div>
          <p class="cmp-note" id="bState">빈칸이 남아 있어 최종 총액은 아직 미확정이에요.</p>
          <div class="bars" id="bBars"></div>
        </div>
      </section>

      <!-- ============ GUIDE ============ -->
      <section class="view" data-view="guide">
        <div class="intro">
          <div>
            <div class="eyebrow">차근차근</div>
            <h1>가이드</h1>
            <p class="lede">어디에서 무엇을 확인할지, 한 단계씩 따라가 보세요. 확인한 단계는 이 브라우저에 저장됩니다.</p>
          </div>
        </div>
        <div class="guide-head"><span style="font-size:11px;color:var(--faint)">진행률 <b id="gDone" style="color:var(--ink)">0</b> / 5</span><div class="progress"><i id="gBar"></i></div></div>
        <div id="guideList"></div>
      </section>

    </main>

    <footer class="foot">
      <span>이 페이지는 리조트·여행사와 무관한 개인 비교 자료입니다.<br>공홈 조회·정리 이지스윔(@easyswim__) · 데이터 기준 2026-11-24 · 통화 USD<br>무료 페이지는 1박 예산 구간까지만 공개합니다 · 정확한 금액은 59,000원 패키지</span>
      <span>요금은 프로모션·환율·재고에 따라 매일 바뀝니다.</span>
    </footer>
  </div>
</div>

<div class="tray">
  <div class="inner">
    <div class="txt"><b id="trayTitle">비교함 비어 있음</b><span class="names" id="trayNames">마음에 드는 리조트를 최대 3곳 담아 보세요</span></div>
    <button class="go off" id="trayGo">비교하기 <span class="n" id="trayN">0</span></button>
  </div>
</div>

<div class="sheet" id="sheet" hidden>
  <div class="back" data-close></div>
  <div class="box" role="dialog" aria-modal="true" aria-labelledby="shTitle">
    <div class="sh-head">
      <div><div class="eyebrow">Compare</div><h2 id="shTitle">비교함</h2></div>
      <button class="x" data-close aria-label="닫기">✕</button>
    </div>
    <div class="sh-body" id="shBody"></div>
    <div class="sh-foot" id="shFoot"></div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script id="data" type="application/json">__DATA__</script>
<script>
__APP_JS__
</script>
</body>
</html>
"""

app_js = open(os.path.join(HERE, "free_app.js"), encoding="utf-8").read()
html = HTML.replace("__DATA__", DATA_JSON).replace("__APP_JS__", app_js)

out_html = os.path.join(HERE, "index.html")
open(out_html, "w", encoding="utf-8").write(html)
out_data = os.path.join(HERE, "data.json")
open(out_data, "w", encoding="utf-8").write(json.dumps(rows, ensure_ascii=False, indent=1))
print("wrote", out_html, len(html), "chars /", len(rows), "rows ->", out_data)
