# HTML 빌드 스크립트 - 실행하면 er_mate.html 생성
import json, os

with open('/Users/sungkwanchoi/NFH_New/er_mate_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data_js = json.dumps(data, ensure_ascii=False)

html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NFH ER Mate</title>
<style>
:root {{
  --primary: #048A81;
  --primary-dark: #1B3A4B;
  --primary-light: #E0F5F3;
  --accent: #F4A261;
  --danger: #E63946;
  --warning: #FFB703;
  --bg: #F4F6F8;
  --card: #FFFFFF;
  --text: #1B2A3B;
  --text-muted: #6B7C93;
  --border: #E2E8F0;
  --shadow: 0 2px 8px rgba(0,0,0,0.08);
  --radius: 12px;
}}
.dark {{
  --bg: #0F1923;
  --card: #1A2535;
  --text: #E8EDF3;
  --text-muted: #8A9BB0;
  --border: #2A3A4E;
  --primary-light: #0D2A28;
  --shadow: 0 2px 8px rgba(0,0,0,0.3);
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: var(--bg); color: var(--text); font-family: -apple-system, 'Noto Sans KR', sans-serif; min-height: 100vh; }}

/* 헤더 */
.header {{ background: var(--primary-dark); color: white; padding: 0 20px; height: 56px;
  display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }}
.header-logo {{ display: flex; align-items: center; gap: 8px; font-size: 18px; font-weight: 700; }}
.header-logo svg {{ width: 28px; height: 28px; }}
.header-actions {{ display: flex; gap: 8px; }}
.btn-icon {{ background: rgba(255,255,255,0.15); border: none; color: white; padding: 6px 12px;
  border-radius: 8px; cursor: pointer; font-size: 13px; transition: background 0.2s; }}
.btn-icon:hover {{ background: rgba(255,255,255,0.25); }}

/* 검색 */
.search-wrap {{ padding: 14px 20px 10px; background: var(--card); border-bottom: 1px solid var(--border); }}
.search-box {{ position: relative; }}
.search-box input {{ width: 100%; padding: 10px 16px 10px 40px; border: 2px solid var(--border);
  border-radius: 10px; font-size: 14px; background: var(--bg); color: var(--text); outline: none; transition: border-color 0.2s; }}
.search-box input:focus {{ border-color: var(--primary); }}
.search-icon {{ position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); }}
.search-results {{ position: absolute; top: 100%; left: 0; right: 0; background: var(--card);
  border: 1px solid var(--border); border-radius: 10px; box-shadow: var(--shadow);
  max-height: 320px; overflow-y: auto; z-index: 200; display: none; }}
.search-results.show {{ display: block; }}
.search-item {{ padding: 10px 16px; cursor: pointer; border-bottom: 1px solid var(--border); }}
.search-item:hover {{ background: var(--primary-light); }}
.search-item-title {{ font-size: 14px; font-weight: 600; }}
.search-item-sub {{ font-size: 12px; color: var(--text-muted); margin-top: 2px; }}
.search-badge {{ display: inline-block; font-size: 10px; padding: 2px 6px; border-radius: 4px;
  background: var(--primary); color: white; margin-left: 6px; }}

/* 탭 */
.tabs {{ display: flex; overflow-x: auto; background: var(--card); border-bottom: 2px solid var(--border);
  padding: 0 12px; gap: 4px; scrollbar-width: none; }}
.tabs::-webkit-scrollbar {{ display: none; }}
.tab {{ padding: 12px 14px; font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap;
  border-bottom: 3px solid transparent; color: var(--text-muted); transition: all 0.2s; user-select: none; }}
.tab.active {{ color: var(--primary); border-bottom-color: var(--primary); }}
.tab:hover {{ color: var(--text); }}

/* 메인 컨텐츠 */
.content {{ padding: 16px 20px; max-width: 1200px; margin: 0 auto; }}

/* 섹션 타이틀 */
.section-title {{ font-size: 15px; font-weight: 700; margin: 20px 0 10px; color: var(--text); display: flex; align-items: center; gap: 6px; }}
.section-title::before {{ content: ''; display: block; width: 4px; height: 16px; background: var(--primary); border-radius: 2px; }}

/* 카드 그리드 */
.card-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; }}
.proc-card {{ background: var(--card); border-radius: var(--radius); padding: 14px 8px;
  text-align: center; cursor: pointer; box-shadow: var(--shadow); transition: all 0.2s;
  border: 2px solid transparent; }}
.proc-card:hover {{ border-color: var(--primary); transform: translateY(-2px); box-shadow: 0 4px 16px rgba(4,138,129,0.2); }}
.proc-card-icon {{ font-size: 28px; margin-bottom: 6px; }}
.proc-card-name {{ font-size: 12px; font-weight: 700; color: var(--text); }}
.proc-card-sub {{ font-size: 10px; color: var(--text-muted); margin-top: 2px; }}

/* 리스트 아이템 */
.list-item {{ background: var(--card); border-radius: var(--radius); padding: 14px 16px;
  margin-bottom: 8px; cursor: pointer; box-shadow: var(--shadow); display: flex;
  align-items: center; justify-content: space-between; transition: all 0.2s; }}
