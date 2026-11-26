(function(){
  "use strict";
  var DATA = JSON.parse(document.getElementById('data').textContent);
  var FORM = "https://docs.google.com/forms/d/e/1FAIpQLSfBbRKPUfFeXjRlNFHVqY-H5gHcgKblJUALwyOMBn5VUtnkIw/viewform";
  var NOTION = "https://app.notion.com/p/1-1-424ad1a95078812b999cc5a134099124";

  var TIER = ["$500대", "$600~800대", "$900~1,200대", "$1,300~1,900대", "$2,000~2,900대", "$3,000+"];
  var TYPE_ORDER = ['라군형','반반형','수중형'];
  var TRANSFER_ORDER = ['스피드보트','수상비행기','국내선+보트'];
  var TAGS = ['가성비','에메랄드 라군','가족','아이동반','수중환경 최상','하이엔드','신상','모던','올인클루시브','허니문 감성','조용함','프라이빗','성인전용','수중 레스토랑'];
  var BUDGETS = [2, 3, 4, 5];
  var VIEW_NAME = {home:'홈', list:'리조트 찾기', pick:'여행 기준', budget:'예산 계산기', guide:'가이드'};

  var state = {view:'home', q:'', type:'전체', transfer:'전체', tags:[], manta:false, maxTier:null,
               sort:'tFeb', sel:[]};

  function $(s,r){ return (r||document).querySelector(s); }
  function esc(s){ return String(s==null?'':s).replace(/[&<>"']/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function num(n){ return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function shortName(n){ return n.split(' (')[0]; }
  function byId(id){ for (var i=0;i<DATA.length;i++) if (DATA[i].id===id) return DATA[i]; return null; }
  function band(r,k){ var t = r[k]; return (t==null) ? null : TIER[t]; }
  function slotLabel(k){ return k==='tFeb' ? '2월 성수기' : '7월 비수기'; }

  var REASONS = {
    blocked:{label:'공홈 접속 차단', msg:'공홈이 자동 접속을 막아 요금 확인이 어려웠어요. 예산대는 상담에서 안내드립니다.'},
    'no-engine':{label:'예약엔진 없음', msg:'공홈에 온라인 예약엔진이 없어(전화·이메일·문의 폼만) 요금 확인이 어려웠어요.'},
    closed:{label:'휴장·예약 미오픈', msg:'공홈이 휴장·개보수 상태이거나 2027년 예약을 아직 열지 않았어요.'},
    soldout:{label:'조회 기간 재고 없음', msg:'2027-02-21~25 조회 기간에 판매되는 객실이 없었어요. 다른 날짜는 상담에서 확인할 수 있어요.'},
    unknown:{label:'추가 확인 필요', msg:'공홈에서 요금을 확인하지 못했어요.'}
  };
  function reasonOf(r){ return REASONS[r.reason]||REASONS.unknown; }

  /* ---------- view switching ---------- */
  function go(v){
    if (!VIEW_NAME[v]) v = 'home';
    state.view = v;
    var views = document.querySelectorAll('.view');
    for (var i=0;i<views.length;i++) views[i].classList.toggle('on', views[i].getAttribute('data-view')===v);
    var btns = document.querySelectorAll('#nav button');
    for (var j=0;j<btns.length;j++) btns[j].classList.toggle('on', btns[j].getAttribute('data-view')===v);
    $('#crumbNow').textContent = VIEW_NAME[v];
    window.scrollTo({top:0,behavior:'smooth'});
    if (v==='list') renderList();
    if (v==='pick') renderPick();
    if (v==='budget') calcBudget();
    if (v==='guide') renderGuide();
    if (v==='home') renderHome();
  }

  /* ---------- filters ---------- */
  function hasManta(r){ return !!(r.big && r.big!=='—' && r.big.indexOf('불가')<0 && /만타|고래상어/.test(r.big)); }

  function matches(r){
    if (state.type!=='전체' && r.type!==state.type) return false;
    if (state.transfer!=='전체' && r.transferKind!==state.transfer) return false;
    for (var i=0;i<state.tags.length;i++) if (r.tags.indexOf(state.tags[i])<0) return false;
    if (state.manta && !hasManta(r)) return false;
    if (state.maxTier!=null){
      if (r.tFeb==null || r.tFeb>state.maxTier) return false;
    }
    var q = state.q.trim().toLowerCase();
    if (q){
      var hay = (r.name+' '+r.atoll+' '+r.transfer+' '+r.tags.join(' ')+' '+r.big+' '+(r.meal||'')+' '+r.type).toLowerCase();
      var parts = q.split(/\s+/);
      for (var p=0;p<parts.length;p++) if (hay.indexOf(parts[p])<0) return false;
    }
    return true;
  }
  function countBy(fn){ var n=0; for (var i=0;i<DATA.length;i++) if (fn(DATA[i])) n++; return n; }
  var BUDGET_LABEL = {2:'~$1,200대', 3:'~$1,900대', 4:'~$2,900대', 5:'$3,000+'};
  function budgetLabel(i){ return BUDGET_LABEL[i] || TIER[i]; }

  function chips(el, items, activeFn, onFn, label){
    var html = (label ? '<span class="lbl">'+esc(label)+'</span>' : '');
    html += items.map(function(it){
      var on = activeFn(it.v);
      return '<button class="chip'+(on?' on':'')+'" data-v="'+esc(it.v)+'" aria-pressed="'+on+'">'+
             esc(it.t)+(it.n!=null?' <small>'+it.n+'</small>':'')+'</button>';
    }).join('');
    el.innerHTML = html;
    el.onclick = function(e){
      var b=e.target.closest('.chip'); if(!b) return;
      onFn(b.getAttribute('data-v'));
    };
  }

  function renderFilters(){
    var trSel = $('#ftransfer');
    if (!trSel.getAttribute('data-built')){
      trSel.innerHTML = '<option value="전체">전체</option>'+TRANSFER_ORDER.map(function(t){
        return '<option value="'+t+'">'+t+'</option>'; }).join('');
      trSel.setAttribute('data-built','1');
    }
    trSel.value = state.transfer;

    chips($('#f-type'), [{v:'전체',t:'전체',n:DATA.length}].concat(TYPE_ORDER.map(function(t){
      return {v:t,t:t,n:countBy(function(r){return r.type===t;})};})),
      function(v){return state.type===v;}, function(v){ state.type=v; renderFilters(); renderList(); }, '바다 형태');

    chips($('#f-tags'), TAGS.map(function(t){
      return {v:t,t:t,n:countBy(function(r){return r.tags.indexOf(t)>=0;})};}),
      function(v){return state.tags.indexOf(v)>=0;}, function(v){
        var i=state.tags.indexOf(v); if(i>=0) state.tags.splice(i,1); else state.tags.push(v);
        renderFilters(); renderList();
      }, '성향');

    var more = [{v:'manta',t:'만타·고래상어',n:countBy(hasManta)}]
      .concat(BUDGETS.map(function(b){ return {v:'b'+b, t:'2월 '+budgetLabel(b), n:countBy(function(r){
        return r.tFeb!=null && r.tFeb<=b; })}; }));
    chips($('#f-more'), more, function(v){
      if (v==='manta') return state.manta;
      return state.maxTier===parseInt(v.slice(1),10);
    }, function(v){
      if (v==='manta') state.manta=!state.manta;
      else { var b=parseInt(v.slice(1),10); state.maxTier = (state.maxTier===b)?null:b; }
      renderFilters(); renderList();
    }, '대물투어 · 예산대(2월 · 세금 포함 1박)');

    var af=[];
    if (state.type!=='전체') af.push({k:'type',t:state.type});
    if (state.transfer!=='전체') af.push({k:'transfer',t:state.transfer});
    state.tags.forEach(function(t){ af.push({k:'tag:'+t,t:t}); });
    if (state.manta) af.push({k:'manta',t:'만타·고래상어'});
    if (state.maxTier!=null) af.push({k:'budget',t:'2월 '+budgetLabel(state.maxTier)});
    if (state.q.trim()) af.push({k:'q',t:'"'+state.q.trim()+'"'});
    var afEl = $('#af');
    afEl.innerHTML = af.map(function(a){
      return '<span class="item">'+esc(a.t)+'<button data-k="'+esc(a.k)+'" aria-label="필터 해제">✕</button></span>';
    }).join('');

    $('#navCount').textContent = DATA.length;
  }

  /* ---------- entry ---------- */
  function statusBadges(r){
    var out=[];
    if (r.reason) out.push('<span class="badge warn">'+esc(reasonOf(r).label)+'</span>');
    if (r.monthNote && r.monthNote.length) out.push('<span class="badge na">'+esc(r.monthNote.join(' · '))+'</span>');
    return out.join('');
  }

  function tierCell(r,k){
    var b = band(r,k);
    if (b!=null) return '<div><span>'+slotLabel(k)+'</span><b>'+esc(b)+'</b></div>';
    return '<div><span>'+slotLabel(k)+'</span><b class="na">—</b></div>';
  }

  function entry(r){
    var sel = state.sel.indexOf(r.id)>=0;
    var nm = r.name.match(/^(.*?)\s*\((.*)\)$/);
    var ko = nm ? nm[1] : r.name, en = nm ? nm[2] : '';

    var kicker = esc(r.type) + ' · ' + esc(r.atoll) + ' · ' + esc(r.transfer);

    var tagList = r.tags.filter(function(t){ return !(t==='성인전용' && r.adult); }).slice(0,4);
    var badges = tagList.map(function(t){return '<span class="badge">'+esc(t)+'</span>';}).join('');
    if (hasManta(r)) badges = '<span class="badge ok">만타 · '+esc(r.big.split('(')[0])+'</span>'+badges;
    if (r.adult) badges += '<span class="badge na">'+esc(r.adult)+'</span>';
    badges += statusBadges(r);

    var priceHtml;
    if (r.tFeb!=null || r.tJul!=null){
      priceHtml = '<div class="pbox">'+
        '<span class="plbl">1박 예산대 · 세금 포함 추정</span>'+
        '<div class="pgrid">'+tierCell(r,'tFeb')+tierCell(r,'tJul')+'</div>'+
        '<a class="pcta" href="'+NOTION+'" target="_blank" rel="noopener">찜한 리조트 정확한 요금 · 1:1 맞춤 받기 ↗'+
          '<span>세금 포함 총액·7월 할인율은 59,000원 패키지</span></a>'+
        '</div>';
    } else {
      priceHtml = '<div class="pbox">'+
        '<span class="plbl">1박 예산대</span>'+
        '<div class="pnow"><b style="font-size:15px;letter-spacing:-.3px">'+esc(reasonOf(r).label)+'</b></div>'+
        '<div class="pest">'+esc(reasonOf(r).msg)+'</div>'+
        '<a class="pcta" href="'+NOTION+'" target="_blank" rel="noopener">1:1 맞춤 상담에서 예산대 확인 ↗</a></div>';
    }

    var actsHtml = '<div class="acts">'+
      '<button class="cmp-btn'+(sel?' on':'')+'" data-cmp="'+r.id+'" aria-pressed="'+sel+'">'+(sel?'✓ 비교함에 담김':'+ 비교함 담기')+'</button>'+
      (r.url?'<a class="site" href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer nofollow">공홈 ↗</a>':'')+
      '</div>';

    var taxLine = r.taxIncluded ? '공홈 표시가에 세금·봉사료 포함'
      : (r.taxUnknown ? '공홈 화면에 세금 표기 없음(계산 시 세금 별도)' : '공홈 표시가 세금·봉사료 별도');
    var poolLine = r.pool==='all' ? '전 객실 풀빌라' : (r.pool==='some' ? '일부 전용 풀' : (r.pool==='none' ? '전용 풀 없음' : '—'));
    var memo = '<details class="memo"><summary>숙소 조건 · 조사 메모</summary><div class="body">'+
      '<div><b>식사</b> '+esc(r.meal||'공홈 표기 확인 필요')+'</div>'+
      '<div><b>세금 기준</b> '+esc(taxLine)+'</div>'+
      '<div><b>전용 풀</b> '+esc(poolLine)+'</div>'+
      '<div><b>대물투어</b> '+esc(r.big||'—')+'</div>'+
      '<div>'+(r.url?'<a href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer nofollow">'+esc(r.url.replace(/^https?:\/\//,''))+'</a>':'공홈 링크 없음')+'</div>'+
      '</div></details>';

    return '<article class="entry'+(sel?' on':'')+'" data-id="'+r.id+'">'+
      '<div class="e-main"><div class="kicker">'+kicker+'</div>'+
      '<h3>'+esc(ko)+(en?' <small>'+esc(en)+'</small>':'')+'</h3>'+
      '<div class="meta">'+esc(r.atoll)+' · '+esc(r.transfer)+'</div>'+
      '<div class="badges">'+badges+'</div>'+
      '<div class="why"><span class="pro">✔ '+esc((r.pros.length?r.pros:['상담에서 취향에 맞춰 정리']).join(' · '))+'</span>'+
      (r.cons.length?'<br><span class="con">! '+esc(r.cons.join(' · '))+'</span>':'')+'</div>'+
      memo+'</div>'+
      '<div class="e-side">'+priceHtml+actsHtml+'</div></article>';
  }

  var SORT_DESC = {tFeb:'2월 예산대 낮은순', tJul:'7월 예산대 낮은순', name:'이름순'};

  function renderList(){
    if (!document.querySelector('[data-view="list"].view')) return;
    var list = DATA.filter(matches);
    var sort = state.sort;
    list.sort(function(a,b){
      if (sort==='name') return a.name.localeCompare(b.name,'ko');
      var va = a[sort], vb = b[sort];
      if (va==null && vb==null) return a.name.localeCompare(b.name,'ko');
      if (va==null) return 1;
      if (vb==null) return -1;
      if (va!==vb) return va-vb;
      return a.name.localeCompare(b.name,'ko');
    });
    var html = list.map(entry).join('');
    if (!html) html = '<div class="empty"><b>조건에 맞는 리조트가 없어요</b><p>필터를 조금 풀거나 검색어를 지워 보세요.</p></div>';
    $('#list').innerHTML = '<div class="grp"><div class="grp-head"><h3>예산대 · 성향 순</h3><span>'+list.length+'곳</span>'+
      '<p>'+esc(SORT_DESC[sort]||'')+' · 표시된 예산대는 세금 포함 추정 1박 구간이에요. 정확한 금액은 패키지에서 확인하세요.</p></div>'+html+'</div>';
    $('#cnt').textContent = list.length;
    renderCmpNow();
    renderTray();
  }

  function renderCmpNow(){
    var box = $('#cmpNow'), names = state.sel.map(byId);
    if (!names.length){ box.hidden = true; box.innerHTML=''; return; }
    box.hidden = false;
    box.innerHTML = '<div class="names"><span style="font-size:10.5px;color:#5f8b7c;align-self:center">비교함 '+names.length+'곳</span>'+
      names.map(function(r){
        return '<span class="nm">'+esc(shortName(r.name))+'<button data-rm="'+r.id+'" aria-label="빼기">✕</button></span>';
      }).join('')+'</div>'+
      '<button class="btn primary" data-open="1">비교표 열기</button>';
  }

  /* ---------- home ---------- */
  function renderHome(){
    var withTier = DATA.filter(function(r){ return r.tFeb!=null; });
    $('#stTotal').textContent = DATA.length + '곳';
    $('#stPriced').textContent = withTier.length + '곳';
    if (withTier.length){
      var mn = 99, mx = -1;
      withTier.forEach(function(r){ if (r.tFeb<mn) mn=r.tFeb; if (r.tFeb>mx) mx=r.tFeb; });
      $('#stWater').textContent = TIER[mn]+' ~ '+TIER[mx].replace('$','$');
    }

    var used = [];
    function take(arr){
      for (var i=0;i<arr.length;i++){ if (used.indexOf(arr[i].id)<0){ used.push(arr[i].id); return arr[i]; } }
      return null;
    }
    var sortedBy = function(k){ return DATA.slice().sort(function(a,b){
      var x=a[k]==null?99:a[k], y=b[k]==null?99:b[k]; return x-y; }); };
    var c1 = take(sortedBy('tFeb').filter(function(r){ return r.tFeb!=null && r.tags.indexOf('가성비')>=0; }));
    if (!c1) c1 = take(sortedBy('tFeb').filter(function(r){ return r.tFeb!=null; }));
    var c2 = take(DATA.filter(function(r){ return r.tFeb!=null && r.tFeb<=3 && (r.tags.indexOf('허니문 감성')>=0 || r.adult); }));
    if (!c2) c2 = take(DATA.filter(function(r){ return r.tFeb!=null && r.tags.indexOf('프라이빗')>=0; }));
    var c3 = take(DATA.filter(function(r){ return r.tFeb!=null && (r.tags.indexOf('가족')>=0 || r.tags.indexOf('아이동반')>=0); }));
    if (!c3) c3 = take(DATA.filter(function(r){ return r.tFeb!=null; }));
    var cands = [c1,c2,c3].filter(function(x){ return !!x; });

    $('#homeCands').innerHTML = cands.map(function(r,i){
      var b = band(r,'tFeb');
      return '<button class="cand" data-cand="'+r.id+'">'+
        '<span class="thumb'+(i===1?' t2':(i===2?' t3':''))+'">'+
          '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3 14c1.8-2 3-2 4.8 0s3 2 4.8 0 3-2 4.8 0 3 2 4.8 0" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M3 18c1.8-2 3-2 4.8 0s3 2 4.8 0 3-2 4.8 0 3 2 4.8 0" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" opacity=".6"/></svg>'+
        '</span>'+
        '<span class="cand-body"><small>CANDIDATE 0'+(i+1)+'</small><strong>'+esc(shortName(r.name))+'</strong>'+
        '<em>2월 '+(b||'확인 전')+' · '+esc(r.type)+' · '+esc(r.transfer)+'</em></span>'+
        '<span class="chev">↗</span></button>';
    }).join('');
  }

  /* ---------- tray / compare ---------- */
  function saveSel(){ try { localStorage.setItem('maldivesSel', JSON.stringify(state.sel)); } catch(e){} }
  function loadSel(){
    try { var v=JSON.parse(localStorage.getItem('maldivesSel')||'[]');
      state.sel = v.filter(function(id){ return !!byId(id); }).slice(0,3); } catch(e){ state.sel=[]; }
  }
  function renderTray(){
    var n = state.sel.length;
    $('#trayN').textContent = n;
    $('#trayTitle').textContent = n ? ('비교함 '+n+'곳 선택됨') : '비교함 비어 있음';
    $('#trayNames').textContent = n
      ? state.sel.map(function(id){ return shortName(byId(id).name); }).join(' · ')
      : '마음에 드는 리조트를 최대 3곳 담아 보세요';
    $('#trayGo').classList.toggle('off', n<1);
  }
  function toast(msg){
    var t=$('#toast'); t.textContent=msg; t.classList.add('on');
    clearTimeout(toast._t); toast._t=setTimeout(function(){ t.classList.remove('on'); },1900);
  }
  function toggle(id){
    var i=state.sel.indexOf(id);
    if (i>=0) state.sel.splice(i,1);
    else if (state.sel.length>=3){ toast('비교는 최대 3곳까지 담을 수 있어요'); return; }
    else state.sel.push(id);
    saveSel(); renderList(); renderTray();
  }

  function tierCellCmp(r,k){
    var b = band(r,k);
    return b!=null ? '<span class="big">'+esc(b)+'</span>' : '<span class="na">—</span>';
  }

  function pkgHtml(){
    return '<div class="pkg"><b>59,000원 올인원 패키지</b> — 98곳 DB에서 고른 찜 3곳 + 맞춤 5곳(총 8곳)의 2·7월 기준가·희망 날짜 실측가, 세금 포함 총액 + 1:1 컨설팅(공홈·OTA 총액 비교, 여행사에 보낼 질문 1장). '+
      '<a href="'+FORM+'" target="_blank" rel="noopener">구글폼 신청 →</a> · <a href="'+NOTION+'" target="_blank" rel="noopener">1:1 맞춤 상담 →</a></div>';
  }

  function openSheet(){
    if (!state.sel.length){ toast('먼저 리조트를 담아 주세요'); return; }
    var rows = state.sel.map(byId);
    var head = '<tr><th class="rowh"></th>'+rows.map(function(r){
      return '<th>'+esc(shortName(r.name))+'<div class="mut" style="font-weight:500">'+esc(r.type)+' · '+esc(r.atoll)+'</div></th>';
    }).join('')+'</tr>';

    var defs = [
      ['2월 성수기<br>1박 예산대', function(r){ return tierCellCmp(r,'tFeb'); }],
      ['7월 비수기<br>1박 예산대', function(r){ return tierCellCmp(r,'tJul'); }],
      ['식사 플랜', function(r){ return esc(r.meal||'—'); }],
      ['세금 표기', function(r){
        return r.taxIncluded?'공홈 표시가 <b>세금 포함</b>':(r.taxUnknown?'표기 없음<br><span class="mut">계산 시 세금 별도</span>':'<b>세금·봉사료 별도</b>'); }],
      ['전용 풀', function(r){
        return r.pool==='all'?'전 객실 풀빌라':(r.pool==='some'?'일부 전용 풀':(r.pool==='none'?'<b>전용 풀 없음</b>':'—')); }],
      ['이동수단', function(r){ return esc(r.transfer); }],
      ['대물투어', function(r){ return esc(r.big||'—'); }],
      ['성향', function(r){ return esc(r.tags.slice(0,4).join(' · ')||'—'); }],
      ['공홈', function(r){ return r.url?'<a href="'+esc(r.url)+'" target="_blank" rel="noopener noreferrer nofollow">열기 ↗</a>':'—'; }],
      ['', function(r){ return '<button class="chip" data-rm="'+r.id+'">빼기</button>'; }]
    ];
    var body = '<div class="cmp-scroll"><table class="cmp"><thead>'+head+'</thead><tbody>'+
      defs.map(function(d){
        return '<tr><th class="rowh">'+d[0]+'</th>'+rows.map(function(r){ return '<td>'+d[1](r)+'</td>'; }).join('')+'</tr>';
      }).join('')+'</tbody></table></div>'+
      '<p class="cmp-note">예산대는 2027-02-21~25 · 07-18~22 각 4박, 성인 2인 1실 기준 공홈 조회값을 세금 포함 1박 구간으로 바꾼 것입니다. 찜한 3곳 + 맞춤 5곳(총 8곳)의 정확한 금액·세금 포함 총액은 59,000원 패키지에서 확인하세요.</p>'+
      '<div id="pkgBox" hidden>'+pkgHtml()+'</div>';

    $('#shTitle').textContent = '비교함 · '+rows.length+'곳';
    $('#shBody').innerHTML = body;
    $('#shFoot').innerHTML =
      '<a class="cta" href="'+NOTION+'" target="_blank" rel="noopener">선택한 '+rows.length+'곳으로 1:1 맞춤 상담 신청 →</a>'+
      '<button class="ghost" id="copyBtn">선택 요약 복사</button>'+
      '<button class="ghost" id="pkgBtn">59,000원 패키지</button>';
    $('#sheet').hidden = false;
    document.body.style.overflow='hidden';

    $('#shBody').onclick = function(e){
      var b = e.target.closest('[data-rm]');
      if (b){ var id=parseInt(b.getAttribute('data-rm'),10); toggle(id); if(state.sel.length) openSheet(); else closeSheet(); }
    };
    $('#copyBtn').onclick = function(){
      var lines = rows.map(function(r){
        return shortName(r.name)+' ('+r.type+', '+r.atoll+', '+r.transfer+') 2월 '+(band(r,'tFeb')||'확인 전')+
          ' / 7월 '+(band(r,'tJul')||'—');
      });
      var txt = '[몰디브 비교] '+lines.join(' | ')+' — 1박 예산대 기준(2026-11-24 공홈 조회 · 이지스윔)';
      if (navigator.clipboard && navigator.clipboard.writeText){
        navigator.clipboard.writeText(txt).then(function(){ toast('선택 요약을 복사했어요'); },
          function(){ toast('복사가 막혔어요 — 길게 눌러 복사해 주세요'); });
      } else { toast('복사가 막혔어요 — 길게 눌러 복사해 주세요'); }
    };
    $('#pkgBtn').onclick = function(){ var p=$('#pkgBox'); p.hidden=!p.hidden; };
  }
  function closeSheet(){ $('#sheet').hidden = true; document.body.style.overflow=''; }

  /* ---------- pick (질문형 5문항) ---------- */
  var PICK = {slot:'tFeb', budget:null, type:'전체', transfer:'전체', tags:[]};
  var QS = [
    {k:'slot', t:'언제 갈까요?', h:'요금을 조회해 둔 두 계절 중에서 골라 주세요. 같은 기간끼리 비교해야 공정해요.',
     opts:[{v:'tFeb',t:'2월 성수기'},{v:'tJul',t:'7월 비수기'}]},
    {k:'budget', t:'1박 예산은 어느 정도인가요?', h:'세금 포함 추정 1박 기준 예산대입니다. 고른 구간까지의 리조트를 보여드려요.',
     opts:[{v:'',t:'상관없음'},{v:'2',t:'~$1,200대'},{v:'3',t:'~$1,900대'},{v:'4',t:'~$2,900대'}]},
    {k:'type', t:'어떤 바다가 좋아요?', h:'라군은 얕고 맑은 바다, 반반형은 라군과 리프가 함께, 수중형은 리프 바로 위예요.',
     opts:[{v:'전체',t:'상관없음'},{v:'라군형',t:'라군형'},{v:'반반형',t:'반반형'},{v:'수중형',t:'수중형'}]},
    {k:'transfer', t:'이동은 어디까지 괜찮아요?', h:'수상비행기는 낮에만 뜨고, 국내선+보트는 한 번 더 갈아타요.',
     opts:[{v:'전체',t:'상관없음'},{v:'스피드보트',t:'스피드보트'},{v:'수상비행기',t:'수상비행기'},{v:'국내선+보트',t:'국내선+보트'}]},
    {k:'tags', t:'꼭 챙기고 싶은 것', h:'여러 개 고를 수 있어요. 고른 조건은 모두 만족하는 곳만 남깁니다.',
     multi:true, opts:[{v:'manta',t:'만타·고래상어'},{v:'가족',t:'가족'},{v:'아이동반',t:'아이동반'},{v:'올인클루시브',t:'올인클루시브'},{v:'프라이빗',t:'프라이빗'},{v:'가성비',t:'가성비'},{v:'신상',t:'신상'},{v:'모던',t:'모던'}]}
  ];

  function renderPick(){
    var body = '';
    QS.forEach(function(q,i){
      body += '<div class="q-card"><div class="q-top"><span class="q-num">0'+(i+1)+'</span><h2>'+esc(q.t)+'</h2></div>'+
        '<p class="q-hint">'+esc(q.h)+'</p><div class="opts">'+
        q.opts.map(function(o){
          var on = q.multi ? PICK.tags.indexOf(o.v)>=0 : String(PICK[q.k]==null?'':PICK[q.k])===String(o.v);
          return '<button class="chip'+(on?' on':'')+'" data-q="'+q.k+'" data-v="'+esc(o.v)+'" aria-pressed="'+on+'">'+esc(o.t||o.v)+'</button>';
        }).join('')+'</div></div>';
    });
    $('#pickBody').innerHTML = body;
  }

  function pickMatches(){
    var slot = PICK.slot;
    var out = DATA.filter(function(r){
      if (r[slot]==null) return false;
      if (PICK.type!=='전체' && r.type!==PICK.type) return false;
      if (PICK.transfer!=='전체' && r.transferKind!==PICK.transfer) return false;
      for (var i=0;i<PICK.tags.length;i++){
        var t = PICK.tags[i];
        if (t==='manta'){ if (!hasManta(r)) return false; }
        else if (r.tags.indexOf(t)<0) return false;
      }
      return true;
    });
    if (PICK.budget!=null){
      var strict = out.filter(function(r){ return r[slot]<=PICK.budget; });
      var soft = out.filter(function(r){ return r[slot]<=PICK.budget+1; });
      out = strict.length ? strict : soft;
    }
    out.sort(function(a,b){ return (a[slot]-b[slot]) || a.name.localeCompare(b.name,'ko'); });
    var relaxed = PICK.budget!=null && !out.some(function(r){ return r[slot]<=PICK.budget; });
    return {list:out.slice(0,3), relaxed:relaxed, total:out.length};
  }

  function runPick(){
    var res = pickMatches(), slot = PICK.slot;
    var wrap = $('#pickResult');
    wrap.hidden = false;
    var head = '<div class="sec-head"><h2>'+esc(slotLabel(slot))+' 기준 후보 '+res.list.length+'곳</h2>'+
      '<button class="text-btn" id="pickAddAll">3곳 모두 비교함 담기 ›</button></div>'+
      '<p class="rs">'+(PICK.budget!=null?('예산 '+budgetLabel(PICK.budget)+' · '):'')+esc(PICK.type==='전체'?'바다 형태 무관':PICK.type)+' · '+
      esc(PICK.transfer==='전체'?'이동수단 무관':PICK.transfer)+' · 예산대 낮은 순'+
      (res.relaxed?' · 예산 안에 드는 곳이 없어 한 구간까지 넓혔어요':'')+'</p>';
    if (!res.list.length){
      wrap.innerHTML = head + '<div class="empty"><b>조건에 맞는 곳이 없어요</b><p>조건을 하나씩 풀어 보세요. 성향은 한두 개부터.</p></div>';
      return;
    }
    wrap.innerHTML = head + res.list.map(function(r){
      var matched = PICK.tags.filter(function(t){
        return t==='manta' ? hasManta(r) : r.tags.indexOf(t)>=0;
      });
      var why = [r.type, r.atoll, r.transfer].join(' · ');
      if (matched.length) why += ' · ' + matched.map(function(t){ return t==='manta'?'만타·고래상어':t; }).join('·');
      return '<div class="rcand"><div class="rbody"><strong>'+esc(shortName(r.name))+'</strong><small>'+esc(why)+'</small></div>'+
        '<div class="rprice">'+esc(band(r,slot)||'확인 전')+'<small>1박 예산대</small></div>'+
        '<button class="chip" data-cmp="'+r.id+'">'+ (state.sel.indexOf(r.id)>=0?'✓ 담김':'+ 담기') +'</button></div>';
    }).join('')+
    '<p class="rs" style="margin:12px 0 0">조건에 맞는 곳은 모두 '+res.total+'곳이에요. 후보 3곳은 예산대가 낮은 순으로 골랐습니다. 정확한 금액은 <a href="'+NOTION+'" target="_blank" rel="noopener">59,000원 패키지 상세</a>에서 확인하세요.</p>';
    var addAll = $('#pickAddAll');
    if (addAll) addAll.onclick = function(){
      res.list.forEach(function(r){ if (state.sel.indexOf(r.id)<0 && state.sel.length<3) state.sel.push(r.id); });
      saveSel(); renderTray(); renderList(); toast('후보를 비교함에 담았어요'); openSheet();
    };
  }

  /* ---------- budget ---------- */
  function wonk(n, cur){ return cur==='usd' ? '$'+num(n) : num(n)+'원'; }
  function calcBudget(){
    var cur = $('#bCur').value, rate = parseFloat($('#bRate').value||'1380')||1380;
    var conv = function(v){ return cur==='usd' ? v/rate : v; };
    var vals = [
      ['숙박', parseFloat($('#bStay').value||'0')||0],
      ['왕복 트랜스퍼', parseFloat($('#bTransfer').value||'0')||0],
      ['세금·그린택스', parseFloat($('#bTax').value||'0')||0],
      ['추가 식음료', parseFloat($('#bFnb').value||'0')||0],
      ['항공', parseFloat($('#bAir').value||'0')||0],
      ['기타', parseFloat($('#bEtc').value||'0')||0]
    ];
    var airOn = $('#bAirOn').value==='1';
    var sum = 0;
    vals.forEach(function(v,i){ if (i===4 && !airOn) return; sum += v[1]; });
    var nights = parseFloat($('#bNights').value||'4');
    var party = parseFloat($('#bParty').value||'2');
    $('#bTotal').textContent = wonk(conv(sum), cur);
    $('#bPer').textContent = wonk(conv(sum/party), cur);
    $('#bNight').textContent = wonk(conv(sum/nights), cur);
    $('#bState').textContent = sum>0
      ? (party!==2||nights!==4 ? '인원·숙박 수를 바꾸면 나눗셈 기준이 바뀌어요. 입력값은 자동 환산되지 않으니 새 조건의 전체 금액으로 고쳐 주세요.' : '입력한 금액은 2인 전체 기준이에요. 세금·트랜스퍼 포함 여부를 꼭 확인하세요.')
      : '빈칸이 남아 있어 최종 총액은 아직 미확정이에요.';
    $('#bBars').innerHTML = vals.filter(function(v,i){ return !(i===4 && !airOn); }).map(function(v){
      var pct = sum>0 ? Math.round(v[1]/sum*1000)/10 : 0;
      return '<div class="barrow"><span>'+v[0]+'</span><div class="track"><i style="width:'+pct+'%"></i></div><b>'+pct.toFixed(1)+'%</b></div>';
    }).join('');
  }

  /* ---------- guide ---------- */
  var GUIDE = [
    {t:'내가 원하는 바다 찾기', p:'라군·반반·수중형 중 무엇이 우선인지, 개인풀·올인클루시브 같은 조건 3가지를 적어 두세요.',
     d:'<b>여행 기준</b> 탭에서 다섯 질문에 답하면 조건에 맞는 후보 3곳을 추려 드려요. 기준이 흐리면 후보가 30곳 넘게 남습니다.'},
    {t:'하우스리프 확인하기', p:'공식 리조트 지도 → 다이빙센터 안내 → 최근 영상 순서로 살펴봐요.',
     d:'입수·출수 지점, 리프까지 거리, 조류, 가이드 동행 조건을 기록하세요. 후기 작성일과 방문 시기를 구분하고 생물 출현은 보장으로 해석하지 마세요.'},
    {t:'이동 동선 비교하기', p:'항공 도착 시각과 리조트 트랜스퍼 막차를 함께 확인해요.',
     d:'말레 도착 시각, 마지막 연결편, 대기 시간, 수하물 제한, 왕복 요금을 리조트에 확인하세요. 수상비행기는 낮에만 운항해 늦은 오후 도착은 말레 숙박이 필요할 수 있어요.'},
    {t:'같은 조건으로 가격 비교하기', p:'같은 날짜·인원·객실·밀플랜으로 공홈과 OTA를 비교해요.',
     d:'결제 직전 총액에서 세금·그린택스·트랜스퍼 포함 여부와 취소 마감의 현지 시간을 확인하세요. 이 사이트는 <b>세금 포함 1박 예산대</b>까지만 보여주고, 리조트별 정확한 금액은 59,000원 패키지에서 확인할 수 있어요.'},
    {t:'함께 검토하고 예약하기', p:'비교함에 3곳을 담아 조건을 나란히 보고, 최종 견적은 리조트·여행사에 직접 확인해요.', d:'요금은 프로모션·환율·재고에 따라 매일 바뀝니다. 예약 전 공홈에서 다시 확인하고, 확인일과 링크를 남겨 두세요.'}
  ];
  function guideState(){
    try { return JSON.parse(localStorage.getItem('maldivesGuide')||'[]'); } catch(e){ return []; }
  }
  function renderGuide(){
    var done = guideState();
    $('#guideList').innerHTML = GUIDE.map(function(g,i){
      var on = done.indexOf(i)>=0;
      return '<div class="guide-item'+(on?' done':'')+'" data-step="'+i+'">'+
        '<span class="g-num">0'+(i+1)+'</span>'+
        '<div><h2>'+esc(g.t)+'</h2><p>'+esc(g.p)+'</p><div class="g-detail">'+g.d+'</div>'+
        '<button class="g-btn" data-g="'+i+'">'+(on?'✓ 확인 완료':'확인 완료로 표시')+'</button></div></div>';
    }).join('');
    $('#gDone').textContent = done.length;
    $('#gBar').style.width = (done.length/GUIDE.length*100)+'%';
  }

  /* ---------- events ---------- */
  document.addEventListener('click', function(e){
    var dv = e.target.closest('button[data-view]');
    if (dv){ go(dv.getAttribute('data-view')); return; }

    var c = e.target.closest('[data-cmp]');
    if (c){ toggle(parseInt(c.getAttribute('data-cmp'),10)); if (state.view==='pick'){ renderPick(); runPick(); } return; }

    var cand = e.target.closest('[data-cand]');
    if (cand){
      var r = byId(parseInt(cand.getAttribute('data-cand'),10));
      if (r){ state.q = shortName(r.name); $('#q').value = state.q; go('list'); renderFilters(); renderList(); }
      return;
    }

    var rm = e.target.closest('[data-rm]');
    if (rm){ toggle(parseInt(rm.getAttribute('data-rm'),10)); if (state.sel.length) openSheet(); else closeSheet(); return; }

    if (e.target.closest('[data-open]')){ openSheet(); return; }
    if (e.target.closest('[data-close]')){ closeSheet(); return; }

    var afb = e.target.closest('#af [data-k]');
    if (afb){
      var k = afb.getAttribute('data-k');
      if (k==='type') state.type='전체';
      else if (k==='transfer') state.transfer='전체';
      else if (k==='manta') state.manta=false;
      else if (k==='budget') state.maxTier=null;
      else if (k==='q'){ state.q=''; $('#q').value=''; }
      else if (k.indexOf('tag:')===0){ var t=k.slice(4); var i=state.tags.indexOf(t); if(i>=0) state.tags.splice(i,1); }
      renderFilters(); renderList(); return;
    }

    var qb = e.target.closest('[data-q]');
    if (qb){
      var qk = qb.getAttribute('data-q'), qv = qb.getAttribute('data-v');
      if (qk==='tags'){
        var idx = PICK.tags.indexOf(qv);
        if (idx>=0) PICK.tags.splice(idx,1); else PICK.tags.push(qv);
      } else if (qk==='budget'){ PICK.budget = qv==='' ? null : parseInt(qv,10); }
      else PICK[qk] = qv;
      renderPick(); runPick(); return;
    }

    var gb = e.target.closest('[data-g]');
    if (gb){
      var gi = parseInt(gb.getAttribute('data-g'),10), gd = guideState(), p = gd.indexOf(gi);
      if (p>=0) gd.splice(p,1); else gd.push(gi);
      try { localStorage.setItem('maldivesGuide', JSON.stringify(gd)); } catch(err){}
      renderGuide(); return;
    }
  });

  $('#q').addEventListener('input', function(e){ state.q=e.target.value; renderFilters(); renderList(); });
  $('#sort').addEventListener('change', function(e){ state.sort=e.target.value; renderList(); });
  $('#ftransfer').addEventListener('change', function(e){ state.transfer=e.target.value; renderFilters(); renderList(); });
  $('#resetAll').addEventListener('click', function(){
    state.q=''; $('#q').value=''; state.type='전체'; state.transfer='전체'; state.tags=[]; state.manta=false; state.maxTier=null;
    state.sort='tFeb'; $('#sort').value='tFeb';
    renderFilters(); renderList();
  });
  $('#freset').addEventListener('click', function(){
    state.q=''; $('#q').value=''; state.type='전체'; state.transfer='전체'; state.tags=[]; state.manta=false; state.maxTier=null;
    renderFilters(); renderList();
  });
  $('#trayGo').addEventListener('click', openSheet);
  $('#homeCompare').addEventListener('click', openSheet);
  $('#pickRun').addEventListener('click', runPick);
  ['bStay','bTransfer','bTax','bFnb','bAir','bEtc','bRate','bCur','bAirOn','bNights','bParty'].forEach(function(id){
    var el = $('#'+id); if (el) el.addEventListener('input', calcBudget);
    if (el) el.addEventListener('change', calcBudget);
  });
  document.addEventListener('keydown', function(e){ if (e.key==='Escape') closeSheet(); });

  loadSel();
  renderFilters();
  renderList();
  renderHome();
  renderTray();
  renderPick();
  calcBudget();
  renderGuide();
})();
