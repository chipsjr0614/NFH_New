/* 복부 3경로 실제 기록 확인 — 진짜 환자 시나리오로 돌려 본다 */
require('/tmp/domstub.js');
const fs = require('fs');
const P = '/Users/sungkwanchoi/Library/Mobile Documents/com~apple~CloudDocs/AI/NFH_New/nursing/app/간호기록V7.html';
const app = fs.readFileSync(P, 'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];

const body = `
function 세팅(setName){
  const b = D.branch.find(x => x.set === setName);
  S.sym = b.sym; S.s1 = b.sel1 || ''; S.s2 = b.sel2 || ''; S.set = setName;
  S.ans = {}; S.off = []; S.pain = PAIN0(); S.det = {}; S.closing = '';
  S.base = S.base || {};
  return b;
}
/* 진술문 글씨로 답을 고른다 — 문항 ID는 빌드마다 바뀌므로 쓰지 않는다.
   ★ 같은 진술문을 쓰는 문항이 다른 경로에도 있어, 반드시 지금 경로 안에서만 찾는다 */
function 답(진술문){
  const st0 = setOf(S.set);
  const 후보 = [...new Set(st0.dx.flatMap(d => d.ae))];
  for (const q of 후보) {
    const st = D.qbank[q].stmts || [];
    const i = st.indexOf(진술문);
    if (i < 0) continue;
    S.ans[q] = (D.qbank[q].fmt === '체크') ? true : i;
    return true;
  }
  console.log('   ✗ 이 경로에 없는 진술문:', 진술문);
  return false;
}
function 출력(제목, setName, 답들, 통증) {
  세팅(setName);
  답들.forEach(답);
  if (통증) { S.pain.on = true; Object.assign(S.pain, 통증); }
  console.log('\\n' + '─'.repeat(62));
  console.log('▣ ' + 제목);
  console.log('─'.repeat(62));
  blocks().forEach(b => {
    console.log('\\n  [' + b.t + ']');
    (b.ae || []).forEach(x => console.log('    · ' + x));
    (b.pe || []).forEach(x => console.log('    ▸ ' + x));
  });
}

출력('① 60세 남 — 명치가 아프고 검은 변을 봤다 (위궤양 출혈)',
     '복부통증',
     ['상복부 통증 있음', '반동압통 없음', '복부 팽만 없음',
      'gas out 됨', '대변 못 봄', '흑색변 있음']);

출력('② 22세 남 — 어제부터 아랫배가 아프고 눌렀다 떼면 더 아프다 (충수돌기염 의심)',
     '복부통증',
     ['하복부 통증 있음', '반동압통 있음', '복부 팽만 없음',
      'gas out 안됨', '대변 못 봄', '혈변 없음']);

출력('③ 78세 여 — 배가 빵빵하고 가스가 안 나온다 (장폐색 의심)',
     '복부통증',
     ['복부 통증 있음', '반동압통 없음', '복부 팽만 있음',
      'gas out 안됨', '대변 못 봄', '혈변 없음']);

출력('④ 45세 여 — 배 아프고 대변은 정상 (단순 복통)',
     '복부통증',
     ['복부 통증 있음', '반동압통 없음', '복부 팽만 없음',
      'gas out 됨', '정상 대변 봄', '혈변 없음']);

출력('⑤ 65세 남 — 눈이 노랗고 열이 나며 배가 아프다 (담관염 의심)',
     '황달',
     ['공막의 황달 있음', '열감 있음', '복부 통증 있음', '가려움증 있음']);

출력('⑥ 28세 여 — 아랫배가 아프고 생리가 늦었다 (자궁외임신 배제 필요)',
     '여성하복부통증',
     ['하복부 통증 있음', '질 출혈 있음', '무월경 있음']);
`;

(0, eval)(app + '\n;\n' + body);
