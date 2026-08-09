/* 62경로 × 모든 진단의 「평가 2줄」이 무엇인지 그대로 떠 둔다.
   peOf를 고치기 전후로 돌려 비교하면 어디가 달라졌는지 한 줄도 안 놓친다. */
require('/tmp/domstub.js');
const fs = require('fs');
const P = '/Users/sungkwanchoi/Library/Mobile Documents/com~apple~CloudDocs/AI/NFH_New/nursing/app/간호기록V7.html';
const app = fs.readFileSync(P, 'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];

const body = `
const out = [];
Object.keys(D.sets).forEach(name => {
  S.set = name;
  const st = D.sets[name];
  st.dx.forEach(dx => {
    out.push(name + ' | ' + dx.name + ' | ' + peOf(dx).map(x => x.pe).join(' / '));
  });
});
console.log(out.join('\\n'));
`;
(0, eval)(app + '\n;\n' + body);
