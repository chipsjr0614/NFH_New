#!/usr/bin/env python3
"""
투약앱_V4.html  →  Artifact(claude.ai) 게시용 빌드

왜 필요한가
  Artifact는 올린 파일을 <!doctype html><head>…</head><body> 로 감싼다.
  V4는 완전한 HTML 문서라 그대로 올리면 html/head/body 가 중첩되고,
  특히 <meta name="viewport"> 가 무시돼 폰에서 데스크탑 폭으로 렌더된다.

무엇을 하는가
  1) V4에서 <style> / body 내용 / <script> 만 뽑아낸다
  2) head 에 들어가야 할 meta(viewport·theme-color·format-detection 등)를
     런타임에 JS로 주입하는 코드를 앞에 붙인다
  3) 결과를 _web 파일로 쓴다  (자동 생성물 — 직접 수정 금지)

★ 원본은 언제나 app/투약앱_V4.html 하나다.
  앱을 고치면 이 스크립트를 다시 돌려서 게시본을 만든다. 손으로 고치지 말 것.

사용:  python3 build_web_260808.py
"""
import re, io, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(BASE, 'app', '투약앱_V4.html')
OUT  = os.path.join(BASE, 'app', '투약앱_V4_web.html')

src = io.open(SRC, encoding='utf-8').read()

style  = re.search(r'<style>(.*?)</style>', src, re.S)
script = re.search(r'<script>(.*?)</script>', src, re.S)
if not style or not script:
    sys.exit('❌ <style> 또는 <script> 블록을 찾지 못했습니다')

# body 안쪽에서 <script> 를 뺀 나머지 = 화면 마크업
body = re.search(r'<body>(.*?)</body>', src, re.S).group(1)
body = body.replace(script.group(0), '').strip()

# head 로 가야 하는 meta 들을 런타임 주입 (Artifact는 head를 대신 만들기 때문)
meta_boot = '''
/* ── Artifact 게시본 부팅: head meta 주입 ────────────────────────────
   Artifact가 head를 대신 만들므로, 모바일에 필수인 meta 를 직접 넣는다.
   viewport 가 없으면 폰에서 데스크탑 폭(980px)으로 렌더된다.        */
(function(){
  function meta(attrs){
    for(var k in attrs){}
    var sel='meta['+(attrs.name?'name="'+attrs.name+'"':'')+']';
    if(attrs.name && document.head.querySelector(sel)) return;
    var m=document.createElement('meta');
    for(var a in attrs) m.setAttribute(a, attrs[a]);
    document.head.appendChild(m);
  }
  meta({name:'viewport', content:'width=device-width,initial-scale=1,viewport-fit=cover'});
  meta({name:'format-detection', content:'telephone=no,date=no,address=no,email=no'});
  meta({name:'apple-mobile-web-app-capable', content:'yes'});
  meta({name:'mobile-web-app-capable', content:'yes'});
  meta({name:'apple-mobile-web-app-status-bar-style', content:'black-translucent'});
  meta({name:'apple-mobile-web-app-title', content:'NFH 투약'});
  var t1=document.createElement('meta'); t1.name='theme-color';
  t1.content='#0F1319'; t1.media='(prefers-color-scheme:dark)'; document.head.appendChild(t1);
  var t2=document.createElement('meta'); t2.name='theme-color';
  t2.content='#EDF1F5'; t2.media='(prefers-color-scheme:light)'; document.head.appendChild(t2);
  document.documentElement.setAttribute('lang','ko');
})();
'''

out = (
    '<title>💊 NFH 통합 투약 앱 V4</title>\n'
    '<style>' + style.group(1) + '</style>\n'
    + body + '\n'
    '<script>' + meta_boot + script.group(1) + '</script>\n'
)

io.open(OUT, 'w', encoding='utf-8').write(out)

print('✅ 게시본 생성: %s' % os.path.relpath(OUT, BASE))
print('   원본 %d KB  →  게시본 %d KB' % (len(src.encode())//1024, len(out.encode())//1024))
for tag in ('<html', '<head', '<body', '<!DOCTYPE'):
    if tag.lower() in out.lower():
        print('   ⚠️ 중첩 위험 태그가 남아 있습니다: %s' % tag)
print('   외부 요청: %d 건 (0이어야 함)'
      % len(re.findall(r'(?:src|href)\s*=\s*["\']https?://', out)))
