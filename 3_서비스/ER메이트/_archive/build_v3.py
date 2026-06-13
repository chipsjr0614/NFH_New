#!/usr/bin/env python3
"""Build /Users/sungkwanchoi/NFH_New/nfh_v3/index.html
nursing_note.html을 그대로 오버레이에 임베드"""
import json, re

SRC     = '/Users/sungkwanchoi/NFH_New/er_mate/er_mate_v2.html'
NURSING = '/Users/sungkwanchoi/NFH_New/nursing/nursing_note.html'
DST     = '/Users/sungkwanchoi/NFH_New/nfh_v3/index.html'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. 원본 파일 읽기
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with open(SRC, 'r') as f:
    src = f.read()
with open(NURSING, 'r') as f:
    nursing_src = f.read()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. DB 정제 (불필요 항목 제거)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
db_match = re.search(r'const DB = (\{.*?\});\s*\n', src, re.DOTALL)
db = json.loads(db_match.group(1))
db['procedures'] = [p for p in db['procedures'] if p['id'] != 'Stroke']
# 사망 task 유지 (🕊️ 아이콘 사용)
REMOVE_GUIDES = {'CCU', 'Stroke Unit', 'LICU', 'CIV', '이송'}
db['guides']     = [g for g in db['guides'] if g['id'] not in REMOVE_GUIDES]
db.pop('nursing', None)

