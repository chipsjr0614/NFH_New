#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간호기록 V6 데이터 빌드
  간호기록_원본_*.xlsx  →  질문은행 + 경로  →  nfh_v6_data.js

핵심 원칙 (CLAUDE.md 절대규칙)
  · 진술문은 진술문 마스터 원문만 사용한다.
  · 자동 교정은 「띄어쓰기·대소문자만 다르고 마스터에 원문이 확실히 있는 경우」로 한정한다.
  · 마스터에 없는 문구는 지어내지 않고 _확인필요.txt 에 보고만 한다.

실행:  python3 build_v6.py
"""
import os, re, glob, json, collections
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
SVC  = os.path.dirname(HERE)                      # 3_서비스/NFH간호기록
OUT_JS   = os.path.join(SVC, 'app', 'nfh_v6_data.js')
OUT_WARN = os.path.join(HERE, '_확인필요.txt')

# ── 입력 파일 ────────────────────────────────────────────────
def newest(pattern):
    c = sorted(glob.glob(os.path.join(HERE, pattern)))
    c = [x for x in c if '백업' not in os.path.basename(x)]
    if not c: raise SystemExit(f'입력 파일 없음: {pattern}')
    return c[-1]

SRC    = newest('간호기록_원본_*.xlsx')
MASTER = os.path.join(SVC, 'Nr.statement_1023_Final.xlsx')

# ── 마스터 적재 ──────────────────────────────────────────────
nsp  = lambda s: re.sub(r'\s', '', str(s))          # 공백 무시
nspc = lambda s: nsp(s).lower()                     # 공백+대소문자 무시

wbm = openpyxl.load_workbook(MASTER, read_only=True)
M_SP, M_SPC = {}, {}
DX_SET = set()
for r in wbm['진술문'].iter_rows(min_row=1, values_only=True):
    if not r[1]: continue
    n, s = r[0], str(r[1]).strip()
    M_SP.setdefault(nsp(s), s)
    M_SPC.setdefault(nspc(s), s)
    if isinstance(n, int) and 7875 <= n <= 8079:
        DX_SET.add(nspc(s))

WARN = []
def canon(text, where):
    """마스터 원문으로 정규화. 없으면 원문 그대로 두고 경고."""
    t = str(text).strip()
    if nsp(t) in M_SP:
        fixed = M_SP[nsp(t)]
        if fixed != t: WARN.append(('띄어쓰기교정', where, t, fixed))
        return fixed
    if nspc(t) in M_SPC:
        fixed = M_SPC[nspc(t)]
        WARN.append(('대소문자교정', where, t, fixed))
        return fixed
    WARN.append(('마스터없음', where, t, ''))
    return t

# ── 토글/선택 진술문 분해 ─────────────────────────────────────
SHORT = ('있음','없음','안됨','됨','강함','약함','가능함','가능하지 않음','정상임','멈춤','좋음')
def split_stmt(v):
    """'열감 있음/없음' → ['열감 있음','열감 없음']  (축약형 확장)"""
    parts = [x.strip() for x in str(v).split('/')]
    if len(parts) == 1: return parts
    out = [parts[0]]
    for x in parts[1:]:
        if x in SHORT:
            stem = parts[0]
            for sh in sorted(SHORT, key=len, reverse=True):
                if parts[0].endswith(sh):
                    stem = parts[0][:-len(sh)].strip(); break
            out.append(f'{stem} {x}'.strip() if stem and stem != parts[0] else x)
        else:
            out.append(x)
    return out

def rows(sheet):
    ws = openpyxl.load_workbook(SRC, read_only=True, data_only=True)[sheet]
    it = ws.iter_rows(values_only=True)
    hdr = [str(h).strip() if h is not None else '' for h in next(it)]
    for r in it:
        d = {hdr[i]: r[i] for i in range(min(len(hdr), len(r)))}
        if any(v is not None and str(v).strip() for v in d.values()):
            yield d

# ── 1) 질문은행 + 경로 ───────────────────────────────────────
QBANK   = collections.OrderedDict()   # qid -> {q, fmt, stmts, core}
QINDEX  = {}                          # (질문문구, 진술문원본) -> qid
PATHSET = collections.OrderedDict()   # 소분류 -> {대분류, dx:[{name, ae:[qid], pe:[문구]}], ae_all:[qid]}

def qkey(q):
    """중복 판정용 질문 키. 앞머리 🩺/💬 표시는 화면 힌트일 뿐이라 무시한다."""
    return nsp(re.sub(r'^[^\w"“\'가-힣]+', '', str(q)))

def qid_for(q, raw, fmt, where):
    # 표기 변형을 흡수하려면 「마스터 원문으로 정규화한 뒤」 중복을 판단해야 한다.
    stmts = [canon(x, where) for x in split_stmt(raw)]
    key = (qkey(q), tuple(stmts))
    if key in QINDEX: return QINDEX[key]
    qid = f'Q{len(QBANK)+1:03d}'
    QBANK[qid] = {'q': str(q).strip(), 'fmt': str(fmt or '체크').strip(),
                  'stmts': stmts, 'paths': set()}
    QINDEX[key] = qid
    return qid

for r in rows('2.사정세트'):
    대, 소 = str(r.get('대분류') or '').strip(), str(r.get('소분류') or '').strip()
    과 = str(r.get('과정') or '').strip()
    raw = r.get('진술문(마스터원문)')
    if not 소 or not 과 or raw is None: continue
    link = str(r.get('진단연결') or '').strip()
    P = PATHSET.setdefault(소, {'대분류': 대, 'dx': collections.OrderedDict(), 'items': []})
    where = f'{소}/{과}'

    if 과 == 'D':
        name = canon(raw, where)
        if nspc(name) not in DX_SET:
            WARN.append(('진단아님', where, name, '마스터 간호진단 목록에 없음'))
        P['dx'].setdefault(name, {'ae': [], 'pe': []})
    elif 과 == 'A&E':
        qid = qid_for(r.get('질문문구(💬)') or '', raw, r.get('입력형식'), where)
        QBANK[qid]['paths'].add(소)
        P['items'].append(('ae', qid, link))
    elif 과 == 'P&E':
        P['items'].append(('pe', canon(raw, where), link))

# 진단별 배치 (진단연결 사용, '공통'은 전 진단에)
for 소, P in PATHSET.items():
    names = list(P['dx'].keys())
    for kind, val, link in P['items']:
        tgt = names if (link == '공통' or link not in names) else [link]
        if not names: continue
        for n in tgt: P['dx'][n][kind].append(val)

# ── 2) 공통 질문(core) 판정 — 경로 절반 이상 등장 ──────────────
NPATH = len(PATHSET)
for qid, v in QBANK.items():
    v['core'] = len(v['paths']) >= NPATH * 0.25
    v['paths'] = sorted(v['paths'])

# ── 3) 주호소 트리 ───────────────────────────────────────────
SYMS, BRANCH = collections.OrderedDict(), []
for r in rows('1.주호소트리'):
    sid = str(r.get('주증상id') or '').strip()
    nm  = str(r.get('주증상') or '').strip()
    if not nm: continue
    SYMS.setdefault(nm, {'id': sid, 'icon': str(r.get('아이콘') or '').strip(),
                         'q1': str(r.get('질문1') or '').strip(),
                         'q2': str(r.get('질문2') or '').strip()})
    BRANCH.append({'sym': nm,
                   'sel1': str(r.get('선택1') or '').strip(),
                   'sel2': str(r.get('선택2') or '').strip(),
                   'set':  str(r.get('소분류') or '').strip()})

# ── 4) 도관 / 낙상교육 / 환자설명 / 마무리질문 ─────────────────
CATH = []
for r in rows('4.도관'):
    raw = r.get('도관 진술문(| 로 구분)') or r.get('도관 진술문')
    if not r.get('도관') or not raw: continue
    CATH.append({'s': str(r['도관']).strip(),
                 'n': str(r.get('정식명칭') or r['도관']).strip(),
                 'd': [canon(x, f"도관/{r['도관']}") for x in str(raw).split('|') if x.strip()],
                 'new': bool(str(r.get('비고') or '').strip()),
                 'top': int(r.get('순서') or 99) <= 10})
EDU  = [{'say': str(r.get('말할 문구(📢)') or '').strip(),
         'recs': list(dict.fromkeys(canon(x, '낙상교육') for x in str(r.get('기록 진술문(여러개는 | 로 구분)') or '').split('|') if x.strip()))}
        for r in rows('5.낙상교육') if r.get('id')]
# 진단명은 공백 차이가 있어 정규화해 묶는다. P&E도 마스터 원문으로 맞춘다.
EXPL_RAW = collections.defaultdict(list)
for r in rows('3.환자설명'):
    if r.get('진단'):
        EXPL_RAW[nsp(r['진단'])].append({'say': str(r.get('말할 문구(📢)') or '').strip().strip('"'),
                                         'pe':  canon(r.get('연동 P&E') or '', '환자설명')})
CLOSING = [{'sel': str(r.get('선택') or '').strip(),
            'q':   str(r.get('질문문구(💬)') or '').strip(),
            'rec': canon(r['진술문(마스터원문)'], '마무리질문') if r.get('진술문(마스터원문)') else '',
            'next':str(r.get('다음동작') or '').strip()}
           for r in rows('6.마무리질문') if r.get('선택')]

# ── 5) 출력 ─────────────────────────────────────────────────
DATA = {
  'meta': {'src': os.path.basename(SRC), 'paths': NPATH, 'questions': len(QBANK)},
  'qbank': {k: {'q': v['q'], 'fmt': v['fmt'], 'stmts': v['stmts'],
                'core': v['core'], 'n': len(v['paths'])} for k, v in QBANK.items()},
  'syms': SYMS, 'branch': BRANCH,
  'sets': {k: {'대분류': v['대분류'],
               'dx': [{'name': n, 'ae': d['ae'], 'pe': d['pe']} for n, d in v['dx'].items()]}
           for k, v in PATHSET.items()},
  'cath': CATH, 'edu': EDU, 'closing': CLOSING,
  # 경로에서 실제 쓰는 진단명 기준으로 환자설명을 붙인다
  'explain': {n: list({e['pe']: e for e in EXPL_RAW.get(nsp(n), [])}.values())
              for n in {dx for P in PATHSET.values() for dx in P['dx']}},
}
os.makedirs(os.path.dirname(OUT_JS), exist_ok=True)
with open(OUT_JS, 'w', encoding='utf-8') as f:
    f.write('/* 자동 생성 — 직접 수정 금지. 데이터는 엑셀을 고치고 build_v6.py 실행 */\n')
    f.write('window.NFH_V6 = ' + json.dumps(DATA, ensure_ascii=False, indent=1) + ';\n')

# ── 6) 경고 리포트 (같은 문구는 1건으로 집계) ─────────────────
UNIQ = collections.OrderedDict()
for kind, where, a, b in WARN:
    UNIQ.setdefault((kind, a, b), where)
cnt = collections.Counter(k[0] for k in UNIQ)

# 같은 질문인데 진술문이 달라 갈린 것 → 선택형으로 합칠 후보
SPLIT = collections.defaultdict(list)
for qid, v in QBANK.items(): SPLIT[qkey(v['q'])].append(qid)
SPLIT = {k: v for k, v in SPLIT.items() if len(v) > 1}
VAGUE = [qid for qid, v in QBANK.items() if len(nsp(v['q'])) <= 6]

with open(OUT_WARN, 'w', encoding='utf-8') as f:
    f.write(f'간호기록 V6 빌드 리포트\n원본: {os.path.basename(SRC)}\n')
    f.write('='*70 + '\n')
    for k, n in cnt.most_common(): f.write(f'  {k:12} {n:4}건\n')
    f.write(f'  {"질문문구없음":12} {len(VAGUE):4}건\n')
    f.write(f'  {"선택형합칠후보":12} {len(SPLIT):4}건\n')
    f.write('='*70 + '\n')
    f.write('\n※ 자동 교정(띄어쓰기·대소문자)은 빌드가 이미 마스터 원문으로 맞췄다. 엑셀은 고치지 않아도 된다.\n')
    f.write('※ 「마스터없음」은 AI가 지어내지 않고 그대로 두었다. 칩스 판단이 필요하다.\n')

    for kind in ['마스터없음', '진단아님', '대소문자교정', '띄어쓰기교정']:
        sel = [(k, w) for k, w in UNIQ.items() if k[0] == kind]
        if not sel: continue
        f.write(f'\n\n[{kind}] {len(sel)}건\n' + '-'*70 + '\n')
        for (_, a, b), where in sel:
            f.write(f'  {where:32} 「{a}」' + (f'  →  「{b}」' if b else '') + '\n')

    if VAGUE:
        f.write(f'\n\n[질문문구없음] {len(VAGUE)}건 — 간호사가 뭘 물어야 할지 알 수 없음\n' + '-'*70 + '\n')
        for qid in VAGUE:
            f.write(f'  {qid}  질문「{QBANK[qid]["q"]}」  진술문 {QBANK[qid]["stmts"]}\n')

    if SPLIT:
        f.write(f'\n\n[선택형 합칠 후보] {len(SPLIT)}건 — 같은 질문인데 진술문이 달라 따로 잡혔다\n' + '-'*70 + '\n')
        for _, qids in SPLIT.items():
            f.write(f'  질문「{QBANK[qids[0]]["q"]}」\n')
            for q in qids: f.write(f'      {q}  {QBANK[q]["stmts"]}\n')

print(f'✅ {OUT_JS}')
print(f'   경로 {NPATH} · 질문 {len(QBANK)}개 (공통 {sum(1 for v in QBANK.values() if v["core"])}개)')
print(f'   도관 {len(CATH)} · 낙상교육 {len(EDU)} · 환자설명 {len(DATA["explain"])}종 · 마무리 {len(CLOSING)}')
print(f'📝 {OUT_WARN}')
for k, n in cnt.most_common(): print(f'   {k:12} {n:4}건')
