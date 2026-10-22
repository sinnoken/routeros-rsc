#!/usr/bin/env python3
"""
比對上游來源與產生的 .rsc，確認每個來源網段都被輸出涵蓋。

用法：
    python -I verify_coverage.py --source URL_OR_FILE --rsc rsc/LIST.rsc [--rsc-old OLD.rsc]

來源每行取第一個欄位（支援 IP、CIDR、IP:port、行尾 # 或 ; 註解），
非全域位址（私有、保留、multicast）不列入檢查，因為產生器會刻意排除。
任一來源網段未被涵蓋時結束碼為 1。
"""
import argparse
import ipaddress
import re
import sys
import urllib.request


def load_text(src: str) -> str:
    if src.startswith(("http://", "https://")):
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
        return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    with open(src, encoding="utf-8", errors="ignore") as f:
        return f.read()


def parse_source(text: str) -> list:
    nets = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";", "/")):
            continue
        token = re.split(r"[\s;#]", line, maxsplit=1)[0]
        if token.startswith("[") and "]" in token:
            token = token[1:token.index("]")]
        elif token.count(".") == 3 and ":" in token:
            token = token.split(":")[0]
        try:
            net = ipaddress.ip_network(token, strict=False)
        except ValueError:
            continue
        if net.network_address.is_global:
            nets.append(net)
    return nets


def parse_rsc(path: str) -> list:
    text = open(path, encoding="utf-8").read()
    return [ipaddress.ip_network(a, strict=False) for a in re.findall(r"\badd address=(\S+)", text)]


def covered(src: list, out: list) -> list:
    """回傳未被輸出涵蓋的來源網段"""
    by_ver = {4: list(ipaddress.collapse_addresses(n for n in out if n.version == 4)),
              6: list(ipaddress.collapse_addresses(n for n in out if n.version == 6))}
    return [n for n in src if not any(n.subnet_of(o) for o in by_ver[n.version])]


def space(nets: list) -> int:
    total = 0
    for ver in (4, 6):
        total += sum(n.num_addresses for n in ipaddress.collapse_addresses(n for n in nets if n.version == ver))
    return total


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", required=True, help="上游清單 URL 或本機檔案")
    ap.add_argument("--rsc", required=True, help="新產生的 .rsc")
    ap.add_argument("--rsc-old", help="舊版 .rsc（選用，比較修改前後）")
    args = ap.parse_args()

    src = parse_source(load_text(args.source))
    new = parse_rsc(args.rsc)
    missing = covered(src, new)
    print(f"來源網段（全域位址）: {len(src)}")
    print(f"新檔 entries: {len(new)}  涵蓋位址數: {space(new):,}  未涵蓋來源網段: {len(missing)}")
    for n in missing[:20]:
        print(f"  MISSING {n}")
    if args.rsc_old:
        old = parse_rsc(args.rsc_old)
        print(f"舊檔 entries: {len(old)}  涵蓋位址數: {space(old):,}  未涵蓋來源網段: {len(covered(src, old))}")
    # 輸出比來源大很多代表聚合或解析可能誤擴大範圍
    if src and space(new) > space(src) * 1.01:
        print("WARN 輸出涵蓋的位址數大於來源，請檢查是否擴大了封鎖範圍")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
