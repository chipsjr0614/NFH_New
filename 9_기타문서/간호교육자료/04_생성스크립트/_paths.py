#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공용 경로 모듈 — 스크립트를 어느 위치에서 실행해도 폴더 구조에 맞게
입력 파일을 찾고 결과를 올바른 폴더에 저장하도록 경로를 자동 보정한다.

폴더 구조 (간호교육자료/):
  01_케이스_엑셀(최종)/   ← 엑셀 결과물
  02_교육프로그램_HTML/    ← HTML 결과물
  04_생성스크립트/         ← 본 스크립트 위치
  99_보관_구버전/          ← 구버전(입력으로 쓰이기도 함)
"""
import os, glob

_HERE = os.path.dirname(os.path.abspath(__file__))     # 04_생성스크립트/
BASE = os.path.dirname(_HERE)                          # 간호교육자료/
FINAL_DIR = os.path.join(BASE, "01_케이스_엑셀(최종)")
HTML_DIR = os.path.join(BASE, "02_교육프로그램_HTML")
ARCHIVE_DIR = os.path.join(BASE, "99_보관_구버전")

for _d in (FINAL_DIR, HTML_DIR):
    os.makedirs(_d, exist_ok=True)


def find(name):
    """폴더 구조 전체에서 파일명을 검색해 실제 경로를 반환.
    못 찾으면 최종 폴더 기준 경로를 반환(신규 생성 대비)."""
    hits = glob.glob(os.path.join(BASE, "**", name), recursive=True)
    return hits[0] if hits else os.path.join(FINAL_DIR, name)


def out_final(name):
    """엑셀 결과물 저장 경로(01 폴더)."""
    return os.path.join(FINAL_DIR, name)


def out_html(name):
    """HTML 결과물 저장 경로(02 폴더)."""
    return os.path.join(HTML_DIR, name)
