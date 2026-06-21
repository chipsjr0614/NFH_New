// nfh_core_260620.js — NFH 간호기록 공유 코어 (단계형 A / 한화면 B 공용)
// 데이터 정본: _archive/nursing_data.json (15 대분류) — 빌드 시점 인라인
// 보조데이터·헬퍼: _archive/간호기록노트.html 에서 추출 (원문 보존)
// ⚠️ 진술문은 마스터 원문만. 임의 생성 금지.
(function(global){
"use strict";

// ── 데이터: nfh_data.js (엑셀 build_nfh.py 산출물)에서 주입 ──
const { DATA={}, SYMS=[], BRANCHES={}, EXPLAIN_SCRIPTS={}, EDU_ITEMS=[], CATS=[] } = (global.NFH_RAW || {});

// ── 헬퍼 (원문 보존) ──
let _uid = 0;
const nuid = () => 'u' + (_uid++);
const isSlash = t => t.includes('/') && !t.trim().endsWith(':');
const isInput = t => t.trim().endsWith(':');

function getQ(text){
  const t = text.toLowerCase();
  if(t.includes('오심') || t.includes('구토')) return '"오심이나 구토가 있으세요?"';
  if(t.includes('복부 불편감') || (t.includes('불편감') && t.includes('복'))) return '"복부가 불편하신가요?"';
  if(t.includes('불편감')) return '"불편하신 부분이 있으세요?"';
  if(t.includes('복부 통증 있음')) return '"배가 아프세요?"';
  if(t.includes('복부통증 없음') || t.includes('복부 통증 없음')) return '"복통은 없으신가요?"';
  if(t.includes('흉부 통증 있음')) return '"가슴이 아프세요?"';
  if(t.includes('흉부통증 없음') || t.includes('흉부 통증 없음')) return '"흉통은 없으신가요?"';
  if(t.includes('통증 있음') || t.includes('통증있음')) return '"통증이 있으세요?"';
  if(t.includes('통증 없음')) return '"통증은 없으신가요?"';
  if(t.includes('두통')) return '"두통이 있으세요?"';
  if(t.includes('dizziness')) return '"어지럽거나 핑 도는 느낌이 있으세요?"';
  if(t.includes('호흡곤란')) return '"숨이 차거나 답답하신가요?"';
  if(t.includes('기침')) return '"기침이 있으세요?"';
  if(t.includes('가래 소리')) return '가래 소리가 들리는지 청진하세요';
  if(t.includes('가래 잘')) return '"가래를 잘 못 뱉으세요?"';
  if(t.includes('가래')) return '"가래가 나오나요?"';
  if(t.includes('열감')) return '"몸이 뜨겁거나 열이 나는 것 같으세요?"';
  if(t.includes('chilling')) return '"오한(춥고 떨림)이 있으세요?"';
  if(t.includes('wheezing')) return '"쌕쌕거리는 숨소리가 있으세요?"';
  if(t.includes('하지부종')) return '"다리가 붓는 느낌이 있으세요?"';
  if(t.includes('흉부 불편감')) return '"가슴이 불편하신가요?"';
  if(t.includes('대변 봄') || t.includes('대변 못')) return '"대변은 보셨나요?"';
  if(t.includes('설사')) return '"설사하셨나요?"';
  if(t.includes('gas out')) return '"방귀는 나오나요?"';
  if(t.includes('동공')) return '동공 크기를 확인하세요 (Rt/Lt)';
  if(t.includes('빛 반사')) return '빛 반사를 확인하세요 (prompt/sluggish/hippus)';
  if(t.includes('감각이상')) return '"몸에 감각이 이상한 부분이 있으세요?"';
  if(t.includes('grasp') || t.includes('사지근력')) return '"양손으로 꽉 쥐어보세요" — 근력 확인';
  if(t.includes('혈변')) return '"대변에 피가 섞여 나오셨나요?"';
  if(t.includes('흑색변')) return '"검은색 대변이 나오셨나요?"';
  if(t.includes('토혈')) return '"피를 토하셨나요?"';
  if(t.includes('객혈')) return '"피가 섞인 가래를 뱉으셨나요?"';
  if(t.includes('질 출혈') || t.includes('질출혈')) return '"질 출혈이 있으세요?"';
  if(t.includes('출혈 없음') || t.includes('출혈없음')) return '"눈에 보이는 출혈은 없으신가요?"';
  if(t.includes('출혈 있음') || t.includes('출혈있음')) return '"출혈이 있으세요?"';
  if(t.includes('inr')) return 'INR 수치를 확인하세요';
  if(t.includes('hemoglobin')) return '혈중 Hemoglobin 수치를 확인하세요';
  if(t.includes('혈소판')) return '혈소판 수치를 확인하세요';
  if(t.includes('seizure')) return '발작 양상을 확인하세요';
  if(t.includes('고혈당 증상')) return '"갈증이 심하거나 소변이 자주 나오세요?"';
  if(t.includes('저혈당 증상')) return '"식은땀이 나거나 손이 떨리세요?"';
  if(t.includes('혈당')) return '혈당 수치를 확인하세요';
  if(t.includes('c-reactive') || t.includes('crp')) return 'CRP 수치를 확인하세요';
  if(t.includes('심전도')) return '심전도(ECG) 결과를 확인하세요';
  if(t.includes('체온')) return '체온을 측정하세요';
  if(t.includes('산소')) return '산소포화도를 확인하세요';
  if(t.includes('foley')) return 'Foley catheter 삽입 여부를 확인하세요';
  return '확인하세요';
}

function esc(s){ return s.replace(/&/g,'&amp;').replace(/"/g,'&quot;'); }

// 슬래시 항목을 완전한 문장으로 확장 (예: "혈변 있음/없음" → ["혈변 있음","혈변 없음"])
function getSlashParts(text){
  const raw = text.split('/').map(p=>p.trim()).filter(Boolean);
  if(raw.length<=1) return raw;

  // 패턴1: "빛 반사 확인결과 prompt/sluggish/hippus 함" 형식
  // → "빛 반사 확인결과 X 함" 으로 각 옵션 확장
  const last = raw[raw.length-1];
  const firstWords = raw[0].split(' ');
  if(firstWords.length>1 && last.endsWith('함') && !last.includes('있') && !last.includes('없')){
    const prefix = firstWords.slice(0,-1).join(' ');
    const suffix = last.endsWith(' 함') ? ' 함' : '함';
    return raw.map(p=>{
      const clean = p.endsWith(' 함') ? p.slice(0,-2).trim() : (p.endsWith('함') ? p.slice(0,-1).trim() : p.trim());
      return prefix + ' ' + clean + suffix;
    });
  }

  // 패턴2: "subject 있음/없음" 또는 "subject 강함/약함" 형식
  // → 두 번째 이후 단어 없는 짧은 부분에 주어 붙이기
  const quals = ['있음','없음','강함','약함','봄','못봄','멈춤','들림','없음'];
  let subject = '';
  for(const q of quals){
    if(raw[0].endsWith(q) && raw[0].length > q.length){
      subject = raw[0].slice(0, raw[0].length - q.length).trim();
      break;
    }
  }
  return raw.map((p,i)=>{
    if(i===0 || !subject) return p;
    // 공백 없는 짧은 단어(한정어만) → 주어 앞에 붙이기
    return p.includes(' ') ? p : subject+' '+p;
  });
}

// ── 주호소 key([대분류,소분류])들에서 A&E/D/P&E 수집 (순수함수, 양 버전 공용) ──
function collect(keys){
  let aeItems=[], dxItems=[], peRaw=[];
  keys.forEach(([ck,sk]) => {
    const sub = DATA[ck] && DATA[ck][sk]; if(!sub) return;
    Object.values(sub).forEach(sd => {
      (sd['사정 및 평가(A&E)']||[]).forEach(item => aeItems.push({...item, uid:nuid()}));
      (sd['간호진단(D)']||[]).forEach(d => { if(d.text && !dxItems.find(x=>x.text===d.text)) dxItems.push(d); });
      (sd['계획 및 중재(P&E)']||[]).forEach(item => { if(item.text) peRaw.push({...item, uid:nuid()}); });
    });
  });
  const peMap = new Map();
  peRaw.forEach(item => { if(!peMap.has(item.text)) peMap.set(item.text, item); });
  const peItems = [...peMap.values()];
  const hasPain = dxItems.some(d => d.text==='급성통증');
  // 환자설명 대본 (진단별, 중복 P&E 제거)
  const seen = new Set(); const eduScripts=[];
  dxItems.forEach(d => (EXPLAIN_SCRIPTS[d.text]||[]).forEach(s => {
    if(!seen.has(s.pe)){ seen.add(s.pe); eduScripts.push({...s, uid:'edu_'+nuid()}); }
  }));
  return {aeItems, dxItems, peItems, hasPain, eduScripts};
}

// ── 기록 미리보기/복사용 텍스트 (양 버전 동일 출력 보장) ──
// items: [{text, section('A&E'|'진단'|'계획'|'비고'|'도관'), symLabel}]
function recordText(items){
  const order = {'도관':0,'A&E':1,'비고':2,'진단':3,'계획':4};
  const groups = {};
  items.forEach(c => { (groups[c.symLabel] = groups[c.symLabel]||[]).push(c); });
  let out = [];
  Object.keys(groups).forEach(label => {
    out.push('['+label+']');
    groups[label].slice().sort((a,b)=>(order[a.section]??9)-(order[b.section]??9))
      .forEach(c => out.push((c.section==='A&E'?'A&E · ':c.section==='진단'?'D · ':c.section==='계획'?'P&E · ':c.section==='비고'?'비고 · ':'· ')+c.text));
    out.push('');
  });
  return out.join('\n').trim();
}

global.NFH = { DATA, SYMS, BRANCHES, EXPLAIN_SCRIPTS, EDU_ITEMS, CATS,
  nuid, isSlash, isInput, getQ, esc, getSlashParts, collect, recordText };
})(window);
