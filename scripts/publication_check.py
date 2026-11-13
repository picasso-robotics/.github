#!/usr/bin/env python3
"""공개 저장소에 올리면 안 되는 내용을 찾는다(CONTRIBUTING.md «공개 전 검사»).

사용:
  python3 publication_check.py FILE [FILE ...]   # 파일마다 검사
  python3 publication_check.py -                 # 표준 입력 검사

찾으면 `파일:줄: 규칙 — 일치한 조각(가림)` 을 출력하고 종료 코드 1, 없으면 0.

org 고유의 금지어(고객·현장 이름, 내부 호스트 등)는 이 공개 파일에 적지 않는다 — 목록 자체가 유출이다.
환경 변수 `PUBLICATION_DENYLIST` 에 한 줄에 정규식 하나로 넣는다(org 비밀로 관리).
"""
import os
import re
import sys

# (규칙 이름, 정규식). 위에서부터 검사한다.
RULES = [
    ("비밀: GitHub 토큰", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{40,}")),
    ("비밀: AWS 접근 키", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("비밀: 개인 키", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("비밀: Slack 토큰", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("비밀: API 키(sk-)", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}")),
    ("비밀: Google API 키", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("비밀: 값이 든 대입", re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*['\"]?(?![<${])[^\s'\"<>]{8,}")),
    ("로컬 경로: Windows 사용자 폴더", re.compile(r"\b[A-Za-z]:[\\/]+Users[\\/]+(?!<)[^\\/\s]+")),
    ("로컬 경로: 홈 폴더", re.compile(r"(?<![\w.])/(?:home|Users)/(?!<)[A-Za-z0-9._-]+")),
    ("로컬 경로: 앱 데이터·임시 폴더", re.compile(r"(?i)\bAppData[\\/]+(?:Local|Roaming)\b|[\\/]Temp[\\/]+claude\b")),
    ("도구 흔적: AI 세션 ID", re.compile(r"\blocal_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-")),
    ("네트워크: 사설 IP", re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b")),
    ("네트워크: 내부 호스트", re.compile(r"\b[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(?:internal|corp|lan)\b")),
]

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
# 공개해도 되는 주소: GitHub noreply, AI 공동 작성 표시, 문서용 예시 도메인.
EMAIL_OK = re.compile(r"(?i)(?:@users\.noreply\.github\.com|^noreply@github\.com|^noreply@anthropic\.com|@example\.(?:com|org|net))$")


def org_rules():
    raw = os.environ.get("PUBLICATION_DENYLIST", "")
    rules = []
    for n, line in enumerate(raw.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            rules.append((f"org 금지어 {n}", re.compile(line)))
        except re.error as e:
            sys.exit(f"PUBLICATION_DENYLIST {n}번 줄의 정규식이 틀렸다: {e}")
    return rules


def mask(text):
    # 출력이 다시 유출이 되지 않게 앞 네 글자만 보인다.
    return text[:4] + "…" if len(text) > 4 else "…"


def scan(name, text, extra):
    found = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for rule, rx in RULES + extra:
            for m in rx.finditer(line):
                found.append(f"{name}:{lineno}: {rule} — {mask(m.group(0))}")
        for m in EMAIL.finditer(line):
            if not EMAIL_OK.search(m.group(0)):
                found.append(f"{name}:{lineno}: 개인정보: 메일 주소 — {mask(m.group(0))}")
    return found


def main(argv):
    if not argv:
        sys.exit(__doc__)
    # Windows 콘솔의 기본 코드페이지에서도 한국어 출력이 죽지 않게 한다.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    extra = org_rules()
    found = []
    for arg in argv:
        if arg == "-":
            found += scan("<stdin>", sys.stdin.read(), extra)
        else:
            with open(arg, encoding="utf-8", errors="replace") as f:
                found += scan(arg, f.read(), extra)
    for line in found:
        print(line)
    if found:
        print(f"\n공개 전 검사: {len(found)}건. 지우거나 자리표시(<이름>, example.com)로 바꾼 뒤 다시 올린다.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
