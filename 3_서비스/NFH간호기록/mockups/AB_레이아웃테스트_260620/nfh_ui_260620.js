// nfh_ui_260620.js — 단계형 A / 한화면 B 공유 렌더 엔진
// 같은 데이터(nfh_core)·같은 컴포넌트를 양 버전이 '배치만 다르게' 사용.
// 사정 문항 판별·환자설명↔P&E 연동·NRS·낙상 로직은 간호기록노트.html(작동본)에서 이식.
(function(global){
"use strict";
const N = global.NFH;
const esc = N.esc, getQ = N.getQ, isSlash = N.isSlash, isInput = N.isInput, getSlashParts = N.getSlashParts;

// 상태: selected=[{id,label,keys,collected}], items=[{uid,text,section,symLabel}]
const S = { selected:[], items:[], nrs:{} };
let _onChange = ()=>{};
function fire(){ _onChange(); }
function setItem(uid, obj){ S.items = S.items.filter(c=>c.uid!==uid); if(obj) S.items.push({uid, ...obj}); }

// ── 양성(있음·이상) 색 판별 — UI 강조 전용(진술문 불변) ──
function posOf(t){
  t = (t||'').trim();
  if(/없음$|없음\b/.test(t)) return false;
  if(/(있음|못봄|상승|증가|감소함|저하|떨어|하강|약함|이상|양성|관찰됨|증가함)/.test(t)) return true;
  if(/봄$/.test(t)) return false;
  if(/정상|명료|가능함/.test(t)) return false;
  return null; // 중립
}

// ── 주호소 추가/제거 ──
function addComplaint(label, keys){
  if(S.selected.find(e=>e.label===label)) return null;
  const collected = N.collect(keys);
  const entry = { id:N.nuid(), label, keys, collected };
  S.selected.push(entry);
  return entry;
}
function removeComplaint(id){
  const e = S.selected.find(x=>x.id===id); if(!e) return;
  S.selected = S.selected.filter(x=>x.id!==id);
  S.items = S.items.filter(c=>c.symLabel!==e.label);
}
function reset(){ S.selected=[]; S.items=[]; S.nrs={}; }

// ── 진단(자동·잠금) : 선택 주호소들의 D + 낙상위험(낙상 진행시) ──
function derivedDx(){
  const out=[]; const seen=new Set();
  S.selected.forEach(e => e.collected.dxItems.forEach(d=>{
    if(d.text && !seen.has(d.text)){ seen.add(d.text); out.push({text:d.text, label:e.label}); }
  }));
  if(S.items.find(c=>c.symLabel==='의식/낙상')) { if(!seen.has('낙상위험')) out.push({text:'낙상위험', label:'의식/낙상'}); }
  return out;
}

// ============================================================
// 사정 섹션 (A&E + NRS + 환자설명 + P&E) — 한 주호소 블록
// ============================================================
function assessHTML(entry){
  const c = entry.collected, sid = entry.id;
  let h = `<div class="sec sec-ae" data-entry="${sid}">
    <div class="sec-h">🔵 사정 【A&amp;E】 — ${esc(entry.label)}</div>`;

  // A&E 문항
  c.aeItems.forEach(item=>{
    const q = getQ(item.text);
    const note = item.note ? `<div class="note-tag">📌 ${esc(item.note)}</div>` : '';
    if(isSlash(item.text)){
      const parts = getSlashParts(item.text);
      const cur = (S.items.find(x=>x.uid===item.uid)||{}).text;
      h += `<div class="q" data-ae="${item.uid}" data-slash="${item.uid}">
        <div class="q-prompt">💬 ${esc(q)}</div>
        <div class="opts">${parts.map(p=>{
          const on = cur===p; const pos = posOf(p);
          const cls = on ? (pos? 'sel-pos':'sel-neg') : '';
          return `<div class="opt ${cls}" data-st="${esc(p)}">${esc(p)}</div>`;
        }).join('')}</div>${note}</div>`;
    } else if(isInput(item.text)){
      const cur = (S.items.find(x=>x.uid===item.uid)||{}).text || '';
      const val = cur.startsWith(item.text) ? cur.slice(item.text.length).trim() : '';
      h += `<div class="q" data-ae="${item.uid}">
        <div class="q-prompt">💬 ${esc(q)}</div>
        <div class="note-tag" style="margin-top:0;margin-bottom:4px;">${esc(item.text)}</div>
        <input class="txt-input" data-inp="${item.uid}" data-ib="${esc(item.text)}" placeholder="직접 입력" value="${esc(val)}">
        ${note}</div>`;
    } else {
      const on = !!S.items.find(x=>x.uid===item.uid);
      h += `<div class="chk-item ${on?'on':''}" data-ae="${item.uid}" data-chk="${item.uid}" data-ct="${esc(item.text)}">
        <div class="chk-box">${on?'✓':''}</div>
        <div style="flex:1"><div class="q-prompt" style="margin-bottom:4px">💬 ${esc(q)}</div>
        <div class="chk-text">${esc(item.text)}</div>${note}</div></div>`;
    }
  });

  // NRS (급성통증 시)
  if(c.hasPain){
    const k = sid;
    const g = (sub)=> (S.nrs[k]&&S.nrs[k][sub]);
    const row=(sub,arr,pre)=>`<div class="nrs-lab">${pre}</div><div class="chips">${arr.map(p=>`<div class="chip ${g(sub)===p?'on':''}" data-nrs="${sub}" data-nv="${esc(p)}">${esc(p)}</div>`).join('')}</div>`;
    h += `<div class="nrs-wrap" data-nrsentry="${k}">
      <div class="q-prompt">📌 통증 평가 (NRS · 비고란)</div>
      <div class="nrs-lab">"얼마나 아프세요? (0=안아픔 / 10=최고)"</div>
      <div class="nrsnum">${[0,1,2,3,4,5,6,7,8,9,10].map(n=>`<div class="chip ${g('score')===String(n)?'on':''}" data-nrs="score" data-nv="${n}">${n}</div>`).join('')}</div>
      ${row('part',['상복부','하복부','우하복부','좌하복부','흉부','머리','전신','기타'],'부위')}
      ${row('patt',['쥐어짜듯','찌르듯','둔하게','타는듯','콕콕'],'양상')}
      ${row('onset',['방금 전','몇 시간 전','어제','며칠 전'],'발병')}
      ${row('dur',['지속적으로','간헐적으로','지금은 없음'],'지속')}
    </div>`;
  }

  // 환자설명 (말하며 체크) → P&E 자동 연동
  if(c.eduScripts.length){
    h += `<div class="sec-h" style="margin-top:6px;background:rgba(255,200,87,.12);color:var(--pe)">📢 환자 설명 — 말하며 체크</div>`;
    c.eduScripts.forEach(s=>{
      const on = !!S.items.find(x=>x.text===s.pe && x.symLabel===entry.label);
      h += `<div class="iv ${on?'on':''}" data-edu="${esc(s.pe)}">
        <div class="script"><span class="spk">📢</span> ${esc(s.say)}</div>
        <div class="rec"><span class="ck">${on?'✓':''}</span> 기록: ${esc(s.pe)}</div></div>`;
    });
  }

  // P&E
  if(c.peItems.length){
    h += `<div class="sec-h" style="margin-top:6px;background:rgba(255,200,87,.12);color:var(--pe)">🟡 계획·중재 【P&amp;E】</div>`;
    c.peItems.forEach(item=>{
      const on = !!S.items.find(x=>x.uid===item.uid);
      const note = item.note ? `<div class="note-tag" style="margin-top:2px">📌 ${esc(item.note)}</div>`:'';
      h += `<div class="chk-item ${on?'on':''}" data-pe="${item.uid}" data-pt="${esc(item.text)}" data-lbl="${esc(entry.label)}">
        <div class="chk-box">${on?'✓':''}</div>
        <div style="flex:1"><div class="chk-text">${esc(item.text)}</div>${note}</div></div>`;
    });
  }

  h += `<button class="allnorm" data-allnorm="${sid}">✓ 이 증상 나머지 다 "없음/정상"으로 (빠른 모드)</button>`;
  h += `</div>`;
  return h;
}

// 사정 섹션 이벤트 바인딩 (root 안의 [data-entry=sid])
function bindAssess(root, entry){
  const sid = entry.id, label = entry.label;
  const scope = root.querySelector(`[data-entry="${sid}"]`); if(!scope) return;

  scope.querySelectorAll('[data-slash]').forEach(q=>{
    q.addEventListener('click', e=>{
      const b = e.target.closest('[data-st]'); if(!b) return;
      q.querySelectorAll('[data-st]').forEach(x=>x.classList.remove('sel-pos','sel-neg'));
      b.classList.add(posOf(b.dataset.st)?'sel-pos':'sel-neg');
      setItem(q.dataset.slash, {text:b.dataset.st, section:'A&E', symLabel:label}); fire();
    });
  });
  scope.querySelectorAll('[data-chk]').forEach(row=>{
    row.addEventListener('click', ()=>{
      const id=row.dataset.chk, on=!row.classList.contains('on');
      row.classList.toggle('on',on); row.querySelector('.chk-box').textContent=on?'✓':'';
      setItem(id, on?{text:row.dataset.ct, section:'A&E', symLabel:label}:null); fire();
    });
  });
  scope.querySelectorAll('[data-inp]').forEach(inp=>{
    inp.addEventListener('blur', ()=>{
      const v=inp.value.trim();
      setItem(inp.dataset.inp, v?{text:inp.dataset.ib+' '+v, section:'A&E', symLabel:label}:null); fire();
    });
  });
  // NRS
  scope.querySelectorAll('[data-nrs]').forEach(chip=>{
    chip.addEventListener('click', ()=>{
      const sub=chip.dataset.nrs, val=chip.dataset.nv, k=sid;
      S.nrs[k]=S.nrs[k]||{};
      const same = S.nrs[k][sub]===val;
      // 같은 그룹 해제
      scope.querySelectorAll(`[data-nrs="${sub}"]`).forEach(x=>x.classList.remove('on'));
      const uid='NRS:'+k+':'+sub;
      if(same){ S.nrs[k][sub]=null; setItem(uid,null); }
      else { S.nrs[k][sub]=val; chip.classList.add('on');
        const map={score:'통증강도 '+val+'점',part:'통증부위 '+val,patt:'통증양상 '+val,onset:'통증기간 '+val+'부터',dur:'통증지속 '+val};
        setItem(uid,{text:map[sub], section:'비고', symLabel:label});
      }
      fire();
    });
  });
  // 환자설명 ↔ P&E 양방향
  scope.querySelectorAll('[data-edu]').forEach(card=>{
    card.addEventListener('click', ()=>{
      const pe=card.dataset.edu, on=!card.classList.contains('on');
      card.classList.toggle('on',on); card.querySelector('.ck').textContent=on?'✓':'';
      const peRow=[...scope.querySelectorAll('[data-pe]')].find(r=>r.dataset.pt===pe);
      if(peRow){ setPe(peRow,on); }
      else { setItem('edu_'+sid+'_'+pe, on?{text:pe, section:'계획', symLabel:label}:null); }
      fire();
    });
  });
  scope.querySelectorAll('[data-pe]').forEach(row=>{
    row.addEventListener('click', ()=>{ setPe(row, !row.classList.contains('on'));
      const eduCard=[...scope.querySelectorAll('[data-edu]')].find(c=>c.dataset.edu===row.dataset.pt);
      if(eduCard){ eduCard.classList.toggle('on', row.classList.contains('on')); eduCard.querySelector('.ck').textContent=row.classList.contains('on')?'✓':''; }
      fire();
    });
  });
  function setPe(row,on){
    row.classList.toggle('on',on); row.querySelector('.chk-box').textContent=on?'✓':'';
    setItem(row.dataset.pe, on?{text:row.dataset.pt, section:'계획', symLabel:row.dataset.lbl}:null);
  }
  // 빠른 모드
  const an = scope.querySelector('[data-allnorm]');
  if(an) an.addEventListener('click', ()=>{
    entry.collected.aeItems.forEach(item=>{
      if(S.items.find(x=>x.uid===item.uid)) return;
      if(isSlash(item.text)){
        const neg = getSlashParts(item.text).find(p=>posOf(p)===false);
        if(neg) setItem(item.uid,{text:neg, section:'A&E', symLabel:label});
      } // 체크형/입력형은 강제 안 함(양성·값이라 누락 표시 유지)
    });
    rerenderEntry(root, entry); fire();
  });
}
// 미응답 A&E 문항 (게이트용)
function pendingAE(entry){ return entry.collected.aeItems.filter(it=>!S.items.find(x=>x.uid===it.uid)); }
function rerenderEntry(root, entry){
  const old = root.querySelector(`[data-entry="${entry.id}"]`); if(!old) return;
  const tmp=document.createElement('div'); tmp.innerHTML=assessHTML(entry);
  old.replaceWith(tmp.firstElementChild); bindAssess(root, entry);
}

// ============================================================
// 진단 패널 (자동·잠금)
// ============================================================
function dxHTML(){
  const dx = derivedDx();
  let h = `<div class="sec sec-d"><div class="sec-h">🔴 간호진단 【D】 — 자동</div>`;
  if(!dx.length){ h+=`<div class="empty2">사정에서 증상을 선택하면 진단이 자동 추천됩니다.</div></div>`; return h; }
  dx.forEach(d=>{ h+=`<div class="dx on locked"><div class="ck">✓</div><div>${esc(d.text)}</div><span class="auto">자동</span></div>`; });
  h+=`</div>`; return h;
}

// ============================================================
// 의식 / 낙상 섹션 (항상)
// ============================================================
function fallHTML(){
  const has=t=>!!S.items.find(c=>c.uid===t);
  const lvl=(S.items.find(c=>c.uid==='con-level')||{}).text||'';
  const lvlv=lvl.startsWith('의식수준 :')?lvl.slice('의식수준 :'.length).trim():'';
  let h=`<div class="sec sec-fall"><div class="sec-h">🔒 의식 / 낙상 (항상)</div>`;
  // 의식
  h+=`<div class="q"><div class="q-prompt">의식</div><div class="opts">
    <div class="opt ${has('con-clear')?'sel-neg':''}" data-con="clear">명료</div>
    <div class="opt ${has('con-low')?'sel-pos':''}" data-con="low">저하</div></div>
    <input class="txt-input" data-conlevel="1" placeholder="의식수준 입력 (GCS 15 미만 시)" value="${esc(lvlv)}" style="${has('con-low')?'':'display:none'}"></div>`;
  // 보호자
  h+=`<div class="q"><div class="q-prompt">보호자</div><div class="opts">
    <div class="opt ${has('guard-y')?'sel-neg':''}" data-guard="y">상주</div>
    <div class="opt ${has('guard-n')?'sel-neg':''}" data-guard="n">없음</div></div></div>`;
  // 낙상교육
  h+=`<div class="sec-h" style="margin-top:6px;background:rgba(255,200,87,.12);color:var(--pe)">📢 낙상 교육 — 말하며 체크</div>`;
  N.EDU_ITEMS.forEach(e=>{
    const on = e.records.every(r=>!!S.items.find(c=>c.uid==='fall_'+r));
    h+=`<div class="iv ${on?'on':''}" data-fedu="${e.id}">
      <div class="script"><span class="spk">📢</span> ${esc(e.say)}</div>
      <div class="rec"><span class="ck">${on?'✓':''}</span> 기록: ${esc(e.records.join(' / '))}</div></div>`;
  });
  h+=`<div class="note-tag" style="margin-top:8px">🔒 낙상위험 진단은 자동 포함됩니다.</div>`;
  h+=`</div>`; return h;
}
function bindFall(root){
  const scope = root.querySelector('.sec-fall'); if(!scope) return;
  scope.querySelectorAll('[data-con]').forEach(b=>b.addEventListener('click',()=>{
    const v=b.dataset.con;
    setItem('con-clear', v==='clear'?{text:'의식 명료함',section:'A&E',symLabel:'의식/낙상'}:null);
    setItem('con-low', v==='low'?{text:'의식 저하',section:'A&E',symLabel:'의식/낙상'}:null);
    if(v!=='low') setItem('con-level', null);
    scope.querySelectorAll('[data-con]').forEach(x=>x.classList.remove('sel-pos','sel-neg'));
    b.classList.add(v==='low'?'sel-pos':'sel-neg');
    const inp=scope.querySelector('[data-conlevel]'); if(inp) inp.style.display = v==='low'?'block':'none';
    fire();
  }));
  const inp=scope.querySelector('[data-conlevel]');
  if(inp) inp.addEventListener('blur',()=>{ const v=inp.value.trim(); setItem('con-level', v?{text:'의식수준 : '+v,section:'A&E',symLabel:'의식/낙상'}:null); fire(); });
  scope.querySelectorAll('[data-guard]').forEach(b=>b.addEventListener('click',()=>{
    const y=b.dataset.guard==='y';
    setItem('guard-y', y?{text:'보호자 환자 옆에 상주하고 있음',section:'A&E',symLabel:'의식/낙상'}:null);
    setItem('guard-n', !y?{text:'보호자 동행하지 않음',section:'A&E',symLabel:'의식/낙상'}:null);
    scope.querySelectorAll('[data-guard]').forEach(x=>x.classList.remove('sel-neg'));
    b.classList.add('sel-neg'); fire();
  }));
  scope.querySelectorAll('[data-fedu]').forEach(card=>card.addEventListener('click',()=>{
    const e=N.EDU_ITEMS.find(x=>x.id===card.dataset.fedu);
    const on=!card.classList.contains('on'); card.classList.toggle('on',on); card.querySelector('.ck').textContent=on?'✓':'';
    e.records.forEach(r=> setItem('fall_'+r, on?{text:r,section:'계획',symLabel:'의식/낙상'}:null));
    fire();
  }));
}

// ============================================================
// 미리보기 / 기록 출력
// ============================================================
function allItems(){
  const items = S.items.slice();
  derivedDx().forEach(d=> items.push({text:d.text, section:'진단', symLabel:d.label}));
  return items;
}
function previewHTML(){
  const items=allItems();
  if(!items.length) return '<div class="empty2">탭하면 여기에 정형 간호기록이 쌓입니다.</div>';
  const order={'도관':0,'A&E':1,'비고':2,'진단':3,'계획':4};
  const tagcls={'A&E':'ae','비고':'note','진단':'d','계획':'pe','도관':'ae'};
  const tagtxt={'A&E':'A&E','비고':'비고','진단':'D','계획':'P&E','도관':'도관'};
  const groups={}; items.forEach(c=>(groups[c.symLabel]=groups[c.symLabel]||[]).push(c));
  let h='';
  Object.keys(groups).forEach(label=>{
    h+=`<div class="rl-grp">[${esc(label)}]</div>`;
    groups[label].slice().sort((a,b)=>(order[a.section]??9)-(order[b.section]??9)).forEach(c=>{
      h+=`<div class="rl ${tagcls[c.section]||''}"><span class="tag">${tagtxt[c.section]||''}</span>${esc(c.text)}</div>`;
    });
  });
  return h;
}
function recordText(){ return N.recordText(allItems()); }
function count(){ return allItems().length; }

global.NFHUI = { S, addComplaint, removeComplaint, reset, pendingAE,
  assessHTML, bindAssess, dxHTML, fallHTML, bindFall, previewHTML, recordText, count,
  set onChange(fn){ _onChange=fn; }, fire };
})(window);
