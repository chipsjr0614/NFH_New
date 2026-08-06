require('/tmp/domstub.js');
const fs=require('fs');
const P='/Users/sungkwanchoi/Library/Mobile Documents/com~apple~CloudDocs/AI/NFH_New/nursing/app/간호기록V7.html';
const app=fs.readFileSync(P,'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
(0,eval)(app+'\n;\n'+fs.readFileSync('/tmp/audit_body.js','utf8'));