.list-item:hover {{ border-left: 4px solid var(--primary); padding-left: 12px; }}
.list-item-left {{ flex: 1; }}
.list-item-title {{ font-size: 14px; font-weight: 700; }}
.list-item-sub {{ font-size: 12px; color: var(--text-muted); margin-top: 3px; }}
.list-item-arrow {{ color: var(--text-muted); font-size: 16px; }}
.badge {{ display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 20px;
  background: var(--primary-light); color: var(--primary); font-weight: 600; margin-left: 6px; }}

/* 카테고리 헤더 */
.cat-header {{ background: var(--primary); color: white; padding: 8px 14px; border-radius: 8px;
  font-size: 13px; font-weight: 700; margin: 16px 0 8px; display: flex; align-items: center; gap: 6px; }}

/* 상세 패널 (슬라이드) */
.panel {{ position: fixed; top: 0; right: -100%; width: min(480px, 100%); height: 100vh;
  background: var(--card); z-index: 300; box-shadow: -4px 0 20px rgba(0,0,0,0.15);
  display: flex; flex-direction: column; transition: right 0.3s ease; overflow: hidden; }}
.panel.open {{ right: 0; }}
.panel-overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 290; display: none; }}
.panel-overlay.show {{ display: block; }}
.panel-header {{ background: var(--primary-dark); color: white; padding: 16px 20px;
  display: flex; align-items: center; gap: 12px; }}
.panel-back {{ background: none; border: none; color: white; font-size: 20px; cursor: pointer; padding: 0; }}
.panel-title {{ font-size: 16px; font-weight: 700; flex: 1; }}
.panel-reset {{ background: rgba(255,255,255,0.2); border: none; color: white; padding: 6px 12px;
  border-radius: 8px; cursor: pointer; font-size: 12px; }}
.panel-body {{ flex: 1; overflow-y: auto; padding: 16px; }}

/* 체크리스트 */
.checklist-section {{ margin-bottom: 16px; }}
.checklist-section-title {{ font-size: 13px; font-weight: 700; padding: 8px 12px;
  border-radius: 8px; margin-bottom: 8px; }}
