const H=document._l.click[0];
const click=a=>H({target:{dataset:a,closest:()=>({dataset:a})},preventDefault(){}});
function html(){ let s=''; for(const k in __reg) s+=(__reg[k].innerHTML||''); return s; }
function 준비(b,의식){ S.sym=S.s1=S.s2=S.set='';S.ans={};S.off=[];S.pain=PAIN0();S.det={};S.closing='';
  S.power={arm:null,leg:null};S.stoolD='';S.consc=null;S.gcs={E:null,V:null,M:null};S.ori={};
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
  const ck=/data-ck="(Q\d+)"/g; while((m=ck.exec(h))) if(S.ans[m[1]]===undefined){click({ck:m[1]});hit=true;}
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

for(const [sym,s1,mode] of [['중독',null,'mix'],['외상',null,'pos'],['소아','⚡ 경련했어요','mix']]){
  const b=D.branch.find(x=>x.sym===sym&&(!s1||x.sel1===s1));
  준비(b,'의식 명료함'); 다답(mode);
  console.log('══ '+sym+(s1?' › '+s1:'')+' ['+mode+'] ══  미응답 '+(missing().length?missing().join(', '):'없음 ✅'));
  console.log(text()); console.log();
}
