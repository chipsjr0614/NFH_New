#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doc-status: 서비스 폴더의 문서 상태 마커를 읽어 '정본(canonical)이 관심사별로 하나뿐인지' 검증한다.

상태 마커
  .md  : 파일 맨 위 YAML frontmatter
           ---
           status: canonical|support|deprecated|archived
           ssot_for: 요구사항      # 이 문서가 정본인 '관심사'
           version: v4
           ---
  .html: 파일 맨 위 주석
           <!-- doc-status: status=canonical ssot_for=UI version=v4 -->
  _archive/ 안의 파일은 마커가 없어도 자동으로 archived 취급.

규칙
  ❌ 같은 (서비스, ssot_for)에 canonical 이 2개 이상  → 충돌 (exit 1)
  ⚠ 정본/보조 문서가 archived/deprecated 문서를 본문에서 링크
  ⚠ 마커 없는 문서 (README/CLAUDE/CONVENTION 은 면제)
"""
import sys, re
from pathlib import Path

ICON = {'canonical':'🟢 정본','support':'🟡 보조','deprecated':'🔴 구버전',
        'archived':'📦 아카이브','?':'⚪ 마커없음'}
EXEMPT = {'README.md','CLAUDE.md','CONVENTION.md'}

def parse_md(text):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.S)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if ':' in line and not line.strip().startswith('#'):
            k, v = line.split(':', 1)
            meta[k.strip()] = v.strip()
    return meta

def parse_html(text):
    m = re.search(r'<!--\s*doc-status:\s*(.*?)-->', text[:2000], re.S)
    if not m:
        return None
    meta = {}
    for tok in m.group(1).split():
        if '=' in tok:
            k, v = tok.split('=', 1)
            meta[k] = v
    return meta

def load_meta(path):
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return None, ''
    if path.suffix == '.md':
        return parse_md(text), text
    if path.suffix == '.html':
        return parse_html(text), text
    return None, text

def scan_service(svc):
    docs = []
    for p in sorted(svc.rglob('*')):
        if p.suffix not in ('.md', '.html'):
            continue
        archived = '_archive' in p.parts
        meta, text = load_meta(p)
        if meta is None:
            meta = {}
        if archived and not meta.get('status'):
            meta['status'] = 'archived'
        docs.append({'rel': p.relative_to(svc), 'path': p, 'text': text,
                     'meta': meta, 'archived': archived,
                     'status': meta.get('status', '?')})
    return docs

def report_service(svc):
    docs = scan_service(svc)
    if not docs:
        return 0
    errors, warns = [], []
    print(f"\n■ {svc.name}")

    # 1) 목록 출력 (아카이브 제외 먼저, 아카이브는 접어서)
    live = [d for d in docs if not d['archived']]
    arch = [d for d in docs if d['archived']]
    for d in live:
        st = d['status']
        if d['rel'].name in EXEMPT and st == '?':
            continue  # 면제 파일은 마커 없어도 조용히
        ssot = d['meta'].get('ssot_for', '')
        ver = d['meta'].get('version', '')
        tail = f"  · {ssot}{(' ' + ver) if ver else ''}" if ssot else ''
        print(f"   {ICON.get(st, st):<10} {str(d['rel'])}{tail}")
        if st == '?' and d['rel'].name not in EXEMPT:
            warns.append(f"마커 없음: {d['rel']}")
    if arch:
        print(f"   📦 아카이브 {len(arch)}개: " + ", ".join(str(d['rel'].name) for d in arch))

    # 2) canonical 충돌 검사 (관심사별 1개)
    by_ssot = {}
    for d in live:
        if d['status'] == 'canonical':
            by_ssot.setdefault(d['meta'].get('ssot_for', '(미지정)'), []).append(d['rel'])
    for ssot, items in by_ssot.items():
        if len(items) > 1:
            errors.append(f"'{ssot}' 정본이 {len(items)}개: " + ", ".join(str(i) for i in items))

    # 3) 정본/보조가 아카이브·구버전 문서를 링크하는지
    #    아카이브 전 원래 경로(= _archive/ 제거)로 정밀 매칭한다.
    #    (basename 만 보면 'app/index.html' 이 아카이브된 'index.html' 과 오탐나므로)
    dead_paths = {}
    for d in docs:
        if d['status'] in ('archived', 'deprecated'):
            orig = str(d['rel']).replace('_archive/', '').replace('_archive\\', '')
            dead_paths[orig] = d['rel'].name
    for d in live:
        if d['status'] not in ('canonical', 'support'):
            continue
        body = re.sub(r'(supersedes|대체)\s*[:=].*', '', d['text'])  # 대체 표기는 제외
        for orig, name in dead_paths.items():
            if orig in body:
                warns.append(f"{d['rel']} 가 구버전/아카이브 '{orig}' 를 참조")

    for e in errors:
        print(f"   ❌ {e}")
    for w in warns:
        print(f"   ⚠  {w}")
    if not errors and not warns:
        print("   ✓ 이상 없음")
    return 1 if errors else 0

def find_services(root):
    base = root / '3_서비스'
    if base.is_dir():
        return [p for p in sorted(base.iterdir()) if p.is_dir()]
    return []

def main(argv):
    root = Path.cwd()
    args = [a for a in argv[1:] if not a.startswith('-')]
    if args:
        services = [Path(a) for a in args]
    else:
        services = find_services(root)
        if not services:
            print("3_서비스/ 를 못 찾음. 검사할 서비스 폴더 경로를 인자로 주세요.")
            return 2
    rc = 0
    print(f"📋 doc-status — 정본 검증 (서비스 {len(services)}개)")
    for svc in services:
        if not Path(svc).is_dir():
            print(f"   (건너뜀, 폴더 아님: {svc})")
            continue
        rc |= report_service(Path(svc))
    print(f"\n{'❌ 충돌 있음 (정본 정리 필요)' if rc else '✅ 모든 서비스 정본 유일'}")
    return rc

if __name__ == '__main__':
    sys.exit(main(sys.argv))
