---
name: doc-status
description: 서비스 폴더의 문서들이 '정본(canonical)이 관심사별로 하나뿐인지'를 검증한다. 각 문서 상단 상태 마커(.md frontmatter / .html 주석)를 읽어 정본·보조·구버전·아카이브를 분류하고, 같은 관심사에 정본이 둘 이상이거나 정본이 구버전을 참조하면 잡아낸다. "어느 게 최신/정본이야?", "문서 버전 헷갈려", 문서를 새로 만들거나 구버전을 아카이브한 뒤 확인할 때 사용.
---

# doc-status

문서가 여러 버전으로 늘어나면 "뭐가 최신인지" 헷갈린다. 이 스킬은 **각 문서가 스스로 선언한 상태 마커**를 읽어 관심사(ssot_for)별 **정본이 하나뿐인지** 기계로 보증한다.

`auto-save` 훅 때문에 git 커밋 날짜는 "최신 내용"의 근거가 못 된다. **상태 마커가 유일한 진실원**이다.

## 상태 마커 규약

**.md — 파일 맨 위 YAML frontmatter:**
```yaml
---
status: canonical      # canonical(정본) | support(보조·배경) | deprecated(구버전) | archived
ssot_for: 요구사항       # 이 문서가 '정본'인 관심사 (요구사항/기능/흐름/UI ...)
version: v4
updated: 2026-06-20
supersedes: v3.1        # (선택) 대체한 이전 버전
---
```

**.html — 파일 맨 위 주석:**
```html
<!-- doc-status: status=canonical ssot_for=UI version=v4 updated=2026-06-18 -->
```

- `_archive/` 폴더 안 파일은 마커가 없어도 자동 **archived** 처리.
- `README.md`·`CLAUDE.md`·`CONVENTION.md`는 도구 강제 파일이라 마커 면제.

## 실행
```bash
python3 .claude/skills/doc-status/status.py [서비스폴더 ...]
```
- 인자 없음 → `3_서비스/*` 전체 서비스 검사.
- 특정 서비스만: `python3 .claude/skills/doc-status/status.py 3_서비스/NFH간호기록`

## 결과 읽는 법
- 🟢 정본 / 🟡 보조 / 🔴 구버전 / 📦 아카이브 / ⚪ 마커없음 으로 문서를 분류해 보여준다.
- ❌ **'<관심사>' 정본이 N개** — 같은 ssot_for에 canonical이 둘 이상. 하나만 남기고 나머지를 support/deprecated로 내리거나 아카이브한다. (exit 1)
- ⚠ **구버전/아카이브 참조** — 정본·보조 문서가 본문에서 아카이브된 파일을 링크. 링크를 정본으로 갱신한다. (`supersedes:`/`대체` 표기는 제외)
- ⚠ **마커 없음** — 상태 마커를 안 단 문서. 위 규약대로 마커를 추가한다.

## 종료코드
`0` 정본 유일(통과) · `1` 정본 충돌 · `2` 검사 대상 못 찾음. 커밋 전 게이트로 쓸 수 있다.

## 새 문서를 만들 때
정본으로 쓸 문서엔 `status: canonical` + `ssot_for`를 붙이고, **그 관심사의 기존 정본은 deprecated로 내리거나 `_archive/`로 옮긴다**(CONVENTION.md §3 — 파일명에 버전 박지 않기). 그래야 정본이 항상 하나로 유지된다.