.ae-title {{ background: #E3F2FD; color: #1565C0; }}
.diag-title {{ background: #FFF3E0; color: #E65100; }}
.plan-title {{ background: #E8F5E9; color: #2E7D32; }}
.prep-title {{ background: #E8F5E9; color: #2E7D32; }}
.med-title  {{ background: #FFF3E0; color: #E65100; }}
.post-title {{ background: #E3F2FD; color: #1565C0; }}
.warn-title {{ background: #FFF3CD; color: #856404; }}
.transport-title {{ background: #F3E5F5; color: #6A1B9A; }}

.check-item {{ display: flex; align-items: flex-start; gap: 10px; padding: 10px 12px;
  border-radius: 8px; margin-bottom: 6px; background: var(--bg); cursor: pointer;
  transition: background 0.15s; user-select: none; }}
.check-item:hover {{ background: var(--primary-light); }}
.check-item.checked {{ opacity: 0.6; }}
.check-item.checked .check-text {{ text-decoration: line-through; color: var(--text-muted); }}
.check-box {{ width: 20px; height: 20px; border: 2px solid var(--primary); border-radius: 5px;
  flex-shrink: 0; display: flex; align-items: center; justify-content: center;
  margin-top: 1px; transition: all 0.15s; }}
.check-item.checked .check-box {{ background: var(--primary); border-color: var(--primary); }}
.check-box-inner {{ color: white; font-size: 12px; display: none; }}
.check-item.checked .check-box-inner {{ display: block; }}
.check-text {{ font-size: 13px; line-height: 1.5; }}
.check-note {{ font-size: 11px; color: var(--text-muted); margin-top: 2px; }}
.warn-item {{ background: #FFF3CD; border-left: 3px solid var(--warning); padding: 8px 12px;
  border-radius: 0 8px 8px 0; margin-bottom: 6px; font-size: 13px; }}

/* 진행률 바 */
.progress-wrap {{ padding: 12px 16px; background: var(--card); border-top: 1px solid var(--border); }}
.progress-text {{ font-size: 12px; color: var(--text-muted); margin-bottom: 6px; display: flex; justify-content: space-between; }}
.progress-bar {{ height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; }}
.progress-fill {{ height: 100%; background: var(--primary); border-radius: 3px; transition: width 0.3s; }}

/* 약물 상세 */
.drug-table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
.drug-table tr {{ border-bottom: 1px solid var(--border); }}
.drug-table td:first-child {{ width: 110px; padding: 10px 12px; font-size: 12px; font-weight: 700;
  color: var(--text-muted); background: var(--bg); }}
.drug-table td:last-child {{ padding: 10px 12px; font-size: 13px; }}
.drug-alias {{ font-size: 12px; color: var(--text-muted); margin: 4px 0 12px; }}
.drug-category-badge {{ display: inline-block; font-size: 11px; padding: 3px 10px;
  border-radius: 20px; background: var(--primary-light); color: var(--primary);
  font-weight: 600; margin-bottom: 8px; }}

/* 간호기록 상세 */
.nursing-note {{ font-size: 11px; color: var(--text-muted); margin-top: 2px; font-style: italic; }}

/* 홈 레이아웃 */
.home-quick {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 8px; }}
.quick-card {{ background: var(--card); border-radius: 10px; padding: 12px 6px; text-align: center;
  cursor: pointer; box-shadow: var(--shadow); transition: all 0.2s; }}
.quick-card:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(4,138,129,0.2); }}
.quick-icon {{ font-size: 26px; margin-bottom: 4px; }}
.quick-name {{ font-size: 11px; font-weight: 700; }}
.quick-count {{ font-size: 10px; color: var(--text-muted); }}

/* 업무가이드 카테고리 색상 */
.cat-준비 {{ background: #E8F5E9; color: #2E7D32; }}
.cat-기입 {{ background: #E3F2FD; color: #1565C0; }}
.cat-참고 {{ background: #F3E5F5; color: #6A1B9A; }}
.cat-주의 {{ background: #FFF3CD; color: #856404; }}
.cat-절차 {{ background: #FFF8E1; color: #F57F17; }}
.cat-동의서 {{ background: #FCE4EC; color: #880E4F; }}
.cat-안내 {{ background: #E0F2F1; color: #00695C; }}

/* 관리자 */
.admin-login {{ max-width: 380px; margin: 60px auto; background: var(--card);
  border-radius: 16px; padding: 40px; box-shadow: var(--shadow); }}
.admin-login h2 {{ text-align: center; margin-bottom: 24px; font-size: 20px; }}
.form-group {{ margin-bottom: 16px; }}
.form-group label {{ display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; }}
.form-group input {{ width: 100%; padding: 10px 14px; border: 2px solid var(--border);
  border-radius: 8px; font-size: 14px; background: var(--bg); color: var(--text); outline: none; }}
.form-group input:focus {{ border-color: var(--primary); }}
.btn-primary {{ width: 100%; padding: 12px; background: var(--primary); color: white;
  border: none; border-radius: 8px; font-size: 15px; font-weight: 700; cursor: pointer; }}
.btn-primary:hover {{ background: #036B63; }}
.admin-wrap {{ display: flex; height: calc(100vh - 56px); }}
.admin-sidebar {{ width: 180px; background: var(--card); border-right: 1px solid var(--border); padding: 16px 0; flex-shrink: 0; }}
.admin-nav-item {{ padding: 12px 20px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s; }}
.admin-nav-item:hover, .admin-nav-item.active {{ background: var(--primary-light); color: var(--primary); }}
.admin-main {{ flex: 1; padding: 20px; overflow-y: auto; }}
.admin-toolbar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
.btn-export {{ background: var(--primary); color: white; border: none; padding: 10px 18px;
  border-radius: 8px; font-size: 13px; font-weight: 700; cursor: pointer; display: flex; align-items: center; gap: 6px; }}
.admin-table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 10px; overflow: hidden; box-shadow: var(--shadow); }}
.admin-table th {{ background: var(--primary-dark); color: white; padding: 10px 14px; font-size: 13px; text-align: left; }}
.admin-table td {{ padding: 10px 14px; font-size: 13px; border-bottom: 1px solid var(--border); }}
.admin-table tr:hover td {{ background: var(--primary-light); }}
.btn-edit {{ background: #E3F2FD; color: #1565C0; border: none; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; margin-right: 4px; }}
.btn-del  {{ background: #FFEBEE; color: #C62828; border: none; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: 600; }}

/* 모달 */
.modal {{ position: fixed; inset: 0; z-index: 500; display: none; align-items: center; justify-content: center; }}
.modal.show {{ display: flex; }}
.modal-overlay {{ position: absolute; inset: 0; background: rgba(0,0,0,0.5); }}
.modal-box {{ position: relative; background: var(--card); border-radius: 16px; padding: 28px;
  width: min(480px, 90%); box-shadow: 0 8px 32px rgba(0,0,0,0.2); z-index: 1; }}
.modal-box h3 {{ margin-bottom: 20px; font-size: 17px; }}
.modal-box .form-group input,
.modal-box .form-group select,
.modal-box .form-group textarea {{ width: 100%; padding: 9px 12px; border: 2px solid var(--border);
  border-radius: 8px; font-size: 13px; background: var(--bg); color: var(--text); outline: none; }}
.modal-box .form-group textarea {{ min-height: 80px; resize: vertical; }}
.modal-btns {{ display: flex; gap: 10px; margin-top: 20px; justify-content: flex-end; }}
.btn-cancel {{ padding: 9px 18px; border: 2px solid var(--border); border-radius: 8px; background: none; color: var(--text); cursor: pointer; font-size: 13px; font-weight: 600; }}
.confirm-modal .modal-box {{ text-align: center; max-width: 320px; }}
.confirm-modal .modal-box h3 {{ color: var(--danger); }}
.confirm-modal .modal-box p {{ font-size: 14px; color: var(--text-muted); margin-bottom: 20px; }}
.btn-danger {{ padding: 9px 18px; background: var(--danger); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; }}

@media (max-width: 600px) {{
  .content {{ padding: 12px 14px; }}
  .card-grid {{ grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); }}
}}
</style>
</head>
<body>

<!-- 헤더 -->
<header class="header">
  <div class="header-logo">
    <svg viewBox="0 0 28 28" fill="none">
      <circle cx="14" cy="14" r="14" fill="#048A81"/>
      <path d="M8 14h12M14 8v12" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
      <circle cx="14" cy="14" r="4" fill="none" stroke="white" stroke-width="2"/>
    </svg>
    NFH ER Mate
  </div>
  <div class="header-actions">
    <button class="btn-icon" onclick="toggleDark()">🌙 다크모드</button>
    <button class="btn-icon" onclick="showAdmin()">⚙️ 관리자</button>
  </div>
</header>

<!-- 검색 -->
<div class="search-wrap">
  <div class="search-box">
    <span class="search-icon">🔍</span>
    <input type="text" id="searchInput" placeholder="시술, 약물, 증상, 업무 등을 검색하세요..."
      oninput="handleSearch(this.value)" onblur="setTimeout(()=>hideSearch(),200)">
    <div class="search-results" id="searchResults"></div>
  </div>
</div>

<!-- 탭 -->
<div class="tabs" id="tabs">
  <div class="tab active" onclick="showTab('home')">🏠 전체</div>
  <div class="tab" onclick="showTab('procedure')">🏥 시술/검사</div>
  <div class="tab" onclick="showTab('drug')">💊 약물</div>
  <div class="tab" onclick="showTab('task')">📋 필수업무</div>
  <div class="tab" onclick="showTab('nursing')">📝 간호기록</div>
  <div class="tab" onclick="showTab('guide')">📚 업무가이드</div>
</div>

<!-- 컨텐츠 -->
<div class="content" id="mainContent"></div>

<!-- 패널 -->
<div class="panel-overlay" id="panelOverlay" onclick="closePanel()"></div>
<div class="panel" id="panel">
  <div class="panel-header">
    <button class="panel-back" onclick="closePanel()">←</button>
    <span class="panel-title" id="panelTitle"></span>
    <button class="panel-reset" id="panelResetBtn" onclick="resetChecks()" style="display:none">초기화</button>
  </div>
  <div class="panel-body" id="panelBody"></div>
  <div class="progress-wrap" id="progressWrap" style="display:none">
    <div class="progress-text">
      <span id="progressText">0 / 0 완료</span>
      <span id="progressPct">0%</span>
    </div>
    <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width:0%"></div></div>
  </div>
</div>

<!-- 편집 모달 -->
<div class="modal" id="editModal">
  <div class="modal-overlay" onclick="closeEditModal()"></div>
  <div class="modal-box">
    <h3>✏️ 항목 수정</h3>
    <div class="form-group"><label>구분</label>
      <select id="editCat"><option>준비사항</option><option>투약/약물</option><option>검사 후</option><option>주의사항</option><option>이송 부서</option></select></div>
    <div class="form-group"><label>내용</label><input type="text" id="editContent"></div>
    <div class="form-group"><label>주의사항 (선택)</label><textarea id="editWarning"></textarea></div>
    <div class="modal-btns">
      <button class="btn-cancel" onclick="closeEditModal()">취소</button>
      <button class="btn-primary" style="width:auto;padding:9px 20px" onclick="saveEdit()">저장</button>
    </div>
  </div>
</div>

<!-- 삭제 확인 모달 -->
<div class="modal confirm-modal" id="confirmModal">
  <div class="modal-overlay" onclick="closeConfirm()"></div>
  <div class="modal-box">
    <h3>⚠️ 삭제 확인</h3>
    <p id="confirmText">정말 삭제하시겠습니까?</p>
    <div class="modal-btns" style="justify-content:center">
      <button class="btn-cancel" onclick="closeConfirm()">취소</button>
      <button class="btn-danger" onclick="confirmDelete()">삭제 확인</button>
    </div>
  </div>
</div>

<script>
const DB = {data_js};

// ── 아이콘 매핑 ──────────────────────────────────
const PROC_ICONS = {{
  'CT':'🖥️','MRI':'🧲','CAG':'🫀','수혈':'🩸','ERCP':'🔬','EGD':'🔭','CFS':'🔬',
  'SFS':'🔬','BAE':'🩺','Embolization':'🩺','PTBD':'🩺','abdPCD':'🩺',
  'chestPCD':'🫁','PCN':'🫘','홀터':'❤️','EEG':'🧠','Echo':'🫀',
  'DJstent':'🩺','C-line':'💉','PEG':'🩺','Cardioversion':'⚡','Pacemaker':'🔋',
  'PTGBD':'🩺','OP':'🏥','Stroke':'🧠','복수천자':'🩺','요추천자':'🦴',
  '흉수천자':'🫁','PCC':'❤️',
}};
const TASK_ICONS = {{'퇴원':'🚪','입원':'🛏️','전원':'🚑','사망':'🕊️'}};
const DRUG_ICONS = {{'진통제/해열제':'💊','마약성 진통제':'💉','심혈관계':'🫀',
  '항응고제':'🩸','항생제':'🧪','스테로이드':'💊','이뇨제':'💧',
  '항구토제':'🤢','기관지확장제':'🫁','진정제/마취제':'😴',
  '항경련제':'⚡','혈전용해제':'🩸','전해질':'⚗️','혈당조절':'🍬',
  '해독제':'🛡️','소화기계':'🫙','삼투성이뇨제':'💧','기타응급약물':'💊'}};
const NURSING_ICONS = {{'통증':'🤕','통증평가':'📊','호흡':'🫁','출혈(눈에 보이는 출혈양상)':'🩸',
  '출혈(기타 외상 출혈-코피, 상처 출혈, 수술 출혈)':'🩹',
  '출혈위험(눈에 보이지 않지만 Hemoglobin 낮거나 과거 출혈 경향 있을떄':'⚠️',
  '감염':'🦠','감염위험':'⚠️','고체온':'🌡️','저체온':'🥶',
  '뇌경색/뇌출혈 의심':'🧠','심근경색 의심':'🫀','고혈당':'📈','저혈당':'📉','Seizure':'⚡'}};

let currentTab = 'home';
let panelChecks = {{}};
let panelType = '';
let panelId = '';
let isDark = false;
let isAdminMode = false;
let editTarget = null;
let deleteTarget = null;

// ── 다크모드 ──────────────────────────────────────
function toggleDark() {{
  isDark = !isDark;
  document.body.classList.toggle('dark', isDark);
}}

// ── 탭 전환 ──────────────────────────────────────
function showTab(tab) {{
  currentTab = tab;
  document.querySelectorAll('.tab').forEach((t,i) => {{
    const tabs = ['home','procedure','drug','task','nursing','guide'];
    t.classList.toggle('active', tabs[i] === tab);
  }});
  if (isAdminMode) {{ renderAdmin(); return; }}
  const renders = {{home:renderHome, procedure:renderProcedure, drug:renderDrug,
    task:renderTask, nursing:renderNursing, guide:renderGuide}};
  renders[tab]?.();
}}

// ── 검색 ──────────────────────────────────────────
function handleSearch(q) {{
  const box = document.getElementById('searchResults');
  if (!q.trim()) {{ box.classList.remove('show'); return; }}
  const kw = q.toLowerCase();
  const results = [];

  DB.procedures.forEach(p => {{
    if (p.name_en.toLowerCase().includes(kw) || p.name_ko.includes(kw))
      results.push({{type:'procedure', id:p.id, title:p.name_ko, sub:p.name_en, badge:'시술'}});
  }});
  DB.drugs.forEach(d => {{
    const match = d.name_en.toLowerCase().includes(kw) || d.name_ko.includes(kw)
      || d.aliases.toLowerCase().includes(kw)
      || d.keywords.some(k=>k.toLowerCase().includes(kw));
    if (match) results.push({{type:'drug', id:d.id, title:d.name_ko, sub:d.name_en+' · '+d.aliases.split(',').slice(0,2).join(', '), badge:'약물'}});
  }});
  DB.tasks.forEach(t => {{
    if (t.name.includes(kw)) results.push({{type:'task', id:t.id, title:t.name+' 체크리스트', sub:t.items.length+'개 항목', badge:'필수업무'}});
    t.items.forEach(item => {{
      if (item.item.includes(kw)) results.push({{type:'task', id:t.id, title:item.item, sub:t.name, badge:'필수업무'}});
    }});
  }});
  DB.nursing.forEach(n => {{
    Object.values(n.symptoms).forEach(s => {{
      if (s.name.includes(kw) || n.name.includes(kw))
        results.push({{type:'nursing', id:n.id+'|'+s.name, title:s.name, sub:n.name, badge:'간호기록'}});
    }});
  }});
  DB.guides.forEach(g => {{
    if (g.name_ko.includes(kw) || g.name_en.toLowerCase().includes(kw))
      results.push({{type:'guide', id:g.id, title:g.name_ko, sub:g.name_en, badge:'업무가이드'}});
  }});

  if (!results.length) {{
    box.innerHTML = '<div class="search-item"><div class="search-item-title">검색 결과 없음</div></div>';
  }} else {{
    box.innerHTML = results.slice(0,12).map(r =>
      `<div class="search-item" onclick="openFromSearch('${{r.type}}','${{r.id}}')">
        <div class="search-item-title">${{r.title}}<span class="search-badge">${{r.badge}}</span></div>
        <div class="search-item-sub">${{r.sub}}</div>
       </div>`).join('');
  }}
  box.classList.add('show');
}}
function hideSearch() {{ document.getElementById('searchResults').classList.remove('show'); }}
function openFromSearch(type, id) {{
  hideSearch();
  document.getElementById('searchInput').value = '';
  if (type === 'procedure') openProcedure(id);
  else if (type === 'drug') openDrug(id);
  else if (type === 'task') openTask(id);
  else if (type === 'guide') openGuide(id);
  else if (type === 'nursing') {{
    const [nid, sid] = id.split('|');
    openNursing(nid, sid);
  }}
}}

// ── 홈 렌더 ──────────────────────────────────────
function renderHome() {{
  const c = document.getElementById('mainContent');
  const topProcs = DB.procedures.slice(0,8);
  const topTasks = DB.tasks;
  const topDrugCats = [...new Set(DB.drugs.map(d=>d.category))].slice(0,6);

  c.innerHTML = `
    <div class="section-title">🏥 시술/검사 바로가기</div>
    <div class="card-grid">
      ${{topProcs.map(p=>`
        <div class="proc-card" onclick="openProcedure('${{p.id}}')">
          <div class="proc-card-icon">${{PROC_ICONS[p.id]||'🏥'}}</div>
          <div class="proc-card-name">${{p.name_ko||p.name_en}}</div>
        </div>`).join('')}}
      <div class="proc-card" onclick="showTab('procedure')">
        <div class="proc-card-icon">📋</div>
        <div class="proc-card-name">전체보기</div>
      </div>
    </div>

    <div class="section-title">💊 약물 카테고리</div>
    <div class="card-grid">
      ${{topDrugCats.map(cat=>`
        <div class="proc-card" onclick="showTab('drug')">
          <div class="proc-card-icon">${{DRUG_ICONS[cat]||'💊'}}</div>
          <div class="proc-card-name" style="font-size:10px">${{cat.replace('/',' ')}}</div>
        </div>`).join('')}}
    </div>

    <div class="section-title">📋 필수업무</div>
    <div class="card-grid">
      ${{topTasks.map(t=>`
        <div class="proc-card" onclick="openTask('${{t.id}}')">
          <div class="proc-card-icon">${{TASK_ICONS[t.name]||'📋'}}</div>
          <div class="proc-card-name">${{t.name}}</div>
          <div class="proc-card-sub">${{t.items.length}}개 항목</div>
        </div>`).join('')}}
    </div>

    <div class="section-title">📚 업무가이드 바로가기</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px">
      ${{DB.guides.slice(0,6).map(g=>`
        <div class="list-item" onclick="openGuide('${{g.id}}')" style="padding:10px 12px">
          <div class="list-item-left">
            <div class="list-item-title" style="font-size:13px">${{g.name_ko}}</div>
            <div class="list-item-sub">${{Object.values(g.items).flat().length}}개 항목</div>
          </div>
          <div class="list-item-arrow">›</div>
        </div>`).join('')}}
    </div>
  `;
}}

// ── 시술 렌더 ──────────────────────────────────────
function renderProcedure() {{
  const c = document.getElementById('mainContent');
  c.innerHTML = `
    <div class="section-title">🏥 시술/검사 준비 체크리스트</div>
    <div class="card-grid">
      ${{DB.procedures.map(p=>`
        <div class="proc-card" onclick="openProcedure('${{p.id}}')">
          <div class="proc-card-icon">${{PROC_ICONS[p.id]||'🏥'}}</div>
          <div class="proc-card-name">${{p.name_ko||p.name_en}}</div>
          <div class="proc-card-sub">${{p.name_en}}</div>
        </div>`).join('')}}
    </div>`;
}}

function openProcedure(id) {{
  const p = DB.procedures.find(x=>x.id===id);
  if (!p) return;
  panelType = 'procedure'; panelId = id;
  if (!panelChecks[id]) panelChecks[id] = {{}};

  const catConfig = [
    ['준비사항','📋','prep-title'],['투약/약물','💉','med-title'],
    ['검사 후','🔍','post-title'],['주의사항','⚠️','warn-title'],['이송 부서','🏥','transport-title']
  ];
  let checkIdx = 0;
  let allItems = [];
  catConfig.forEach(([cat]) => {{ if(p[cat]) p[cat].forEach(()=>allItems.push(cat)); }});

  let html = '';
  catConfig.forEach(([cat, icon, cls]) => {{
    const items = p[cat] || [];
    if (!items.length) return;
    const isWarn = cat === '주의사항' || cat === '이송 부서';
    html += `<div class="checklist-section">
      <div class="checklist-section-title ${{cls}}">${{icon}} ${{cat}}</div>`;
    items.forEach((item, i) => {{
      const key = cat+'_'+i;
      if (isWarn) {{
        html += `<div class="warn-item">⚠️ ${{item}}</div>`;
      }} else {{
        const chk = panelChecks[id][key] ? 'checked' : '';
        html += `<div class="check-item ${{chk}}" onclick="toggleCheck('${{key}}')">
          <div class="check-box"><span class="check-box-inner">✓</span></div>
          <div><div class="check-text">${{item}}</div></div>
        </div>`;
      }}
    }});
    html += '</div>';
  }});

  openPanel(p.name_ko || p.name_en, html, true);
  updateProgress(id);
}}

// ── 약물 렌더 ──────────────────────────────────────
function renderDrug() {{
  const c = document.getElementById('mainContent');
  const cats = [...new Set(DB.drugs.map(d=>d.category))];
  c.innerHTML = cats.map(cat => {{
    const drugs = DB.drugs.filter(d=>d.category===cat);
    return `<div class="cat-header">${{DRUG_ICONS[cat]||'💊'}} ${{cat}}</div>
      ${{drugs.map(d=>`
        <div class="list-item" onclick="openDrug('${{d.id}}')">
          <div class="list-item-left">
            <div class="list-item-title">${{d.name_en}} <span style="font-weight:400;color:var(--text-muted)">${{d.name_ko}}</span></div>
            <div class="list-item-sub">${{d.aliases.split(',').slice(0,3).join(' · ')}}</div>
          </div>
          <div class="list-item-arrow">›</div>
        </div>`).join('')}}`;
  }}).join('');
}}

function openDrug(id) {{
  const d = DB.drugs.find(x=>x.id===id);
  if (!d) return;
  panelType = 'drug'; panelId = id;

  const rows = [
    ['💊 용량', d.dose], ['🧪 믹스법', d.mix],
    ['🚗 투여경로', d.route], ['⏱️ 속도', d.speed]
  ].filter(r=>r[1]).map(r=>`<tr><td>${{r[0]}}</td><td>${{r[1]}}</td></tr>`).join('');

  const html = `
    <div class="drug-category-badge">${{d.category}}</div>
    <div class="drug-alias">별칭: ${{d.aliases||'-'}}</div>
    <table class="drug-table"><tbody>${{rows}}</tbody></table>
    ${{d.warning ? `<div style="margin-top:12px">
      <div class="checklist-section-title warn-title">⚠️ 주의사항</div>
      ${{d.warning.split('/').map(w=>`<div class="warn-item">${{w.trim()}}</div>`).join('')}}
    </div>` : ''}}`;

  openPanel(d.name_en + ' / ' + d.name_ko, html, false);
}}

// ── 필수업무 렌더 ──────────────────────────────────
function renderTask() {{
  const c = document.getElementById('mainContent');
  c.innerHTML = `
    <div class="section-title">📋 필수업무 체크리스트</div>
    <div class="card-grid">
      ${{DB.tasks.map(t=>`
        <div class="proc-card" onclick="openTask('${{t.id}}')">
          <div class="proc-card-icon">${{TASK_ICONS[t.name]||'📋'}}</div>
          <div class="proc-card-name">${{t.name}}</div>
          <div class="proc-card-sub">${{t.items.length}}개 항목</div>
        </div>`).join('')}}
    </div>`;
}}

function openTask(id) {{
  const t = DB.tasks.find(x=>x.id===id);
  if (!t) return;
  panelType = 'task'; panelId = id;
  if (!panelChecks[id]) panelChecks[id] = {{}};

  const html = t.items.map(item => {{
    const key = 'item_'+item.num;
    const chk = panelChecks[id][key] ? 'checked' : '';
    return `<div class="check-item ${{chk}}" onclick="toggleCheck('${{key}}')">
      <div class="check-box"><span class="check-box-inner">✓</span></div>
      <div>
        <div class="check-text"><strong>${{item.num}}.</strong> ${{item.item}}</div>
        ${{item.desc ? `<div class="check-note">${{item.desc}}</div>` : ''}}
      </div>
    </div>`;
  }}).join('');

  openPanel(t.name + ' 체크리스트', html, true);
  updateProgress(id);
}}

// ── 간호기록 렌더 ──────────────────────────────────
function renderNursing() {{
  const c = document.getElementById('mainContent');
  c.innerHTML = DB.nursing.map(n => `
    <div class="cat-header">${{NURSING_ICONS[n.name]||'📝'}} ${{n.name}}</div>
    ${{Object.values(n.symptoms).map(s=>`
      <div class="list-item" onclick="openNursing('${{n.id}}','${{s.name}}')">
        <div class="list-item-left">
          <div class="list-item-title">${{s.name}}</div>
        </div>
        <div class="list-item-arrow">›</div>
      </div>`).join('')}}
  `).join('');
}}

function openNursing(nid, sname) {{
  const n = DB.nursing.find(x=>x.id===nid);
  if (!n) return;
  const s = n.symptoms[sname];
  if (!s) return;
  panelType = 'nursing'; panelId = nid+'|'+sname;
  if (!panelChecks[panelId]) panelChecks[panelId] = {{}};

  const sectionConfig = {{
    '사정 및 평가(A&E)': ['📊 사정 및 평가', 'ae-title'],
    '간호진단(D)':       ['🏷️ 간호진단',      'diag-title'],
    '계획 및 중재(P&E)': ['📌 계획 및 중재',  'plan-title'],
  }};

  let html = '';
  let globalIdx = 0;
  Object.entries(s.sections).forEach(([subName, procs]) => {{
    html += `<div style="font-size:12px;font-weight:700;color:var(--text-muted);margin:14px 0 6px;padding-left:4px">${{subName}}</div>`;
    Object.entries(procs).forEach(([proc, items]) => {{
      const [title, cls] = sectionConfig[proc] || [proc, 'ae-title'];
      html += `<div class="checklist-section">
        <div class="checklist-section-title ${{cls}}">${{title}}</div>`;
      items.forEach(item => {{
        const key = 'n_'+globalIdx++;
        const chk = panelChecks[panelId][key] ? 'checked' : '';
        html += `<div class="check-item ${{chk}}" onclick="toggleCheck('${{key}}')">
          <div class="check-box"><span class="check-box-inner">✓</span></div>
          <div>
            <div class="check-text">${{item.text}}</div>
            ${{item.note ? `<div class="nursing-note">📌 ${{item.note}}</div>` : ''}}
          </div>
        </div>`;
      }});
      html += '</div>';
    }});
  }});

  openPanel(sname, html, true);
  updateProgress(panelId);
}}

// ── 업무가이드 렌더 ──────────────────────────────────
function renderGuide() {{
  const c = document.getElementById('mainContent');
  c.innerHTML = DB.guides.map(g => `
    <div class="list-item" onclick="openGuide('${{g.id}}')">
      <div class="list-item-left">
        <div class="list-item-title">${{g.name_ko}} <span style="font-size:11px;color:var(--text-muted)">${{g.name_en}}</span></div>
        <div class="list-item-sub">${{Object.values(g.items).flat().length}}개 항목</div>
      </div>
      <div class="list-item-arrow">›</div>
    </div>`).join('');
}}

function openGuide(id) {{
  const g = DB.guides.find(x=>x.id===id);
  if (!g) return;
  panelType = 'guide'; panelId = id;

  const catCls = {{'준비':'cat-준비','기입':'cat-기입','참고':'cat-참고','주의':'cat-주의','절차':'cat-절차','동의서':'cat-동의서','안내':'cat-안내'}};
  const html = Object.entries(g.items).map(([cat, items]) =>
    `<div class="checklist-section">
      <div class="checklist-section-title ${{catCls[cat]||'ae-title'}}">${{cat}}</div>
      ${{items.map(item => item.includes('⚠️')
        ? `<div class="warn-item">${{item}}</div>`
        : `<div class="check-item"><div class="check-box"></div><div class="check-text">${{item}}</div></div>`
      ).join('')}}
    </div>`
  ).join('');

  openPanel(g.name_ko, html, false);
}}

// ── 패널 제어 ──────────────────────────────────────
function openPanel(title, html, hasProgress) {{
  document.getElementById('panelTitle').textContent = title;
  document.getElementById('panelBody').innerHTML = html;
  document.getElementById('panelResetBtn').style.display = hasProgress ? '' : 'none';
  document.getElementById('progressWrap').style.display = hasProgress ? '' : 'none';
  document.getElementById('panel').classList.add('open');
  document.getElementById('panelOverlay').classList.add('show');
}}
function closePanel() {{
  document.getElementById('panel').classList.remove('open');
  document.getElementById('panelOverlay').classList.remove('show');
}}

// ── 체크 토글 ──────────────────────────────────────
function toggleCheck(key) {{
  if (!panelChecks[panelId]) panelChecks[panelId] = {{}};
  panelChecks[panelId][key] = !panelChecks[panelId][key];
  const items = document.querySelectorAll('.check-item');
  items.forEach(el => {{
    const onclick = el.getAttribute('onclick');
    if (onclick && onclick.includes(`'${{key}}'`)) {{
      el.classList.toggle('checked', !!panelChecks[panelId][key]);
    }}
  }});
  updateProgress(panelId);
}}
function resetChecks() {{
  panelChecks[panelId] = {{}};
  document.querySelectorAll('.check-item').forEach(el => el.classList.remove('checked'));
  updateProgress(panelId);
}}
function updateProgress(id) {{
  const checks = panelChecks[id] || {{}};
  const total = document.querySelectorAll('.check-item').length;
  const done = Object.values(checks).filter(Boolean).length;
  document.getElementById('progressText').textContent = `${{done}} / ${{total}} 완료`;
  const pct = total ? Math.round(done/total*100) : 0;
  document.getElementById('progressPct').textContent = pct + '%';
  document.getElementById('progressFill').style.width = pct + '%';
}}

// ── 관리자 ──────────────────────────────────────────
let adminSection = 'procedure';
function showAdmin() {{
  const pw = prompt('관리자 비밀번호를 입력하세요:');
  if (pw !== '1234') {{ if(pw!==null) alert('비밀번호가 올바르지 않습니다.'); return; }}
  isAdminMode = true;
  document.getElementById('mainContent').innerHTML = '';
  renderAdmin();
}}
function renderAdmin() {{
  const c = document.getElementById('mainContent');
  const sectionData = {{
    procedure: DB.procedures,
    drug: DB.drugs,
    task: DB.tasks,
    guide: DB.guides,
  }};
  const sectionNames = {{procedure:'시술/검사', drug:'약물', task:'필수업무', guide:'업무가이드'}};
  const items = sectionData[adminSection] || [];

  c.innerHTML = `
    <div class="admin-wrap">
      <div class="admin-sidebar">
        ${{Object.entries(sectionNames).map(([k,v])=>`
          <div class="admin-nav-item ${{adminSection===k?'active':''}}" onclick="adminSection='${{k}}';renderAdmin()">${{v}}</div>
        `).join('')}}
      </div>
      <div class="admin-main">
        <div class="admin-toolbar">
          <strong>${{sectionNames[adminSection]}} 관리</strong>
          <button class="btn-export" onclick="exportData()">💾 웹 패키지 내보내기</button>
        </div>
        <table class="admin-table">
          <thead><tr><th>이름(영문)</th><th>이름(한글)</th><th>항목 수</th><th>관리</th></tr></thead>
          <tbody>
            ${{items.map((item,i)=>`
              <tr>
                <td>${{item.name_en||item.id||item.name||''}}</td>
                <td>${{item.name_ko||item.name||''}}</td>
                <td>${{item.items?.length || Object.values(item['준비사항']||{{}}).length || '-'}}</td>
                <td>
                  <button class="btn-edit" onclick="openEdit(${{i}})">수정</button>
                  <button class="btn-del" onclick="openDelete(${{i}})">삭제</button>
                </td>
              </tr>`).join('')}}
          </tbody>
        </table>
      </div>
    </div>`;
}}
function openEdit(i) {{
  editTarget = i;
  document.getElementById('editModal').classList.add('show');
}}
function closeEditModal() {{ document.getElementById('editModal').classList.remove('show'); }}
function saveEdit() {{ closeEditModal(); alert('저장되었습니다. (실제 저장은 서버 연동 후 반영)'); }}
function openDelete(i) {{
  deleteTarget = i;
  document.getElementById('confirmText').textContent = '정말 이 항목을 삭제하시겠습니까?';
  document.getElementById('confirmModal').classList.add('show');
}}
function closeConfirm() {{ document.getElementById('confirmModal').classList.remove('show'); }}
function confirmDelete() {{ closeConfirm(); alert('삭제되었습니다. (실제 삭제는 서버 연동 후 반영)'); }}
function exportData() {{
  const blob = new Blob([JSON.stringify(DB.data, null, 2)], {{type:'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'er_mate_data_' + new Date().toISOString().slice(0,10) + '.json';
  a.click();
  alert('JSON 데이터를 내보냈습니다. HTML 파일과 함께 배포하세요.');
}}

// ── 초기화 ──────────────────────────────────────────
renderHome();
</script>
</body>
</html>'''

out = '/Users/sungkwanchoi/NFH_New/er_mate.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize(out)
print(f"✅ er_mate.html 생성 완료 ({size//1024}KB)")
