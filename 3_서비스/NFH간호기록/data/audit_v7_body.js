/* 간호기록 V7 감사 — 61경로 × 의식 2 × 답 3 = 366 케이스
   ①모순 ②중복 ③글씨 ④누락 ⑤빈진단 ⑥순서 ⑦오류 ⑧미완 */
const H=document._l.click[0];
const click=a=>H({target:{dataset:a,closest:()=>({dataset:a})},preventDefault(){}});
function html(){ let s=''; for(const k in __reg) s+=(__reg[k].innerHTML||''); return s; }
function 준비(b,의식){ S.sym=S.s1=S.s2=S.set='';S.ans={};S.off=[];S.pain=PAIN0();S.det={};S.closing='';
  S.power={arm:null,leg:null};S.stoolD='';S.q='';S.cathDone=true;S.consc=null;S.gcs={E:null,V:null,M:null};S.ori={};
  S.nm='홍길동';S.id='12345678';S.edu=true;S.guard='보호자 환자 옆에 상주하고 있음';S.memo='';
  click({sym:b.sym}); if(b.sel1)click({s1:b.sel1}); if(b.sel2)click({s2:b.sel2}); click({cs:의식||'의식 명료함'}); }
function 다답(mode){ let i=0;
 for(let n=0;n<10;n++){ const h=html(); let m,hit=false;
  const re=/data-(yn|sel)="(Q\d+)" data-i="(\d)">/g,o={};
  while((m=re.exec(h))) (o[m[2]]=o[m[2]]||[]).push([m[1],+m[3]]);
  for(const q in o){ if(S.ans[q]!==undefined) continue; const st=(D.qbank[q]||{}).stmts||[];
    const 음=x=>NEGP.test(st[x])||NORMP.test(st[x])||/변화 없음/.test(st[x]);
    const want = mode==='pos'? false : mode==='neg'? true : (i++%2===0);
    const t=(want? o[q].find(([,x])=>음(x)) : o[q].find(([,x])=>!음(x))) || o[q][0];
    click(t[0]==='yn'?{yn:q,i:String(t[1])}:{sel:q,i:String(t[1])}); hit=true; }
  if(mode==='pos'){ const ck=/data-ck="(Q\d+)"/g; const 뿌={};
    while((m=ck.exec(h))){ const q=m[1]; if(S.ans[q]!==undefined) continue;
      const t=(D.qbank[q].stmts||[])[0]||'';
      const r=t.replace(/(상승됨|저하됨|증가함|떨어짐|하강함|감소함)$/,'').trim();
      if(뿌[r]) continue; 뿌[r]=1;            /* 서로 반대인 체크는 하나만 */
      click({ck:q}); hit=true; } }
  const vb=/data-vb="(Q\d+)" data-k="([^"]*)" data-v="([^"]*)"/g,vs={};
  while((m=vb.exec(h))){const k=m[1]+'/'+m[2];if(vs[k])continue;vs[k]=1;const c=S.ans[m[1]];
    if((m[2]==='v')?c===undefined:!(c&&c[m[2]])){click({vb:m[1],k:m[2],v:m[3]});hit=true;}}
  detGroups().forEach(g=>{ if(!(S.det[g]||[]).length && (SITES[g]||[]).length){click({site:g,v:SITES[g][0].v});hit=true;} });
  ['E','V','M'].forEach((k,x)=>{if(S.consc==='의식수준 저하됨'&&!S.gcs[k]){click({gc:k,n:String([3,4,5][x])});hit=true;}});
  oriList().forEach(([k])=>{if(S.consc==='의식수준 저하됨'&&S.ori[k]===undefined){click({or:k,v:'1'});hit=true;}});
  if(neuroOpen()){ if(!S.power.arm){click({pw:'arm',v:'V'});hit=true;} if(!S.power.leg){click({pw:'leg',v:'IV'});hit=true;} }
  if(stoolOpen()&&!S.stoolD){click({sd:'3일'});hit=true;}
  const p=pn();
  if(isPainCase()&&painFound()){if(!p.parts.length)click({ppart:'1',v:(P.parts[0]||{}).v});
    if(p.inten==null)click({pint:'1',v:'5'});if(!p.pats.length)click({ppat:'1',v:P.patterns[0]});
    if(!p.freq)click({pfreq:'1',v:P.freqs[0]});if(!p.dur)click({pdur:'1',v:P.durs[0]});hit=true;}
  if(needSmc())['s','m','c'].forEach(k=>{if(!p.smc[k]){click({psmc:'1',k,v:'양호함'});hit=true;}});
  if(!S.closing&&(D.closing||[]).length){click({cl:D.closing[0].sel});hit=true;}
  if(!hit)break; } }
