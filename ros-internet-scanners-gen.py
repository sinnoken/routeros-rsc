#!/usr/bin/env python3
"""
generate_rsc.py

將 OpenFilters/internet-scanners repo 中 cidr/*_v4.txt、cidr/*_v6.txt
合併成單一 Mikrotik RouterOS v7 可用的 .rsc 匯入檔（firewall address-list）。

用法:
    # 方式一：自動 clone 上游 repo 再產生 (需要 git + 網路)
    python3 generate_rsc.py --output internet-scanners.rsc

    # 方式二：已經 checkout 過上游 repo，直接指定路徑 (GitHub Actions 建議用這個)
    python3 generate_rsc.py --source-dir upstream/cidr --output internet-scanners.rsc

    # 連 inactive/ 內的舊區段也一併匯入 (預設不含)
    python3 generate_rsc.py --include-inactive --output internet-scanners.rsc
"""

import argparse
import ipaddress
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

UPSTREAM_REPO = "https://github.com/OpenFilters/internet-scanners.git"
DEFAULT_LIST_NAME = "internet-scanners"


def clone_upstream(tmp_dir: Path) -> Path:
    """git clone 上游 repo 到暫存目錄, 回傳 cidr/ 目錄路徑"""
    print(f"[*] Cloning {UPSTREAM_REPO} ...", file=sys.stderr)
    subprocess.run(
        ["git", "clone", "--depth", "1", UPSTREAM_REPO, str(tmp_dir)],
        check=True,
    )
    return tmp_dir / "cidr"


def source_name_from_filename(path: Path) -> str:
    """a10networks_v4.txt -> a10networks"""
    stem = path.stem  # a10networks_v4
    for suffix in ("_v4", "_v6"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def collect_entries(cidr_dir: Path, include_inactive: bool):
    """
    掃描 cidr_dir 底下所有 *_v4.txt / *_v6.txt (以及可選的 inactive/ 子目錄)
    回傳 dict: { "v4": {cidr: source_name, ...}, "v6": {...} }
    (同一個 CIDR 若出現在多個檔案，只保留第一個來源做 comment)
    """
    result = {"v4": {}, "v6": {}}

    dirs_to_scan = [cidr_dir]
    if include_inactive:
        inactive_dir = cidr_dir.parent / "inactive"
        if inactive_dir.is_dir():
            dirs_to_scan.append(inactive_dir)

    for base_dir in dirs_to_scan:
        for pattern, family in (("*_v4.txt", "v4"), ("*_v6.txt", "v6")):
            for f in sorted(base_dir.glob(pattern)):
                source = source_name_from_filename(f)
                text = f.read_text(encoding="utf-8", errors="ignore")
                for line in text.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    try:
                        net = ipaddress.ip_network(line, strict=False)
                    except ValueError:
                        print(f"[!] 略過無法解析的項目: {line} ({f})", file=sys.stderr)
                        continue
                    norm = str(net)
                    fam = "v4" if net.version == 4 else "v6"
                    if norm not in result[fam]:
                        result[fam][norm] = source

    return result


def sort_key(cidr_str: str):
    net = ipaddress.ip_network(cidr_str)
    return (net.version, int(net.network_address), net.prefixlen)


def build_rsc(entries, list_name: str, include_inactive: bool) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    v4_items = sorted(entries["v4"].items(), key=lambda kv: sort_key(kv[0]))
    v6_items = sorted(entries["v6"].items(), key=lambda kv: sort_key(kv[0]))

    lines = []
    lines.append("# ===================================================================")
    lines.append("# Mikrotik RouterOS v7 firewall address-list import file")
    lines.append("# Source : https://github.com/OpenFilters/internet-scanners")
    lines.append(f"# Generated: {now}")
    lines.append(f"# List name : {list_name}")
    lines.append(f"# Entries  : IPv4={len(v4_items)}  IPv6={len(v6_items)}")
    if include_inactive:
        lines.append("# 註: 已包含 inactive/ (歷史/已停用) 區段")
    lines.append("# ===================================================================")
    lines.append("")

    # --- IPv4 ---
    lines.append(":log info \"internet-scanners: start updating address-list\"")
    lines.append("/ip firewall address-list")
    lines.append(f'remove [find list="{list_name}"]')
    for cidr, source in v4_items:
        lines.append(
            f'add address={cidr} list="{list_name}" comment="{source}"'
        )
    lines.append("")

    # --- IPv6 ---
    lines.append("/ipv6 firewall address-list")
    lines.append(f'remove [find list="{list_name}"]')
    for cidr, source in v6_items:
        lines.append(
            f'add address={cidr} list="{list_name}" comment="{source}"'
        )
    lines.append("")
    lines.append(
        f':log info "internet-scanners: address-list updated ({len(v4_items)} IPv4 / {len(v6_items)} IPv6)"'
    )
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=str,
        default=None,
        help="已存在的 internet-scanners repo 內 cidr/ 目錄路徑（若省略則自動 git clone）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="internet-scanners.rsc",
        help="輸出的 .rsc 檔案路徑 (預設: internet-scanners.rsc)",
    )
    parser.add_argument(
        "--list-name",
        type=str,
        default=DEFAULT_LIST_NAME,
        help=f"Mikrotik address-list 名稱 (預設: {DEFAULT_LIST_NAME})",
    )
    parser.add_argument(
        "--include-inactive",
        action="store_true",
        help="連同 inactive/ 目錄內已停用的區段一併匯入",
    )
    args = parser.parse_args()

    tmp_dir = None
    try:
        if args.source_dir:
            cidr_dir = Path(args.source_dir)
            if not cidr_dir.is_dir():
                print(f"[!] 找不到目錄: {cidr_dir}", file=sys.stderr)
                sys.exit(1)
        else:
            tmp_dir = Path(tempfile.mkdtemp(prefix="internet-scanners-"))
            cidr_dir = clone_upstream(tmp_dir)

        entries = collect_entries(cidr_dir, args.include_inactive)
        total = len(entries["v4"]) + len(entries["v6"])
        if total == 0:
            print("[!] 沒有讀到任何 CIDR 項目，請確認來源路徑是否正確", file=sys.stderr)
            sys.exit(1)

        rsc_text = build_rsc(entries, args.list_name, args.include_inactive)
        out_path = Path(args.output)
        out_path.write_text(rsc_text, encoding="utf-8")

        print(
            f"[+] 完成：{out_path} "
            f"(IPv4={len(entries['v4'])}, IPv6={len(entries['v6'])}, 合計={total})"
        )
    finally:
        if tmp_dir and tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
