#!/usr/bin/env python3
"""
依 references/sources.json 檢查各上游來源是否有變動。

檢查項目：
  - GitHub repo 的 LICENSE 檔 SHA 與 SPDX 是否和基準相同（不同代表授權文字被修改）
  - feed 網址是否仍可下載（404 常代表搬家，搬家常伴隨改授權）
  - feed 檔頭是否仍包含應保留的版權聲明（header_patterns）

用法：
    python -I check_upstream.py [--sources references/sources.json] [--only ID ...]

只回報變動，不修改基準；人工確認後請手動更新 sources.json。
有變動或錯誤時結束碼為 1。未帶 GITHUB_TOKEN 時 GitHub API 每小時限 60 次。
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = {"User-Agent": "routeros-rsc-license-audit"}


def get(url: str, api: bool = False):
    headers = dict(UA)
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if os.getenv("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read()


def check_github(gh: dict) -> list:
    issues = []
    repo, path = gh["repo"], gh["license_path"]
    try:
        _, body = get(f"https://api.github.com/repos/{repo}/contents/{path}", api=True)
        sha = json.loads(body).get("sha")
        if sha != gh["license_sha"]:
            issues.append(f"{repo}/{path} 已變更：SHA {gh['license_sha'][:8]} -> {str(sha)[:8]}，請閱讀新授權")
    except urllib.error.HTTPError as e:
        issues.append(f"{repo}/{path} 無法讀取（HTTP {e.code}），repo 或授權檔可能已搬移")
    try:
        _, body = get(f"https://api.github.com/repos/{repo}/license", api=True)
        spdx = (json.loads(body).get("license") or {}).get("spdx_id")
        if spdx != gh["spdx"]:
            issues.append(f"{repo} SPDX 變更：{gh['spdx']} -> {spdx}")
    except urllib.error.HTTPError as e:
        issues.append(f"{repo} 授權 API 錯誤（HTTP {e.code}）")
    return issues


def check_feed(url: str, patterns: list) -> list:
    try:
        _, body = get(url)
    except urllib.error.HTTPError as e:
        return [f"{url} 無法下載（HTTP {e.code}），來源可能已搬移"]
    except urllib.error.URLError as e:
        return [f"{url} 連線失敗：{e.reason}"]
    head = "\n".join(body.decode("utf-8", "ignore").splitlines()[:60])
    return [f"{url} 檔頭找不到應保留的聲明：/{p}/" for p in patterns if not re.search(p, head)]


def main() -> int:
    here = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sources", default=str(here / "references" / "sources.json"))
    ap.add_argument("--only", nargs="*", help="只檢查指定 id")
    args = ap.parse_args()

    data = json.loads(Path(args.sources).read_text(encoding="utf-8"))
    total = 0
    for s in data["sources"]:
        if args.only and s["id"] not in args.only:
            continue
        issues = []
        if "github" in s:
            issues += check_github(s["github"])
        for url in s.get("feeds", []):
            issues += check_feed(url, s.get("header_patterns", []))
        status = "OK " if not issues else "CHG"
        print(f"[{status}] {s['id']:18} {s['redistribution']:22} last_verified={s['last_verified']}")
        for i in issues:
            print(f"        - {i}")
        for page in s.get("terms_pages", []):
            print(f"        ? 條款頁需人工確認：{page}")
        total += len(issues)
    print(f"\n{total} 項變動或錯誤")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
