#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
심장/순환기 교육용 SVG 도해 라이브러리.
- SVG: {id: svg_markup}  (각 그림은 흰 카드 배경 포함 → 다크/라이트 모두 가독)
- SVG_MAP: {케이스번호: {섹션제목 부분문자열: svg_id}}
ECG류는 _ecg() 헬퍼로 일관 생성, 해부·흐름도는 개별 작성.
"""

FONT = "'Apple SD Gothic Neo','Noto Sans KR',sans-serif"

# ── 섹션 매핑 (섹션 제목에 키가 '포함'되면 해당 그림 삽입) ──────────────
SVG_MAP = {
 "01": {"해부": "coronary_map", "병태생리": "athero4", "ECG": "ecg_stemi"},
 "02": {"병태생리": "occlusion_partial_full", "검사": "ecg_nstemi"},
 "03": {"정의": "plaque_stable_unstable", "검사": "ecg_ua"},
 "04": {"병태생리": "pulmonary_edema", "증상": "left_right_hf"},
 "05": {"정의": "htn_urg_emerg", "치료": "map_target"},
 "06": {"ECG": "ecg_vf", "치료": "cpr_chain"},
 "07": {"검사": "ecg_vt", "치료": "vt_algorithm"},
 "08": {"병태생리": "atrial_thrombus", "검사": "ecg_af"},
 "09": {"병태생리": "conduction_system", "검사": "ecg_avb3"},
 "10": {"병태생리": "tamponade", "검사": "ecg_pericarditis"},
 "11": {"병태생리": "aortic_dissection", "증상": "dissection_signs"},
}

SVG = {}

# ════════════════════════════════════════════════════════════════
# ECG 생성 헬퍼
# ════════════════════════════════════════════════════════════════
_GRID = ('<defs>'
 '<pattern id="g_sm" width="10" height="10" patternUnits="userSpaceOnUse">'
 '<path d="M10 0H0V10" fill="none" stroke="#f3c7cb" stroke-width="0.7"/></pattern>'
 '<pattern id="g_lg" width="50" height="50" patternUnits="userSpaceOnUse">'
 '<rect width="50" height="50" fill="url(#g_sm)"/>'
 '<path d="M50 0H0V50" fill="none" stroke="#e88e95" stroke-width="1.5"/></pattern>'
 '</defs>')

def _beat(x, b, st=0, tw=1, Rh=80, wide=False, p=True):
    """한 박동 PQRST 좌표 리스트. st:ST레벨(+상승), tw:T방향(+1정상,-1역전), wide:넓은 QRS."""
    o = []
    if p: o += [(0,0),(13,-12),(26,0)]
    else: o += [(0,0)]
    o += [(42,0)]
    if wide:
        o += [(50,16),(78,-Rh),(108,34),(132,-st)]; s0 = 132
    else:
        o += [(48,11),(57,-Rh),(67,28),(76,-st)]; s0 = 76
    o += [(s0+30,-st)]
    t = s0+30
    o += [(t+20,-st-24*tw),(t+44,-st),(t+58,0)]
    return [(x+dx, b+dy) for dx,dy in o]

def _poly(points, color, w=3):
    pts = " ".join(f"{px:.0f},{py:.0f}" for px,py in points)
    return f'<polyline fill="none" stroke="{color}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round" points="{pts}"/>'

def _ecg(title, beats, color="#b23039", footer="", highlight=None, baseline=True):
    """beats: _beat(...) 결과 리스트들을 이어 하나의 파형으로. highlight:(x,y,r,label)."""
    W, H = 1180, 430
    b = 235
    body = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">', _GRID,
            f'<rect width="{W}" height="{H}" rx="18" fill="#ffffff"/>',
            f'<text x="34" y="50" font-size="27" font-weight="800" fill="#1a2a3a">{title}</text>',
            f'<line x1="34" y1="66" x2="{W-34}" y2="66" stroke="#e3e8ee" stroke-width="2"/>',
            f'<rect x="34" y="92" width="{W-68}" height="210" rx="10" fill="url(#g_lg)" stroke="#e88e95" stroke-width="1.6"/>']
    if baseline:
        body.append(f'<line x1="46" y1="{b}" x2="{W-46}" y2="{b}" stroke="#2e9d4f" stroke-width="1.1" stroke-dasharray="6 5"/>')
    flat = []
    for be in beats: flat += be
    body.append(_poly(flat, color, 3.2))
    if highlight:
        hx,hy,hr,lab = highlight
        body.append(f'<circle cx="{hx}" cy="{hy}" r="{hr}" fill="none" stroke="#ff7a00" stroke-width="3"/>')
        body.append(f'<path d="M{hx} {hy-hr-34} l0 20 l-8 0 l8 14 l8 -14 l-8 0 Z" fill="#ff7a00"/>')
        body.append(f'<text x="{hx+16}" y="{hy-hr-18}" font-size="20" font-weight="800" fill="#ff7a00">{lab}</text>')
    if footer:
        body.append(f'<rect x="34" y="324" width="{W-68}" height="84" rx="11" fill="#fff4ec" stroke="#ff7a00" stroke-width="1.8"/>')
        for i,line in enumerate(footer.split("\n")):
            fw = "800" if i==0 else "500"
            fc = "#b23039" if i==0 else "#3a4654"
            body.append(f'<text x="54" y="{356+i*26}" font-size="17" font-weight="{fw}" fill="{fc}">{line}</text>')
    body.append('</svg>')
    return "".join(body)

def _tile(b, count, x0, gap, **kw):
    out = []
    for i in range(count):
        out.append(_beat(x0 + i*gap, b, **kw))
    return out

# ── ECG 도해들 ──────────────────────────────────────────────
# STEMI: 정상 대비는 별도 손제작(2패널)
def _ecg_stemi():
    W,H=1180,430; b=235
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">',_GRID,
       f'<rect width="{W}" height="{H}" rx="18" fill="#fff"/>',
       f'<text x="34" y="50" font-size="27" font-weight="800" fill="#1a2a3a">정상 vs STEMI — ST를 보라</text>',
       f'<line x1="34" y1="66" x2="{W-34}" y2="66" stroke="#e3e8ee" stroke-width="2"/>']
    # 정상 패널
    s.append(f'<rect x="34" y="90" width="540" height="210" rx="10" fill="url(#g_lg)" stroke="#e88e95" stroke-width="1.6"/>')
    s.append(f'<text x="50" y="116" font-size="17" font-weight="800" fill="#2e9d4f">정상</text>')
    s.append(f'<line x1="46" y1="{b}" x2="566" y2="{b}" stroke="#2e9d4f" stroke-width="1.1" stroke-dasharray="6 5"/>')
    flat=[]
    for be in _tile(b,3,70,165,st=0,tw=1): flat+=be
    s.append(_poly([(x,y) for x,y in flat if x<566],"#1a2a3a",3))
    s.append(f'<text x="150" y="290" font-size="14.5" fill="#5b6876">ST 분절이 기준선과 같은 높이</text>')
    # STEMI 패널
    s.append(f'<rect x="606" y="90" width="540" height="210" rx="10" fill="url(#g_lg)" stroke="#e88e95" stroke-width="1.6"/>')
    s.append(f'<text x="622" y="116" font-size="17" font-weight="800" fill="#b23039">STEMI (ST 상승)</text>')
    s.append(f'<line x1="618" y1="{b}" x2="1138" y2="{b}" stroke="#2e9d4f" stroke-width="1.1" stroke-dasharray="6 5"/>')
    flat=[]
    for be in _tile(b,3,642,165,st=42,tw=1): flat+=be
    s.append(_poly([(x,y) for x,y in flat if 618<x<1138],"#b23039",3.2))
    s.append(f'<circle cx="757" cy="183" r="22" fill="none" stroke="#ff7a00" stroke-width="3"/>')
    s.append(f'<text x="700" y="290" font-size="14.5" fill="#b23039" font-weight="700">ST가 기준선 위로 볼록하게 상승</text>')
    # 핵심박스
    s.append(f'<rect x="34" y="318" width="{W-68}" height="92" rx="11" fill="#fff4ec" stroke="#ff7a00" stroke-width="1.8"/>')
    s.append(f'<text x="54" y="348" font-size="17" font-weight="800" fill="#b23039">💡 ST 상승 = 즉시 보고</text>')
    s.append(f'<text x="54" y="376" font-size="15.5" fill="#3a4654">진단기준: 인접 2개 유도 1mm↑ (V2·V3은 2mm↑)  ·  변화순서: 과첨예T → ST상승 → T역전 → 병적Q파</text>')
    s.append(f'<text x="54" y="400" font-size="14.5" fill="#8b6a4f">처음엔 ST만 봐 — 기준선보다 올라갔으면 일단 보고. 나머지는 나중에 배워도 돼.</text>')
    s.append('</svg>'); return "".join(s)

SVG["ecg_stemi"] = _ecg_stemi()

SVG["ecg_nstemi"] = _ecg(
 "NSTEMI 심전도 — ST 하강 · T파 역전",
 _tile(235,4,70,270, st=-30, tw=-1),
 footer="ST 분절 하강(≥0.5mm) 또는 T파 역전 — ST는 안 올라가지만 Troponin은 오른다\n심내막하 허혈 → 재분극 이상이 '하강'으로 나타남 · 정상 ECG도 NSTEMI 배제 못 함",
 highlight=(170,265,24,"ST 하강"))

SVG["ecg_ua"] = _ecg(
 "불안정 협심증 — 일과성 ST 하강 / T 역전",
 _tile(235,4,70,270, st=-22, tw=-1),
 color="#c2611a",
 footer="흉통 때 ST 하강·T역전 → 통증 멎으면 정상화(가역적·일과성)\nUA와 NSTEMI 구분은 Troponin뿐 — Serial(0·3~6h)로 괴사 배제",
 highlight=(170,260,22,"일과성"))

SVG["ecg_vt"] = _ecg(
 "심실빈맥 (VT) — 넓고 규칙적인 QRS",
 _tile(235,5,70,210, st=0, tw=-1, Rh=95, wide=True, p=False),
 footer="넓은 QRS(≥120ms) 빈맥이 규칙적으로 연속 — 방실해리·융합/포획박동이면 VT 강력 시사\n넓은 QRS 빈맥은 일단 VT로 대응(SVT로 단정 금지) · 무맥이면 즉시 제세동",
 highlight=(148,150,30,"넓은 QRS"))

SVG["ecg_pericarditis"] = _ecg(
 "심낭염 심전도 — 광범위 ST 상승 · PR 하강",
 _tile(235,4,70,270, st=26, tw=1),
 footer="여러 영역에 걸친 '오목한(concave)' ST 상승 + PR 분절 하강 (한 혈관 영역에 국한된 STEMI와 다름)\n앉아 앞으로 숙이면 완화·흡기 시 악화 → STEMI와 감별",
 highlight=(170,200,22,"광범위 ST↑"))

def _ecg_af():
    W,H=1180,430; b=235
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">',_GRID,
       f'<rect width="{W}" height="{H}" rx="18" fill="#fff"/>',
       f'<text x="34" y="50" font-size="27" font-weight="800" fill="#1a2a3a">심방세동 (AF) — 불규칙하게 불규칙 · P파 소실</text>',
       f'<line x1="34" y1="66" x2="{W-34}" y2="66" stroke="#e3e8ee" stroke-width="2"/>',
       f'<rect x="34" y="92" width="{W-68}" height="210" rx="10" fill="url(#g_lg)" stroke="#e88e95" stroke-width="1.6"/>']
    # 불규칙 R-R + P 없음 (QRS만, 간격 다르게)
    xs=[80,250,470,640,860,1010]
    flat=[]
    for i,x in enumerate(xs):
        flat += _beat(x,b,st=0,tw=1,p=False)
    # f파(잔물결) 베이스라인
    import math
    fwave="M46 "+str(b)
    for k in range(46,1134,8):
        fwave+=f" L{k} {b-6 if (k//8)%2 else b+4}"
    s.append(f'<path d="{fwave}" fill="none" stroke="#c98a90" stroke-width="1.2" opacity="0.8"/>')
    s.append(_poly([(x,y) for x,y in flat if x<1134],"#1f5fae",3.1))
    s.append(f'<rect x="34" y="324" width="{W-68}" height="84" rx="11" fill="#eef4fd" stroke="#1f7ae0" stroke-width="1.8"/>')
    s.append(f'<text x="54" y="356" font-size="17" font-weight="800" fill="#1559a8">💡 R-R 간격이 제멋대로 · 뚜렷한 P 대신 잔물결(f파)</text>')
    s.append(f'<text x="54" y="384" font-size="15" fill="#3a4654">빠르면(RVR) 심박수 조절 · 색전 예방 위해 CHA₂DS₂-VASc로 항응고 · 48h↑는 항응고 후 율동전환</text>')
    s.append('</svg>'); return "".join(s)
SVG["ecg_af"] = _ecg_af()

def _ecg_vf():
    W,H=1180,430; b=235
    import random; random.seed(7)
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">',_GRID,
       f'<rect width="{W}" height="{H}" rx="18" fill="#fff"/>',
       f'<text x="34" y="50" font-size="27" font-weight="800" fill="#1a2a3a">심실세동 (VF) — 무질서한 파형, 식별 가능한 QRS 없음</text>',
       f'<line x1="34" y1="66" x2="{W-34}" y2="66" stroke="#e3e8ee" stroke-width="2"/>',
       f'<rect x="34" y="92" width="{W-68}" height="210" rx="10" fill="url(#g_lg)" stroke="#e88e95" stroke-width="1.6"/>']
    pts=[]; x=46; amp=70
    while x<1134:
        x+=random.randint(7,16)
        pts.append((x, b+random.randint(-amp,amp)))
    s.append(_poly(pts,"#b23039",3))
    s.append(f'<rect x="34" y="324" width="{W-68}" height="84" rx="11" fill="#fdeced" stroke="#ef4444" stroke-width="1.8"/>')
    s.append(f'<text x="54" y="356" font-size="17" font-weight="800" fill="#b23039">💡 즉시 제세동 + CPR (맥 확인에 시간 끌지 말 것)</text>')
    s.append(f'<text x="54" y="384" font-size="15" fill="#3a4654">제세동 → 2분 CPR → 리듬확인 반복 · Epinephrine · 불응성엔 Amiodarone · 가역원인(H&amp;T) 교정</text>')
    s.append('</svg>'); return "".join(s)
SVG["ecg_vf"] = _ecg_vf()

def _ecg_avb3():
    W,H=1180,430; b=235
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">',_GRID,
       f'<rect width="{W}" height="{H}" rx="18" fill="#fff"/>',
       f'<text x="34" y="50" font-size="27" font-weight="800" fill="#1a2a3a">완전방실차단 — P와 QRS가 따로 논다(방실해리)</text>',
       f'<line x1="34" y1="66" x2="{W-34}" y2="66" stroke="#e3e8ee" stroke-width="2"/>',
       f'<rect x="34" y="92" width="{W-68}" height="210" rx="10" fill="url(#g_lg)" stroke="#e88e95" stroke-width="1.6"/>',
       f'<line x1="46" y1="{b}" x2="1134" y2="{b}" stroke="#2e9d4f" stroke-width="1" stroke-dasharray="6 5"/>']
    # P파: 규칙적·빠름 (파랑)
    px=80
    pxs=[]
    while px<1120:
        pxs.append(px)
        s.append(f'<path d="M{px} {b} Q {px+13} {b-20} {px+26} {b}" fill="none" stroke="#1f7ae0" stroke-width="2.6"/>')
        s.append(f'<text x="{px+6}" y="{b-26}" font-size="14" fill="#1f7ae0" font-weight="700">P</text>')
        px+=120
    # QRS: 규칙적·느림·독립 (빨강, 넓은 이탈박동)
    for qx in [120, 470, 820]:
        s.append(_poly(_beat(qx,b,st=0,tw=1,Rh=85,wide=True,p=False),"#b23039",3.1))
    s.append(f'<rect x="34" y="324" width="{W-68}" height="84" rx="11" fill="#eef4fd" stroke="#1f7ae0" stroke-width="1.8"/>')
    s.append(f'<text x="54" y="356" font-size="17" font-weight="800" fill="#1559a8">💡 P는 P대로(빠름), QRS는 QRS대로(느림) — 서로 무관</text>')
    s.append(f'<text x="54" y="384" font-size="15" fill="#3a4654">넓은 QRS·HR 20~40 이탈박동은 불안정 · Atropine 무효 많음 → 경피 페이싱 / 가역원인 교정</text>')
    s.append('</svg>'); return "".join(s)
SVG["ecg_avb3"] = _ecg_avb3()

# ════════════════════════════════════════════════════════════════
# 해부 · 병태생리 도해
# ════════════════════════════════════════════════════════════════
SVG["coronary_map"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 540" font-family="''' + FONT + '''">
  <defs>
    <linearGradient id="myo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9656b"/><stop offset="1" stop-color="#b23039"/></linearGradient>
    <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000" flood-opacity="0.18"/></filter>
  </defs>
  <rect width="780" height="540" rx="18" fill="#ffffff"/>
  <text x="32" y="48" font-size="26" font-weight="800" fill="#1a2a3a">관상동맥 지도 — 어느 혈관이 막히면 어디가?</text>
  <line x1="32" y1="62" x2="748" y2="62" stroke="#e3e8ee" stroke-width="2"/>
  <g filter="url(#sh)"><path d="M300 150 C250 110 175 120 160 195 C148 255 175 330 250 405 C300 455 360 480 400 488 C440 480 500 455 550 405 C625 330 652 255 640 195 C625 120 550 110 500 150 C465 175 430 200 400 200 C370 200 335 175 300 150 Z" fill="url(#myo)" stroke="#8d242c" stroke-width="3"/></g>
  <path d="M360 150 C360 95 345 70 330 55" fill="none" stroke="#c98b95" stroke-width="14" stroke-linecap="round"/>
  <path d="M445 150 C448 100 470 78 492 66" fill="none" stroke="#c98b95" stroke-width="14" stroke-linecap="round"/>
  <path d="M398 175 C396 250 392 330 386 430" fill="none" stroke="#f2a900" stroke-width="9" stroke-linecap="round"/>
  <circle cx="398" cy="178" r="7" fill="#f2a900"/>
  <path d="M420 188 C500 205 560 250 560 330" fill="none" stroke="#2e9d4f" stroke-width="9" stroke-linecap="round"/>
  <path d="M362 188 C275 215 222 270 235 360" fill="none" stroke="#1f7ae0" stroke-width="9" stroke-linecap="round"/>
  <g font-size="16">
    <rect x="560" y="120" width="196" height="74" rx="10" fill="#fff7e6" stroke="#f2a900" stroke-width="2"/>
    <circle cx="578" cy="142" r="6" fill="#f2a900"/><text x="592" y="147" font-weight="800" fill="#9a6b00">LAD (전하행지)</text>
    <text x="574" y="170" fill="#5b4a1f">심실 전벽 · V1~V4 ST↑</text><text x="574" y="188" fill="#b23039" font-weight="700">가장 위험</text>
    <line x1="560" y1="157" x2="430" y2="300" stroke="#f2a900" stroke-width="2" stroke-dasharray="4 4"/>
    <rect x="560" y="350" width="196" height="74" rx="10" fill="#eafaef" stroke="#2e9d4f" stroke-width="2"/>
    <circle cx="578" cy="372" r="6" fill="#2e9d4f"/><text x="592" y="377" font-weight="800" fill="#1d6b36">LCX (좌회선지)</text>
    <text x="574" y="400" fill="#264f33">측벽 · I·aVL·V5·V6 ST↑</text><text x="574" y="418" fill="#5b6876">진단이 까다로움</text>
    <line x1="560" y1="387" x2="558" y2="330" stroke="#2e9d4f" stroke-width="2" stroke-dasharray="4 4"/>
    <rect x="24" y="350" width="200" height="92" rx="10" fill="#eaf3fd" stroke="#1f7ae0" stroke-width="2"/>
    <circle cx="42" cy="372" r="6" fill="#1f7ae0"/><text x="56" y="377" font-weight="800" fill="#1559a8">RCA (우관상동맥)</text>
    <text x="38" y="400" fill="#1d3a5f">하벽·우심실 · II·III·aVF ST↑</text><text x="38" y="420" fill="#b23039" font-weight="700">NTG 금기 · 수액 필요</text>
    <text x="38" y="438" fill="#5b6876">서맥 동반 잦음</text>
    <line x1="224" y1="395" x2="240" y2="360" stroke="#1f7ae0" stroke-width="2" stroke-dasharray="4 4"/>
  </g>
  <text x="32" y="520" font-size="14" fill="#8b98a8">※ "막히는 혈관 → 변하는 ECG 유도 → 임상 주의점"을 한눈에</text>
</svg>'''

SVG["athero4"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 460" font-family="''' + FONT + '''">
  <defs>
    <radialGradient id="lumen" cx="0.5" cy="0.4" r="0.6"><stop offset="0" stop-color="#ffe1e3"/><stop offset="1" stop-color="#f2b8bc"/></radialGradient>
    <linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f5c9a0"/><stop offset="1" stop-color="#e0a173"/></linearGradient>
  </defs>
  <rect width="880" height="460" rx="18" fill="#ffffff"/>
  <text x="32" y="46" font-size="25" font-weight="800" fill="#1a2a3a">죽상경화 진행 4단계 — 혈관이 막히기까지</text>
  <line x1="32" y1="60" x2="848" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(120,210)"><circle r="95" fill="url(#wall)" stroke="#c98248" stroke-width="3"/><circle r="62" fill="url(#lumen)" stroke="#d98a90" stroke-width="2"/><text x="0" y="6" font-size="15" fill="#b23039" font-weight="700" text-anchor="middle">정상 혈류</text><text x="0" y="135" font-size="18" font-weight="800" fill="#1a2a3a" text-anchor="middle">① 정상</text><text x="0" y="160" font-size="13.5" fill="#5b6876" text-anchor="middle">내강이 넓게 열림</text></g>
  <g transform="translate(345,210)"><circle r="95" fill="url(#wall)" stroke="#c98248" stroke-width="3"/><circle r="62" fill="url(#lumen)" stroke="#d98a90" stroke-width="2"/><path d="M-62 0 A62 62 0 0 1 40 -47 C8 -18 8 18 40 47 A62 62 0 0 1 -62 0 Z" fill="#ffd54a" stroke="#d9a200" stroke-width="2"/><text x="-6" y="6" font-size="13" fill="#7a5b00" font-weight="700" text-anchor="middle">플라크</text><text x="0" y="135" font-size="18" font-weight="800" fill="#1a2a3a" text-anchor="middle">② 플라크 축적</text><text x="0" y="160" font-size="13.5" fill="#5b6876" text-anchor="middle">콜레스테롤 쌓여 좁아짐</text></g>
  <g transform="translate(570,210)"><circle r="95" fill="url(#wall)" stroke="#c98248" stroke-width="3"/><circle r="62" fill="url(#lumen)" stroke="#d98a90" stroke-width="2"/><path d="M-62 0 A62 62 0 0 1 40 -47 C8 -18 8 18 40 47 A62 62 0 0 1 -62 0 Z" fill="#ffd54a" stroke="#d9a200" stroke-width="2"/><path d="M-2 -40 L-18 -8 L2 2 L-14 38" fill="none" stroke="#b23039" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/><text x="-6" y="-52" font-size="13" fill="#b23039" font-weight="800" text-anchor="middle">파열!</text><text x="0" y="135" font-size="18" font-weight="800" fill="#1a2a3a" text-anchor="middle">③ 플라크 파열</text><text x="0" y="160" font-size="13.5" fill="#5b6876" text-anchor="middle">표면 터지며 혈액 노출</text></g>
  <g transform="translate(795,210)"><circle r="95" fill="url(#wall)" stroke="#c98248" stroke-width="3"/><circle r="62" fill="url(#lumen)" stroke="#d98a90" stroke-width="2"/><path d="M-62 0 A62 62 0 0 1 40 -47 C8 -18 8 18 40 47 A62 62 0 0 1 -62 0 Z" fill="#ffd54a" stroke="#d9a200" stroke-width="2"/><circle cx="-8" cy="0" r="34" fill="#6b2d34"/><circle cx="-22" cy="-12" r="9" fill="#8d3a43"/><circle cx="6" cy="10" r="8" fill="#8d3a43"/><text x="-8" y="5" font-size="12" fill="#ffd7da" font-weight="700" text-anchor="middle">혈전</text><text x="0" y="135" font-size="18" font-weight="800" fill="#b23039" text-anchor="middle">④ 혈전 폐색</text><text x="0" y="160" font-size="13.5" fill="#5b6876" text-anchor="middle">완전 막힘 → 심근경색</text></g>
  <g fill="#9aa7b5"><path d="M222 200 l24 0 l0 -7 l16 12 l-16 12 l0 -7 l-24 0 Z"/><path d="M447 200 l24 0 l0 -7 l16 12 l-16 12 l0 -7 l-24 0 Z"/><path d="M672 200 l24 0 l0 -7 l16 12 l-16 12 l0 -7 l-24 0 Z"/></g>
  <text x="440" y="410" font-size="14" fill="#8b98a8" text-anchor="middle">※ "수도관에 녹이 쌓이다 → 터지고 → 막힌다"  ·  DAPT는 ③④단계(혈전 형성)를 차단</text>
</svg>'''

SVG["occlusion_partial_full"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 420" font-family="''' + FONT + '''">
  <rect width="820" height="420" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">부분 폐색(NSTEMI) vs 완전 폐색(STEMI)</text>
  <line x1="32" y1="60" x2="788" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <!-- 부분 폐색 -->
  <g transform="translate(0,40)">
    <rect x="60" y="70" width="700" height="64" rx="32" fill="#f7d8c0" stroke="#d9a276" stroke-width="3"/>
    <rect x="70" y="84" width="680" height="36" rx="18" fill="#ffd9dc"/>
    <path d="M360 84 q60 18 0 36 q-60 -18 0 -36 Z" fill="#6b2d34"/>
    <path d="M120 102 H330" stroke="#c0392b" stroke-width="6" stroke-linecap="round" marker-end="url(#a1)"/>
    <text x="70" y="56" font-size="18" font-weight="800" fill="#c2611a">NSTEMI · 부분 폐색</text>
    <text x="420" y="100" font-size="14" fill="#b23039" font-weight="700">혈전이 내강 일부만</text>
    <text x="420" y="120" font-size="13.5" fill="#5b6876">→ ST 하강·T역전 / Troponin↑</text>
  </g>
  <!-- 완전 폐색 -->
  <g transform="translate(0,210)">
    <rect x="60" y="70" width="700" height="64" rx="32" fill="#f7d8c0" stroke="#d9a276" stroke-width="3"/>
    <rect x="70" y="84" width="680" height="36" rx="18" fill="#ffd9dc"/>
    <ellipse cx="380" cy="102" rx="48" ry="20" fill="#6b2d34"/>
    <path d="M120 102 H300" stroke="#c0392b" stroke-width="6" stroke-linecap="round"/>
    <text x="500" y="98" font-size="22" fill="#b23039" font-weight="800">✕ 막힘</text>
    <text x="70" y="56" font-size="18" font-weight="800" fill="#b23039">STEMI · 완전 폐색</text>
    <text x="430" y="122" font-size="13.5" fill="#5b6876">→ ST 상승 / D2B 90분 PCI</text>
  </g>
  <text x="32" y="404" font-size="13.5" fill="#8b98a8">※ 둘 다 Troponin↑(괴사 동반). 차이는 폐색 정도와 ECG·긴급도.</text>
</svg>'''

SVG["plaque_stable_unstable"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 430" font-family="''' + FONT + '''">
  <defs><radialGradient id="lm2" cx="0.5" cy="0.4" r="0.6"><stop offset="0" stop-color="#ffe1e3"/><stop offset="1" stop-color="#f2b8bc"/></radialGradient></defs>
  <rect width="820" height="430" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">안정형 vs 불안정형 플라크 — 막의 두께가 운명</text>
  <line x1="32" y1="60" x2="788" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(215,235)">
    <circle r="105" fill="#f5c9a0" stroke="#c98248" stroke-width="3"/><circle r="70" fill="url(#lm2)"/>
    <path d="M-70 0 A70 70 0 0 1 50 -50 C30 -20 30 20 50 50 A70 70 0 0 1 -70 0 Z" fill="#ffe08a"/>
    <path d="M-70 0 A70 70 0 0 1 50 -50" fill="none" stroke="#2e9d4f" stroke-width="9"/>
    <text x="-8" y="0" font-size="13" fill="#7a5b00" font-weight="700" text-anchor="middle">지질핵(작음)</text>
    <text x="0" y="150" font-size="18" font-weight="800" fill="#1d6b36" text-anchor="middle">안정형 협심증</text>
    <text x="0" y="174" font-size="13.5" fill="#5b6876" text-anchor="middle">두꺼운 섬유막 → 잘 안 터짐</text>
  </g>
  <g transform="translate(605,235)">
    <circle r="105" fill="#f5c9a0" stroke="#c98248" stroke-width="3"/><circle r="70" fill="url(#lm2)"/>
    <path d="M-70 0 A70 70 0 0 1 50 -50 C20 -10 20 10 50 50 A70 70 0 0 1 -70 0 Z" fill="#ffcf4d"/>
    <path d="M-70 0 A70 70 0 0 1 50 -50" fill="none" stroke="#e08a00" stroke-width="3" stroke-dasharray="6 5"/>
    <path d="M2 -48 l-14 26 l16 10 l-12 30" fill="none" stroke="#b23039" stroke-width="4" stroke-linecap="round"/>
    <text x="-8" y="6" font-size="13" fill="#7a5b00" font-weight="700" text-anchor="middle">지질핵(큼)</text>
    <text x="0" y="150" font-size="18" font-weight="800" fill="#b23039" text-anchor="middle">불안정형(UA)</text>
    <text x="0" y="174" font-size="13.5" fill="#5b6876" text-anchor="middle">얇은 막 → 파열 임박</text>
  </g>
  <text x="32" y="414" font-size="13.5" fill="#8b98a8">※ UA = 안정시 흉통·악화 패턴, Troponin 정상. 곧 NSTEMI/STEMI로 갈 수 있는 경고.</text>
</svg>'''

SVG["pulmonary_edema"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 440" font-family="''' + FONT + '''">
  <rect width="820" height="440" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">심인성 폐부종 — 좌심실이 못 짜내면</text>
  <line x1="32" y1="60" x2="788" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <!-- 흐름 박스 -->
  <g font-size="14.5" font-weight="700" fill="#1a2a3a">
    <rect x="40" y="86" width="150" height="58" rx="10" fill="#ffe7e9" stroke="#b23039" stroke-width="2"/>
    <text x="115" y="110" text-anchor="middle">좌심실 펌프</text><text x="115" y="130" text-anchor="middle" fill="#b23039">기능 저하</text>
    <rect x="230" y="86" width="160" height="58" rx="10" fill="#fff1e0" stroke="#e08a00" stroke-width="2"/>
    <text x="310" y="110" text-anchor="middle">좌심방·폐정맥</text><text x="310" y="130" text-anchor="middle" fill="#c2611a">압력 상승</text>
    <rect x="430" y="86" width="170" height="58" rx="10" fill="#eaf3fd" stroke="#1f7ae0" stroke-width="2"/>
    <text x="515" y="110" text-anchor="middle">폐모세혈관에서</text><text x="515" y="130" text-anchor="middle" fill="#1559a8">체액 누출</text>
    <rect x="640" y="86" width="150" height="58" rx="10" fill="#e9f7ee" stroke="#2e9d4f" stroke-width="2"/>
    <text x="715" y="110" text-anchor="middle">폐포에 물</text><text x="715" y="130" text-anchor="middle" fill="#1d6b36">가스교환 장애</text>
  </g>
  <g fill="#9aa7b5"><path d="M192 115 l30 0 l0 -7 l16 12 l-16 12 l0 -7 l-30 0 Z"/><path d="M392 115 l30 0 l0 -7 l16 12 l-16 12 l0 -7 l-30 0 Z"/><path d="M602 115 l30 0 l0 -7 l16 12 l-16 12 l0 -7 l-30 0 Z"/></g>
  <!-- 폐포 단면 -->
  <g transform="translate(250,290)">
    <circle r="110" fill="#fde9ec" stroke="#e0a9b0" stroke-width="3"/>
    <circle r="70" fill="#cfe6ff" stroke="#1f7ae0" stroke-width="2"/>
    <text x="0" y="-30" font-size="14" fill="#1559a8" text-anchor="middle" font-weight="700">폐포(공기)</text>
    <g fill="#1f7ae0"><circle cx="-20" cy="20" r="7"/><circle cx="10" cy="40" r="6"/><circle cx="30" cy="5" r="5"/><circle cx="-35" cy="-10" r="5"/></g>
    <text x="0" y="70" font-size="13" fill="#1559a8" text-anchor="middle">체액 차오름</text>
    <path d="M95 0 A95 95 0 0 0 70 -64" fill="none" stroke="#b23039" stroke-width="10" stroke-linecap="round"/>
    <text x="118" y="-30" font-size="13.5" fill="#b23039" font-weight="700">모세혈관</text>
  </g>
  <g font-size="15" fill="#3a4654">
    <text x="430" y="250" font-weight="800" fill="#b23039">왜 이런 증상?</text>
    <text x="430" y="280">• 기좌호흡: 누우면 정맥환류↑ → 폐울혈 악화</text>
    <text x="430" y="306">• 분홍빛 거품 가래: 폐포 누출액 + 공기</text>
    <text x="430" y="332">• 양폐 수포음(crackle): 폐포 내 액체</text>
    <text x="430" y="358" fill="#1559a8" font-weight="700">→ 앉히고 산소·NIV / LMNOP(이뇨·혈관확장)</text>
  </g>
</svg>'''

SVG["left_right_hf"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 420" font-family="''' + FONT + '''">
  <rect width="820" height="420" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">좌심부전 vs 우심부전 — 막힌 쪽 '뒤'로 정체된다</text>
  <line x1="32" y1="60" x2="788" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(210,250)">
    <ellipse cx="0" cy="-70" rx="80" ry="55" fill="#cfe6ff" stroke="#1f7ae0" stroke-width="2.5"/>
    <text x="0" y="-66" font-size="15" fill="#1559a8" text-anchor="middle" font-weight="800">폐 울혈</text>
    <path d="M0 -16 C-40 -16 -50 30 0 60 C50 30 40 -16 0 -16 Z" fill="#e9656b" stroke="#b23039" stroke-width="2.5"/>
    <text x="0" y="100" font-size="18" font-weight="800" fill="#1559a8" text-anchor="middle">좌심부전</text>
    <text x="0" y="126" font-size="13.5" fill="#5b6876" text-anchor="middle">호흡곤란·기좌호흡</text>
    <text x="0" y="146" font-size="13.5" fill="#5b6876" text-anchor="middle">수포음·분홍거품가래</text>
  </g>
  <line x1="410" y1="90" x2="410" y2="380" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(610,250)">
    <path d="M0 -16 C-40 -16 -50 30 0 60 C50 30 40 -16 0 -16 Z" fill="#e9656b" stroke="#b23039" stroke-width="2.5"/>
    <g stroke="#2e9d4f" stroke-width="6" stroke-linecap="round"><line x1="-70" y1="-60" x2="-70" y2="0"/><line x1="70" y1="-60" x2="70" y2="0"/></g>
    <text x="0" y="-50" font-size="15" fill="#1d6b36" text-anchor="middle" font-weight="800">전신 정맥 울혈</text>
    <text x="0" y="100" font-size="18" font-weight="800" fill="#1d6b36" text-anchor="middle">우심부전</text>
    <text x="0" y="126" font-size="13.5" fill="#5b6876" text-anchor="middle">경정맥 팽대·하지부종</text>
    <text x="0" y="146" font-size="13.5" fill="#5b6876" text-anchor="middle">간비대·복수</text>
  </g>
  <text x="32" y="404" font-size="13.5" fill="#8b98a8">※ 좌심 뒤 = 폐, 우심 뒤 = 전신정맥. 급성 비대상성은 주로 좌심부전→폐부종.</text>
</svg>'''

SVG["atrial_thrombus"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 430" font-family="''' + FONT + '''">
  <rect width="820" height="430" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">심방세동의 진짜 위험 — 좌심방 혈전 → 색전</text>
  <line x1="32" y1="60" x2="788" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(250,250)">
    <path d="M0 -70 C-90 -70 -110 40 0 110 C110 40 90 -70 0 -70 Z" fill="#e9656b" stroke="#b23039" stroke-width="3"/>
    <ellipse cx="-35" cy="-40" rx="42" ry="30" fill="#c0454c" stroke="#8d242c" stroke-width="2"/>
    <text x="-35" y="-36" font-size="12.5" fill="#fff" text-anchor="middle" font-weight="700">좌심방</text>
    <!-- 좌심방이 + 혈전 -->
    <path d="M-72 -48 q-26 -6 -30 14 q22 8 34 -2 Z" fill="#7a2f37" stroke="#5b2228" stroke-width="2"/>
    <circle cx="-92" cy="-40" r="9" fill="#3a1418"/>
    <text x="-118" y="-58" font-size="12.5" fill="#b23039" font-weight="700">좌심방이</text>
    <text x="-118" y="-42" font-size="12.5" fill="#b23039" font-weight="700">혈전</text>
  </g>
  <!-- 화살표 → 뇌 -->
  <path d="M430 170 C520 130 590 120 640 130" fill="none" stroke="#c0392b" stroke-width="5" stroke-dasharray="2 0" marker-end=""/>
  <path d="M636 128 l-20 -8 l6 9 l-7 9 Z" fill="#c0392b"/>
  <g transform="translate(690,150)">
    <path d="M0 0 C-34 -30 14 -64 30 -34 C54 -52 78 -16 50 6 C58 30 20 40 8 22 C-12 30 -22 12 0 0 Z" fill="#f1c0c4" stroke="#b23039" stroke-width="2.5"/>
    <circle cx="22" cy="-12" r="8" fill="#3a1418"/>
    <text x="24" y="46" font-size="15" fill="#b23039" text-anchor="middle" font-weight="800">뇌색전</text>
  </g>
  <g font-size="15" fill="#3a4654">
    <text x="60" y="350" font-weight="800" fill="#b23039">왜?</text>
    <text x="60" y="378">수축 못 하는 심방(특히 좌심방이)에 피가 고임 → 혈전 → 떨어져 나가 뇌·전신 색전</text>
    <text x="60" y="404" fill="#1559a8" font-weight="700">→ CHA₂DS₂-VASc로 항응고 · AF&gt;48h는 항응고 후 율동전환</text>
  </g>
</svg>'''

SVG["conduction_system"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 470" font-family="''' + FONT + '''">
  <rect width="760" height="470" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">심장 전도계 — 3도 차단은 'AV에서 끊김'</text>
  <line x1="32" y1="60" x2="728" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(300,260)">
    <path d="M0 -120 C-150 -120 -175 70 0 175 C175 70 150 -120 0 -120 Z" fill="#f3b5ba" stroke="#b23039" stroke-width="3"/>
    <line x1="0" y1="-110" x2="0" y2="120" stroke="#d98a90" stroke-width="2"/>
    <!-- SA node -->
    <circle cx="48" cy="-78" r="11" fill="#f2a900" stroke="#9a6b00" stroke-width="2"/>
    <text x="66" y="-82" font-size="13.5" font-weight="700" fill="#9a6b00">SA결절 (박동원)</text>
    <!-- AV node -->
    <circle cx="6" cy="6" r="12" fill="#1f7ae0" stroke="#1559a8" stroke-width="2"/>
    <text x="24" y="2" font-size="13.5" font-weight="700" fill="#1559a8">AV결절</text>
    <!-- His-Purkinje -->
    <path d="M6 18 C6 50 -40 80 -70 120" fill="none" stroke="#2e9d4f" stroke-width="5"/>
    <path d="M6 18 C6 50 50 80 80 120" fill="none" stroke="#2e9d4f" stroke-width="5"/>
    <path d="M6 18 L6 70" stroke="#2e9d4f" stroke-width="5"/>
    <text x="-150" y="135" font-size="13" fill="#1d6b36" font-weight="700">His속·각·Purkinje</text>
    <!-- 차단 표시 -->
    <line x1="-30" y1="30" x2="42" y2="-18" stroke="#ef4444" stroke-width="5"/>
    <text x="40" y="40" font-size="15" fill="#b23039" font-weight="800">⛔ 차단</text>
  </g>
  <g font-size="14.5" fill="#3a4654">
    <text x="500" y="150" font-weight="800" fill="#b23039">3도(완전) 차단</text>
    <text x="500" y="180">심방→심실 전달이 완전 차단</text>
    <text x="500" y="206">→ 심실은 느린 '이탈박동'에 의존</text>
    <text x="500" y="240" font-weight="700" fill="#1559a8">접합부 이탈: 좁은 QRS 40~60</text>
    <text x="500" y="266" font-weight="700" fill="#b23039">심실 이탈: 넓은 QRS 20~40(위험)</text>
    <text x="500" y="300">Atropine 무효 많음 → 경피 페이싱</text>
  </g>
</svg>'''

SVG["tamponade"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" font-family="''' + FONT + '''">
  <rect width="800" height="450" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">심낭압전 — 물주머니가 심장을 누른다</text>
  <line x1="32" y1="60" x2="768" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(250,265)">
    <ellipse cx="0" cy="0" rx="160" ry="150" fill="#cfe6ff" stroke="#1f7ae0" stroke-width="3"/>
    <text x="0" y="-118" font-size="14" fill="#1559a8" text-anchor="middle" font-weight="800">심낭 삼출액</text>
    <path d="M0 -70 C-70 -70 -82 40 0 90 C82 40 70 -70 0 -70 Z" fill="#e9656b" stroke="#b23039" stroke-width="3"/>
    <path d="M-10 -40 C-26 -40 -30 0 -10 22 C-2 4 -2 -22 -10 -40 Z" fill="#a83139"/>
    <text x="0" y="20" font-size="12.5" fill="#fff" text-anchor="middle" font-weight="700">눌린 심장</text>
    <g stroke="#1f7ae0" stroke-width="2" fill="none"><path d="M-150 -20 A150 150 0 0 1 -120 -90"/><path d="M150 20 A150 150 0 0 1 120 90"/></g>
  </g>
  <g font-size="15" fill="#3a4654">
    <text x="470" y="130" font-size="17" font-weight="800" fill="#b23039">Beck 3징</text>
    <text x="470" y="162">① 저혈압 (충만 안 됨)</text>
    <text x="470" y="190">② 경정맥 팽대 (정맥 울혈)</text>
    <text x="470" y="218">③ 심음 감약 (액체가 막음)</text>
    <text x="470" y="256" font-weight="700" fill="#c2611a">+ 기이맥(흡기 시 SBP&gt;10↓)</text>
    <text x="470" y="298" font-weight="800" fill="#b23039">→ 즉시 심낭천자</text>
    <text x="470" y="326" fill="#5b6876">이뇨·혈관확장 금기(전부하 의존)</text>
    <text x="470" y="352" fill="#5b6876">천자 전까지 수액으로 충만 보조</text>
  </g>
</svg>'''

SVG["aortic_dissection"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 440" font-family="''' + FONT + '''">
  <rect width="820" height="440" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">대동맥 박리 — 내막이 찢어져 '가성내강' 생성</text>
  <line x1="32" y1="60" x2="788" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <!-- 대동맥 종단면 -->
  <g transform="translate(60,90)">
    <path d="M40 300 C40 120 120 40 250 40 C360 40 420 110 470 200" fill="none" stroke="#e0a9b0" stroke-width="56" stroke-linecap="round"/>
    <path d="M40 300 C40 120 120 40 250 40 C360 40 420 110 470 200" fill="none" stroke="#ffd9dc" stroke-width="40" stroke-linecap="round"/>
    <!-- 박리 피판 -->
    <path d="M150 70 C200 110 210 170 205 250" fill="none" stroke="#b23039" stroke-width="3" stroke-dasharray="7 5"/>
    <ellipse cx="178" cy="150" rx="16" ry="60" fill="#8d242c" opacity="0.6"/>
    <text x="120" y="120" font-size="13.5" fill="#b23039" font-weight="800">내막 파열구</text>
    <path d="M118 128 L150 95" stroke="#b23039" stroke-width="2"/>
    <text x="220" y="160" font-size="13" fill="#7a2f37" font-weight="700">가성내강</text>
    <text x="60" y="270" font-size="13" fill="#1559a8" font-weight="700">진성내강</text>
  </g>
  <g font-size="14.5" fill="#3a4654">
    <text x="560" y="120" font-size="16" font-weight="800" fill="#b23039">Stanford 분류</text>
    <rect x="560" y="135" width="220" height="70" rx="10" fill="#fdeced" stroke="#ef4444" stroke-width="1.6"/>
    <text x="574" y="162" font-weight="800" fill="#b23039">A형 — 상행 침범</text>
    <text x="574" y="186" fill="#5b6876">압전·MI·판막부전 위험 → 응급수술</text>
    <rect x="560" y="220" width="220" height="64" rx="10" fill="#eef4fd" stroke="#1f7ae0" stroke-width="1.6"/>
    <text x="574" y="246" font-weight="800" fill="#1559a8">B형 — 하행만</text>
    <text x="574" y="270" fill="#5b6876">대개 약물치료(β차단 먼저)</text>
    <text x="560" y="330" font-weight="700" fill="#c2611a">β차단으로 SBP100~120·HR&lt;60 먼저</text>
    <text x="560" y="356" fill="#8b98a8">혈관확장만 단독 금지(반사빈맥→악화)</text>
  </g>
</svg>'''

SVG["dissection_signs"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 410" font-family="''' + FONT + '''">
  <rect width="800" height="410" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">박리의 침상 단서 — 양팔 혈압차 · 종격동 확대</text>
  <line x1="32" y1="60" x2="768" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <!-- 사람 + 양팔 혈압 -->
  <g transform="translate(190,250)">
    <circle cx="0" cy="-110" r="34" fill="#f1c0c4" stroke="#b23039" stroke-width="2.5"/>
    <path d="M-55 30 C-55 -55 55 -55 55 30 Z" fill="#f3b5ba" stroke="#b23039" stroke-width="2.5"/>
    <rect x="-130" y="-40" width="56" height="34" rx="6" fill="#eaf3fd" stroke="#1f7ae0" stroke-width="2"/>
    <text x="-102" y="-17" font-size="15" fill="#1559a8" text-anchor="middle" font-weight="800">142</text>
    <rect x="74" y="-40" width="56" height="34" rx="6" fill="#fdeced" stroke="#ef4444" stroke-width="2"/>
    <text x="102" y="-17" font-size="15" fill="#b23039" text-anchor="middle" font-weight="800">98</text>
    <line x1="-55" y1="-20" x2="-130" y2="-23" stroke="#9aa7b5" stroke-width="3"/>
    <line x1="55" y1="-20" x2="130" y2="-23" stroke="#9aa7b5" stroke-width="3"/>
    <text x="0" y="80" font-size="15" fill="#b23039" text-anchor="middle" font-weight="800">양팔 SBP 차이 ↑</text>
  </g>
  <!-- 흉부 X선 종격동 확대 -->
  <g transform="translate(530,210)">
    <rect x="-110" y="-110" width="220" height="220" rx="10" fill="#0d1117" stroke="#2a3441" stroke-width="2"/>
    <path d="M-30 -90 C-70 -40 -70 60 -40 95 L40 95 C70 60 70 -40 30 -90 Z" fill="#3a4654" opacity="0.7"/>
    <ellipse cx="0" cy="-50" rx="60" ry="40" fill="#7b8a9a" opacity="0.85"/>
    <text x="0" y="-46" font-size="12.5" fill="#fff" text-anchor="middle" font-weight="700">종격동 확대</text>
    <text x="0" y="135" font-size="14" fill="#5b6876" text-anchor="middle">흉부 X선</text>
  </g>
  <text x="32" y="392" font-size="13.5" fill="#8b98a8">※ 찢어지는 흉통/등통 + 양팔 혈압차 → 대동맥 박리 강력 의심. 확진은 CT 혈관조영.</text>
</svg>'''

# ════════════════════════════════════════════════════════════════
# 흐름도 · 그래프
# ════════════════════════════════════════════════════════════════
SVG["htn_urg_emerg"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 430" font-family="''' + FONT + '''">
  <rect width="820" height="430" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">고혈압 위기 — 핵심은 '표적장기손상' 유무</text>
  <line x1="32" y1="60" x2="788" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <rect x="300" y="80" width="220" height="48" rx="24" fill="#fff4ec" stroke="#ff7a00" stroke-width="2"/>
  <text x="410" y="110" font-size="16" font-weight="800" fill="#b23039" text-anchor="middle">SBP&gt;180 / DBP&gt;120</text>
  <path d="M380 128 L250 160" stroke="#9aa7b5" stroke-width="2"/><path d="M440 128 L570 160" stroke="#9aa7b5" stroke-width="2"/>
  <!-- Urgency -->
  <g>
    <rect x="50" y="160" width="330" height="230" rx="14" fill="#eef7f0" stroke="#2e9d4f" stroke-width="2"/>
    <text x="70" y="190" font-size="18" font-weight="800" fill="#1d6b36">Urgency (긴급)</text>
    <text x="70" y="218" font-size="15" fill="#3a4654">표적장기손상 <tspan font-weight="800">없음</tspan></text>
    <text x="70" y="250" font-size="14.5" fill="#3a4654">→ 경구약·외래</text>
    <text x="70" y="276" font-size="14.5" fill="#3a4654">→ 수 시간~일 단위로 천천히</text>
    <text x="70" y="316" font-size="14" fill="#b23039" font-weight="700">급강압이 오히려 위험!</text>
  </g>
  <!-- Emergency -->
  <g>
    <rect x="440" y="160" width="330" height="230" rx="14" fill="#fdeced" stroke="#ef4444" stroke-width="2"/>
    <text x="460" y="190" font-size="18" font-weight="800" fill="#b23039">Emergency (응급)</text>
    <text x="460" y="218" font-size="15" fill="#3a4654">표적장기손상 <tspan font-weight="800" fill="#b23039">있음</tspan></text>
    <text x="460" y="246" font-size="14" fill="#5b6876">뇌(뇌증·뇌졸중)·심장(ACS·폐부종)</text>
    <text x="460" y="270" font-size="14" fill="#5b6876">신장·대동맥(박리)·눈(망막)</text>
    <text x="460" y="304" font-size="14.5" fill="#3a4654">→ IV 강압제, 즉시</text>
    <text x="460" y="332" font-size="14" fill="#c2611a" font-weight="700">단, 첫 1시간 MAP 25%만 ↓</text>
  </g>
</svg>'''

SVG["map_target"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 420" font-family="''' + FONT + '''">
  <rect width="800" height="420" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">강압 목표 — 첫 1시간 MAP 25%만 낮춘다</text>
  <line x1="32" y1="60" x2="768" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <!-- 축 -->
  <line x1="90" y1="100" x2="90" y2="330" stroke="#9aa7b5" stroke-width="2"/>
  <line x1="90" y1="330" x2="740" y2="330" stroke="#9aa7b5" stroke-width="2"/>
  <text x="50" y="110" font-size="13" fill="#5b6876">MAP</text>
  <text x="700" y="355" font-size="13" fill="#5b6876">시간</text>
  <!-- 위험대 (급강압 금지 영역) -->
  <rect x="90" y="300" width="650" height="30" fill="#fdeced"/>
  <text x="110" y="320" font-size="12.5" fill="#b23039">과도한 급강압 = 분수령 허혈(금지)</text>
  <!-- 곡선 -->
  <polyline fill="none" stroke="#1f7ae0" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"
    points="120,120 250,200 450,250 690,280"/>
  <circle cx="120" cy="120" r="6" fill="#b23039"/><circle cx="250" cy="200" r="6" fill="#ff7a00"/>
  <circle cx="450" cy="250" r="6" fill="#2e9d4f"/><circle cx="690" cy="280" r="6" fill="#2e9d4f"/>
  <g font-size="13.5" fill="#3a4654">
    <text x="120" y="108" text-anchor="middle" font-weight="700" fill="#b23039">시작</text>
    <text x="250" y="188" text-anchor="middle" font-weight="700" fill="#c2611a">1h: 약 25%↓</text>
    <text x="450" y="238" text-anchor="middle" font-weight="700" fill="#1d6b36">2~6h: 160/100</text>
    <text x="690" y="268" text-anchor="middle" font-weight="700" fill="#1d6b36">24~48h: 정상화</text>
  </g>
  <text x="90" y="392" font-size="13.5" fill="#8b98a8">※ 뇌·신장 자동조절이 고혈압에 적응돼 있어 급강압 시 허혈. 단계적 강압이 안전.</text>
</svg>'''

SVG["cpr_chain"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 860 380" font-family="''' + FONT + '''">
  <rect width="860" height="380" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">제세동 가능 리듬(VF/무맥성VT) 대응</text>
  <line x1="32" y1="60" x2="828" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g font-size="15" font-weight="700">
    <rect x="40" y="100" width="170" height="80" rx="12" fill="#fdeced" stroke="#ef4444" stroke-width="2"/>
    <text x="125" y="135" text-anchor="middle" fill="#b23039">① 즉시 제세동</text>
    <text x="125" y="160" text-anchor="middle" font-size="13" fill="#5b6876">(비동기)</text>
    <rect x="250" y="100" width="170" height="80" rx="12" fill="#fff4ec" stroke="#ff7a00" stroke-width="2"/>
    <text x="335" y="135" text-anchor="middle" fill="#c2611a">② CPR 2분</text>
    <text x="335" y="160" text-anchor="middle" font-size="13" fill="#5b6876">고품질 가슴압박</text>
    <rect x="460" y="100" width="170" height="80" rx="12" fill="#eef4fd" stroke="#1f7ae0" stroke-width="2"/>
    <text x="545" y="135" text-anchor="middle" fill="#1559a8">③ 리듬 확인</text>
    <text x="545" y="160" text-anchor="middle" font-size="13" fill="#5b6876">→ 반복</text>
    <rect x="670" y="100" width="150" height="80" rx="12" fill="#eef7f0" stroke="#2e9d4f" stroke-width="2"/>
    <text x="745" y="135" text-anchor="middle" fill="#1d6b36">④ 약물</text>
    <text x="745" y="160" text-anchor="middle" font-size="12.5" fill="#5b6876">Epi · Amiodarone</text>
  </g>
  <g fill="#9aa7b5"><path d="M210 140 l24 0 l0 -7 l16 12 l-16 12 l0 -7 l-24 0 Z"/><path d="M420 140 l24 0 l0 -7 l16 12 l-16 12 l0 -7 l-24 0 Z"/><path d="M630 140 l24 0 l0 -7 l16 12 l-16 12 l0 -7 l-24 0 Z"/></g>
  <rect x="40" y="220" width="780" height="120" rx="12" fill="#f7f9fc" stroke="#dde5ee" stroke-width="1.6"/>
  <text x="60" y="252" font-size="16" font-weight="800" fill="#b23039">핵심</text>
  <text x="60" y="282" font-size="15" fill="#3a4654">• 끊김 없는 고품질 가슴압박(속도·깊이·완전 이완)이 생존을 결정</text>
  <text x="60" y="310" font-size="15" fill="#3a4654">• 가역 원인(H&amp;T): 저산소·저혈량·저/고칼륨·저체온·산증 / 긴장성기흉·압전·혈전·독소</text>
  <text x="60" y="332" font-size="13.5" fill="#8b98a8">무맥성 VT는 VF와 동일하게 대응 — 빠른 제세동이 핵심</text>
</svg>'''

SVG["vt_algorithm"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 440" font-family="''' + FONT + '''">
  <rect width="840" height="440" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">넓은 QRS 빈맥(VT) — 맥박·안정성으로 갈린다</text>
  <line x1="32" y1="60" x2="808" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <rect x="320" y="80" width="200" height="48" rx="24" fill="#1a2a3a"/>
  <text x="420" y="110" font-size="16" font-weight="800" fill="#fff" text-anchor="middle">넓은 QRS 빈맥</text>
  <!-- 3갈래 -->
  <g font-size="14.5">
    <rect x="40" y="170" width="240" height="120" rx="12" fill="#fdeced" stroke="#ef4444" stroke-width="2"/>
    <text x="160" y="198" text-anchor="middle" font-size="15" font-weight="800" fill="#b23039">맥박 없음</text>
    <text x="160" y="226" text-anchor="middle" fill="#3a4654">즉시 제세동(비동기)</text>
    <text x="160" y="250" text-anchor="middle" fill="#3a4654">+ CPR + Epi</text>
    <text x="160" y="274" text-anchor="middle" fill="#3a4654">+ Amiodarone</text>

    <rect x="300" y="170" width="240" height="120" rx="12" fill="#fff4ec" stroke="#ff7a00" stroke-width="2"/>
    <text x="420" y="198" text-anchor="middle" font-size="15" font-weight="800" fill="#c2611a">맥박O · 불안정</text>
    <text x="420" y="224" text-anchor="middle" fill="#5b6876">(저혈압·의식저하·흉통)</text>
    <text x="420" y="252" text-anchor="middle" fill="#3a4654">동기화 심율동전환</text>
    <text x="420" y="276" text-anchor="middle" fill="#8b6a4f">(synchronized)</text>

    <rect x="560" y="170" width="240" height="120" rx="12" fill="#eef7f0" stroke="#2e9d4f" stroke-width="2"/>
    <text x="680" y="198" text-anchor="middle" font-size="15" font-weight="800" fill="#1d6b36">맥박O · 안정</text>
    <text x="680" y="226" text-anchor="middle" fill="#3a4654">Amiodarone IV</text>
    <text x="680" y="250" text-anchor="middle" fill="#3a4654">(또는 Procainamide)</text>
    <text x="680" y="274" text-anchor="middle" fill="#3a4654">+ 원인 교정</text>
  </g>
  <g stroke="#9aa7b5" stroke-width="2" fill="none"><path d="M380 128 L160 170"/><path d="M420 128 L420 170"/><path d="M460 128 L680 170"/></g>
  <rect x="40" y="320" width="760" height="92" rx="12" fill="#f3eaff" stroke="#8e24aa" stroke-width="1.8"/>
  <text x="60" y="350" font-size="15" font-weight="800" fill="#6a1b9a">다형성 / Torsades</text>
  <text x="60" y="378" font-size="14.5" fill="#3a4654">MgSO₄ IV · QT 연장 유발약 중단 · K 교정 · 무맥이면 비동기 제세동</text>
  <text x="60" y="400" font-size="13.5" fill="#8b98a8">넓은 QRS 빈맥은 애매하면 VT로 간주하는 게 안전</text>
</svg>'''

# ════════════════════════════════════════════════════════════════
# 범용 도해 엔진 헬퍼 (흐름도 / 다단 패널 / 핵심 패널)
# ════════════════════════════════════════════════════════════════
def _e(s): return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
_PAL=[("#eef4fd","#1f7ae0","#1559a8"),("#fff1e0","#e08a00","#c2611a"),
      ("#fdeced","#ef4444","#b23039"),("#eef7f0","#2e9d4f","#1d6b36"),
      ("#f3eaff","#8e24aa","#6a1b9a")]

def _flow(title, steps, footer="", accent="#b23039"):
    n=len(steps); bw=200 if n<=4 else 168; gap=46 if n<=4 else 26
    total=n*bw+(n-1)*gap; W=max(880,total+100); x0=(W-total)//2
    H=430; by=176; bh=126
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">',
       f'<rect width="{W}" height="{H}" rx="18" fill="#fff"/>',
       f'<text x="34" y="48" font-size="25" font-weight="800" fill="#1a2a3a">{_e(title)}</text>',
       f'<line x1="34" y1="64" x2="{W-34}" y2="64" stroke="#e3e8ee" stroke-width="2"/>']
    for i,st in enumerate(steps):
        a=st[0]; b=st[1] if len(st)>1 else ""
        fx=x0+i*(bw+gap); fill,brd,tc=_PAL[i%5]; cx=fx+bw//2
        s.append(f'<rect x="{fx}" y="{by}" width="{bw}" height="{bh}" rx="13" fill="{fill}" stroke="{brd}" stroke-width="2"/>')
        if b:
            s.append(f'<text x="{cx}" y="{by+54}" font-size="15.5" font-weight="800" fill="{tc}" text-anchor="middle">{_e(a)}</text>')
            s.append(f'<text x="{cx}" y="{by+82}" font-size="13.5" fill="#3a4654" text-anchor="middle">{_e(b)}</text>')
        else:
            s.append(f'<text x="{cx}" y="{by+70}" font-size="15.5" font-weight="800" fill="{tc}" text-anchor="middle">{_e(a)}</text>')
        if i<n-1:
            ax=fx+bw; ay=by+bh//2
            s.append(f'<path d="M{ax+6} {ay} l{gap-22} 0 l0 -7 l14 12 l-14 12 l0 -7 l-{gap-22} 0 Z" fill="#9aa7b5"/>')
    if footer:
        s.append(f'<rect x="34" y="322" width="{W-68}" height="86" rx="11" fill="#fff7ef" stroke="{accent}" stroke-width="1.6"/>')
        for i,ln in enumerate(footer.split("\n")):
            s.append(f'<text x="54" y="{354+i*26}" font-size="16" font-weight="{"800" if i==0 else "500"}" fill="{accent if i==0 else "#3a4654"}">{_e(ln)}</text>')
    s.append('</svg>'); return "".join(s)

def _cols(title, panels, footer=""):
    n=len(panels); pw=320 if n<=2 else 252; gap=28
    total=n*pw+(n-1)*gap; W=max(880,total+80); x0=(W-total)//2
    H=430; py=92; ph=290
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">',
       f'<rect width="{W}" height="{H}" rx="18" fill="#fff"/>',
       f'<text x="34" y="48" font-size="25" font-weight="800" fill="#1a2a3a">{_e(title)}</text>',
       f'<line x1="34" y1="64" x2="{W-34}" y2="64" stroke="#e3e8ee" stroke-width="2"/>']
    for i,p in enumerate(panels):
        fx=x0+i*(pw+gap); fill=p.get("fill","#f7f9fc"); brd=p["c"]; tc=p.get("tc",brd)
        s.append(f'<rect x="{fx}" y="{py}" width="{pw}" height="{ph}" rx="14" fill="{fill}" stroke="{brd}" stroke-width="2"/>')
        s.append(f'<text x="{fx+18}" y="{py+34}" font-size="17.5" font-weight="800" fill="{tc}">{_e(p["t"])}</text>')
        if p.get("sub"): s.append(f'<text x="{fx+18}" y="{py+58}" font-size="13.5" fill="#5b6876">{_e(p["sub"])}</text>')
        y0=py+(82 if p.get("sub") else 64)
        for j,ln in enumerate(p["lines"]):
            s.append(f'<text x="{fx+18}" y="{y0+j*28}" font-size="14.5" fill="#3a4654">{_e(ln)}</text>')
    if footer:
        s.append(f'<text x="40" y="412" font-size="13.5" fill="#8b98a8">{_e(footer)}</text>')
    s.append('</svg>'); return "".join(s)

def _panel(title, lines, footer="", accent="#b23039", sub="", badge=""):
    W=900; H=430
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="{FONT}">',
       f'<rect width="{W}" height="{H}" rx="18" fill="#fff"/>',
       f'<text x="34" y="48" font-size="25" font-weight="800" fill="#1a2a3a">{_e(title)}</text>',
       f'<line x1="34" y1="64" x2="{W-34}" y2="64" stroke="#e3e8ee" stroke-width="2"/>',
       f'<rect x="40" y="88" width="{W-80}" height="{300 if footer else 320}" rx="14" fill="#f7f9fc" stroke="#dde5ee" stroke-width="1.6"/>']
    y=128
    if sub:
        s.append(f'<text x="62" y="{y}" font-size="16.5" font-weight="800" fill="{accent}">{_e(sub)}</text>'); y+=36
    for ln in lines:
        bold = ln.startswith("*")
        t = ln[1:] if bold else ln
        s.append(f'<text x="62" y="{y}" font-size="16" font-weight="{"800" if bold else "500"}" fill="{accent if bold else "#3a4654"}">{_e(t)}</text>')
        y+=34
    if footer:
        s.append(f'<text x="40" y="412" font-size="13.5" fill="#8b98a8">{_e(footer)}</text>')
    s.append('</svg>'); return "".join(s)

# ── 고칼륨혈증 ECG ─────────────────────────────────────────
SVG["ecg_hyperk"] = _ecg(
 "고칼륨혈증 — 첨예(텐트형) T파부터",
 _tile(235,4,70,270, st=0, tw=2.5),
 footer="진행: 첨예 T파 → PR연장·P소실 → QRS 확장 → sine wave → 심정지\n①칼슘(심장 보호)→②인슐린·포도당/β2(세포 내 이동)→③이뇨·투석(체외 제거)",
 highlight=(126,176,24,"첨예 T"))

# ════════════════════════════════════════════════════════════════
# 핵심 장기 작화 (개별)
# ════════════════════════════════════════════════════════════════
SVG["lung_pneumothorax"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 440" font-family="''' + FONT + '''">
  <rect width="840" height="440" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">기흉 — 정상 vs 긴장성(종격동 편위)</text>
  <line x1="32" y1="60" x2="808" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <!-- 정상측 흉곽 -->
  <g transform="translate(40,90)">
    <rect x="0" y="0" width="360" height="300" rx="16" fill="#f7eef0" stroke="#d9a9b0" stroke-width="2"/>
    <line x1="180" y1="14" x2="180" y2="286" stroke="#cbb3b8" stroke-width="3"/>
    <path d="M150 40 C70 60 60 200 130 270 C170 250 175 120 150 40 Z" fill="#f6b8be" stroke="#b23039" stroke-width="2.5"/>
    <path d="M210 40 C290 60 300 200 230 270 C190 250 185 120 210 40 Z" fill="#f6b8be" stroke="#b23039" stroke-width="2.5"/>
    <text x="180" y="305" font-size="15" font-weight="800" fill="#1d6b36" text-anchor="middle">정상 (양폐 팽창)</text>
  </g>
  <!-- 긴장성 -->
  <g transform="translate(440,90)">
    <rect x="0" y="0" width="360" height="300" rx="16" fill="#f7eef0" stroke="#d9a9b0" stroke-width="2"/>
    <line x1="230" y1="14" x2="230" y2="286" stroke="#cbb3b8" stroke-width="3" stroke-dasharray="6 5"/>
    <text x="252" y="150" font-size="13" fill="#b23039" font-weight="700">기관·종격동</text>
    <text x="252" y="168" font-size="13" fill="#b23039" font-weight="700">반대편 밀림</text>
    <!-- 허탈된 좌폐 -->
    <path d="M120 130 C90 150 92 210 130 240 C150 220 150 160 120 130 Z" fill="#e58c93" stroke="#b23039" stroke-width="2.5"/>
    <text x="70" y="110" font-size="13" fill="#b23039" font-weight="700">허탈된 폐</text>
    <path d="M70 100 L110 140" stroke="#b23039" stroke-width="2"/>
    <!-- 공기 영역 -->
    <text x="60" y="250" font-size="22" fill="#8b98a8">air</text>
    <!-- 우폐 눌림 -->
    <path d="M300 60 C340 90 345 210 290 260 C255 230 250 120 300 60 Z" fill="#f6b8be" stroke="#b23039" stroke-width="2.5"/>
    <text x="180" y="305" font-size="15" font-weight="800" fill="#b23039" text-anchor="middle">긴장성 (저혈압·기관편위)</text>
  </g>
  <text x="32" y="424" font-size="13.5" fill="#8b98a8">※ 편측 호흡음 소실+저혈압+기관 반대편 편위 → 영상 전 바늘감압→흉관</text>
</svg>'''

SVG["abd_quadrants"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 460" font-family="''' + FONT + '''">
  <rect width="800" height="460" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">급성 복통 — 위치로 원인을 좁힌다</text>
  <line x1="32" y1="60" x2="768" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(250,250)">
    <rect x="-170" y="-150" width="340" height="320" rx="40" fill="#fdeef0" stroke="#d9a9b0" stroke-width="2.5"/>
    <line x1="0" y1="-150" x2="0" y2="170" stroke="#cbb3b8" stroke-width="2"/>
    <line x1="-170" y1="10" x2="170" y2="10" stroke="#cbb3b8" stroke-width="2"/>
    <text x="-85" y="-90" font-size="15" font-weight="800" fill="#b23039" text-anchor="middle">RUQ</text>
    <text x="85" y="-90" font-size="15" font-weight="800" fill="#1559a8" text-anchor="middle">LUQ</text>
    <text x="-85" y="100" font-size="15" font-weight="800" fill="#1d6b36" text-anchor="middle">RLQ</text>
    <text x="85" y="100" font-size="15" font-weight="800" fill="#c2611a" text-anchor="middle">LLQ</text>
    <circle cx="0" cy="10" r="7" fill="#8e24aa"/><text x="0" y="38" font-size="12" fill="#6a1b9a" text-anchor="middle">배꼽주위</text>
  </g>
  <g font-size="14.5" fill="#3a4654">
    <text x="470" y="120" font-weight="800" fill="#b23039">RUQ</text><text x="470" y="146">담낭·간·담관</text>
    <text x="470" y="186" font-weight="800" fill="#1559a8">LUQ</text><text x="470" y="212">비장·위·췌장(체부)</text>
    <text x="470" y="252" font-weight="800" fill="#1d6b36">RLQ</text><text x="470" y="278">충수염·난소·요관</text>
    <text x="470" y="318" font-weight="800" fill="#c2611a">LLQ</text><text x="470" y="344">게실염·난소·요관</text>
    <text x="470" y="384" font-weight="800" fill="#6a1b9a">상복부→등</text><text x="470" y="410">췌장염·대동맥</text>
  </g>
</svg>'''

SVG["brain_territory"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 460" font-family="''' + FONT + '''">
  <rect width="800" height="460" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">뇌혈관 영역 &amp; FAST — 빨리 알아채기</text>
  <line x1="32" y1="60" x2="768" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(250,260)">
    <path d="M0 -150 C-150 -150 -175 0 -120 110 C-80 170 80 170 120 110 C175 0 150 -150 0 -150 Z" fill="#f3e1c8" stroke="#b78b53" stroke-width="3"/>
    <path d="M-110 -40 C-120 60 -60 130 0 140 L0 -120 C-60 -120 -100 -90 -110 -40 Z" fill="#cfe6ff" opacity="0.8"/>
    <path d="M110 -40 C120 60 60 130 0 140 L0 -120 C60 -120 100 -90 110 -40 Z" fill="#ffe0c2" opacity="0.8"/>
    <ellipse cx="0" cy="-70" rx="44" ry="48" fill="#d8f0dd" opacity="0.9"/>
    <text x="-70" y="20" font-size="14" font-weight="800" fill="#1559a8" text-anchor="middle">MCA</text>
    <text x="70" y="20" font-size="14" font-weight="800" fill="#c2611a" text-anchor="middle">MCA</text>
    <text x="0" y="-66" font-size="13" font-weight="800" fill="#1d6b36" text-anchor="middle">ACA</text>
    <text x="0" y="120" font-size="13" font-weight="800" fill="#6a1b9a" text-anchor="middle">PCA</text>
  </g>
  <g font-size="15" fill="#3a4654">
    <text x="470" y="120" font-size="17" font-weight="800" fill="#b23039">FAST</text>
    <text x="470" y="152"><tspan font-weight="800">F</tspan>ace 안면 비대칭</text>
    <text x="470" y="184"><tspan font-weight="800">A</tspan>rm 한쪽 팔 처짐</text>
    <text x="470" y="216"><tspan font-weight="800">S</tspan>peech 말 어눌</text>
    <text x="470" y="248"><tspan font-weight="800">T</tspan>ime 발병시각·즉시</text>
    <text x="470" y="296" font-size="14" fill="#5b6876">MCA: 편마비·실어 / ACA: 다리 위약</text>
    <text x="470" y="320" font-size="14" fill="#5b6876">PCA: 시야장애 / 후방: 현훈·복시</text>
    <text x="470" y="360" font-weight="800" fill="#b23039">CT로 출혈/경색 먼저 감별</text>
  </g>
</svg>'''

SVG["skin_cellulitis"] = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 420" font-family="''' + FONT + '''">
  <rect width="820" height="420" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">봉소염 — 피부밑 감염 · 경계 표시로 추적</text>
  <line x1="32" y1="60" x2="788" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(40,90)">
    <rect x="0" y="0" width="430" height="40" fill="#f6d9bf" stroke="#cda077" stroke-width="1.5"/><text x="445" y="26" font-size="14" fill="#8b6a4f">표피</text>
    <rect x="0" y="40" width="430" height="90" fill="#fbe3e5" stroke="#dca9ae" stroke-width="1.5"/><text x="445" y="90" font-size="14" fill="#8b6a4f">진피</text>
    <rect x="0" y="130" width="430" height="90" fill="#fff6d6" stroke="#d9c98a" stroke-width="1.5"/><text x="445" y="180" font-size="14" fill="#8b6a4f">피하지방</text>
    <ellipse cx="200" cy="95" rx="120" ry="55" fill="#ef6a72" opacity="0.45"/>
    <text x="200" y="100" font-size="14" font-weight="800" fill="#b23039" text-anchor="middle">감염·염증 확산</text>
    <path d="M70 70 q10 -16 20 0 q10 16 20 0" fill="none" stroke="#b23039" stroke-width="2" stroke-dasharray="4 3"/>
    <text x="200" y="250" font-size="13.5" fill="#5b6876" text-anchor="middle">발적·열감·압통(경계 불분명) — 펜으로 경계 그려 진행 추적</text>
  </g>
  <g font-size="14.5" fill="#3a4654">
    <text x="540" y="120" font-weight="800" fill="#b23039">위험 신호(괴사성)</text>
    <text x="540" y="150">소견보다 극심한 통증</text>
    <text x="540" y="178">빠른 진행·수포·피부괴사</text>
    <text x="540" y="206">捻발음(가스)·전신독성</text>
    <text x="540" y="244" font-weight="800" fill="#b23039">→ 응급 변연절제</text>
    <text x="540" y="272" font-size="13.5" fill="#5b6876">농양은 절개배농(항생제만 X)</text>
  </g>
</svg>'''

# ════════════════════════════════════════════════════════════════
# 케이스 12~60 도해 (헬퍼 기반) + 매핑
# ════════════════════════════════════════════════════════════════
# 🫁 호흡기
SVG["edema_resp_flow"]=_flow("급성 폐부종(호흡기) — 가스교환 장애",[("유발","압력↑ / 막손상"),("폐포로 체액","누출·정체"),("가스교환 장애","확산거리↑"),("저산소혈증","호흡곤란")],footer="심인성=압력↑(이뇨·혈관확장) / 비심인성 ARDS=막손상(원인치료·폐보호 환기)\n공통: 앉히고 산소·NIV가 1차")
SVG["edema_resp_cmp"]=_cols("심인성 vs 비심인성(ARDS)",[{"t":"심인성","c":"#b23039","fill":"#fdeced","sub":"압력 상승","lines":["좌심부전·허혈·판막","BNP↑·심비대","→ 이뇨·혈관확장(NTG)"]},{"t":"비심인성 ARDS","c":"#1f7ae0","fill":"#eef4fd","sub":"막 투과성↑","lines":["패혈증·흡인·외상","정상 심장·BNP 낮음","→ 원인치료+폐보호 환기"]}],footer="감별이 치료 방향을 가른다")
SVG["pneumonia_flow"]=_flow("폐렴 — 폐포가 삼출로 굳는다",[("병원체 흡입·흡인",""),("폐포 염증·삼출",""),("경화(consolidation)",""),("환기-관류 불균형","저산소")],footer="노인은 비전형(발열 없이 의식저하·빈호흡) · 배양 후 조기 항생제")
SVG["curb65"]=_panel("폐렴 중증도 — CURB-65",["*Confusion 의식저하","*Urea BUN>19mg/dL","*Respiratory rate ≥30","*Blood pressure SBP<90 / DBP≤60","*65세 이상","각 1점 → 외래(0~1)·입원(2)·중환자(≥3) 고려"],sub="점수로 진료 강도 결정",accent="#1559a8")
SVG["pe_flow"]=_flow("폐색전증 — 다리 혈전이 폐로",[("DVT(하지 정맥혈전)",""),("우심 거쳐 폐동맥","색전"),("폐 사강·우심부담",""),("저산소·쇼크","")],footer="갑작스런 호흡곤란+빈맥+저산소인데 X선 정상 → PE 의심")
SVG["pe_dx"]=_panel("PE 진단·치료",["*확진: CT 폐동맥조영","저위험: Wells↓ + D-dimer 음성으로 배제","ECG: 동성빈맥(가끔 S1Q3T3)","항응고: 의심 단계부터(금기 없으면)","*대량 PE(쇼크): 혈전용해/제거"],sub="저위험 배제·고위험 영상",accent="#b23039")
SVG["pneumo_tx"]=_panel("기흉 처치",["*긴장성: 영상 전 바늘감압→흉관","바늘감압: 2nd ICS 중쇄골선 또는 4·5th 전액와선","증상성·큰 기흉: 흉관 배액","개방성: 3면 밀폐 드레싱","소량·무증상: 산소 주며 관찰"],sub="긴장성은 임상진단으로 즉시",accent="#b23039")
SVG["asthma_flow"]=_flow("천식 — 가역적 기도 폐색",[("유발(알레르겐·감염)",""),("기관지 수축·부종","점액↑"),("호기 기류 제한","천명·공기걸림"),("호흡일↑","")],footer="SABA 반복+조기 스테로이드 · silent chest·말 못함=위험")
SVG["asthma_sev"]=_panel("천식 중증도 신호",["경증~중등: 천명·말하기 가능","*중증: 한 단어씩·앉아 호흡·보조근","*생명위협: 말 못함·청색증·처짐","*silent chest(천명 사라짐)=기류 거의 없음","ABG CO₂ 정상화/상승=피로 신호"],sub="말하기·천명·의식으로 판단",accent="#c2611a")
SVG["copd_flow"]=_flow("COPD 악화 — CO₂ 저류 주의",[("악화(흔히 감염)",""),("기류제한·점액↑",""),("환기 불량","CO₂ 저류"),("고탄산성 산증","")],footer="조절 산소 88~92% · 기관지확장제+스테로이드±항생제 · 산증→NIV")
SVG["copd_o2"]=_panel("산소·환기 핵심",["*SpO₂ 목표 88~92% (과투여 금물)","과산소→호흡억제·V/Q악화→CO₂↑·의식저하","기관지확장제(SABA+항콜린)","전신 스테로이드 ±(화농성)항생제","*고탄산성 산증 지속→NIV(BiPAP)"],sub="저산소는 교정하되 과투여 금지",accent="#1559a8")
SVG["tb_flow"]=_flow("결핵 — 흡입에서 재활성화까지",[("비말핵 흡입",""),("폐포 대식세포 감염",""),("육아종으로 봉쇄",""),("재활성화","공동 형성")],footer="2주↑ 기침·야간발한·체중감소 · 공동=전염력↑")
SVG["tb_mgmt"]=_panel("결핵 관리 핵심",["*공기매개 격리(음압실·N95)","객담 AFB도말·PCR·배양(다른 날)","상엽 침윤·공동(흉부 X선)","*4제 병합(INH+RIF+PZA+EMB)","직접복약확인(DOT)·법정감염병 신고"],sub="격리가 최우선",accent="#1d6b36")
SVG["hv_flow"]=_flow("과호흡 — 알칼리증·테타니",[("불안·공황",""),("과도한 환기","CO₂ 과배출"),("호흡성 알칼리증","pH↑"),("이온화 Ca↓","손발저림·테타니")],footer="안정·호흡 조절 · 봉지 재호흡 지양(숨은 저산소)")
SVG["hv_ddx"]=_panel("‘과호흡’ 단정 전 배제",["*PE(폐색전)","*ACS(심근경색)","*DKA(당뇨케톤산증)","패혈증·저산소·갑상선항진","SpO₂ 저하 동반→기질적 원인 의심"],sub="과호흡은 배제 진단",accent="#b23039")
# 🧠 신경계
SVG["stroke_flow"]=_flow("허혈성 뇌졸중 — Time is brain",[("혈전·색전",""),("뇌혈류 차단",""),("허혈 중심부·penumbra",""),("재관류 골든타임","")],footer="발병시각 확인 · CT로 출혈 배제 후 혈전용해/혈전제거")
SVG["ich_flow"]=_flow("출혈성 뇌졸중 — 혈종이 압박",[("혈관 파열",""),("뇌실질 혈종",""),("혈종 확장·부종",""),("두개내압↑·탈출","")],footer="CT 확인 전 혈전용해·항응고 금지 · 와파린/DOAC 즉시 역전")
SVG["stroke_ct_cmp"]=_cols("CT — 경색 vs 출혈",[{"t":"허혈성(경색)","c":"#1559a8","fill":"#eef4fd","lines":["저음영(어둡게)","초기엔 미묘","→ 혈전용해 대상"]},{"t":"출혈성","c":"#b23039","fill":"#fdeced","lines":["고음영(밝게)","즉시 보임","→ 용해 절대 금기"]}],footer="증상만으론 구분 불가 → CT가 갈림길")
SVG["tia_flow"]=_flow("TIA — 경색 임박 경고",[("일시적 폐색",""),("신경결손",""),("재개통·완전 회복",""),("곧 경색 위험","48h 최고")],footer="회복됐어도 귀가 금지 · ABCD2 · 항혈소판 신속")
SVG["abcd2"]=_panel("TIA 평가·관리",["MRI(미세경색)·CT(출혈 배제)","경동맥 도플러/CTA·ECG(AF)","*48시간 이내가 경색 위험 최고","항혈소판 신속 시작","AF→항응고 / 경동맥 고도협착→재개통"],sub="임박 뇌졸중으로 접근",accent="#b23039")
SVG["sah_flow"]=_flow("지주막하 출혈 — 동맥류 파열",[("뇌동맥류 파열",""),("지주막하 출혈",""),("급격한 ICP↑",""),("재출혈·혈관연축","")],footer="벼락두통 · CT→음성시 LP(황색변성)")
SVG["sah_mgmt"]=_panel("SAH 핵심",["*‘인생 최악’ 벼락두통","CT(초기 민감)→음성+의심시 LP","황색변성(xanthochromia) 확인","재출혈 예방: 안정·혈압·조기 처치(코일/클립)","*혈관연축: 니모디핀(3~14일)"],sub="재출혈·연축이 사망 원인",accent="#b23039")
SVG["mening_flow"]=_flow("뇌수막염 — 수막 감염",[("병원체 침입",""),("수막 염증·부종",""),("뇌압↑·뇌관류↓",""),("뇌손상·패혈증","")],footer="발열·두통·경부강직 · 세균성=즉시 항생제+덱사메타손")
SVG["mening_mgmt"]=_panel("뇌수막염 — 놓치면 안 될 것",["*세균성 의심→검사로 항생제 늦추지 말 것","덱사메타손(폐렴구균)을 항생제와 함께","의식저하·국소징후→LP 전 CT","점상출혈성 발진→수막알균(비말격리)","CSF: 다형핵↑·당↓·단백↑"],sub="조기 항생제가 생명",accent="#b23039")
SVG["seizure_flow"]=_flow("경련 — 뇌 과흥분",[("흥분-억제 균형 붕괴",""),("뉴런 동시 과흥분",""),("발작(운동·의식)",""),("발작 후 회복기","")],footer="유발: 저혈당·저Na·저산소·발열·약물/금단 → 혈당부터")
SVG["seizure_mgmt"]=_panel("발작 대응",["*보호: 측위·주변 안전·시간 측정","구강 내 물건·억지 제지 금지","*모든 경련은 혈당부터","5분 이상 지속→지속상태(벤조)","발열+발작·국소징후→수막염/구조병변"],sub="보호와 원인 동시",accent="#c2611a")
SVG["se_flow"]=_flow("간질지속상태 — 시간이 약효를 깎는다",[("지속·반복 발작",""),("GABA 수용체 감소",""),("벤조 반응성↓",""),("흥분독성·뇌손상","")],footer="조기·충분량 투여가 관건 · 5분↑ 또는 회복없는 반복")
SVG["se_steps"]=_panel("지속상태 단계 치료",["*1단계: 벤조디아제핀(충분량)","2단계: 항경련제 부하(Levetiracetam 등)","*3단계(불응성): 마취제+삽관+EEG","기도·산소·혈당·전해질 동시 교정","멈춰도 의식 안 돌아오면 비경련성(EEG)"],sub="벤조→항경련제→마취제",accent="#b23039")
SVG["vertigo_cmp"]=_cols("현훈 — 말초 vs 중추",[{"t":"말초(내이)","c":"#1d6b36","fill":"#eef7f0","lines":["BPPV·전정신경염·메니에르","수평-회선 안진(방향 일정)","이명·청력저하 가능","신경결손 없음(대개 양호)"]},{"t":"중추(뇌)","c":"#b23039","fill":"#fdeced","lines":["소뇌·뇌간 뇌졸중","보행 불가·국소신경징후","방향 바뀌는/수직 안진","약한 어지럼인데 증상 심함"]}],footer="중추 의심→MRI(후방순환은 초기 CT 음성 가능)")
SVG["hints"]=_panel("HINTS — 급성 지속현훈 감별",["Head Impulse(두부충동검사)","Nystagmus(안진 방향)","Test of Skew(교대가림 편위)","보행·소뇌검사·신경학적 진찰","*‘중추 시사’면 뇌졸중 경로로"],sub="감별이 곧 분류",accent="#1559a8")
SVG["gbs_flow"]=_flow("길랑-바레 — 감염 후 자가면역",[("선행 감염","설사·상기도"),("분자모방·자가면역",""),("말초신경 탈수초",""),("상행성 대칭 마비","")],footer="호흡근·자율신경 위험 → FVC 추세 감시 · IVIG/혈장교환")
SVG["gbs_mgmt"]=_panel("GBS 감시·치료",["발끝부터 상행 대칭 위약·반사소실","CSF: 알부민세포해리(단백↑·세포정상)","*호흡근 침범→FVC 추세·삽관 준비","*자율신경 불안정(혈압·맥박 급변)","IVIG 또는 혈장교환(조기)"],sub="호흡·자율신경이 위험",accent="#b23039")
# 🫀 소화기
SVG["ugib_flow"]=_flow("상부 위장관 출혈",[("궤양/정맥류 등",""),("상부 소화관 출혈",""),("토혈·흑색변",""),("저혈량·쇼크","")],footer="소생 1순위(굵은 IV2개·수혈) · 비정맥류=PPI / 정맥류=Octreotide+항생제")
SVG["ugib_cmp"]=_cols("비정맥류 vs 정맥류",[{"t":"비정맥류(궤양 등)","c":"#1559a8","fill":"#eef4fd","lines":["고용량 PPI 정주","내시경 지혈","커피색 토혈·흑색변"]},{"t":"정맥류(간경변)","c":"#b23039","fill":"#fdeced","lines":["Octreotide/Terlipressin","*예방적 항생제(생존↑)","내시경 결찰(EVL)"]}],footer="간경변 단서면 접근이 달라진다")
SVG["lgib_flow"]=_flow("하부 위장관 출혈",[("게실·혈관이형성 등",""),("하부 소화관 출혈",""),("적색 혈변",""),("대부분 자연지혈","일부 대량")],footer="대량 적색변은 빠른 상부출혈도 가능→상부 배제 필수")
SVG["lgib_mgmt"]=_panel("하부 출혈 접근",["*적색 혈변이라도 상부 배제","대장내시경(위치·지혈)","활동성 출혈→CT 혈관조영/색전","소생·응고/항응고 교정","노인·항응고제는 급격 불안정 주의"],sub="상부 배제 후 위치 진단",accent="#1d6b36")
SVG["acute_abd_red"]=_panel("외과적 복통 신호",["*판자배(강직)·반발통=복막자극","박동성 종괴+저혈압→대동맥류 파열","가임 여성 하복통→자궁외임신(임신검사)","고령·면역저하는 증상 경미해도 중증","검사: CBC·CRP·리파제·젖산·임신·영상"],sub="복막자극=외과 의뢰",accent="#b23039")
SVG["panc_flow"]=_flow("췌장염 — 효소 자가소화",[("담석·음주 등",""),("효소 조기 활성",""),("자가소화·염증",""),("전신염증·제3공간","저혈량")],footer="리파제 3배↑ · 적극적 수액+금식+진통 · 담석성 담관염→ERCP")
SVG["panc_mgmt"]=_panel("췌장염 핵심",["*리파제(아밀라제) 정상 3배↑","*적극적 수액(소변량으로 적정)","금식·충분한 진통·진토","담석 확인(초음파)·중증시 조영 CT","저혈압·핍뇨·빈호흡→중증(장기부전)"],sub="수액이 치료의 중심",accent="#c2611a")
SVG["chole_flow"]=_flow("담낭염 — 담석 폐색",[("담석이 담낭관 폐색",""),("담즙 정체·염증",""),("부종·세균 중복",""),("괴저·천공(중증)","")],footer="Murphy 양성·초음파 · 발열+황달+RUQ통(Charcot)=담관염→ERCP")
SVG["chole_mgmt"]=_panel("담낭염·담관염",["RUQ통(우견 방사)·Murphy 양성","초음파: 결석·담낭벽 비후·주위 액체","금식·수액·진통·항생제","*조기 복강경 담낭절제","*Charcot 3징=담관염→ERCP 배액"],sub="담관염은 더 응급",accent="#b23039")
SVG["cirr_flow"]=_flow("간경변 — 문맥압 항진",[("만성 간손상",""),("섬유화·결절",""),("문맥압 항진",""),("정맥류·복수·뇌증","")],footer="뇌증=Lactulose+유발인자 / 복수+열=SBP / 정맥류 출혈 관리")
SVG["cirr_compl"]=_panel("간경변 합병증",["정맥류 출혈(토혈·흑색변)","복수·하지부종 / *SBP(복수+발열·복통)","*간성뇌증: Lactulose+유발인자 교정","응고장애(INR↑)·황달","뇌증 유발: 출혈·감염·변비·전해질"],sub="합병증별로 대응",accent="#5d4037")
SVG["varix_flow"]=_flow("식도 정맥류 출혈",[("간경변·문맥압↑",""),("측부순환 정맥류",""),("압력·벽긴장→파열",""),("대량 출혈","")],footer="기도보호 1순위 · Octreotide+예방적 항생제 · 결찰→실패시 풍선·TIPS")
SVG["varix_mgmt"]=_panel("정맥류 출혈 처치",["*대량 토혈+의식저하→기도보호(삽관)","굵은 IV 2개·균형수혈 소생","Octreotide/Terlipressin(문맥압↓)","*예방적 항생제(생존율 직결)","내시경 결찰→실패시 풍선/TIPS"],sub="기도→약물→내시경",accent="#b23039")
SVG["ileus_cmp"]=_cols("장폐색 — 기계적 vs 마비성",[{"t":"기계적","c":"#b23039","fill":"#fdeced","lines":["유착·탈장·종양","고음 금속성 장음","교액=수술 응급","완전폐색→수술 평가"]},{"t":"마비성","c":"#1559a8","fill":"#eef4fd","lines":["수술후·복막염·전해질","장음 감소·소실","원인 교정(전해질 등)","대개 보존적 호전"]}],footer="팽만·구토·배변정지 공통 / 금식·비위관 감압·수액")
SVG["ileus_strang"]=_panel("교액(허혈) 경고",["*지속·심한 통증","*발열·복막자극","*젖산↑·백혈구↑","분변성 구토·심한 팽만(완전폐색)","→ 응급수술(장괴사 전)"],sub="교액은 시간 싸움",accent="#b23039")
SVG["gastro_flow"]=_flow("위장관염 — 탈수가 핵심",[("바이러스·세균·독소",""),("장점막 자극",""),("구토·설사",""),("수분·전해질 소실","탈수")],footer="ORS 소량 자주(1차) · 혈변·고열·심한 복통은 경고")
SVG["gastro_warn"]=_panel("위장관염 — 관리·경고",["경·중등도: 경구수분보충(ORS)","중증 탈수·쇼크: 정맥수액","항생제 대부분 불필요(선택적)","*혈성 설사+고열+심한 복통→감별","EHEC 의심시 항생제·지사제 신중(HUS)"],sub="수분 보충이 중심",accent="#1d6b36")
SVG["perit_flow"]=_flow("복막염 — 천공·오염",[("천공/장기 파열",""),("복강 오염·염증",""),("체액이동·세균혈증",""),("패혈증·쇼크","")],footer="판자배·반발통·free air · 소생+광범위 항생제+수술")
SVG["perit_mgmt"]=_panel("복막염 처치",["*판자배+반발통+발열→외과 즉시","X선 유리공기(free air)=천공","소생(수액)·패혈증 번들","경험적 광범위 항생제","*수술적 감염원 제거(source control)"],sub="수술이 근본",accent="#b23039")
# 🩺 신장/비뇨기
SVG["aki_cols"]=_cols("급성 신부전 — 3분류가 먼저",[{"t":"신전성","c":"#1559a8","fill":"#eef4fd","sub":"관류↓","lines":["탈수·쇼크·심부전","→ 수액·관류 회복"]},{"t":"신성","c":"#b23039","fill":"#fdeced","sub":"실질 손상","lines":["ATN·신독소·사구체염","→ 원인 치료"]},{"t":"신후성","c":"#1d6b36","fill":"#eef7f0","sub":"폐색","lines":["요폐·결석·전립선","→ 도뇨·감압"]}],footer="소변량·Cr·K 추세 / 신독성약 회피")
SVG["aki_dialysis"]=_panel("응급투석 적응 (AEIOU)",["*고칼륨혈증(ECG 변화)","중증 대사성 산증","*체액과잉(폐부종)","요독 증상(뇌증·심막염)","약물로 안 잡히는 생명위협→투석"],sub="약물 불응 생명위협 합병증",accent="#00695c")
SVG["hyperk_flow"]=_flow("고칼륨혈증 — 조용한 살인자",[("신부전·약물·세포파괴",""),("혈청 K↑",""),("심근 막전위 변화",""),("치명적 부정맥·심정지","")],footer="무증상도 위험 · ECG(첨예T→QRS확장)가 중증도")
SVG["hyperk_tx"]=_panel("고칼륨 치료 — 순서",["*①칼슘(심장 보호): ECG 변화시 즉시","칼슘은 K를 낮추지 않음(보호만)","②세포 내 이동: 인슐린+포도당, β2","(산증시 중탄산) — 일시적","*③체외 제거: 이뇨·양이온수지·투석","유발약 중단·원인 교정"],sub="보호→이동→제거",accent="#00695c")
SVG["stone_flow"]=_flow("신장결석 — 산통의 기전",[("결석이 요관 폐색",""),("요 정체·신우압↑",""),("평활근 경련",""),("옆구리→서혜부 산통","혈뇨")],footer="비조영 CT · NSAID 진통+수분 · 결석+감염(발열)=응급 감압")
SVG["stone_mgmt"]=_panel("신장결석 처치",["옆구리→서혜부 방사통·혈뇨","비조영 복부 CT(표준)","*NSAID 1차 진통(+α차단제 배출)","수분 유지·작은 결석은 자연배출","*결석+발열(폐색성 감염)→스텐트/신루"],sub="대개 보존, 감염은 응급",accent="#00695c")
SVG["uti_cmp"]=_cols("하부(방광염) vs 상부(신우신염)",[{"t":"하부 방광염","c":"#1559a8","fill":"#eef4fd","lines":["배뇨통·빈뇨·절박뇨","치골상부 불편","발열 없음","경구 항생제"]},{"t":"상부 신우신염","c":"#b23039","fill":"#fdeced","lines":["발열·오한","옆구리통(CVA 압통)","오심·구토","적극 항생제(중증=정주)"]}],footer="배양 후 항생제 / 폐색=감압 / 패혈증 주의")
SVG["uti_mgmt"]=_panel("요로감염 주의",["소변검사(농뇨)·배양(항생제 전)","*폐색(결석 등)+감염→감압 필수","저혈압·의식저하→요로패혈증(번들)","임산부·당뇨·남성·노인=복잡성","상부·복잡성은 적극 치료"],sub="폐색·패혈증 경계",accent="#b23039")
SVG["hd_flow"]=_flow("투석 환자 — 거르면 쌓인다",[("투석 거름/부족",""),("칼륨·체액 축적",""),("부정맥·폐부종",""),("응급투석 필요","")],footer="통로(누공) 보호 · 심혈관·감염 흔함")
SVG["hd_access"]=_panel("투석 응급 핵심",["*고칼륨·폐부종→응급투석(약물은 임시)","*통로 팔: 혈압·채혈·주사 금지","thrill(진동) 확인 / 출혈은 압박","발열·통로 발적→감염(배양·항생제)","*흉통→심혈관 위험 매우 높음(ACS)"],sub="통로 보호·심혈관·감염",accent="#00695c")
# 🍬 내분비/대사
SVG["dka_flow"]=_flow("DKA — 인슐린 결핍",[("인슐린 결핍",""),("지방분해·케톤","산증"),("고혈당·삼투성 이뇨","탈수"),("전해질 소실","")],footer="수액→인슐린→칼륨 · 혈당 서서히 · 유발인자 교정")
SVG["dka_mgmt"]=_panel("DKA 치료 순서",["*수액 소생(탈수 교정) 먼저","칼륨 확인(인슐린 전 K<3.3이면 보류)","정주 인슐린(혈당 서서히↓)","산증·케톤·전해질 추적","유발인자(감염·심근경색) 교정"],sub="수액·칼륨·인슐린",accent="#e65100")
SVG["hhs_cmp"]=_cols("DKA vs HHS",[{"t":"DKA","c":"#e65100","fill":"#fff1e0","lines":["케톤산증 뚜렷","pH↓·케톤↑","주로 1형·젊음"]},{"t":"HHS","c":"#b23039","fill":"#fdeced","lines":["산증 거의 없음","극심한 고혈당(>600)","노인 2형·의식저하"]}],footer="HHS는 수액이 1순위 · 혈당·삼투압 서서히(뇌부종)")
SVG["hhs_mgmt"]=_panel("HHS 치료",["*대량 수액이 1순위(탈수)","K 확인 후 보충(인슐린 전 K<3.3 보류)","수액 후 인슐린, 혈당 서서히↓","*급격 강하→뇌부종 위험","유발인자(감염·MI) 함께 치료"],sub="수액 먼저·서서히",accent="#e65100")
SVG["hypo_flow"]=_flow("저혈당 — 뇌는 포도당 의존",[("혈당 <70",""),("교감 항진","떨림·발한·빈맥"),("신경당결핍","혼돈·의식저하"),("경련·뇌손상","")],footer="모든 의식저하는 혈당부터 · 의식따라 경구/정맥/글루카곤")
SVG["hypo_mgmt"]=_panel("저혈당 처치",["*모든 의식저하 환자 혈당부터","의식 있음: 경구 단순당 15~20g","*의식 없음: 정맥 포도당/글루카곤(경구 금지)","15분 후 재측정·복합탄수화물 유지","*설폰요소제·지속형 인슐린→재발(관찰)"],sub="1초가 급하다",accent="#e65100")
SVG["thyroid_flow"]=_flow("갑상선 위기 — 호르몬 폭주",[("기저 항진+유발",""),("호르몬·교감 폭발",""),("다장기 항진","고열·빈맥·뇌증"),("다장기 부전","")],footer="치료 순서: β차단→항갑상선제→요오드(거꾸로 금지)")
SVG["thyroid_mgmt"]=_panel("갑상선 위기 치료 순서",["*①β차단제(증상·심박)","*②항갑상선제(생성 차단, PTU/MMI)","*③요오드(항갑상선제 이후! 분비 억제)","해열(냉각·아세트아미노펜)·수액·스테로이드","아스피린 지양(호르몬 유리)"],sub="순서가 생명",accent="#e65100")
SVG["adrenal_flow"]=_flow("부신 위기 — 코르티솔 결핍",[("부신부전+스트레스",""),("코르티솔 결핍",""),("혈관긴장·당 실패",""),("불응성 쇼크","")],footer="수액·승압 불응 쇼크+저Na·고K·저혈당 → 의심만으로 스테로이드")
SVG["adrenal_mgmt"]=_panel("부신 위기 치료",["*수액·승압 불응 쇼크→의심","*Hydrocortisone 즉시(확진 기다리지 말 것)","생리식염수 적극 수액·저혈당 교정","저Na·고K·저혈당 조합이 단서","유발(감염 등)·전해질 교정"],sub="스테로이드가 생명",accent="#e65100")
SVG["hypona_flow"]=_flow("저나트륨혈증 — 뇌부종",[("수분 과잉(희석)",""),("혈장 저삼투",""),("물이 뇌세포로",""),("뇌부종(두통·경련)","")],footer="교정 속도 제한(과교정=ODS) · 체액상태로 원인 분류")
SVG["hypona_cmp"]=_cols("체액상태로 원인 분류",[{"t":"저혈량","c":"#1559a8","fill":"#eef4fd","lines":["구토·이뇨·탈수","→ 등장식염수"]},{"t":"정상혈량","c":"#1d6b36","fill":"#eef7f0","lines":["SIADH·갑상선·부신","→ 수분제한"]},{"t":"고혈량","c":"#b23039","fill":"#fdeced","lines":["심부전·간경변·신부전","→ 수분·염분 제한"]}],footer="중증(경련)만 3% 식염수 신중·소폭 / 과교정 금지")
# 🦠 감염/패혈증
SVG["sepsis_flow"]=_flow("패혈증 — 감염의 전신 반응",[("감염",""),("전신 염증 반응",""),("혈관확장·투과성↑",""),("조직 저관류·장기부전","")],footer="qSOFA(의식·호흡↑·SBP↓) · Hour-1 번들")
SVG["sepsis_bundle"]=_panel("Hour-1 번들",["*젖산 측정(관류·반응 지표)","*혈액배양 2세트(항생제 전)","*광범위 항생제 신속 투여","저혈압/젖산↑→결정질 30mL/kg","불응성 저혈압→노르에피네프린"],sub="1시간 안에 동시 진행",accent="#1b5e20")
SVG["septic_shock_flow"]=_flow("패혈성 쇼크 — 분포성 쇼크",[("감염·염증매개체",""),("혈관확장·누출+심억제",""),("수액불응 저혈압",""),("젖산↑·장기부전","")],footer="수액 후에도 승압제 필요+젖산↑ = 패혈성 쇼크")
SVG["septic_shock_mgmt"]=_panel("패혈성 쇼크 처치",["*1시간 번들(젖산·배양·항생제·수액30mL/kg)","*수액 불응→노르에피네프린(MAP≥65)","*감염원 제거(농양 배농·장치 제거)","젖산 청소·관류·소변량 재평가","배양은 항생제 전(단, 늦추지 말 것)"],sub="번들+승압+감염원 제거",accent="#1b5e20")
SVG["cellulitis_mgmt"]=_panel("봉소염 처치·감별",["발적·열감·압통(경계 표시 추적)","경험적 항생제(MRSA 위험 고려)","*농양→절개배농(항생제만 부족)","*괴사성근막염: 극심한 통증·빠른 진행·捻발음","→ 응급 변연절제+소생"],sub="경계 추적·괴사성 감별",accent="#1b5e20")
SVG["urosepsis_flow"]=_flow("요로패혈증",[("요로감염",""),("균혈증·전신염증",""),("저관류·장기부전",""),("패혈성 쇼크 가능","")],footer="폐색 동반 여부가 핵심(있으면 감압) · 번들+광범위 항생제")
SVG["urosepsis_mgmt"]=_panel("요로패혈증 핵심",["발열·옆구리통+패혈증 징후","소변·혈액배양(항생제 전)·젖산","*폐색(결석·수신증)→즉시 감압(스텐트/신루)","경험적 광범위 항생제·수액","수액 불응→노르에피네프린"],sub="폐색=감압이 핵심",accent="#1b5e20")
SVG["isolation_cmp"]=_cols("전파경로별 격리",[{"t":"비말주의","c":"#1559a8","fill":"#eef4fd","sub":"큰 비말·근거리","lines":["독감·코로나·수막알균","수술용 마스크","1인실/코호트·1~2m"]},{"t":"공기주의","c":"#b23039","fill":"#fdeced","sub":"비말핵·장거리","lines":["결핵·홍역·수두","*N95+음압 1인실","이동 최소화"]}],footer="의심부터 격리(검사 전)·조기 선별·손위생")
SVG["isolation_mgmt"]=_panel("감염관리 기본",["입구 선별·즉시 마스크","의심 단계부터 격리 시작","공기매개(결핵·홍역·수두)=N95·음압","개인보호구 착·탈의 수칙","*손위생이 모든 것의 기본"],sub="조기 분리·손위생",accent="#1b5e20")
# 😰 기타 내과
SVG["anemia_flow"]=_flow("급성 출혈성 빈혈",[("급성 실혈",""),("순환혈액량↓",""),("빈맥·기립성→저혈압",""),("저혈량 쇼크","")],footer="초기 Hb 정상 함정(혈액농축) · 활력징후·기립성으로 판단")
SVG["anemia_mgmt"]=_panel("출혈성 빈혈 핵심",["*초기 Hb 정상도 안심 금지","빈맥·기립성 저혈압=조기 단서","출혈원 탐색(위장관·복강·후복막·외상)","굵은 IV·수액·수혈 소생","*대량출혈→균형수혈+지혈+응고교정"],sub="활력징후가 Hb보다 빠르다",accent="#455a64")
SVG["dic_flow"]=_flow("DIC — 소모성 응고장애",[("기저질환(패혈증 등)",""),("전신 응고 활성",""),("인자·혈소판 소모",""),("출혈 + 미세혈전","")],footer="원인 치료가 최우선 · 혈소판↓·PT↑·피브리노겐↓·D-dimer↑")
SVG["dic_mgmt"]=_panel("DIC 핵심",["*항상 기저질환 동반→원인 치료 우선","검사: 혈소판↓·PT/aPTT 연장","피브리노겐↓·D-dimer/FDP↑","출혈/시술시 성분 보충(혈소판·FFP·동결침전물)","출혈과 혈전이 동시(오판 금지)"],sub="원인 치료가 본질",accent="#455a64")
SVG["fn_flow"]=_flow("발열성 호중구감소증",[("세포독성 항암",""),("골수억제·호중구↓",""),("면역 최전선 부재",""),("발열로도 패혈증 급속","")],footer="발열=응급 · 배양 후 1시간 내 광범위 항생제")
SVG["fn_mgmt"]=_panel("발열성 호중구감소증",["*항암 후 발열=그 자체가 응급","*1시간 내 경험적 광범위 항생제(항녹농균)","혈액배양 2세트(말초+카테터)","보호격리·손위생","직장체온·관장 등 점막손상 시술 지양"],sub="1시간이 생명",accent="#455a64")
SVG["hyperca_flow"]=_flow("악성종양 고칼슘혈증",[("종양(PTHrP·골용해)",""),("칼슘↑",""),("삼투성 이뇨·탈수",""),("칼슘 배설↓ 악순환","")],footer="대량 수액이 1순위 · 비스포스포네이트(±칼시토닌)")
SVG["hyperca_mgmt"]=_panel("고칼슘혈증 치료",["증상: 다뇨·변비·오심·혼돈(stones·bones·groans)","*①대량 생리식염수(탈수 교정 먼저)","②비스포스포네이트(효과 며칠)±칼시토닌","*탈수 전 이뇨제 금물","원발 암 치료·신기능 따라 용량"],sub="수액→칼슘강하제",accent="#455a64")
SVG["ana_flow"]=_flow("아나필락시스 — 즉시형 과민",[("알레르겐 노출",""),("비만세포 탈과립",""),("히스타민 등 방출",""),("혈관확장+기관지수축","쇼크·기도부종")],footer="에피네프린 IM이 1순위(항히스타민·스테로이드는 보조)")
SVG["ana_mgmt"]=_panel("아나필락시스 처치",["*①에피네프린 IM(대퇴 전외측) 즉시","1:1000 0.3~0.5mg, 5~15분마다 반복","②기도·산소·앙와위+다리거상","③수액(저혈압시 빠른 볼루스)","④보조: 항히스타민·스테로이드 / β차단제→글루카곤"],sub="에피네프린이 1순위",accent="#455a64")
SVG["tox_syndrome"]=_panel("독성증후군(Toxidrome)으로 추정",["오피오이드: 의식↓·호흡↓·동공축소→날록손","교감흥분: 빈맥·고혈압·산동·발한","항콜린성: 고열·홍조·산동·섬망·장음↓","콜린성: 침·눈물·서맥·축동·설사","진정-수면: 졸림·호흡억제"],sub="증상 묶음으로 계열 추정",accent="#455a64")
SVG["tox_mgmt"]=_panel("중독 처치 원칙",["*약물보다 ABC(기도·호흡·순환) 우선","*아세트아미노펜: 초기 무증상도 간부전→농도·NAC","오피오이드→날록손, TCA→중탄산","활성탄: 조기·기도안전 시(흡인 주의)","의도적 음독→다약물·정신과 평가"],sub="ABC→해독제→흡수감소",accent="#455a64")

SVG_MAP.update({
 "12":{"병태생리":"edema_resp_flow","검사":"edema_resp_cmp"},
 "13":{"병태생리":"pneumonia_flow","검사":"curb65"},
 "14":{"병태생리":"pe_flow","검사":"pe_dx"},
 "15":{"병태생리":"lung_pneumothorax","치료":"pneumo_tx"},
 "16":{"병태생리":"asthma_flow","증상":"asthma_sev"},
 "17":{"병태생리":"copd_flow","치료":"copd_o2"},
 "18":{"병태생리":"tb_flow","치료":"tb_mgmt"},
 "19":{"병태생리":"hv_flow","검사":"hv_ddx"},
 "20":{"병태생리":"stroke_flow","해부":"brain_territory"},
 "21":{"병태생리":"ich_flow","검사":"stroke_ct_cmp"},
 "22":{"병태생리":"tia_flow","검사":"abcd2"},
 "23":{"병태생리":"sah_flow","검사":"sah_mgmt"},
 "24":{"병태생리":"mening_flow","치료":"mening_mgmt"},
 "25":{"병태생리":"seizure_flow","치료":"seizure_mgmt"},
 "26":{"병태생리":"se_flow","치료":"se_steps"},
 "27":{"병태생리":"vertigo_cmp","검사":"hints"},
 "28":{"병태생리":"gbs_flow","검사":"gbs_mgmt"},
 "29":{"병태생리":"ugib_flow","검사":"ugib_cmp"},
 "30":{"병태생리":"lgib_flow","검사":"lgib_mgmt"},
 "31":{"증상":"abd_quadrants","검사":"acute_abd_red"},
 "32":{"병태생리":"panc_flow","검사":"panc_mgmt"},
 "33":{"병태생리":"chole_flow","검사":"chole_mgmt"},
 "34":{"병태생리":"cirr_flow","증상":"cirr_compl"},
 "35":{"병태생리":"varix_flow","치료":"varix_mgmt"},
 "36":{"병태생리":"ileus_cmp","검사":"ileus_strang"},
 "37":{"병태생리":"gastro_flow","치료":"gastro_warn"},
 "38":{"병태생리":"perit_flow","검사":"perit_mgmt"},
 "39":{"병태생리":"aki_cols","치료":"aki_dialysis"},
 "40":{"병태생리":"hyperk_flow","검사":"ecg_hyperk","치료":"hyperk_tx"},
 "41":{"병태생리":"stone_flow","검사":"stone_mgmt"},
 "42":{"병태생리":"uti_cmp","검사":"uti_mgmt"},
 "43":{"병태생리":"hd_flow","치료":"hd_access"},
 "44":{"병태생리":"dka_flow","검사":"dka_mgmt"},
 "45":{"병태생리":"hhs_cmp","검사":"hhs_mgmt"},
 "46":{"병태생리":"hypo_flow","치료":"hypo_mgmt"},
 "47":{"병태생리":"thyroid_flow","치료":"thyroid_mgmt"},
 "48":{"병태생리":"adrenal_flow","치료":"adrenal_mgmt"},
 "49":{"병태생리":"hypona_flow","검사":"hypona_cmp"},
 "50":{"병태생리":"sepsis_flow","검사":"sepsis_bundle"},
 "51":{"병태생리":"septic_shock_flow","치료":"septic_shock_mgmt"},
 "52":{"병태생리":"skin_cellulitis","치료":"cellulitis_mgmt"},
 "53":{"병태생리":"urosepsis_flow","검사":"urosepsis_mgmt"},
 "54":{"병태생리":"isolation_cmp","치료":"isolation_mgmt"},
 "55":{"병태생리":"anemia_flow","검사":"anemia_mgmt"},
 "56":{"병태생리":"dic_flow","검사":"dic_mgmt"},
 "57":{"병태생리":"fn_flow","치료":"fn_mgmt"},
 "58":{"병태생리":"hyperca_flow","치료":"hyperca_mgmt"},
 "59":{"병태생리":"ana_flow","진단":"ana_mgmt"},
 "60":{"증상":"tox_syndrome","치료":"tox_mgmt"},
})

# ════════════════════════════════════════════════════════════════
# 외과계열 — 신규 작화 + 헬퍼 도해 + 매핑(SVG_MAP_SURG)
# ════════════════════════════════════════════════════════════════
SVG["burn_depth"]='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 880 440" font-family="''' + FONT + '''">
  <rect width="880" height="440" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">화상 깊이(1~3도) &amp; 범위(9의 법칙)</text>
  <line x1="32" y1="60" x2="848" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(40,90)">
    <rect x="0" y="0" width="430" height="46" fill="#f6d9bf" stroke="#cda077" stroke-width="1.5"/><text x="445" y="30" font-size="14" fill="#8b6a4f">표피</text>
    <rect x="0" y="46" width="430" height="100" fill="#fbe3e5" stroke="#dca9ae" stroke-width="1.5"/><text x="445" y="100" font-size="14" fill="#8b6a4f">진피</text>
    <rect x="0" y="146" width="430" height="100" fill="#fff6d6" stroke="#d9c98a" stroke-width="1.5"/><text x="445" y="200" font-size="14" fill="#8b6a4f">피하지방</text>
    <rect x="20" y="2" width="120" height="42" fill="#ffcaca" opacity="0.6"/><text x="80" y="28" font-size="13" font-weight="800" fill="#b23039" text-anchor="middle">1도(표피)</text>
    <rect x="160" y="2" width="120" height="120" fill="#ff9aa0" opacity="0.6"/><text x="220" y="70" font-size="13" font-weight="800" fill="#b23039" text-anchor="middle">2도(부분층)</text>
    <rect x="300" y="2" width="120" height="240" fill="#7a3b40" opacity="0.55"/><text x="360" y="130" font-size="13" font-weight="800" fill="#5b1e22" text-anchor="middle">3도(전층)</text>
    <text x="0" y="272" font-size="13" fill="#5b6876">1도=발적·통증 / 2도=물집·심한 통증 / 3도=가죽같이·무통(함정)</text>
  </g>
  <g transform="translate(560,95)">
    <text x="120" y="-6" font-size="14" font-weight="800" fill="#1a2a3a" text-anchor="middle">Rule of 9s (성인)</text>
    <circle cx="120" cy="28" r="20" fill="#fde3e5" stroke="#b23039" stroke-width="2"/><text x="120" y="33" font-size="12" text-anchor="middle" fill="#b23039">9</text>
    <rect x="92" y="50" width="56" height="90" rx="8" fill="#fde3e5" stroke="#b23039" stroke-width="2"/><text x="120" y="100" font-size="12" text-anchor="middle" fill="#b23039">앞18<tspan x="120" dy="14">뒤18</tspan></text>
    <rect x="40" y="56" width="40" height="84" rx="8" fill="#fde3e5" stroke="#b23039" stroke-width="2"/><text x="60" y="102" font-size="12" text-anchor="middle" fill="#b23039">9</text>
    <rect x="160" y="56" width="40" height="84" rx="8" fill="#fde3e5" stroke="#b23039" stroke-width="2"/><text x="180" y="102" font-size="12" text-anchor="middle" fill="#b23039">9</text>
    <rect x="92" y="150" width="24" height="120" rx="8" fill="#fde3e5" stroke="#b23039" stroke-width="2"/><text x="104" y="215" font-size="12" text-anchor="middle" fill="#b23039">18</text>
    <rect x="124" y="150" width="24" height="120" rx="8" fill="#fde3e5" stroke="#b23039" stroke-width="2"/><text x="136" y="215" font-size="12" text-anchor="middle" fill="#b23039">18</text>
    <text x="120" y="292" font-size="12.5" fill="#5b6876" text-anchor="middle">손바닥 ≈ 1% · 2도 이상만 TBSA</text>
  </g>
</svg>'''

SVG["compartment"]='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 430" font-family="''' + FONT + '''">
  <rect width="820" height="430" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">구획증후군 — 칸 안의 압력이 혈류를 막는다</text>
  <line x1="32" y1="60" x2="788" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(230,250)">
    <circle r="135" fill="#f3d9c2" stroke="#c98248" stroke-width="4"/>
    <circle r="118" fill="#f6b8be" stroke="#d98a90" stroke-width="2"/>
    <line x1="-118" y1="0" x2="118" y2="0" stroke="#cda" stroke-width="2" opacity="0.5"/>
    <line x1="0" y1="-118" x2="0" y2="118" stroke="#cda" stroke-width="2" opacity="0.5"/>
    <circle cx="0" cy="0" r="20" fill="#fff" stroke="#8b6a4f" stroke-width="3"/><text x="0" y="5" font-size="11" text-anchor="middle" fill="#8b6a4f">뼈</text>
    <g fill="#b23039"><path d="M0 -150 l8 16 l-16 0 Z"/><path d="M0 150 l8 -16 l-16 0 Z"/><path d="M-150 0 l16 8 l0 -16 Z"/><path d="M150 0 l-16 8 l0 -16 Z"/></g>
    <text x="0" y="-160" font-size="13" fill="#b23039" text-anchor="middle" font-weight="700">부종 → 압력↑</text>
  </g>
  <g font-size="15" fill="#3a4654">
    <text x="450" y="120" font-size="17" font-weight="800" fill="#b23039">5P (특히 조기)</text>
    <text x="450" y="152">*안 듣는 점증 통증</text>
    <text x="450" y="180">*수동 신전 시 극심한 통증</text>
    <text x="450" y="208">Paresthesia 이상감각</text>
    <text x="450" y="236">Pallor 창백 · Paralysis 마비</text>
    <text x="450" y="264">Pulselessness 무맥(후기·함정)</text>
    <text x="450" y="302" font-weight="800" fill="#b23039">석고 제거·사지 심장높이</text>
    <text x="450" y="330" font-weight="800" fill="#b23039">→ 응급 근막절개</text>
  </g>
</svg>'''

SVG["edh_sdh_ct"]='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 430" font-family="''' + FONT + '''">
  <rect width="840" height="430" rx="18" fill="#fff"/>
  <text x="32" y="46" font-size="24" font-weight="800" fill="#1a2a3a">두부 CT — 경막외(볼록렌즈) vs 경막하(초승달)</text>
  <line x1="32" y1="60" x2="808" y2="60" stroke="#e3e8ee" stroke-width="2"/>
  <g transform="translate(210,240)">
    <circle r="150" fill="#1a2330" stroke="#3a4654" stroke-width="3"/>
    <circle r="120" fill="#586273"/>
    <path d="M-118 -22 A120 120 0 0 1 -70 -98 A86 40 0 0 0 -118 -22 Z" fill="#e6edf3"/>
    <text x="0" y="170" font-size="17" font-weight="800" fill="#b23039" text-anchor="middle">EDH — 볼록렌즈(lens)</text>
    <text x="0" y="194" font-size="13" fill="#5b6876" text-anchor="middle">동맥성·중경막동맥 · 의식명료기</text>
  </g>
  <g transform="translate(630,240)">
    <circle r="150" fill="#1a2330" stroke="#3a4654" stroke-width="3"/>
    <circle r="120" fill="#586273"/>
    <path d="M-120 0 A120 120 0 0 1 -10 -119 A150 150 0 0 0 -120 0 Z" fill="#e6edf3"/>
    <text x="0" y="170" font-size="17" font-weight="800" fill="#b23039" text-anchor="middle">SDH — 초승달(crescent)</text>
    <text x="0" y="194" font-size="13" fill="#5b6876" text-anchor="middle">교정맥·뇌좌상 동반·예후 나쁨</text>
  </g>
</svg>'''

# ── 외과/외상 G ──
SVG["appendicitis_flow"]=_flow("급성 충수염 — 폐색에서 천공까지",[("충수 내강 폐색","분변석 등"),("내압↑·세균 증식",""),("염증·허혈",""),("괴저·천공","복막염")],footer="배꼽주위→우하복부 이동통·McBurney 반발통 · 가임여성은 자궁외임신 배제")
SVG["mcburney_panel"]=_panel("충수염 — 단서·처치",["*이동통(배꼽→RLQ)·McBurney 반발통","Rovsing·요근·폐쇄근 징후","CT(성인)/초음파(소아·임신)·임신검사","*충수절제(복강경)이 표준","금식·수액·진통·경험적 항생제"],sub="시간 끌면 천공",accent="#37474f")
SVG["hernia_flow"]=_flow("감돈·교액 탈장",[("탈장 내용물 끼임","감돈"),("정맥울혈·부종",""),("동맥 차단·허혈","교액"),("괴사·천공","")],footer="환납 안 되는 압통·발적+구토 → 교액 응급수술 · 무리한 도수정복 금지")
SVG["hernia_panel"]=_panel("탈장 — 교액 신호·처치",["환납 안 되는 압통성 종괴","*발적·구토·장폐색→교액","*무리한 환납 금지(괴사장 복강내)","금식·수액·비위관","교액·괴사 의심→즉시 외과(장 절제)"],sub="교액=응급수술",accent="#37474f")
SVG["abdtrauma_flow"]=_flow("복부 외상 — 겉보다 속",[("둔상/관통상",""),("실질장기 출혈 / 천공",""),("복강내 대량출혈",""),("쇼크","")],footer="둔상=비장·간 출혈 / 관통=천공·오염 · 후복막 출혈은 안 보임")
SVG["fast_panel"]=_panel("복부 외상 — 평가·처치",["*1차평가 ABCDE","*불안정+FAST 양성→즉시 개복","안정→조영 CT로 정밀 평가","*박힌 관통물 제거 금지(고정 이송)","수액·균형수혈·source control"],sub="불안정은 영상보다 수술",accent="#37474f")
SVG["hemoshock_flow"]=_flow("출혈성 쇼크 — 멈추고 채운다",[("대량 실혈",""),("순환혈액량↓",""),("저관류·젖산↑",""),("저체온·산증·응고병","악순환")],footer="출혈통제 우선 · 1:1:1 균형수혈 · 조기 TXA·칼슘·보온 · 허용적 저혈압")
SVG["transfusion_panel"]=_panel("출혈성 쇼크 — 처치",["*출혈 통제 먼저(압박·지혈대·바인더)","*적혈구:혈장:혈소판 ≈ 1:1:1","결정질 최소화(희석성 응고병)","조기 TXA·칼슘 보충·가온/보온","*미통제 출혈은 허용적 저혈압"],sub="죽음의 삼각형 차단",accent="#b23039")
SVG["limbisch_flow"]=_flow("급성 사지 동맥폐색",[("색전/혈전",""),("동맥 폐색",""),("원위부 허혈","근육·신경"),("괴사(수시간)","")],footer="6P · 시간=조직 · 즉시 헤파린+혈관팀 · 재관류 후 구획증후군")
SVG["sixp_panel"]=_panel("사지 허혈 — 6P·처치",["Pain·Pallor·Pulselessness","Paresthesia·Paralysis·냉감","*마비·감각소실=진행된 허혈","*의심 즉시 헤파린·혈관팀","재관류(혈전제거/용해)→구획·고칼륨 감시"],sub="골든타임 싸움",accent="#37474f")
SVG["mesisch_flow"]=_flow("장간막 허혈 — 늦으면 치명",[("색전/혈전/저관류",""),("장 혈류 차단",""),("장 허혈·괴사",""),("복막염·패혈증","")],footer="‘통증>소견’ 불균형 · AF 노인 갑작스런 복통 · 젖산↑=괴사")
SVG["mesisch_panel"]=_panel("장간막 허혈 — 진단·처치",["*통증은 극심한데 소견 경미","AF·심부전 노인 갑작스런 복통","*CT 혈관조영(1차 확진)","젖산↑·대사성 산증=괴사 진행","항응고+재개통+괴사장 절제"],sub="진단 지연=사망",accent="#37474f")
SVG["giperf_flow"]=_flow("소화관 천공",[("궤양 등으로 천공",""),("위산·내용물 누출",""),("복막 자극·오염",""),("복막염·패혈증","")],footer="갑작스런 심한 상복통·판자배 · free air · 금식·항생제·수술")
SVG["giperf_panel"]=_panel("천공 — 단서·처치",["갑작스런 극심한 상복통→전반화","*판자배(강직)·반발통","*X선/CT 유리공기(free air)","금식·비위관·수액·광범위 항생제·PPI","*응급수술(봉합·세척)"],sub="free air=천공",accent="#37474f")
SVG["nf_panel"]=_panel("괴사성 근막염 — 응급",["*소견보다 극심한 통증·빠른 진행","수포·피부괴사·捻발음·전신독성","*수술적 탐색이 확진","*응급 변연절제(항생제만으론 불충분)","광범위 항생제+패혈증 소생"],sub="시간=생명",accent="#37474f")
SVG["anorectal_panel"]=_panel("항문직장 응급",["항문주위 농양: 발적·압통·파동감","*농양→절개배농(항생제만 부족)","혈전성 외치핵: 초기엔 절제·보존","*당뇨·면역저하 회음부 감염→푸르니에 괴저","발열·광범위 발적→심부·괴사성"],sub="농양은 배농",accent="#37474f")
SVG["wound_flow"]=_flow("상처 관리 — 세척이 8할",[("열상·자상·교상",""),("대량 세척·이물제거",""),("신경·혈관·건 평가",""),("봉합 전략 결정","")],footer="고오염·교상=지연봉합 · 파상풍·동물교상 광견병 예방")
SVG["wound_panel"]=_panel("상처 — 평가·예방",["*신경·혈관·건 손상 평가(손·손목)","대량 세척·이물·괴사조직 제거","깨끗·신선=일차봉합","*고오염·교상·지연=지연봉합·개방","파상풍 톡소이드±면역글로불린"],sub="세척·구조물 평가",accent="#37474f")
SVG["fb_panel"]=_panel("이물 — 무엇을·어디에",["*식도 단추전지→수시간 내 괴사(응급 제거)","*자석 2개↑·날카로운 것→천공 위험","기도이물·완전폐색→기도응급","무증상 둔한 이물→경과 관찰","X선/CT로 위치·개수 확인"],sub="고위험은 즉시 제거",accent="#37474f")
SVG["solidorgan_panel"]=_panel("간·비장 손상",["좌/우상복부 둔상·견부 방사통(Kehr)","*불안정→즉시 개복지혈","*안정→CT 등급→관찰·혈관색전","관찰 중 Hb↓·악화→지연출혈","비장절제 후 협막세균 예방접종"],sub="안정=관찰, 불안정=수술",accent="#37474f")
# ── 화상 B ──
SVG["burn_transfer_criteria"]=_panel("화상센터 전원 기준",["대면적·전층(3도) 화상","*얼굴·손·발·회음·주요 관절","*전기·화학·흡입 손상·동반외상","소아·고령·중대 기저질환","→ 화상센터 전원 고려"],sub="중증·특수부위·특수기전",accent="#bf360c")
SVG["inhal_flow"]=_flow("흡입 손상 — 기도가 먼저 죽인다",[("밀폐공간 화재",""),("열·연기·유독가스",""),("상기도 부종(진행성)",""),("기도 폐색·ARDS","")],footer="안면화상·그을린 코털·쉰목소리·검댕가래 → 조기 삽관 · CO·시안화물 동반")
SVG["inhal_panel"]=_panel("흡입 손상 — 처치",["*부종 진행성→‘이른’ 기관삽관","*CO중독은 SpO₂ 정상처럼 보임","CO-Hb 측정·고농도 산소","시안화물 의심(젖산↑)→하이드록소코발라민","폐손상→폐보호 환기"],sub="늦으면 삽관 불가",accent="#bf360c")
SVG["parkland_flow"]=_flow("화상 수액 — 왜 필요한가",[("광범위 화상",""),("모세혈관 누출",""),("제3공간 체액 이동",""),("저혈량 쇼크","")],footer="Parkland: 4mL×kg×TBSA, 첫8h 절반(수상시각 기준)")
SVG["parkland_panel"]=_panel("Parkland — 적정·주의",["4mL × 체중 × TBSA(%), 첫8h 1/2","*‘수상 시각’ 기준 계산","*소변량으로 적정(성인 0.5mL/kg/h)","과대소생→구획증후군·폐부종","과소→신손상 / 2도 이상만 TBSA"],sub="공식은 시작점, 소변량이 진짜",accent="#bf360c")
SVG["chem_flow"]=_flow("화학 화상 — 계속 타는 화상",[("화학물질 접촉",""),("물질 잔존·반응 지속",""),("시간 비례 손상",""),("세척으로 정지","")],footer="대량·장시간 세척(분말은 먼저 털기) · 알칼리>산 깊이 · 중화제 지양")
SVG["chem_panel"]=_panel("화학 화상 — 처치",["*오염 의복·분말 제거 후 다량 물 세척","*분말은 물 붓기 전 먼저 털어내기","중화제 지양(발열로 악화)","*불산(HF)→칼슘(저칼슘·부정맥)","눈 화상→즉시·지속 대량 세척"],sub="대량 세척이 1순위",accent="#bf360c")
SVG["elec_flow"]=_flow("전기 화상 — 빙산형 손상",[("전류 통과",""),("심부 근육·신경 손상",""),("부정맥·근융해",""),("고칼륨·신손상·구획","")],footer="입·출구보다 경로 손상 큼 · 심전도·CK·소변색 감시")
SVG["elec_panel"]=_panel("전기 화상 — 처치",["표면 작아도 심부 광범위 손상","*전류 심장 통과→부정맥(지속 심전도)","*어두운 소변·CK↑→횡문근융해","적극 수액·소변량 유지·고칼륨 감시","통과부 부종·통증→구획증후군(근막절개)"],sub="심장·근융해·구획",accent="#bf360c")
SVG["burnwound_panel"]=_panel("화상 상처·감염",["세척·국소 항균제·드레싱·변연절제","*발열·진물·악취·전신악화→화상 패혈증","예방적 ‘전신’ 항생제는 권장X(감염시 치료)","*사지·흉부 환상 전층화상→가피절개","고열량·고단백 영양·통증·파상풍"],sub="감염과의 싸움",accent="#bf360c")
SVG["cold_flow"]=_flow("동상·저체온 — 한랭손상",[("한랭 노출",""),("조직 빙결/심부체온↓",""),("혈관·세포 손상",""),("괴사 / 부정맥","")],footer="동상=급속 재가온(문지름·재동결 금지) · 저체온=중심 재가온·부드럽게")
SVG["cold_panel"]=_panel("동상·저체온 — 처치",["동상: 따뜻한 물 급속 재가온","*마사지·문지름 금지 / 재동결 위험시 보류","저체온: 젖은옷 제거·가온수액·중심 재가온","*거친 조작→심실세동(부드럽게)","‘따뜻해질 때까지 사망선고 보류’"],sub="재가온이 핵심",accent="#bf360c")
# ── 정형 O ──
SVG["compartment_panel"]=_panel("구획증후군 — 처치",["*진통제에 안 듣는 점증 통증","*수동신전 시 극심한 통증","맥박은 마지막까지(‘맥 있으니 괜찮다’ 금물)","조이는 석고·붕대 제거·사지 심장높이","*지연→비가역 괴사→응급 근막절개"],sub="조기 통증이 단서",accent="#4e342e")
SVG["pelvis_flow"]=_flow("골반골절 — 후복막 대량출혈",[("고에너지 외상",""),("골반환 파괴",""),("정맥얼기·동맥 손상",""),("후복막 대량출혈(안 보임)","")],footer="겉 경미해도 쇼크면 의심 · 큰돌기 골반바인더")
SVG["pelvis_panel"]=_panel("골반골절 — 처치",["불안정 골반+저혈압→후복막 출혈","*골반바인더(큰돌기 높이)","*골반 반복 흔들기 금지(혈괴 탈락)","균형수혈+색전술/외고정","요도구 출혈·회음부 혈종→요도손상"],sub="바인더로 즉시 안정화",accent="#4e342e")
SVG["openfx_flow"]=_flow("개방성 골절 — 감염이 핵심",[("뼈-외부 교통",""),("오염",""),("골·연부조직 감염",""),("골수염","")],footer="조기 항생제·파상풍 · 멸균드레싱·사진(반복 노출 금지) · 수술 세척")
SVG["openfx_panel"]=_panel("개방성 골절 — 처치",["*조기 경험적 항생제+파상풍","원위 신경·혈관·구획 평가","*멸균 식염수 거즈로 덮고 사진","반복 노출 금지→수술장 세척·변연절제","심한 오염·혈관손상→사지 구제 응급"],sub="감염·골수염 예방",accent="#4e342e")
SVG["spine_flow"]=_flow("척추·척수 손상 — 이차손상 예방",[("외상",""),("척추 골절·탈구",""),("척수 압박·부종",""),("부적절 조작→이차손상","")],footer="전척추 고정·통나무 굴리기 · 신경성 쇼크(저혈압+서맥)")
SVG["spine_panel"]=_panel("척추·척수 손상 — 처치",["*의심→전척추 고정 유지(조작 금지)","사지 운동·감각 레벨 기록","*저혈압+서맥=신경성 쇼크(출혈도 배제)","고위 경추→호흡근 마비 위협","악화→재평가·영상·신경외과"],sub="움직이지 마",accent="#4e342e")
SVG["disloc_flow"]=_flow("관절 탈구",[("관절면 이탈",""),("변형·기능소실",""),("신경·혈관 견인",""),("조기 정복 필요","")],footer="고관절 후방탈구(괴사)·무릎탈구(슬와동맥)=조기 정복 응급")
SVG["disloc_panel"]=_panel("탈구 — 정복 원칙",["변형·탄성고정","*정복 전·후 신경·혈관 평가 필수","*고관절 후방탈구→대퇴골두 괴사","*무릎탈구→슬와동맥 손상 호발","정복 후 영상 확인·고정"],sub="정복 전후 신경혈관",accent="#4e342e")
SVG["septicarthritis_flow"]=_flow("화농성 관절염 — 시간 싸움",[("세균 감염(혈행 등)",""),("관절액 화농",""),("연골 파괴",""),("비가역 손상","")],footer="단관절 발적·열감·운동통+발열 · 관절천자(배양)→응급 배농·세척")
SVG["septicarthritis_panel"]=_panel("화농성 관절염·골수염",["단일 관절 발적·열감·심한 운동통+발열","*관절천자(백혈구·배양)—항생제 전","CBC·CRP·ESR·혈액배양·MRI(골수염)","*응급 배농·세척(항생제 단독 부족)","경험적 정맥 항생제→표적·장기"],sub="연골=시간싸움",accent="#4e342e")
SVG["amputation_storage_panel"]=_panel("절단편 보존 — 올바르게",["*생리식염수 적신 거즈로 감싸기","→ 방수 봉투 → 얼음물에 담가 냉장","*얼음·드라이아이스 직접 접촉 금지(동상)","물에 담가 불리지 말 것","허혈시간 단축·재접합 기관 이송"],sub="얼음 직접 접촉 금지",accent="#4e342e")
SVG["amputation_bleed_panel"]=_panel("절단 — 환자 처치",["*직접압박·거상→실패 시 지혈대","수액·수혈 소생·진통·파상풍","환자 출혈통제가 절단편보다 우선","근위부일수록 허혈에 취약(시간↓)","재접합 가능 기관으로 신속 동반 이송"],sub="환자 출혈 통제 먼저",accent="#4e342e")
SVG["fes_flow"]=_flow("지방색전 — 골절 후 24~72h",[("장골 골절",""),("골수 지방 유입",""),("폐·뇌 색전+염증",""),("저산소·신경증상","점상출혈")],footer="고전 3징(저산소+의식변화+점상출혈) · 지지치료 · 조기고정 예방")
SVG["fes_panel"]=_panel("지방색전 — 평가·처치",["장골골절 후 24~72h 발생","*저산소+신경증상+점상출혈(상체)","특이치료 없음→산소·호흡 지지","PE·폐좌상·외상성 뇌손상 감별","*조기 골절 고정이 예방"],sub="지지치료+예방",accent="#4e342e")
SVG["rhabdo_flow"]=_flow("압궤·횡문근융해",[("근육 손상·압박",""),("세포내 물질 유출","K·미오글로빈·CK"),("미오글로빈뇨",""),("고칼륨·신손상","")],footer="콜라색 소변·CK↑ · 적극 수액·소변량 · 재관류 시 고칼륨")
SVG["rhabdo_panel"]=_panel("횡문근융해 — 처치",["*콜라색 소변+CK 급상승","*적극 수액·소변량 유지(신보호)","*고칼륨혈증·ECG 변화 감시","장시간 압박 해제 시 고칼륨 급상승 대비","구획증후군 병발 평가(근막절개)"],sub="수액·소변·고칼륨",accent="#4e342e")
SVG["fx_assess_panel"]=_panel("골절 — 기본 평가",["개방/폐쇄·변형·압통·부종","*원위 신경·혈관(5P 경계) 확인","동반손상·구획증후군 평가","개방·신경혈관손상·구획=응급","고정 전·후 신경혈관 재평가"],sub="신경혈관이 먼저",accent="#4e342e")
SVG["fx_fix_panel"]=_panel("골절 — 고정·처치",["적절 정렬 후 부목(상·하 관절 포함)","*부목 과도 조임→구획증후군","거상·냉찜질(RICE)·진통","개방창은 멸균드레싱·항생제","*소아 성장판 손상은 미묘→압통 주의"],sub="부목·RICE·통증",accent="#4e342e")
# ── 흉부 T ──
SVG["hemothorax_flow"]=_flow("대량 혈흉",[("폐·흉벽·대혈관 손상",""),("흉강 내 혈액 축적",""),("저혈량+폐 압박",""),("쇼크·가스교환 장애","")],footer="타진 둔탁(기흉은 과공명) · 흉관 · 초기 1.5L·지속출혈=개흉")
SVG["hemothorax_panel"]=_panel("대량 혈흉 — 처치",["편측 호흡음 소실+타진 둔탁+쇼크","*흉관 삽입(진단+배액+정량화)","*즉시 ~1.5L 또는 지속 다량→개흉","균형수혈로 소생하며 흉부외과","기흉(과공명)과 타진으로 감별"],sub="둔탁=혈흉",accent="#01579b")
SVG["flail_flow"]=_flow("동요가슴·폐좌상",[("늑골 다발골절",""),("흉벽 분절 역설운동",""),("기저 폐좌상(지연성)",""),("점진적 저산소","")],footer="진짜 문제는 폐좌상 · 통증조절 핵심 · 과수액 주의·환기보조")
SVG["flail_panel"]=_panel("동요가슴 — 처치",["역설호흡·흉벽 변형·압통","*진짜 위험=기저 폐좌상(지연성 저산소)","*통증 조절(얕은 호흡·무기폐 예방)","산소·악화 시 NIV/기계환기","과도한 수액 회피(좌상 폐 부종)"],sub="통증조절+산소화 추세",accent="#01579b")
SVG["tampo_trauma_panel"]=_panel("외상성 심장눌림증",["전흉부 외상+Beck 3징·기이맥","*eFAST(심낭삼출·우심 허탈)","*소량에도 급속 진행(분초)","천자(임시)→응급 개흉(근본)","이뇨·혈관확장 금기(전부하 유지)"],sub="eFAST→개흉",accent="#01579b")
SVG["aorta_trauma_panel"]=_panel("외상성 대동맥 손상",["고에너지 급감속+종격동 확대","*혈압·심박 먼저 낮춤(β차단)","혈관확장만 단독 금지(반사빈맥)","CT 혈관조영(확진)","TEVAR/수술 — 파열 전 응급"],sub="전단력 먼저 낮추기",accent="#01579b")
SVG["boerhaave_flow"]=_flow("식도 파열(Boerhaave)",[("심한 구토 등",""),("식도 전층 파열",""),("종격동 오염",""),("종격동염·패혈증","")],footer="Mackler 3징(구토+흉통+피하기종) · AMI·췌장염 오인 · 조영/CT · 수술")
SVG["boerhaave_panel"]=_panel("식도 파열 — 단서·처치",["*심한 구토 후 흉통+피하기종","AMI·췌장염으로 오인 주의","수용성 조영 식도조영/CT","금식·광범위 항생제·수액 소생","*수술적 복원·배액(조기)"],sub="종격동염=치명",accent="#01579b")
SVG["penetrating_flow"]=_flow("흉부 관통상·심장 손상",[("심장위험구역 관통",""),("심장·대혈관 손상",""),("압전 또는 대량혈흉",""),("급사 위험","")],footer="eFAST로 감별 · 관통물 고정(제거 금지) · 즉시 수술·소생적 개흉")
SVG["penetrating_panel"]=_panel("흉부 관통상 — 처치",["*심장위험구역 관통→심장손상 가정","*eFAST(심낭·흉강) 즉시","압전(Beck3징) vs 대량혈흉 감별","*박힌 관통물 제거 금지(고정)","수액·균형수혈→즉시 수술"],sub="압전 vs 혈흉",accent="#01579b")
SVG["chesttube_panel"]=_panel("흉관 — 관리·관찰",["안전삼각(중~전액와선, 4·5늑간) 삽입","*호흡성 파동(oscillation)=개방·정상","*지속 기포=공기누출","갑작스런 다량 혈성 배액→보고","배액량·색 시간마다 기록"],sub="파동·기포·배액 관찰",accent="#01579b")
SVG["chesttube_safety_panel"]=_panel("흉관 — 안전·응급",["*배액병은 항상 흉부보다 아래(역류 방지)","*함부로 클램프 금지(긴장성 기흉)","관 이탈→삽입부 폐쇄드레싱·관찰","연결 분리→정해진 절차","제거는 호기말/발살바 시 신속+밀폐"],sub="클램프·역류 주의",accent="#01579b")
# ── 신경외과 NS ──
SVG["tbi_flow"]=_flow("외상성 뇌손상 — 2차손상 예방",[("외상(1차 손상)",""),("저산소·저혈압(2차)",""),("뇌압↑·부종",""),("뇌관류↓·악화","")],footer="GCS 반복(추세)·동공 · 산소·혈압 사수 · 악화=CT·신경외과")
SVG["gcs_panel"]=_panel("TBI — 평가·처치",["GCS 13~15 경증 / 9~12 중등도 / ≤8 중증","*GCS 하락·동공 부동→병변 진행(CT)","*산소·혈압 유지(2차손상 예방)","상체 30°·중립·발열·경련 관리","항응고·고령은 경미 외상도 영상"],sub="GCS 추세가 핵심",accent="#283593")
SVG["edh_panel"]=_panel("경막외 혈종(EDH)",["*의식명료기 후 급격한 악화","CT 볼록렌즈·측두골 골절","한쪽 동공산대+반대편 마비=탈출","*응급 개두술(빠르면 예후 양호)","ABC·뇌압·응고 역전(가교)"],sub="명료기→급변",accent="#283593")
SVG["sdh_panel"]=_panel("급성 경막하 혈종",["CT 초승달·정중선 이동","*뇌좌상 동반 흔함→예후 나쁨","두꺼운 혈종·뇌이동→개두술","ICP·2차손상 적극 관리","고령·항응고제→응고 역전"],sub="초승달·예후 주의",accent="#283593")
SVG["csdh_flow"]=_flow("만성 경막하 혈종",[("노인·뇌위축",""),("경미 외상·미세출혈",""),("수주에 걸쳐 축적",""),("점진적 증상","")],footer="점진적 두통·인지·보행·편마비 → 치매/뇌졸중 오인 주의 · 천공배액")
SVG["csdh_panel"]=_panel("만성 SDH — 단서·처치",["*노인의 점진적 두통·인지·보행장애","경미 외상력·항응고제 복용","CT: 저/혼합 밀도(양측성도)","*증상성·큰 혈종→천공배액(극적 호전)","소형 무증상→관찰·항응고 검토"],sub="치매로 오인 금지",accent="#283593")
SVG["icp_flow"]=_flow("두개내압 상승·뇌탈출",[("두개내 용적 증가",""),("보상 한계 초과",""),("ICP 급등",""),("뇌관류↓·탈출","")],footer="Cushing 3징·동공·자세 · 상체거상·고삼투·과환기(일시)·감압")
SVG["icp_panel"]=_panel("ICP 상승 — 처치",["*Cushing 3징(고혈압+서맥+불규칙호흡)","동공 부동·산대·의식 급저하","상체 30°·중립·정상 환기·발열관리","*고삼투(만니톨/고장식염수)","과환기는 일시 가교 · 원인제거·감압"],sub="시간 싸움",accent="#283593")
SVG["skullfx_flow"]=_flow("두개골 골절",[("두부 충격",""),("선상/함몰/두개저",""),("CSF 누출/뇌 압박",""),("감염/뇌손상","")],footer="두개저 단서(raccoon·Battle·CSF누출) · 비강삽입 금지 · 함몰=수술")
SVG["skullfx_panel"]=_panel("두개골 골절 — 단서·처치",["raccoon eyes·Battle sign·맑은 비루/이루","*두개저 골절→비강 비위관 금지(경구로)","CSF 누출→수막염 위험·감염 감시","*개방성·심한 함몰→수술","고막혈종도 두개저 단서"],sub="비강삽입 금지",accent="#283593")
SVG["penhead_flow"]=_flow("관통성 두부 손상",[("이물·발사체 관통",""),("경로상 뇌·혈관 손상",""),("출혈·오염",""),("감염·경련","")],footer="박힌 이물 고정(제거 금지) · 항생제·파상풍·항경련 · 수술 정리")
SVG["penhead_panel"]=_panel("관통성 두부 — 처치",["*박힌 이물 현장 제거 금지(고정)","광범위 항생제·파상풍·항경련제","경로상 혈관손상→지연출혈 가능","ABC·뇌압 관리","총상은 광범위 손상·예후 불량"],sub="이물 고정",accent="#283593")
SVG["hydroceph_flow"]=_flow("급성 수두증",[("CSF 순환·흡수 장애",""),("뇌실 확장",""),("두개내압↑",""),("의식저하·탈출 위험","")],footer="두통·구토·상방주시장애 · 폐쇄성→뇌실외배액(EVD) 응급")
SVG["hydroceph_panel"]=_panel("급성 수두증 — 처치",["두통·구토·의식저하·상방주시장애","CT/MRI: 뇌실 확장·폐쇄·원인","*폐쇄성→뇌실외배액(EVD) 응급","원인(출혈·종양·감염) 치료","지속→영구 션트(VP)"],sub="EVD로 감압",accent="#283593")
SVG["brainabscess_flow"]=_flow("뇌농양 — 덩어리 감염",[("인접/혈행 전파",""),("뇌실질 화농",""),("종괴효과·ICP↑",""),("국소징후·뇌손상","")],footer="발열+두통+국소징후 · 배농+장기 항생제 · 수막염과 구분")
SVG["brainabscess_panel"]=_panel("뇌농양 — 처치",["발열+두통+국소신경징후+의식저하","조영 MRI/CT: 고리조영 종괴","*종괴라 배농 필요(항생제만 부족)","종괴효과 시 요추천자 신중","부비동·중이·치아·심내막염 원발 탐색"],sub="배농+장기 항생제",accent="#283593")
SVG["shunt_flow"]=_flow("VP 션트 기능부전",[("션트 폐쇄/단절/과배액",""),("CSF 배출 실패",""),("뇌실 재확장·ICP↑",""),("응급","")],footer="션트 환자 두통·구토·의식저하→기능부전 의심 · 발열·복부증상=감염")
SVG["shunt_panel"]=_panel("VP 션트 — 평가·처치",["*션트 환자 ICP 재상승 증상→의심","뇌 CT(뇌실 크기)·shunt series(단절)","*막히면 뇌압 급상승(응급)","발열·션트 경로 발적/복부→감염","폐쇄=교정/교체 · 감염=제거+항생제+외배액"],sub="신경외과 연계",accent="#283593")
SVG["cauda_flow"]=_flow("마미증후군",[("대형 추간판탈출 등",""),("마미(신경다발) 압박",""),("배뇨·하지·회음 장애",""),("비가역(지연 시)","")],footer="안장마취·배뇨장애·양하지 위약 → 응급 MRI→응급 감압(시간=기능)")
SVG["cauda_panel"]=_panel("마미증후군 — 핵심 3징",["*안장(회음) 감각저하","*방광·직장 장애(요저류/실금)","*양측 좌골신경통·하지 위약","잔뇨(방광스캔)·항문긴장도·MRI","허리통증 환자에서 배뇨·안장감각 확인"],sub="응급 감압",accent="#283593")
SVG["mscc_flow"]=_flow("전이성 척수 압박(MSCC)",[("척추 전이",""),("경막외 압박",""),("척수 허혈·부종",""),("진행성 신경결손","")],footer="암+진행성 등통증→신경결손 전 치료 · 즉시 스테로이드+전척추 MRI")
SVG["mscc_panel"]=_panel("MSCC — 단서·처치",["암 환자 진행성·야간 악화 등통증","하지 위약·감각저하·배뇨장애","*통증이 신경결손보다 선행(기회)","*의심 즉시 스테로이드+응급 전척추 MRI","방사선/수술 감압(보행 가능할 때)"],sub="마비 전에 잡기",accent="#283593")

SVG_MAP_SURG = {
 "G01":{"정의":"appendicitis_flow","증상":"mcburney_panel"},
 "G02":{"기전":"hernia_flow","증상":"hernia_panel"},
 "G03":{"기전":"abdtrauma_flow","검사":"fast_panel"},
 "G04":{"정의":"hemoshock_flow","평가":"transfusion_panel"},
 "G05":{"정의":"limbisch_flow","평가":"sixp_panel"},
 "G06":{"기전":"mesisch_flow","검사":"mesisch_panel"},
 "G07":{"정의":"giperf_flow","검사":"giperf_panel"},
 "G08":{"정의":"skin_cellulitis","평가":"nf_panel"},
 "G09":{"평가":"anorectal_panel"},
 "G10":{"정의":"wound_flow","평가":"wound_panel"},
 "G11":{"평가":"fb_panel"},
 "G12":{"평가":"solidorgan_panel"},
 "B01":{"깊이":"burn_depth","전원":"burn_transfer_criteria"},
 "B02":{"기전":"inhal_flow","검사":"inhal_panel"},
 "B03":{"원리":"parkland_flow","적정":"parkland_panel"},
 "B04":{"기전":"chem_flow","처치":"chem_panel"},
 "B05":{"기전":"elec_flow","검사":"elec_panel"},
 "B06":{"감염":"burnwound_panel"},
 "B07":{"전원":"burn_transfer_criteria"},
 "B08":{"분류":"cold_flow","처치":"cold_panel"},
 "O01":{"기전":"compartment","평가":"compartment_panel"},
 "O02":{"기전":"pelvis_flow","평가":"pelvis_panel"},
 "O03":{"분류":"openfx_flow","평가":"openfx_panel"},
 "O04":{"기전":"spine_flow","평가":"spine_panel"},
 "O05":{"기전":"disloc_flow","평가":"disloc_panel"},
 "O06":{"기전":"septicarthritis_flow","검사":"septicarthritis_panel"},
 "O07":{"절단편":"amputation_storage_panel","절단부":"amputation_bleed_panel"},
 "O08":{"기전":"fes_flow","검사":"fes_panel"},
 "O09":{"기전":"rhabdo_flow","평가":"rhabdo_panel"},
 "O10":{"평가":"fx_assess_panel","고정":"fx_fix_panel"},
 "T01":{"기전":"lung_pneumothorax","처치":"pneumo_tx"},
 "T02":{"기전":"hemothorax_flow","검사":"hemothorax_panel"},
 "T03":{"기전":"flail_flow","평가":"flail_panel"},
 "T04":{"기전":"tamponade","검사":"tampo_trauma_panel"},
 "T05":{"기전":"aortic_dissection","검사":"aorta_trauma_panel"},
 "T06":{"기전":"boerhaave_flow","검사":"boerhaave_panel"},
 "T07":{"기전":"penetrating_flow","평가":"penetrating_panel"},
 "T08":{"관리":"chesttube_panel","안전":"chesttube_safety_panel"},
 "NS01":{"분류":"tbi_flow","평가":"gcs_panel"},
 "NS02":{"기전":"edh_sdh_ct","검사":"edh_panel"},
 "NS03":{"기전":"edh_sdh_ct","검사":"sdh_panel"},
 "NS04":{"기전":"csdh_flow","검사":"csdh_panel"},
 "NS05":{"기전":"icp_flow","처치":"icp_panel"},
 "NS06":{"분류":"skullfx_flow","평가":"skullfx_panel"},
 "NS07":{"기전":"penhead_flow","평가":"penhead_panel"},
 "NS08":{"기전":"hydroceph_flow","검사":"hydroceph_panel"},
 "NS09":{"기전":"brainabscess_flow","검사":"brainabscess_panel"},
 "NS10":{"역할":"shunt_flow","검사":"shunt_panel"},
 "NS11":{"기전":"cauda_flow","평가":"cauda_panel"},
 "NS12":{"기전":"mscc_flow","검사":"mscc_panel"},
}
