#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
소아 지속주입(CIV) 계산 검증 — 투약앱_V4.html

왜 필요한가
  PEDS_CIV 는 교수·약제부 회신이 올 때마다 값이 채워진다.
  그때 「농도만 넣고 범위를 안 넣는다」거나 「계산 가능한데 질의 배지가 남는다」
  같은 어긋남이 생기기 쉽다. 손으로 화면을 보며 세지 않으려고 만든 검사기.

무엇을 검사하나
  1) civRate 계산식이 손계산과 맞는가
  2) PEDS_CIV 각 항목의 상태가 일관적인가
     - 계산 가능(conc+steps)한데 질의 배지가 남아 있지 않은가
     - 계산 불가인데 막힌 이유(ask)가 비어 있지 않은가
     - def(기본 눈금)가 steps 안에 있는가
  3) renderPedsCIV 출력에 undefined / NaN 이 새지 않는가

사용:  python3 검증_소아CIV_260811.py
필요:  macOS 내장 JavaScriptCore (jsc) — node 없이 동작
"""
import io, os, re, subprocess, sys, tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(BASE, 'app', '투약앱_V4.html')
JSC  = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc'

if not os.path.exists(JSC):
    sys.exit('❌ jsc 를 찾지 못했습니다: %s' % JSC)

src = io.open(SRC, encoding='utf-8').read()
m = re.search(r'<script>(.*?)</script>', src, re.S)
if not m:
    sys.exit('❌ <script> 블록을 찾지 못했습니다')

tmp = tempfile.mkdtemp()
app_js = os.path.join(tmp, 'app.js')
io.open(app_js, 'w', encoding='utf-8').write(m.group(1))

# 앱은 브라우저 전제로 짜여 있다 → 계산 함수만 부르기 위한 최소 DOM 스텁
HARNESS = r'''
var _el = new Proxy({}, { get:function(t,k){
  if(k==='classList') return {add:function(){},remove:function(){},toggle:function(){}};
  if(k==='style')     return {setProperty:function(){},removeProperty:function(){},getPropertyValue:function(){return ''}};
  if(k==='forEach'||k==='map') return function(){ return []; };
  if(k==='value'||k==='innerHTML'||k==='textContent') return '';
  if(k==='offsetHeight'||k==='offsetWidth'||k==='scrollTop') return 0;
  if(k==='dataset') return {};
  return function(){ return _el; };
}, set:function(){ return true; } });
var document = { getElementById:function(){return _el}, querySelectorAll:function(){return []},
  querySelector:function(){return _el}, addEventListener:function(){},
  createElement:function(){return _el}, head:_el, documentElement:_el, body:_el };
var window = { addEventListener:function(){}, matchMedia:function(){return {matches:false,addEventListener:function(){}}} };
var localStorage = { getItem:function(){return null}, setItem:function(){} };
var navigator = { userAgent:'' };
load('__APP_JS__');

var fail = 0;
function chk(ok, label, extra){ print((ok?'  ✅ ':'  ❌ ') + label + (extra?('  '+extra):'')); if(!ok) fail++; }

print('── 1. 계산식 (손계산 대조) ──');
// ml/hr = mcg/kg/min × kg × 60 ÷ 농도(mcg/mL)
// ★ 소아 전용 계산 함수는 만들지 않는다 (요구사항정의서 §2.4.2 — 계산 이원화 금지).
//   성인과 동일한 검증 엔진 calcInfusion 을 그대로 검사한다.
function CIV(mk,w,conc){ return calcInfusion(mk,'mcg/kg/min',conc,w); }
chk(typeof calcInfusion==='function', '성인 엔진 calcInfusion 을 사용 중');
chk(typeof this.civRate==='undefined', '소아 전용 중복 구현(civRate) 없음');
chk(CIV(10,10,2000)===3,      '10kg · 10mcg/kg/min · 2000mcg/mL → 3 ml/hr',      '실제 '+CIV(10,10,2000));
chk(Math.abs(CIV(2,3,2000)-0.18)<1e-9,  '3kg · 2mcg/kg/min → 0.18 ml/hr',        '실제 '+CIV(2,3,2000));
chk(Math.abs(CIV(20,32,2000)-19.2)<1e-9,'32kg · 20mcg/kg/min → 19.2 ml/hr',      '실제 '+CIV(20,32,2000));

print('── 2. PEDS_CIV 상태 일관성 ──');
PEDS_CIV.forEach(function(d){
  var calc = !!(d.conc && d.steps);
  print('  ' + (calc?'계산 ✅':'보류 ⬜') + '  ' + d.name +
        '  conc=' + d.conc + '  range=' + (d.range?d.range.join('~'):'null') +
        '  ' + (d.ask?('Q'+d.ask.q):'—'));
  if(calc){
    chk(d.steps.indexOf(d.def)>=0, '   ' + d.name + ': def 가 steps 안에 있음');
    chk(!d.ask,                    '   ' + d.name + ': 계산 가능 → 질의 배지 없음');
    chk(!!d.range,                 '   ' + d.name + ': 용량 범위 있음');
  } else {
    chk(!!d.ask && !!d.ask.q,      '   ' + d.name + ': 막힌 이유(Q번호) 기재됨');
    chk(!!d.ask && !!d.ask.why,    '   ' + d.name + ': 막힌 사유 문장 있음');
  }
});

print('── 3. renderPedsCIV 출력 ──');
[3, 15, 32].forEach(function(w){
  var html = renderPedsCIV(w);
  chk(html.indexOf('undefined')<0, w+'kg: undefined 누출 없음');
  chk(html.indexOf('NaN')<0,       w+'kg: NaN 누출 없음');
  chk(html.indexOf('Infinity')<0,  w+'kg: Infinity 누출 없음');
});
// 계산 가능한 약물 수와 화면 배지가 맞는가
var okN = PEDS_CIV.filter(function(d){ return d.conc && d.steps; }).length;
chk(renderPedsCIV(15).indexOf(okN+'/'+PEDS_CIV.length+' 계산 가능')>=0,
    '헤더 배지가 실제 계산 가능 수('+okN+'/'+PEDS_CIV.length+')와 일치');

print('');
print(fail===0 ? '✅ 전부 통과' : ('❌ 실패 ' + fail + '건'));
if(fail) { throw new Error('검증 실패'); }
'''

harness = os.path.join(tmp, 'test.js')
io.open(harness, 'w', encoding='utf-8').write(HARNESS.replace('__APP_JS__', app_js))

print('검증 대상: %s' % os.path.relpath(SRC, BASE))
r = subprocess.run([JSC, harness], capture_output=True, text=True)
sys.stdout.write(r.stdout)
if r.stderr.strip():
    sys.stderr.write(r.stderr)
sys.exit(r.returncode)