const 꼬리=/(있음|없음|됨|안됨|함|못함|못 봄|봄|증가함|증가됨|감소함|감소됨|변화 없음|상승함|상승됨|하강함|하강됨|저하됨|저하함|떨어짐|약함|강함|촉지됨|보임)$/;
const 뿌리=t=>t.replace(꼬리,'').replace(/[\s:,]+$/,'').trim();
const 기록사정=()=>blocks().flatMap(b=>b.ae||[]).map(x=>x.replace(/\([^)]*\)$/,'').trim());
const R={모순:[],중복:[],글씨:[],누락:[],빈진단:[],순서:[],오류:[],미완:[]};
let 케이스=0;
for(const 의식 of ['의식 명료함','의식수준 저하됨'])
for(const mode of ['neg','pos','mix'])
for(const b of D.branch){ if(!b.set) continue;
 const L=`${b.sym}${b.sel1?'›'+b.sel1:''}[${의식==='의식 명료함'?'명료':'저하'}/${mode}]`;
 try{ 준비(b,의식); 다답(mode);
  if(missing().length){ R.미완.push(`${L} → ${missing().slice(0,2).join(', ')}`); continue; }
  케이스++;
  const seen={}, cnt={};
  기록사정().forEach(x=>{ cnt[x]=(cnt[x]||0)+1; const r=뿌리(x); if(!r) return; (seen[r]=seen[r]||new Set()).add(x); });
  Object.keys(seen).forEach(r=>{ if(seen[r].size>1) R.모순.push(`${L} — ${[...seen[r]].join(' + ')}`); });
  Object.keys(cnt).forEach(x=>{ if(cnt[x]>1) R.중복.push(`${L} — 「${x}」 ${cnt[x]}번`); });
  const rec=new Set(기록사정());
  allQs().forEach(q=>{ const s2=stmt(q,ansOf(q));
    if(s2 && !rec.has(s2.replace(/\([^)]*\)$/,'').trim()) && !/^(동공크기|혈압|INR|의식수준) :/.test(s2))
      R.누락.push(`${L} — 「${s2}」`); });
  const lines=text().split('\n');
  for(let i=0;i<lines.length;i++) if(/^진단\) /.test(lines[i]) && !/^사정\) /.test(lines[i-1]||'')) R.빈진단.push(`${L} — ${lines[i]}`);
 }catch(e){ R.오류.push(`${L}: ${e.message}`); } }
let 쌍=0;
for(const b of D.branch){ if(!b.set) continue; 준비(b,'의식 명료함');
  const h=html(); const re=/data-yn="(Q\d+)" data-i="(\d)">([^<]*)</g; let m; const g={};
  while((m=re.exec(h))) (g[m[1]]=g[m[1]]||[]).push([+m[2],m[3].trim()]);
  for(const q in g){ const p=g[q]; if(p.length!==2) continue; const st=D.qbank[q].stmts;
    p.forEach(([i,lab])=>{ if(!st[i].endsWith(lab)) R.글씨.push(`${b.sym} ${q}「${lab}」≠「${st[i]}」`);
      click({yn:q,i:String(i)}); if(stmt(q,S.ans[q])!==st[i]) R.글씨.push(`${b.sym} ${q}「${lab}」→「${stmt(q,S.ans[q])}」`);
      click({yn:q,i:String(i)}); });
    if(/없음$/.test(st[p[0][0]])&&/있음$/.test(st[p[1][0]])) R.순서.push(`${b.sym} ${q}`);
    쌍++; } }
console.log(`케이스 ${케이스}/366 완주 · 토글 버튼쌍 ${쌍}개\n`);
const 이름={모순:'① 한 기록에 「있음」과 「없음」이 함께',중복:'② 같은 진술문이 두 번',
  글씨:'③ 버튼 글씨 ↔ 기록 불일치',누락:'④ 눌렀는데 기록에 없음',빈진단:'⑤ 진단만 있고 사정이 빔',
  순서:'⑥ 「없음」이 왼쪽',오류:'⑦ 스크립트 오류',미완:'⑧ 끝까지 못 채운 경로'};
Object.keys(이름).forEach(k=>{ const u=[...new Set(R[k])];
  console.log(`${이름[k]} — ${u.length}건`);
  u.slice(0,6).forEach(x=>console.log('     '+x));
  if(u.length>6) console.log(`     … 외 ${u.length-6}건`); });