# Fix 3: 이송 부서 전화번호 제거 (xlsx 기준 — 번호 없음)
for p in db['procedures']:
    if '이송 부서' in p:
        p['이송 부서'] = [re.sub(r'\(☏[^)]*\)', '(☏)', x) for x in p['이송 부서']]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. nursing_note.html 파싱
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS 추출 (html/body/* 글로벌 리셋 제거 후 스코핑)
nursing_css_raw = re.search(r'<style>(.*?)</style>', nursing_src, re.DOTALL).group(1)
nursing_css_raw = re.sub(r'\*\s*\{[^}]*\}', '', nursing_css_raw)           # * reset 제거
nursing_css_raw = re.sub(r'html\s*,\s*body\s*\{[^}]*\}', '', nursing_css_raw)  # html,body 제거
nursing_css_raw = re.sub(r'html\s*\{[^}]*\}', '', nursing_css_raw)
nursing_css_raw = re.sub(r'body\s*\{[^}]*\}', '', nursing_css_raw)
# popup z-index 100 → 450 (overlay z-index 300보다 높게)
nursing_css_raw = nursing_css_raw.replace('z-index:100', 'z-index:450')

# 모든 CSS 규칙에 #ov-nursing 스코프 추가
def scope_css(css, scope):
    result = []
    i = 0
    while i < len(css):
        # 공백/줄바꿈 건너뜀
        if css[i] in ' \t\n\r':
            result.append(css[i]); i += 1; continue
        # { 찾기
        j = i
        while j < len(css) and css[j] != '{':
            j += 1
        if j >= len(css):
            result.append(css[i:]); break
        selector = css[i:j].strip()
        # { } 블록 찾기 (중첩 고려)
        depth = 0; k = j
        while k < len(css):
            if css[k] == '{': depth += 1
            elif css[k] == '}':
                depth -= 1
                if depth == 0: break
            k += 1
        block = css[j:k+1]
        # @media 처리: 내부 규칙에 재귀 적용
        if selector.lstrip().startswith('@media'):
            inner = scope_css(block[1:-1], scope)
            result.append(f'{selector} {{{inner}}}\n')
        elif selector.strip():
            parts = [s.strip() for s in selector.split(',') if s.strip()]
            scoped = ', '.join(f'{scope} {p}' for p in parts)
            result.append(f'{scoped} {block}\n')
        i = k + 1
    return ''.join(result)

nursing_css_scoped = scope_css(nursing_css_raw, '#ov-nursing')

# HTML body 추출 (5개 스크린 + 팝업)
nursing_html_body = re.search(r'<body>(.*?)</body>', nursing_src, re.DOTALL).group(1).strip()

# JS 전체 추출
nursing_js_full = re.search(r'<script>(.*?)</script>', nursing_src, re.DOTALL).group(1)

# 동공크기 → Rt/Lt 2칸 분리
nursing_js_full = re.sub(
    r'\{"text":"동공크기 :","note":"([^"]*)"\}',
    r'{"text":"동공크기 Rt:","note":"\1"},{"text":"동공크기 Lt:","note":"\1"}',
    nursing_js_full
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. 오버레이 추가 CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERLAY_CSS = """
/* ── Overlays ── */
.overlay{position:fixed;inset:0;z-index:300;display:flex;flex-direction:column;
  transform:translateY(100%);transition:transform 0.35s cubic-bezier(0.4,0,0.2,1);background:var(--bg)}
.overlay.show{transform:translateY(0)}
.overlay-header{background:var(--primary-dk);color:white;
  padding:env(safe-area-inset-top) 16px 0;
  min-height:calc(52px + env(safe-area-inset-top));
  display:flex;align-items:flex-end;gap:12px;position:sticky;top:0;z-index:100;
  box-shadow:0 2px 8px rgba(0,0,0,0.2);flex-shrink:0}
.overlay-header .btn-back,.overlay-header .ov-title{padding-bottom:12px}
.ov-title{flex:1;font-size:16px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.overlay-body{flex:1;overflow-y:auto;padding:0}
.ov-dim{position:fixed;inset:0;z-index:299;background:rgba(0,0,0,0.5);display:none}
.ov-dim.show{display:block}

/* ── 빠른실행 버튼 ── */
.quick-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:24px}
.quick-btn{background:var(--primary);color:white;border:none;border-radius:16px;
  padding:22px 12px;text-align:center;cursor:pointer;font-size:14px;font-weight:700;
  box-shadow:0 4px 14px rgba(4,138,129,0.3);transition:all 0.2s;line-height:1.5;width:100%}
.quick-btn:hover{background:#036B63;transform:translateY(-2px);box-shadow:0 6px 18px rgba(4,138,129,0.4)}
.quick-btn:active{transform:translateY(0)}
.quick-btn .qb-icon{font-size:28px;display:block;margin-bottom:6px}
/* ── 시술 칩 ── */
.proc-chips{display:flex;gap:8px;overflow-x:auto;padding:4px 0 12px;scrollbar-width:none;-webkit-overflow-scrolling:touch}
.proc-chips::-webkit-scrollbar{display:none}
.proc-chip{flex-shrink:0;background:var(--card);border:1.5px solid var(--border);border-radius:20px;
  padding:8px 15px;font-size:13px;font-weight:600;color:var(--text);cursor:pointer;white-space:nowrap;transition:.15s;outline:none}
.proc-chip:hover{border-color:var(--primary);color:var(--primary)}
.proc-chip:active{background:var(--primary);color:#fff;border-color:var(--primary)}
/* ── 섹션 헤더 ── */
.sec-hdr{display:flex;justify-content:space-between;align-items:center;margin:20px 0 10px}
.sec-hdr-title{font-size:12px;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.6px}
.sec-hdr-link{font-size:13px;color:var(--primary);cursor:pointer;font-weight:600}

/* ── Drug Calculator (다크모드 연동) ── */
.ov-calc{background:var(--card);color:var(--text);min-height:100%;padding:16px;font-family:-apple-system,sans-serif}
body.dark .ov-calc{background:#0d1117;color:#e6edf3;}
.ov-calc-tabs{display:flex;background:var(--bg);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:10}
body.dark .ov-calc-tabs{background:#161b22;border-bottom-color:#30363d;}
.ov-calc-tab{flex:1;padding:13px 6px;text-align:center;font-size:13px;font-weight:600;cursor:pointer;color:var(--text-muted);border-bottom:3px solid transparent;transition:.2s}
body.dark .ov-calc-tab{color:#8b949e;}
.ov-calc-tab.active{color:var(--primary);border-bottom-color:var(--primary)}
body.dark .ov-calc-tab.active{color:#58a6ff;border-bottom-color:#58a6ff}
.ov-calc-panel{display:none;padding:16px;max-width:1100px;margin:0 auto}
.ov-calc-panel.active{display:block}

/* ── Antibiotic ── */
.ab-search{width:100%;padding:12px 16px 12px 44px;border:2px solid var(--primary);border-radius:10px;font-size:15px;background:var(--bg);color:var(--text);outline:none;margin-bottom:16px}
.ab-search-wrap{position:relative}
.ab-search-icon{position:absolute;left:13px;top:50%;transform:translateY(-50%);font-size:18px;pointer-events:none}
.ab-result{background:var(--card);border-radius:12px;padding:16px;margin-top:8px;box-shadow:var(--shadow)}
.ab-row{display:flex;align-items:center;gap:10px;padding:9px 12px;border-bottom:1px solid var(--border);font-size:14px}
.ab-row:last-child{border-bottom:none}
.ab-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.ab-dot.ok{background:#22c55e}
.ab-dot.no{background:#ef4444}
.ab-dot.na{background:#94a3b8}
.ab-hint{font-size:12px;color:var(--text-muted);margin-bottom:12px}
.ab-divider{font-size:11px;font-weight:700;color:var(--text-muted);padding:8px 12px 4px;text-transform:uppercase;letter-spacing:.5px}
.ab-diluent-card{background:var(--card);border-radius:12px;padding:16px;margin-top:12px;box-shadow:var(--shadow)}
.ab-diluent-title{font-size:13px;font-weight:700;margin-bottom:10px;color:var(--text-muted)}
.ab-diluent-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border);font-size:14px}
.ab-diluent-row:last-child{border-bottom:none}
.ab-ok-badge{background:#dcfce7;color:#16a34a;padding:3px 10px;border-radius:6px;font-size:12px;font-weight:700}
.ab-no-badge{background:#fee2e2;color:#dc2626;padding:3px 10px;border-radius:6px;font-size:12px;font-weight:700}
.dark .ab-ok-badge{background:#14532d;color:#86efac}
.dark .ab-no-badge{background:#450a0a;color:#fca5a5}

/* ── Nursing 오버레이 (다크모드 연동, 스크롤) ── */
#ov-nursing { background: var(--bg) !important; }
body.dark #ov-nursing { background: #0a0a14 !important; }
#ov-nursing > .overlay-body {
  display: flex;
  flex-direction: column;
  overflow: hidden !important;
  flex: 1;
}
#ov-nursing .app { height: 100% !important; max-width: 100% !important; }
#ov-nursing .screen { min-height: 0; }
#ov-nursing .topbar { display: none !important; }

/* ── Nursing 라이트모드 오버라이드 ── */
body:not(.dark) #ov-nursing .app,
body:not(.dark) #ov-nursing .screen { background: var(--bg); }
body:not(.dark) #ov-nursing .body { background: var(--bg) !important; }
body:not(.dark) #ov-nursing .foot { background: var(--bg) !important; border-top-color: var(--border) !important; }
body:not(.dark) #ov-nursing .chk-item { border-bottom-color: var(--border) !important; color: var(--text) !important; }
body:not(.dark) #ov-nursing .chk-box { background: var(--card) !important; border-color: var(--border) !important; }
body:not(.dark) #ov-nursing .chk-text { color: var(--text) !important; }
body:not(.dark) #ov-nursing .prog { background: var(--border) !important; }
body:not(.dark) #ov-nursing .txt-input { background: var(--card) !important; color: var(--text) !important; border-color: var(--border) !important; }
body:not(.dark) #ov-nursing .combined-sec { background: var(--card) !important; border-color: var(--border) !important; }
body:not(.dark) #ov-nursing .opt-btn { background: var(--card) !important; color: var(--text) !important; border-color: var(--border) !important; }
body:not(.dark) #ov-nursing .slash-btn { background: var(--card) !important; color: var(--text-muted) !important; border-color: var(--border) !important; }
body:not(.dark) #ov-nursing .slash-btn.on { background: var(--primary) !important; color: white !important; }
body:not(.dark) #ov-nursing .nrs-btn { background: var(--card) !important; color: var(--text) !important; border-color: var(--border) !important; }
body:not(.dark) #ov-nursing .edu-item { background: var(--card) !important; border-color: var(--border) !important; color: var(--text) !important; }
body:not(.dark) #ov-nursing .popup-box { background: var(--bg) !important; }
body:not(.dark) #ov-nursing .popup-hdr { border-bottom-color: var(--border) !important; color: var(--text) !important; }
body:not(.dark) #ov-nursing .popup-foot { border-top-color: var(--border) !important; }
body:not(.dark) #ov-nursing .p-item { color: var(--text) !important; border-bottom-color: var(--border) !important; }
body:not(.dark) #ov-nursing .p-top-hdr,
body:not(.dark) #ov-nursing .p-sym-hdr { color: var(--text-muted) !important; border-bottom-color: var(--border) !important; }
body:not(.dark) #ov-nursing .screen-title { color: var(--text) !important; }
body:not(.dark) #ov-nursing .screen-sub { color: var(--text-muted) !important; }
body:not(.dark) #ov-nursing .sym-item { background: var(--card) !important; border-color: var(--border) !important; color: var(--text) !important; }
body:not(.dark) #ov-nursing .sym-sub { color: var(--text-muted) !important; }
body:not(.dark) #ov-nursing .cat-title { color: var(--text-muted) !important; }
body:not(.dark) #ov-nursing .branch-btn { background: var(--card) !important; border-color: var(--border) !important; color: var(--text) !important; }
body:not(.dark) #ov-nursing .fall-row { border-bottom-color: var(--border) !important; color: var(--text) !important; }

/* ── Nursing (원본 CSS 스코핑) ── */
""" + nursing_css_scoped

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. 오버레이 HTML
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OVERLAY_HTML = """
<!-- ── Overlay Dim ── -->
<div class="ov-dim" id="ovDim" onclick="closeAllOverlays()"></div>

<!-- ── Overlay A: 성인 계산기 ── -->
<div class="overlay" id="ov-adult">
  <div class="overlay-header">
    <button class="btn-back" onclick="closeOverlay('adult')">&#8592; 닫기</button>
    <span class="ov-title">💉 성인 응급 약물 계산기</span>
  </div>
  <div class="overlay-body">
    <div class="ov-calc">
      <div class="ov-calc-tabs">
        <div class="ov-calc-tab active" onclick="showCalcTab('adult','adult-calc')">💉 성인계산기</div>
        <div class="ov-calc-tab" onclick="showCalcTab('adult','info-calc')">🔍 약물정보</div>
      </div>
      <div id="adult-calc" class="ov-calc-panel active">
        <div style="display:flex;align-items:center;gap:12px;background:#161b22;border:1px solid #30363d;border-radius:10px;padding:14px 18px;margin-bottom:16px">
          <label style="font-size:14px;color:#8b949e;white-space:nowrap">환자 체중</label>
          <input type="number" id="adultWeight" value="70" min="1" max="200"
            style="background:#0d1117;border:1px solid #388bfd;color:#fff;font-size:24px;font-weight:700;width:90px;padding:6px 10px;border-radius:8px;text-align:center"
            oninput="updateAdult()">
          <span style="font-size:16px;color:#8b949e">kg</span>
          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-left:auto">
            <button onclick="setAW(50)" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:12px;padding:5px 11px;border-radius:6px;cursor:pointer">50kg</button>
            <button onclick="setAW(60)" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:12px;padding:5px 11px;border-radius:6px;cursor:pointer">60kg</button>
            <button onclick="setAW(70)" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:12px;padding:5px 11px;border-radius:6px;cursor:pointer">70kg</button>
            <button onclick="setAW(80)" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:12px;padding:5px 11px;border-radius:6px;cursor:pointer">80kg</button>
            <button onclick="setAW(90)" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:12px;padding:5px 11px;border-radius:6px;cursor:pointer">90kg</button>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:160px 1fr;gap:16px" id="adultLayout">
          <div style="display:flex;flex-direction:column;gap:6px;position:sticky;top:52px;height:fit-content" id="adultSidebar"></div>
          <div id="adultContent"></div>
        </div>
      </div>
      <div id="info-calc" class="ov-calc-panel">
        <div style="position:relative;margin-bottom:16px">
          <span style="position:absolute;left:14px;top:50%;transform:translateY(-50%);font-size:18px">🔍</span>
          <input type="text" id="drugSearchInput" placeholder="약물명 검색 (한글/영문)..."
            style="width:100%;background:#161b22;border:1px solid #388bfd;color:#e6edf3;font-size:16px;padding:12px 16px 12px 44px;border-radius:10px"
            oninput="filterDrugInfo()">
        </div>
        <div id="drugInfoList" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px;margin-bottom:16px"></div>
        <div id="drugInfoCard"></div>
      </div>
    </div>
  </div>
</div>

<!-- ── Overlay B: 소아 계산기 ── -->
<div class="overlay" id="ov-peds">
  <div class="overlay-header">
    <button class="btn-back" onclick="closeOverlay('peds')">&#8592; 닫기</button>
    <span class="ov-title">👶 소아 응급 계산기</span>
  </div>
  <div class="overlay-body">
    <div class="ov-calc">
      <div style="display:flex;align-items:center;gap:12px;background:#161b22;border:1px solid #30363d;border-radius:10px;padding:14px 18px;margin-bottom:16px">
        <label style="font-size:14px;color:#8b949e;white-space:nowrap">체중</label>
        <input type="number" id="pedsWeight" value="15" min="1" max="80"
          style="background:#0d1117;border:1px solid #388bfd;color:#fff;font-size:24px;font-weight:700;width:90px;padding:6px 10px;border-radius:8px;text-align:center"
          oninput="updatePeds()">
        <span style="font-size:16px;color:#8b949e">kg</span>
        <div style="display:flex;flex-wrap:wrap;gap:6px;margin-left:auto">
          <button onclick="setPW(3.5,'신생아')" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:11px;padding:5px 8px;border-radius:6px;cursor:pointer">신생아</button>
          <button onclick="setPW(10,'1세')" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:11px;padding:5px 8px;border-radius:6px;cursor:pointer">1세</button>
          <button onclick="setPW(14,'3세')" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:11px;padding:5px 8px;border-radius:6px;cursor:pointer">3세</button>
          <button onclick="setPW(18,'5세')" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:11px;padding:5px 8px;border-radius:6px;cursor:pointer">5세</button>
          <button onclick="setPW(22,'7세')" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:11px;padding:5px 8px;border-radius:6px;cursor:pointer">7세</button>
          <button onclick="setPW(32,'10세')" style="background:#21262d;border:1px solid #30363d;color:#c9d1d9;font-size:11px;padding:5px 8px;border-radius:6px;cursor:pointer">10세</button>
        </div>
      </div>
      <div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap">
        <div class="ov-calc-tab active" onclick="showPedsSub('emerg')" style="flex:none;padding:8px 18px;border-radius:20px;background:#21262d;border:1px solid #30363d;color:#8b949e;font-size:13px;font-weight:600;cursor:pointer;transition:.2s" id="peds-tab-emerg">🚨 응급</div>
        <div class="ov-calc-tab" onclick="showPedsSub('drugs')" style="flex:none;padding:8px 18px;border-radius:20px;background:#21262d;border:1px solid #30363d;color:#8b949e;font-size:13px;font-weight:600;cursor:pointer;transition:.2s" id="peds-tab-drugs">💊 약물</div>
        <div class="ov-calc-tab" onclick="showPedsSub('fluids')" style="flex:none;padding:8px 18px;border-radius:20px;background:#21262d;border:1px solid #30363d;color:#8b949e;font-size:13px;font-weight:600;cursor:pointer;transition:.2s" id="peds-tab-fluids">💧 수액</div>
      </div>
      <div id="peds-sub-emerg"></div>
      <div id="peds-sub-drugs" style="display:none"></div>
      <div id="peds-sub-fluids" style="display:none"></div>
    </div>
  </div>
</div>

<!-- ── Overlay C: 항생제 병용투여 ── -->
<div class="overlay" id="ov-antibiotic">
  <div class="overlay-header">
    <button class="btn-back" onclick="closeOverlay('antibiotic')">&#8592; 닫기</button>
    <span class="ov-title">🧬 항생제 병용투여</span>
  </div>
  <div class="overlay-body" style="padding:16px">
    <div class="ab-search-wrap">
      <span class="ab-search-icon">🔍</span>
      <input class="ab-search" id="abSearch" type="text"
        placeholder="항생제 이름 검색..."
        oninput="lookupAntibiotic(this.value)">
    </div>
    <p class="ab-hint">약물을 선택하면 병용 가능 여부가 표시됩니다. N = 근거없음</p>
    <div id="abResult"></div>
    <div id="abDiluent"></div>
  </div>
</div>

<!-- ── Overlay D: 간호기록 (nursing_note.html 원본 임베드) ── -->
<div class="overlay" id="ov-nursing">
  <div class="overlay-header">
    <button class="btn-back" onclick="closeOverlay('nursing')">&#8592; 닫기</button>
    <span class="ov-title">📝 간호기록</span>
  </div>
  <div class="overlay-body">
""" + nursing_html_body + """
  </div>
</div>
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. 오버레이 시스템 + 성인/소아 계산기 + 항생제 JS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXTRA_JS = r"""
// ══════════════════════════════════════════════════════════════════
// OVERLAY SYSTEM
// ══════════════════════════════════════════════════════════════════
function openOverlay(name){
  document.getElementById('ov-'+name).classList.add('show');
  document.getElementById('ovDim').classList.add('show');
  document.body.style.overflow='hidden';
  if(name==='adult'){updateAdult();initDrugInfo();}
  if(name==='peds'){updatePeds();}
  if(name==='nursing'){
    if(typeof resetAll==='function') resetAll();
  }
  if(name==='antibiotic'){
    document.getElementById('abSearch').value='';
    document.getElementById('abResult').innerHTML='';
    document.getElementById('abDiluent').innerHTML='';
  }
}

// Fix: nursing 홈 버튼 → 오버레이 닫기 (스크립트 하단 실행시 DOM 이미 준비됨)
document.querySelectorAll('#ov-nursing .home-btn').forEach(function(btn){
  var nb = btn.cloneNode(true);
  btn.parentNode.replaceChild(nb, btn);
  nb.addEventListener('click', function(){ closeOverlay('nursing'); });
});

// Fix: initCatheter 리스너 누적 버그 — 매 호출 시 catheter-list 클론으로 리스너 초기화
if(typeof initCatheter !== 'undefined'){
  const _origIC = initCatheter;
  initCatheter = function(){
    const el = document.getElementById('catheter-list');
    if(el){ const f = el.cloneNode(false); el.parentNode.replaceChild(f, el); }
    _origIC();
  };
}
function closeOverlay(name){
  document.getElementById('ov-'+name).classList.remove('show');
  if(!document.querySelector('.overlay.show'))
    document.getElementById('ovDim').classList.remove('show'),document.body.style.overflow='';
}
function closeAllOverlays(){
  document.querySelectorAll('.overlay').forEach(el=>el.classList.remove('show'));
  document.getElementById('ovDim').classList.remove('show');
  document.body.style.overflow='';
}
function switchCalcTab(ov,panelId){
  document.querySelectorAll(`#ov-${ov} .ov-calc-tab`).forEach(t=>t.classList.remove('active'));
  document.querySelectorAll(`#ov-${ov} .ov-calc-panel`).forEach(p=>p.classList.remove('active'));
  document.getElementById(panelId).classList.add('active');
}
function showCalcTab(ov,panel){
  switchCalcTab(ov,panel);
  event.currentTarget.classList.add('active');
}

// ══════════════════════════════════════════════════════════════════
// DRUG INFO (37약물)
// ══════════════════════════════════════════════════════════════════
const DRUG_DB = [
  {name:'Acetylcysteine',kr:'아세틸시스테인',conc:'600mg/6ml, 1000mg/10ml',bolus:'Bolus 가능 (900mg까지)',infusion:'1VI + 50ml (0.1-0.75mg/kg/ml)',diluent:'N/S, D5W',time:'Bolus: 5분 이상 / Infusion: 30분~16시간',caution:'',stable:'실온 24시간'},
  {name:'Calcium Gluconate',kr:'칼슘글루코네이트',conc:'2g/20ml (100mg/ml)',bolus:'Bolus 가능: CPR 상황에서만',infusion:'1A + 50-100ml (10-50mg/ml)',diluent:'N/S, D5W',time:'Bolus: CPR 상황에서만 / Infusion: 10분 이상',caution:'탄산수소나트륨과 배합금지, IM 불가',stable:'희석 후 즉시 사용'},
  {name:'Chlorpheniramine',kr:'클로르페니라민',conc:'4mg/2ml',bolus:'Bolus 가능',infusion:'1A + N/S 50ml',diluent:'N/S',time:'Bolus: 1분 / Infusion: 정보 없음',caution:'SC, IM 투여 가능',stable:'희석 후 즉시 / 5℃ 24시간'},
  {name:'Deferoxamine',kr:'데페록사민',conc:'500mg',bolus:'Bolus 불가',infusion:'8VI + WFI 후 + 1000ml (1-8mg/ml)',diluent:'WFI → N/S, D5W',time:'15mg/kg/hr 이하',caution:'SC, IM 가능',stable:'실온(23℃이하) 24시간'},
  {name:'Dexamethasone',kr:'덱사메타손',conc:'5mg/1ml',bolus:'Bolus 가능 (8mg까지)',infusion:'5A + 50ml (0.5mg/ml)',diluent:'N/S, D5W',time:'Bolus: 1-4분 / Infusion: 15-30분',caution:'',stable:'24시간 이내 사용'},
  {name:'Dexketoprofen',kr:'덱스케토프로펜',conc:'50mg/2ml',bolus:'Bolus 불가',infusion:'50mg + N/S 100ml',diluent:'N/S',time:'Infusion: 30분',caution:'투약 전후 N/S flushing / IM 가능',stable:'25℃ 차광 24시간'},
  {name:'Digoxin',kr:'디곡신',conc:'0.25mg/1ml',bolus:'Bolus 가능',infusion:'2A + 8ml (4배 이상 희석)',diluent:'N/S, D5W',time:'Bolus: 5분 이상 / Infusion: 10-20분',caution:'IM 가능',stable:'정보없음'},
  {name:'Esomeprazole',kr:'에소메프라졸',conc:'40mg',bolus:'Bolus 가능: 1VI + 5ml',infusion:'1VI+50ml / Loading 2VI+100ml / CIV 8mg/hr',diluent:'N/S만',time:'Bolus: 3분 이상 / Infusion: 10-30분',caution:'단독투여, only N/S, 투약 전후 N/S flushing',stable:'12시간 이내'},
  {name:'Famotidine',kr:'파모티딘',conc:'20mg',bolus:'Bolus 가능: 1VI + 5-10ml',infusion:'1VI + 100ml',diluent:'N/S, D5W',time:'Bolus: 2분 이상 / Infusion: 15-30분',caution:'IM 가능',stable:'냉장·실온 48시간'},
  {name:'Filgrastim',kr:'필그라스팀',conc:'75/150/300mcg',bolus:'Bolus 불가, SC 권장',infusion:'처방량 + 50ml (5-15mcg/ml)',diluent:'N/S, D5W',time:'Infusion: 15-30분',caution:'단독투여, SC 권장',stable:'D5W 희석: 12-24시간'},
  {name:'Fosaprepitant',kr:'포사프레피탄트',conc:'150mg',bolus:'Bolus 불가',infusion:'1VI + 150mg (1mg/ml)',diluent:'N/S',time:'Infusion: 20-30분',caution:'심하게 흔들거나 급속주입 금기',stable:'실온 24시간'},
  {name:'Granisetron',kr:'그라니세트론',conc:'1mg/1ml, 3mg/1ml',bolus:'Bolus 가능: 1mg + N/S 5ml',infusion:'3mg + 50ml',diluent:'1mg:N/S / 3mg:N/S,D5W,하트만',time:'Bolus: 30초 이상(1mg) / Infusion: 5분 이상(3mg)',caution:'',stable:'즉시 사용 권장'},
  {name:'Hydrocortisone',kr:'하이드로코르티손',conc:'100mg',bolus:'Bolus 가능 (100mg까지)',infusion:'1VI + 100ml (0.1-1mg/ml)',diluent:'N/S, D5W',time:'Bolus: 30초 이상 / Infusion: 10분 이상',caution:'IM 가능',stable:'즉시 사용 권장'},
  {name:'Lacosamide',kr:'라코사미드',conc:'200mg/20ml',bolus:'Bolus 권장 안함',infusion:'1VI + 100ml',diluent:'N/S, D5W',time:'Infusion: 30-60분',caution:'빠른 투여 시 서맥 등 부작용 증가',stable:'냉장 24시간 / 상온 4시간'},
  {name:'Levetiracetam',kr:'레비티라세탐',conc:'500mg/5ml',bolus:'Bolus 권장 안함',infusion:'처방량 + 100ml',diluent:'N/S, D5W',time:'Infusion: 15분 이상 / CIV: 200-400mg/hr',caution:'',stable:'15-30℃ 4시간'},
  {name:'Lorazepam',kr:'로라제팜',conc:'4mg/1ml',bolus:'Bolus 가능: 1A + 1ml (1:1 희석)',infusion:'CIV: 0.01-0.1mg/kg/hr',diluent:'N/S, WFI',time:'Bolus: 2-5분 이상 (2mg/min 이하)',caution:'0.08-1.0mg/ml 침전 주의 / IM 가능',stable:'정보없음'},
  {name:'Magnesium Sulfate',kr:'마그네슘설페이트',conc:'2g/20ml (100mg/ml)',bolus:'Bolus 가능: CPR 상황에서만',infusion:'1VI + 50ml (10% 이하)',diluent:'N/S, D5W',time:'Bolus: 1분 이상(심정지) / Infusion: 150mg/min 이하',caution:'IM 가능',stable:'정보없음'},
  {name:'Methylprednisolone',kr:'메틸프레드니솔론',conc:'40mg, 125mg, 500mg',bolus:'Bolus 가능 (250mg까지)',infusion:'처방량 + 50ml',diluent:'N/S, D5W',time:'Bolus: 5분 이상 / Infusion: 15-60분',caution:'고용량 급속 투여 시 심정지·부정맥 보고',stable:'희석 후 48시간'},
  {name:'Metoclopramide',kr:'메토클로프라미드',conc:'10mg/2ml',bolus:'Bolus 가능',infusion:'1A + N/S 50ml (10mg 이상 시)',diluent:'N/S',time:'Bolus: 3분 이상 / Infusion: 15분 이상',caution:'알칼리성 수액 배합 금기',stable:'실온·비차광 24시간'},
  {name:'Morphine Sulfate',kr:'모르핀',conc:'10mg/1ml, 30mg/2ml, 100mg/10ml',bolus:'Bolus 가능',infusion:'10·30mg→+50ml / 100mg→+100ml (1mg/ml)',diluent:'WFI, D5W, N/S',time:'Bolus: 4-10mg, 4-5분 이상 / CIV: 최대 10mg/hr',caution:'경막외·수막강 내 투여 금지',stable:'실온 14일'},
  {name:'Ondansetron',kr:'온단세트론',conc:'4mg/2ml, 8mg/4ml',bolus:'Bolus 가능',infusion:'1VI + 50ml',diluent:'N/S, D5W, 링거, 만니톨',time:'Bolus: 30초-2분 이상(16mg까지) / Infusion: 15분 이상',caution:'',stable:'냉장(2-8℃) 24시간'},
  {name:'Palonosetron',kr:'팔로노세트론',conc:'0.075mg/1.5ml, 0.25mg/5ml',bolus:'Bolus 가능',infusion:'정보없음',diluent:'N/S, D5W',time:'Bolus: 0.075mg→10초 / 0.25mg→30초 이상',caution:'단독투여, 투약 전후 N/S flushing',stable:'정보없음'},
  {name:'Pamidronate',kr:'파미드로네이트',conc:'15mg/1ml',bolus:'정보부족',infusion:'15-90mg → 250-500ml',diluent:'N/S',time:'2-4시간 이상 (최대 20mg/hr)',caution:'칼슘함유액(링겔, 하트만) 혼합불가',stable:'정보없음'},
  {name:'Pantoprazole',kr:'판토프라졸',conc:'40mg',bolus:'Bolus 가능: 1VI + N/S 10ml',infusion:'1VI+100ml / Loading 2VI+100ml / CIV 2VI+80ml',diluent:'N/S (Bolus: N/S만), D5W',time:'Bolus: 2분 / Infusion: 15분 이상',caution:'',stable:'25℃이하 12시간'},
  {name:'Pethidine',kr:'페티딘',conc:'25mg/0.5ml',bolus:'Bolus 가능 (10mg/1ml)',infusion:'1mg/ml (CIV)',diluent:'N/S, D5W',time:'Bolus: 천천히',caution:'급속 정맥주사 시 호흡억제·혈압강하·심정지 위험',stable:'정보없음'},
  {name:'Phosten',kr:'포스텐(인산)',conc:'2.722g(P 20mmol)/20ml',bolus:'Bolus 불가',infusion:'말초: 1A+250ml / 중심: 1A+100ml',diluent:'TPN, D50W, N/S, D5W',time:'K로써 최대 25mEq/hr',caution:'',stable:'정보없음'},
  {name:'Phytonadione',kr:'비타민K1',conc:'10mg/1ml',bolus:'권장 안함',infusion:'1A + 50ml 이상',diluent:'N/S, D5W',time:'Infusion: 20분 이상',caution:'SC, IM 가능',stable:'희석 후 즉시 사용'},
  {name:'Potassium Chloride',kr:'염화칼륨',conc:'40mEq/20ml',bolus:'Bolus 절대 불가',infusion:'말초: 1A+500ml / 중심: 1A+200ml',diluent:'N/S, D5W, 하트만',time:'K로써 최대 25mEq/hr',caution:'반드시 희석 후 사용',stable:'정보없음'},
  {name:'Propacetamol',kr:'프로파세타몰',conc:'1g',bolus:'Bolus 가능: 1VI + WFI 5ml',infusion:'1VI + 50-125ml',diluent:'N/S, D5W',time:'Bolus: 1-2분 / Infusion: 15분',caution:'IM 가능',stable:'2시간 이내 사용'},
  {name:'Rasburicase',kr:'라스부리카제',conc:'1.5mg',bolus:'권장 안함',infusion:'처방량(0.2mg/kg/day) + N/S 50ml',diluent:'N/S',time:'Infusion: 30분',caution:'단독투여, N/S 외 배합금기',stable:'냉장 24시간'},
  {name:'Remifentanil',kr:'레미펜타닐',conc:'1mg, 5mg',bolus:'Bolus 가능 (마취유도 시만)',infusion:'5mg + 100ml (50mcg/ml)',diluent:'WFI, D5W, N/S',time:'Bolus: 1mcg/kg 30초 이상 / CIV: 0.5-1mcg/kg/min',caution:'젖산 함유 수액(하트만 등) 불가',stable:'실온 24시간'},
  {name:'Thiamine',kr:'티아민(비타민B1)',conc:'50mg/2ml',bolus:'Bolus 가능 (100mg 미만)',infusion:'1A + 100ml (최대 200mg)',diluent:'N/S, D5W, 하트만',time:'Infusion: 15-30분',caution:'100mg 이상 시 Infusion 권고 / SC, IM 가능',stable:'정보없음'},
  {name:'Tramadol',kr:'트라마돌',conc:'100mg/2ml',bolus:'Bolus 가능',infusion:'정보없음 (최대 400mg/day)',diluent:'N/S, D5W',time:'Bolus: 3-5분',caution:'IM 가능',stable:'정보없음'},
  {name:'Tranexamic Acid',kr:'트라넥삼산',conc:'500mg/5ml',bolus:'Bolus 가능',infusion:'1A + 125ml',diluent:'N/S, D5W',time:'Bolus: 3-5분 / Infusion: 100mg/min 이하',caution:'IM 가능',stable:'실온 4시간'},
  {name:'Valproate',kr:'발프로에이트',conc:'150mg/1.5ml, 300mg/3ml',bolus:'Bolus 가능',infusion:'1A + 50ml',diluent:'N/S, D5W',time:'Bolus: 3-5분 / Infusion: 20mg/min 이하',caution:'',stable:'15-30℃ 24시간'},
  {name:'Norepinephrine',kr:'노르에피네프린(CIV)',conc:'말초: 16mcg/ml / 중심: 40mcg/ml',bolus:'-',infusion:'말초: 8mg+D5W 492ml / 중심: 4mg+D5W 96ml',diluent:'D5W',time:'CIV 지속주입',caution:'말초 조직괴사 주의, 중심정맥 권장',stable:'24hr'},
  {name:'Dopamine',kr:'도파민(CIV)',conc:'프리믹스 2000mcg/ml',bolus:'-',infusion:'400mg/200ml bag 프리믹스',diluent:'프리믹스',time:'CIV 지속주입',caution:'빈맥 주의',stable:'24hr'},
  {name:'Vasopressin',kr:'바소프레신(CIV)',conc:'0.2u/ml',bolus:'-',infusion:'20u + D5W 99ml',diluent:'D5W',time:'CIV 지속주입',caution:'',stable:'24hr'},
];
let selDrugInfo=null;
function initDrugInfo(){renderDrugInfoList(DRUG_DB);}
function filterDrugInfo(){
  const q=document.getElementById('drugSearchInput').value.toLowerCase();
  renderDrugInfoList(DRUG_DB.filter(d=>d.name.toLowerCase().includes(q)||d.kr.includes(q)));
}
function renderDrugInfoList(list){
  const el=document.getElementById('drugInfoList');
  el.innerHTML=list.map(d=>`<div onclick="showDrugInfoCard('${d.name}')"
    style="background:#21262d;border:1px solid ${selDrugInfo===d.name?'#388bfd':'#30363d'};
    border-radius:8px;padding:10px 14px;cursor:pointer;font-size:13px;transition:.2s;
    color:${selDrugInfo===d.name?'#58a6ff':'#c9d1d9'}">
    ${d.name}<br><span style="font-size:11px;color:#8b949e">${d.kr}</span></div>`).join('');
}
function showDrugInfoCard(name){
  selDrugInfo=name;
  filterDrugInfo();
  const d=DRUG_DB.find(x=>x.name===name);
  const card=document.getElementById('drugInfoCard');
  card.innerHTML=`<div style="background:#161b22;border:1px solid #388bfd;border-radius:10px;padding:18px">
    <div style="font-size:18px;font-weight:700;margin-bottom:4px;color:#e6edf3">${d.name}</div>
    <div style="font-size:13px;color:#8b949e;margin-bottom:14px">${d.kr} · ${d.conc}</div>
    <div style="display:flex;gap:12px;padding:9px 0;border-bottom:1px solid #21262d;font-size:13px"><span style="color:#8b949e;min-width:90px;font-weight:600">💊 Bolus</span><span style="color:#e6edf3;flex:1">${d.bolus||'-'}</span></div>
    <div style="display:flex;gap:12px;padding:9px 0;border-bottom:1px solid #21262d;font-size:13px"><span style="color:#8b949e;min-width:90px;font-weight:600">💧 Infusion</span><span style="color:#e6edf3;flex:1">${d.infusion||'-'}</span></div>
    <div style="display:flex;gap:12px;padding:9px 0;border-bottom:1px solid #21262d;font-size:13px"><span style="color:#8b949e;min-width:90px;font-weight:600">🧪 희석수액</span><span style="color:#e6edf3;flex:1">${d.diluent||'-'}</span></div>
    <div style="display:flex;gap:12px;padding:9px 0;border-bottom:1px solid #21262d;font-size:13px"><span style="color:#8b949e;min-width:90px;font-weight:600">⏱️ 투여시간</span><span style="color:#e6edf3;flex:1">${d.time||'-'}</span></div>
    ${d.caution?`<div style="display:flex;gap:12px;padding:9px 0;border-bottom:1px solid #21262d;font-size:13px"><span style="color:#8b949e;min-width:90px;font-weight:600">⚠️ 주의</span><span style="color:#f85149;flex:1">${d.caution}</span></div>`:''}
    <div style="display:flex;gap:12px;padding:9px 0;font-size:13px"><span style="color:#8b949e;min-width:90px;font-weight:600">🧊 안정시간</span><span style="color:#e6edf3;flex:1">${d.stable||'-'}</span></div>
  </div>`;
}

// ══════════════════════════════════════════════════════════════════
// ADULT DRUG CALCULATOR
// ══════════════════════════════════════════════════════════════════
const ADULT_DRUGS = [
  {id:'norepi',name:'Norepinephrine',badge:'혈관수축제',color:'#56d364',twoCol:true,
   routes:[{label:'말초 정맥',detail:'8mg + D5W 492ml',conc:16,unit:'mcg/ml'},{label:'중심 정맥',detail:'4mg + D5W 96ml',conc:40,unit:'mcg/ml'}],
   doses:[4,8,12,16,20],doseUnit:'mcg/min',weightBased:false,highlight:8},
  {id:'dopa',name:'Dopamine',badge:'승압제',color:'#58a6ff',twoCol:false,
   routes:[{label:'프리믹스',detail:'400mg/200ml bag',conc:2000,unit:'mcg/ml'}],
   doses:[5,10,15,20,25,30,35,40],doseUnit:'mcg/kg/min',weightBased:true,highlight:10},
  {id:'dobu',name:'Dobutamine',badge:'강심제',color:'#bc8cff',twoCol:false,
   routes:[{label:'프리믹스',detail:'500mg/250ml bag',conc:2000,unit:'mcg/ml'}],
   doses:[5,10,15,20,25,30,35,40],doseUnit:'mcg/kg/min',weightBased:true,highlight:10},
  {id:'epi',name:'Epinephrine',badge:'승압/강심',color:'#f85149',twoCol:false,
   routes:[{label:'표준',detail:'1mg + NS 99ml',conc:10,unit:'mcg/ml'}],
   doses:[0.1,0.2,0.3,0.4,0.5],doseUnit:'mcg/kg/min',weightBased:true,highlight:0.1},
  {id:'vaso',name:'Vasopressin',badge:'혈관수축제',color:'#ffa726',twoCol:false,
   routes:[{label:'표준',detail:'20u + D5W 99ml',conc:0.2,unit:'u/ml'}],
   doses:[0.01,0.02,0.03],doseUnit:'unit/min',weightBased:false,highlight:0.02},
];
let _activeAdultDrug='norepi';
function setAW(w){document.getElementById('adultWeight').value=w;updateAdult();}
function calcRate(dose,conc,wb,w){return wb?(dose*w*60)/conc:(dose*60)/conc;}
function selectAdultDrug(id){_activeAdultDrug=id;updateAdult();}
function updateAdult(){
  const w=parseFloat(document.getElementById('adultWeight').value)||70;
  document.getElementById('adultSidebar').innerHTML=ADULT_DRUGS.map(d=>
    `<button onclick="selectAdultDrug('${d.id}')"
      style="background:${d.id===_activeAdultDrug?'#1c2d45':'#21262d'};
      border:1px solid ${d.id===_activeAdultDrug?'#388bfd':'#30363d'};
      color:${d.id===_activeAdultDrug?'#58a6ff':'#8b949e'};
      padding:10px 12px;border-radius:8px;cursor:pointer;text-align:left;font-size:13px;font-weight:600;width:100%">
      <span style="color:${d.color}">${d.name}</span><br>
      <span style="font-size:10px;color:#8b949e">${d.badge}</span>
    </button>`).join('');
  const drug=ADULT_DRUGS.find(d=>d.id===_activeAdultDrug);
  const content=document.getElementById('adultContent');
  if(!drug){content.innerHTML='';return;}
  const tblStyle='width:100%;border-collapse:collapse';
  const thStyle='background:#0d1117;color:#8b949e;font-size:11px;font-weight:600;padding:8px 14px;text-align:left;border-bottom:1px solid #30363d';
  const tdStyle='padding:9px 14px;font-size:13px;border-bottom:1px solid #21262d';
  if(drug.twoCol){
    const r0=drug.routes[0],r1=drug.routes[1];
    const rows=drug.doses.map(dose=>{
      const v0=calcRate(dose,r0.conc,drug.weightBased,w).toFixed(1);
      const v1=calcRate(dose,r1.conc,drug.weightBased,w).toFixed(1);
      const hl=dose===drug.highlight;
      return `<tr style="${hl?'background:#1c2d45':''}">
        <td style="${tdStyle};color:#8b949e">${dose} ${drug.doseUnit}</td>
        <td style="${tdStyle};color:#56d364;font-size:${hl?'17px':'14px'};font-weight:700">${v0} ml/hr</td>
        <td style="${tdStyle};color:#ffa726;font-size:${hl?'17px':'14px'};font-weight:700">${v1} ml/hr</td>
      </tr>`;
    }).join('');
    content.innerHTML=`<div style="background:#161b22;border:1px solid #30363d;border-radius:10px;overflow:hidden">
      <div style="padding:12px 16px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #30363d;background:#1a2f1a">
        <div><div style="font-size:15px;font-weight:700;color:#56d364">${drug.name}</div><div style="font-size:12px;color:#8b949e">체중 ${w}kg 기준</div></div>
        <span style="background:#1a2f1a;color:#56d364;font-size:11px;padding:3px 10px;border-radius:20px;font-weight:600">${drug.badge}</span>
      </div>
      <div style="padding:14px 16px">
        <table style="${tblStyle}">
          <tr>
            <th style="${thStyle}">용량</th>
            <th style="${thStyle};color:#56d364">🟢 말초 (${r0.conc}mcg/ml)<br><span style="font-weight:400;font-size:10px">${r0.detail}</span></th>
            <th style="${thStyle};color:#ffa726">🟠 중심 (${r1.conc}mcg/ml)<br><span style="font-weight:400;font-size:10px">${r1.detail}</span></th>
          </tr>${rows}
        </table>
      </div></div>`;
  } else {
    const route=drug.routes[0];
    const rows=drug.doses.map(dose=>{
      const rate=calcRate(dose,route.conc,drug.weightBased,w).toFixed(1);
      const hl=dose===drug.highlight;
      return `<tr style="${hl?'background:#1c2d45':''}">
        <td style="${tdStyle};color:#8b949e">${dose} ${drug.doseUnit}</td>
        <td style="${tdStyle};font-size:${hl?'18px':'14px'};font-weight:700;color:${drug.color}">${rate} ml/hr</td>
      </tr>`;
    }).join('');
    content.innerHTML=`<div style="background:#161b22;border:1px solid #30363d;border-radius:10px;overflow:hidden">
      <div style="padding:12px 16px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #30363d">
        <div><div style="font-size:15px;font-weight:700;color:${drug.color}">${drug.name}</div>
          <div style="font-size:12px;color:#8b949e">${route.detail} · ${route.conc} ${route.unit} · 체중 ${w}kg</div>
        </div>
        <span style="background:#21262d;color:${drug.color};font-size:11px;padding:3px 10px;border-radius:20px;font-weight:600">${drug.badge}</span>
      </div>
      <div style="padding:14px 16px">
        <table style="${tblStyle}">
          <tr><th style="${thStyle}">용량</th><th style="${thStyle}">주입 속도</th></tr>${rows}
        </table>
      </div></div>`;
  }
}

// ══════════════════════════════════════════════════════════════════
// PEDS CALCULATOR
// ══════════════════════════════════════════════════════════════════
const AIRWAY_TABLE=[
  {wMin:1,wMax:5,ett:'3.0',depth:'9-10',laryngo:'0 (직날)',opa:'50mm',npa:'3.5Fr',lma:'1'},
  {wMin:5,wMax:8,ett:'3.0-3.5',depth:'10-11',laryngo:'1 (직날)',opa:'60mm',npa:'4.0Fr',lma:'1.5'},
  {wMin:8,wMax:10,ett:'3.5',depth:'11-12',laryngo:'1 (직날)',opa:'70mm',npa:'4.5Fr',lma:'1.5'},
  {wMin:10,wMax:12,ett:'3.5',depth:'12-13',laryngo:'1 (만곡)',opa:'70mm',npa:'5.0Fr',lma:'2'},
  {wMin:12,wMax:15,ett:'4.0',depth:'13-15',laryngo:'2 (만곡)',opa:'80mm',npa:'5.5Fr',lma:'2'},
  {wMin:15,wMax:19,ett:'4.5',depth:'15-16',laryngo:'2 (만곡)',opa:'80mm',npa:'6.0Fr',lma:'2'},
  {wMin:19,wMax:24,ett:'5.0',depth:'16-17',laryngo:'2 (만곡)',opa:'90mm',npa:'6.5Fr',lma:'2.5'},
  {wMin:24,wMax:30,ett:'5.5',depth:'17-19',laryngo:'2-3(만곡)',opa:'90mm',npa:'7.0Fr',lma:'2.5'},
  {wMin:30,wMax:999,ett:'6.0',depth:'18-20',laryngo:'3 (만곡)',opa:'100mm',npa:'7.5Fr',lma:'3'},
];
const VITAL_TABLE=[
  {wMax:4,group:'신생아',hr:'100-160',rr:'30-60',sbp:'60-90',dbp:'30-60'},
  {wMax:10,group:'영아',hr:'100-160',rr:'25-55',sbp:'70-100',dbp:'40-65'},
  {wMax:14,group:'유아(1-3세)',hr:'90-150',rr:'20-40',sbp:'80-110',dbp:'50-80'},
  {wMax:18,group:'학령전기',hr:'80-140',rr:'20-30',sbp:'85-115',dbp:'55-80'},
  {wMax:32,group:'학령기',hr:'70-120',rr:'15-25',sbp:'90-120',dbp:'55-80'},
  {wMax:999,group:'청소년',hr:'60-100',rr:'12-20',sbp:'100-130',dbp:'60-85'},
];
function setPW(w,label){document.getElementById('pedsWeight').value=w;updatePeds();}
function getAW(w){return AIRWAY_TABLE.find(r=>w>=r.wMin&&w<r.wMax)||AIRWAY_TABLE[AIRWAY_TABLE.length-1];}
function getVT(w){return VITAL_TABLE.find(r=>w<=r.wMax)||VITAL_TABLE[VITAL_TABLE.length-1];}
function maint(w){if(w<=10)return(4*w).toFixed(1);if(w<=20)return(40+2*(w-10)).toFixed(1);return(60+(w-20)).toFixed(1);}
function fp(n,d=1){return parseFloat(n.toFixed(d));}
function showPedsSub(name){
  ['emerg','drugs','fluids'].forEach(s=>{
    document.getElementById('peds-sub-'+s).style.display=s===name?'block':'none';
    const t=document.getElementById('peds-tab-'+s);
    if(t){t.style.background=s===name?'#1c2d45':'#21262d';t.style.borderColor=s===name?'#388bfd':'#30363d';t.style.color=s===name?'#58a6ff':'#8b949e';}
  });
}
function updatePeds(){
  const w=parseFloat(document.getElementById('pedsWeight').value)||15;
  const aw=getAW(w),vt=getVT(w);
  const tvMin=fp(w*6),tvMax=fp(w*8);
  const d1=fp(w*2),d2=fp(w*4),dMax=Math.min(fp(w*10),200);
  const C=(bg,color,content)=>`<div style="background:#161b22;border:1px solid #30363d;border-radius:10px;overflow:hidden;margin-bottom:14px">
    <div style="padding:12px 16px;border-bottom:1px solid #30363d;background:${bg}"><span style="font-size:15px;font-weight:700;color:${color}">${content}</span></div>
    <div style="padding:14px 16px">`;
  const EC=`</div></div>`;
  const TH=`background:#0d1117;color:#8b949e;font-size:11px;padding:8px 14px;text-align:left;border-bottom:1px solid #30363d`;
  const TD=`padding:9px 14px;font-size:13px;border-bottom:1px solid #21262d`;
  const TR=(hl,a,b)=>`<tr style="${hl?'background:#1c2d45':''}"><td style="${TD};color:#8b949e">${a}</td><td style="${TD};font-weight:${hl?700:600};color:${hl?'#58a6ff':'#e6edf3'};font-size:${hl?'16px':'13px'}">${b}</td></tr>`;
  const TBL=(rows)=>`<table style="width:100%;border-collapse:collapse">${rows}</table>`;
  const GRID=`display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px`;
  document.getElementById('peds-sub-emerg').innerHTML=`<div style="${GRID}">
  ${C('#0a1628','#58a6ff','🌡️ 정상 활력징후')}${TBL(TR(false,'HR',vt.hr+' 회/분')+TR(false,'RR',vt.rr+' 회/분')+TR(false,'SBP',vt.sbp+' mmHg')+TR(false,'DBP',vt.dbp+' mmHg')+TR(false,'SpO2','≥ 95%'))}${EC}
  ${C('#0a0f0a','#39c5cf','🫁 기도 장비')}${TBL(TR(true,'ETT (커프드)',aw.ett)+TR(false,'삽입 깊이',aw.depth+' cm')+TR(false,'후두경',aw.laryngo)+TR(false,'OPA',aw.opa)+TR(false,'NPA',aw.npa)+TR(false,'LMA',aw.lma))}${EC}
  ${C('#0a1628','#58a6ff','🌬️ 인공호흡기')}${TBL(TR(true,'TV (6-8ml/kg)',tvMin+'-'+tvMax+' ml')+TR(false,'RR',vt.rr+' 회/분')+TR(false,'FiO2','1.0 → SpO2 94-99%')+TR(false,'PEEP','5 cmH₂O')+TR(false,'흡기시간',(w<5?'0.3-0.4':w<10?'0.4-0.5':w<18?'0.5-0.7':'0.7-1.0')+'초'))}${EC}
  ${C('#1a1500','#e3b341','⚡ 제세동')}${TBL(TR(true,'1차 (2J/kg)',d1+' J')+TR(false,'2차 (4J/kg)',d2+' J')+TR(false,'최대 (10J/kg, max 200J)',dMax+' J'))}${EC}
  ${C('#1a0808','#f85149','💊 심정지 약물')}${TBL(TR(true,'Epinephrine (0.01mg/kg)',fp(w*0.01)+'mg IV/IO')+TR(false,'Amiodarone (5mg/kg)',fp(w*5)+'mg')+TR(false,'Lidocaine (1mg/kg)',fp(w*1)+'mg')+TR(false,'NaHCO₃ (1mEq/kg)',fp(w*1)+'mEq')+TR(false,'Ca Gluconate (60mg/kg)',fp(w*60)+'mg')+TR(false,'D50W (0.5g/kg)',fp(w*0.5)+'g = '+fp(w*1)+'ml'))}${EC}
  ${C('#1a0a2a','#bc8cff','🧠 경련')}${TBL(TR(true,'Midazolam IN (0.2mg/kg)',fp(w*0.2)+'mg')+TR(false,'Lorazepam IV (0.1mg/kg)',fp(w*0.1)+'mg')+TR(false,'Levetiracetam IV (60mg/kg)',fp(w*60)+'mg')+TR(false,'Valproate IV (30mg/kg)',fp(w*30)+'mg')+TR(false,'Phenobarbital IV (20mg/kg)',fp(w*20)+'mg'))}${EC}
  ${C('#1a0f00','#ffa726','🚨 아나필락시스')}${TBL(TR(true,'Epi IM (0.01mg/kg, 1:1000)',fp(Math.min(w*0.01,0.5),2)+'mg (max 0.5mg)')+TR(false,'수액 볼루스 (20ml/kg)',fp(w*20)+'ml')+TR(false,'Hydrocortisone (1mg/kg)',fp(w*1)+'mg')+TR(false,'Chlorpheniramine (0.1mg/kg)',fp(w*0.1)+'mg'))}${EC}
  </div>`;
  document.getElementById('peds-sub-drugs').innerHTML=`<div style="${GRID}">
  ${C('#0a0f0a','#39c5cf','💉 RSI')}${TBL(TR(false,'Atropine 전처치 (0.02mg/kg)',fp(Math.max(Math.min(w*0.02,0.5),0.1),2)+'mg min 0.1mg')+TR(true,'Ketamine 유도 (1-2mg/kg)',fp(w*1)+'-'+fp(w*2)+'mg')+TR(true,'Rocuronium (1.2mg/kg)',fp(w*1.2)+'mg')+TR(false,'Succinylcholine (1-2mg/kg)',fp(w*1)+'-'+fp(w*2)+'mg'))}${EC}
  ${C('#0a1a0a','#56d364','💊 진통제')}${TBL(TR(true,'Fentanyl IV (1-2mcg/kg)',fp(w*1)+'-'+fp(w*2)+'mcg')+TR(false,'Fentanyl IN (1.5-2mcg/kg)',fp(w*1.5)+'-'+fp(w*2)+'mcg')+TR(false,'Morphine IV (0.05-0.1mg/kg)',fp(w*0.05,2)+'-'+fp(w*0.1,2)+'mg')+TR(false,'Ketorolac IV (0.5mg/kg, max 30mg)',fp(Math.min(w*0.5,30))+'mg')+TR(false,'Acetaminophen PO (15mg/kg)',fp(w*15)+'mg'))}${EC}
  ${C('#1a0a2a','#bc8cff','😴 진정제')}${TBL(TR(true,'Midazolam IV (0.05-0.1mg/kg)',fp(w*0.05,2)+'-'+fp(w*0.1,2)+'mg')+TR(false,'Midazolam IN (0.2-0.3mg/kg)',fp(w*0.2)+'-'+fp(w*0.3)+'mg')+TR(false,'Ketamine IV (1-2mg/kg)',fp(w*1)+'-'+fp(w*2)+'mg')+TR(false,'Ketamine IM (4-5mg/kg)',fp(w*4)+'-'+fp(w*5)+'mg')+TR(false,'Propofol IV (1-2mg/kg)',fp(w*1)+'-'+fp(w*2)+'mg')+TR(false,'Dexmedetomidine loading (0.5-1mcg/kg)',fp(w*0.5)+'-'+fp(w*1)+'mcg'))}${EC}
  ${C('#1a1500','#e3b341','🤢 항구토제')}${TBL(TR(true,'Ondansetron IV (0.15mg/kg, max 8mg)',fp(Math.min(w*0.15,8),1)+'mg')+TR(false,'Metoclopramide IV (0.1mg/kg, max 10mg)',fp(Math.min(w*0.1,10),1)+'mg')+TR(false,'Dexamethasone IV (0.15mg/kg, max 10mg)',fp(Math.min(w*0.15,10),1)+'mg'))}${EC}
  </div>`;
  const ml=maint(w);
  document.getElementById('peds-sub-fluids').innerHTML=`<div style="${GRID}">
  ${C('#0a1628','#58a6ff','💧 수액 볼루스')}${TBL(TR(true,'저혈량/탈수 (20ml/kg)',fp(w*20)+'ml')+TR(false,'패혈성 쇼크 (10-20ml/kg)',fp(w*10)+'-'+fp(w*20)+'ml')+TR(false,'아나필락시스 (20ml/kg)',fp(w*20)+'ml')+TR(false,'심인성 쇼크 (5-10ml/kg)',fp(w*5)+'-'+fp(w*10)+'ml 천천히')+TR(false,'DKA 초기 (10-20ml/kg)',fp(w*10)+'-'+fp(w*20)+'ml 뇌부종 주의')+TR(false,'신생아 소생 (10ml/kg)',fp(w*10)+'ml'))}${EC}
  ${C('#0a1a0a','#56d364','🧴 유지수액 (Holliday-Segar)')}
    <div style="background:#1c2d45;border:1px solid #388bfd;border-radius:8px;padding:12px 16px;text-align:center;margin-bottom:12px">
      <div style="font-size:13px;color:#8b949e;margin-bottom:4px">체중 ${w}kg 유지수액</div>
      <div style="font-size:20px;font-weight:700;color:#58a6ff">${ml} ml/hr</div>
    </div>
    ${TBL(TR(false,'≤ 10 kg','4 ml/kg/hr')+TR(false,'10-20 kg','40 + 2×초과kg ml/hr')+TR(false,'> 20 kg','60 + 1×초과kg ml/hr'))}${EC}
  ${C('#1a0808','#f85149','🩸 쇼크별 수액 전략')}${TBL(TR(false,'저혈량성','N/S 20ml/kg 반복 (총 60ml/kg)')+TR(false,'패혈성','10-20ml/kg, 매 bolus 후 재평가')+TR(false,'심인성','5-10ml/kg 매우 주의, 느리게')+TR(false,'아나필락시스','20ml/kg + Epi IM 필수')+TR(false,'폐쇄성','원인 제거 우선 (감압, 심낭천자)'))}${EC}
  </div>`;
}

// ══════════════════════════════════════════════════════════════════
// ANTIBIOTIC COMPATIBILITY
// ══════════════════════════════════════════════════════════════════
const AB_MATRIX = {
  rows:['Acyclovir','Caspofungin','Cefepime','Ceftriaxone','Ciprofloxacin','Levofloxacin','Linezolid','Liposomal ampho B','Meropenem','Metronidazole','Micafungin','Pip/Tazobactam','TMP-SMX','Vancomycin','Voriconazole'],
  cols:['Acyclovir','Caspofungin','Cefepime','Ceftriaxone','Ciprofloxacin','Fluconazole','Levofloxacin','Linezolid','Meropenem','Pip/Tazo','TMP-SMX','Vancomycin'],
  data:{
    'Acyclovir':     [null,'불가','불가','가능','불가','가능','불가','가능','불가','불가','가능','가능'],
    'Caspofungin':   ['불가',null,'불가','불가','가능','가능','가능','가능','가능','불가','불가','가능'],
    'Cefepime':      ['불가','불가',null,'N','불가','가능','가능','가능','N','가능','가능','불가'],
    'Ceftriaxone':   ['가능','불가','N',null,'N','불가','가능','가능','N','N','불가','가능'],
    'Ciprofloxacin': ['불가','가능','불가','N',null,'N','N','가능','불가','불가','N','가능'],
    'Levofloxacin':  ['불가','가능','가능','가능','N','가능',null,'가능','N','불가','가능','가능'],
    'Linezolid':     ['가능','가능','가능','가능','가능','가능','가능',null,'가능','가능','가능','가능'],
    'Liposomal ampho B':['가능','불가','불가','가능','불가','N','불가','가능','불가','가능','가능','불가'],
    'Meropenem':     ['불가','가능','N','N','불가','가능','N','가능',null,'N','N','가능'],
    'Metronidazole': ['N','불가','N','N','N','N','N','N','N','N','가능','N'],
    'Micafungin':    ['N','N','N','N','N','N','불가','N','N','N','N','N'],
    'Pip/Tazobactam':['불가','불가','가능','N','불가','가능','불가','가능','N',null,'가능','불가'],
    'TMP-SMX':       ['가능','불가','가능','불가','N','불가','가능','가능','N','가능',null,'불가'],
    'Vancomycin':    ['가능','가능','불가','불가','가능','가능','가능','가능','가능','불가','불가',null],
    'Voriconazole':  ['가능','가능','불가','가능','가능','가능','가능','가능','가능','가능','가능','가능'],
  }
};
const AB_DILUENT = {
  'Amphotericin B':   {d5w:'가능',ns:'불가'},
  'Ampicillin':       {d5w:'불가',ns:'가능'},
  'Caspofungin':      {d5w:'불가',ns:'가능'},
  'Ertapenem':        {d5w:'불가',ns:'가능'},
  'Liposomal ampho B':{d5w:'가능',ns:'불가'},
};
function lookupAntibiotic(q){
  q=q.trim();
  const res=document.getElementById('abResult');
  const dil=document.getElementById('abDiluent');
  if(!q){res.innerHTML='';dil.innerHTML='';return;}
  const match=AB_MATRIX.rows.find(d=>d.toLowerCase().includes(q.toLowerCase()));
  if(!match){
    res.innerHTML=`<div class="ab-result" style="text-align:center;color:var(--text-muted)">검색 결과 없음<br><small>${AB_MATRIX.rows.join(', ')}</small></div>`;
    dil.innerHTML='';return;
  }
  const rowData=AB_MATRIX.data[match];
  const cols=AB_MATRIX.cols;
  const ok=[],no=[],na=[];
  rowData.forEach((v,i)=>{if(v===null)return;if(v==='가능')ok.push(cols[i]);else if(v==='불가')no.push(cols[i]);else na.push(cols[i]);});
  AB_MATRIX.rows.forEach(row=>{
    if(row===match)return;
    const ci=AB_MATRIX.cols.indexOf(match);if(ci<0)return;
    const v=AB_MATRIX.data[row]?.[ci];if(!v||v===null)return;
    const addTo=v==='가능'?ok:v==='불가'?no:na;
    if(!addTo.includes(row))addTo.push(row);
  });
  res.innerHTML=`<div class="ab-result">
    <div style="font-size:16px;font-weight:700;margin-bottom:12px;color:var(--text)">${match}</div>
    ${ok.length?`<div class="ab-divider">🟢 병용 가능 (${ok.length}개)</div>${ok.map(d=>`<div class="ab-row"><div class="ab-dot ok"></div><span>${d}</span></div>`).join('')}`:''}
    ${no.length?`<div class="ab-divider">🔴 병용 불가 (${no.length}개)</div>${no.map(d=>`<div class="ab-row"><div class="ab-dot no"></div><span>${d}</span></div>`).join('')}`:''}
    ${na.length?`<div class="ab-divider">⬜ 근거없음 (${na.length}개)</div>${na.map(d=>`<div class="ab-row"><div class="ab-dot na"></div><span>${d}</span></div>`).join('')}`:''}
  </div>`;
  const dilEntry=AB_DILUENT[match];
  if(dilEntry){
    dil.innerHTML=`<div class="ab-diluent-card">
      <div class="ab-diluent-title">💧 희석수액 주의</div>
      <div class="ab-diluent-row"><span>${match}</span>
        D5W: <span class="${dilEntry.d5w==='가능'?'ab-ok-badge':'ab-no-badge'}">${dilEntry.d5w}</span>
        &nbsp; N/S: <span class="${dilEntry.ns==='가능'?'ab-ok-badge':'ab-no-badge'}">${dilEntry.ns}</span>
      </div>
    </div>`;
  } else dil.innerHTML='';
}
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. 최종 HTML 조합
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
output = src.replace('<title>NFH ER Mate</title>', '<title>NFH ER Mate v3</title>')

# DB 교체
old_db = db_match.group(0)
new_db = 'const DB = ' + json.dumps(db, ensure_ascii=False, indent=2) + ';\n'
output = output.replace(old_db, new_db, 1)

# 오버레이 CSS 추가
output = output.replace('</style>', OVERLAY_CSS + '\n</style>', 1)

# 간호기록 탭 제거
output = output.replace(
    '    <div class="tab" onclick="showTab(\'nursing\')">📝 간호기록</div>\n', '')

# 오버레이 HTML + nursing JS를 </body> 직전에 삽입
# nursing JS는 오버레이 HTML 바로 뒤, 원본 <script> 전에 삽입
output = output.replace(
    '\n<script>',
    OVERLAY_HTML + '\n<script id="nursing-js">\n' + nursing_js_full + '\n</script>\n<script>',
    1)

# JS 패치들
# TASK_ICONS — 사망:'🕊️' 유지 (수정 없음)

output = output.replace(
    "const tabs=['home','procedure','drug','task','nursing','guide'];",
    "const tabs=['home','procedure','drug','task','guide'];")

output = output.replace(
    "{home:renderHome,procedure:renderProcedure,drug:renderDrug,\n    task:renderTask,nursing:renderNursing,guide:renderGuide}",
    "{home:renderHome,procedure:renderProcedure,drug:renderDrug,\n    task:renderTask,guide:renderGuide}")

# handleSearch에서 nursing 검색 → SYMS 사용 (nursing JS에서 정의됨)
output = output.replace(
    """  DB.nursing.forEach(n=>{
    Object.values(n.symptoms).forEach(s=>{
      if(s.name.includes(kw)||n.name.includes(kw))
        results.push({type:'nursing',id:n.id+'|||'+s.name,title:s.name,sub:n.name,badge:'간호기록'});
    });
  });""",
    """  if(typeof SYMS!=='undefined') SYMS.forEach(s=>{
    if(s.label.includes(kw)||s.id.includes(kw))
      results.push({type:'nursing',id:s.id,title:s.label,sub:'간호기록',badge:'간호기록'});
  });""")

# openFromSearch nursing + druginfo + adultcalc 처리
output = output.replace(
    "else if(type==='nursing'){const sep=id.indexOf('|||');openNursing(id.slice(0,sep),id.slice(sep+3));}",
    "else if(type==='nursing'){openOverlay('nursing');}\n"
    "  else if(type==='druginfo'){openOverlay('adult');setTimeout(()=>{switchCalcTab('adult','info-calc');showDrugInfoCard(id);},50);}\n"
    "  else if(type==='adultcalc'){openOverlay('adult');setTimeout(()=>{switchCalcTab('adult','adult-calc');selectAdultDrug(id);},50);}")

# handleSearch에 DRUG_DB + ADULT_DRUGS 추가 + slice 12→20
output = output.replace(
    "  DB.guides.forEach(g=>{\n"
    "    if(g.name_ko.includes(kw)||g.name_en.toLowerCase().includes(kw))\n"
    "      results.push({type:'guide',id:g.id,title:g.name_ko,sub:g.name_en,badge:'업무가이드'});\n"
    "  });\n"
    "  if(!results.length){\n"
    "    box.innerHTML='<div class=\"search-item\"><div class=\"search-item-title\">검색 결과 없음</div></div>';\n"
    "  } else {\n"
    "    box.innerHTML=results.slice(0,12).map(r=>",
    "  DB.guides.forEach(g=>{\n"
    "    if(g.name_ko.includes(kw)||g.name_en.toLowerCase().includes(kw))\n"
    "      results.push({type:'guide',id:g.id,title:g.name_ko,sub:g.name_en,badge:'업무가이드'});\n"
    "  });\n"
    "  if(typeof DRUG_DB!=='undefined') DRUG_DB.forEach(d=>{\n"
    "    if(d.name.toLowerCase().includes(kw)||d.kr.includes(kw))\n"
    "      results.push({type:'druginfo',id:d.name,title:d.name,sub:d.kr+' · '+d.conc,badge:'약물정보'});\n"
    "  });\n"
    "  if(typeof ADULT_DRUGS!=='undefined') ADULT_DRUGS.forEach(d=>{\n"
    "    if(d.name.toLowerCase().includes(kw))\n"
    "      results.push({type:'adultcalc',id:d.id,title:d.name,sub:d.badge+' CIV 계산기',badge:'성인계산기'});\n"
    "  });\n"
    "  if(!results.length){\n"
    "    box.innerHTML='<div class=\"search-item\"><div class=\"search-item-title\">검색 결과 없음</div></div>';\n"
    "  } else {\n"
    "    box.innerHTML=results.slice(0,20).map(r=>")

# renderHome에 빠른실행 + 간호기록 바로가기 추가
quick_html = """const quickHtml=`
    <div class="quick-grid">
      <button class="quick-btn" onclick="openOverlay('adult')"><span class="qb-icon">💉</span>성인 응급<br>약물 계산기</button>
      <button class="quick-btn" onclick="openOverlay('peds')"><span class="qb-icon">👶</span>소아 응급<br>계산기</button>
      <button class="quick-btn" onclick="openOverlay('antibiotic')"><span class="qb-icon">🧬</span>항생제<br>병용투여</button>
      <button class="quick-btn" onclick="openOverlay('nursing')"><span class="qb-icon">📝</span>간호기록<br>작성</button>
    </div>`;"""

output = output.replace(
    "  const c=document.getElementById('mainContent');\n  const guideIds=",
    "  const c=document.getElementById('mainContent');\n  " + quick_html + "\n  const guideIds=")

new_home_template = r"""  c.innerHTML=quickHtml+`
    <div class="sec-hdr"><span class="sec-hdr-title">🏥 시술/검사</span><span class="sec-hdr-link" onclick="showTab('procedure')">전체 ›</span></div>
    ${['MRI','CT','EGD','CAG'].map(id=>{const p=DB.procedures.find(q=>q.id===id);return p?`
      <div class="list-item" onclick="openProcedure('${p.id}')">
        <div class="list-item-left">
          <div style="font-size:18px;margin-right:8px">${PROC_ICONS[p.id]||'🏥'}</div>
          <div>
            <div class="list-item-title">${p.name_ko||p.name_en}</div>
            ${p.name_en&&p.name_ko?`<div style="font-size:11px;color:var(--text-muted)">${p.name_en}</div>`:''}
          </div>
        </div>
        <div class="list-item-arrow">›</div>
      </div>`:''}).join('')}
    <div class="sec-hdr"><span class="sec-hdr-title">📋 필수업무</span></div>
    ${DB.tasks.map(t=>`
      <div class="list-item" onclick="openTask('${t.id}')">
        <div class="list-item-left">
          <div style="font-size:20px;margin-right:4px">${TASK_ICONS[t.name]||'📋'}</div>
          <div class="list-item-title">${t.name} 체크리스트</div>
        </div>
        <div style="display:flex;align-items:center;gap:6px">
          <span style="font-size:12px;color:var(--text-muted)">${t.items.length}개</span>
          <div class="list-item-arrow">›</div>
        </div>
      </div>`).join('')}
    <div class="sec-hdr"><span class="sec-hdr-title">📚 업무가이드</span><span class="sec-hdr-link" onclick="showTab('guide')">전체 ›</span></div>
    ${['수혈','마약반납','A-line','enema'].map(id=>{const g=DB.guides.find(x=>x.id===id);return g?`
      <div class="list-item" onclick="openGuide('${g.id}')" style="padding:10px 14px">
        <div class="list-item-left"><div class="list-item-title" style="font-size:13px">${g.name_ko}</div></div>
        <div class="list-item-arrow">›</div>
      </div>`:''}).join('')}
  `;
}"""

old_home_template = r"""  c.innerHTML=`
    <div class="section-title">🏥 시술/검사 바로가기</div>
    <div class="card-grid">
      ${topProcs.map(p=>`
        <div class="proc-card" onclick="openProcedure(this.dataset.id)" data-id="${p.id}">
          <div class="proc-card-icon">${PROC_ICONS[p.id]||'🏥'}</div>
          <div class="proc-card-name">${p.name_ko||p.name_en}</div>
        </div>`).join('')}
      <div class="proc-card" onclick="showTab('procedure')">
        <div class="proc-card-icon">📋</div><div class="proc-card-name">전체보기</div>
      </div>
    </div>
    <div class="section-title">💊 약물 카테고리</div>
    <div class="card-grid">
      ${drugCats.map(cat=>`
        <div class="proc-card" onclick="showTab('drug');setTimeout(()=>setDrugFilter(this.dataset.cat),50)" data-cat="${cat}">
          <div class="proc-card-icon">${DRUG_ICONS[cat]||'💊'}</div>
          <div class="proc-card-name" style="font-size:10px">${cat.replace('/',' ')}</div>
        </div>`).join('')}
    </div>
    <div class="section-title">📋 필수업무</div>
    <div class="card-grid">
      ${DB.tasks.map(t=>`
        <div class="proc-card" onclick="openTask(this.dataset.id)" data-id="${t.id}">
          <div class="proc-card-icon">${TASK_ICONS[t.name]||'📋'}</div>
          <div class="proc-card-name">${t.name}</div>
          <div class="proc-card-sub">${t.items.length}개 항목</div>
        </div>`).join('')}
    </div>
    <div class="section-title">📝 간호기록 바로가기</div>
    <div class="card-grid">
      ${nursShortcuts.map(n=>`
        <div class="proc-card" onclick="openNursing(this.dataset.nid,this.dataset.sname)" data-nid="${n.nid}" data-sname="${n.sname}">
          <div class="proc-card-icon">${n.icon}</div>
          <div class="proc-card-name">${n.label}</div>
        </div>`).join('')}
    </div>
    <div class="section-title">📚 업무가이드 바로가기</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px">
      ${guideShortcuts.map(g=>`
        <div class="list-item" onclick="openGuide(this.dataset.id)" data-id="${g.id}" style="padding:10px 12px">
          <div class="list-item-left">
            <div class="list-item-title" style="font-size:13px">${g.name_ko}</div>
          </div>
          <div class="list-item-arrow">›</div>
        </div>`).join('')}
    </div>`;
}"""

output = output.replace(old_home_template, new_home_template)

# renderNursing/openNursing 제거 (DB.nursing 없음)
output = re.sub(r'function renderNursing\(\)\{.*?(?=\nfunction openNursing)',
                'function renderNursing(){}\n', output, flags=re.DOTALL)
output = re.sub(r'function openNursing\(nid,sname\)\{.*?(?=\nfunction renderGuide)',
                'function openNursing(nid,sname){openOverlay("nursing");}\n', output, flags=re.DOTALL)

# EXTRA_JS (성인/소아 계산기 + 항생제) 추가
output = output.replace('\nrenderHome();\n</script>',
                        '\n' + EXTRA_JS + '\nrenderHome();\n</script>')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. 저장 & 검증
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with open(DST, 'w') as f:
    f.write(output)

print(f"✅ Built: {DST}")
print(f"   Size: {len(output):,} bytes (~{len(output)//1024}KB)")

checks = [
    ('overlay adult',     'id="ov-adult"' in output),
    ('overlay peds',      'id="ov-peds"' in output),
    ('overlay antibiotic','id="ov-antibiotic"' in output),
    ('overlay nursing',   'id="ov-nursing"' in output),
    ('nursing 원본 HTML', 's-catheter' in output),
    ('nursing 원본 JS',   'initCatheter' in output),
    ('nursing CSS 스코핑','#ov-nursing .screen' in output),
    ('quick buttons',     'quick-grid' in output),
    ('간호기록 버튼',     "openOverlay('nursing')" in output),
    ('ADULT_DRUGS',       'const ADULT_DRUGS' in output),
    ('AB_MATRIX',         'const AB_MATRIX' in output),
    ('no DB.nursing',     '"nursing":' not in output.split('const AB_MATRIX')[0]),
    ('no Stroke proc',    '"id": "Stroke"' not in output),
    ('no CCU guide',      '"id": "CCU"' not in output),
    ('사망 🕊️ 복구',      '"사망"' in output.split('const PROC_ICONS')[0]),
]
print()
all_ok = True
for name, ok in checks:
    if not ok: all_ok = False
    print(f"  {'✅' if ok else '❌'} {name}")
print('\n' + ('🎉 ALL OK' if all_ok else '❌ SOME FAILED'))
