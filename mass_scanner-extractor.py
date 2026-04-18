import urllib.request
import urllib.error
import ipaddress
import sys
import time
import bisect
import argparse
from datetime import datetime, timezone

# ── 設定區 ────────────────────────────────────────────────────────────────────
URL = "https://raw.githubusercontent.com/stamparm/maltrail/master/trails/static/mass_scanner_cidr.txt"
MAX_COMMENT_LEN = 110
RETRY_COUNT = 3
RETRY_DELAY = 2  # 秒

OUTPUT_V4 = "mass_scanner.rsc"
OUTPUT_V6 = "mass_scanner_v6.rsc"

# ── 本地自訂清單 (請使用「IP # 註解」的單行格式) ─────────────────────────────────
LOCAL_LIST_DATA = """
# https://opendata.rapid7.com/about/

5.63.151.96/27 # opendata.rapid7.com
71.6.233.0/24 # opendata.rapid7.com
88.202.190.128/27 # opendata.rapid7.com
146.185.25.160/27 # opendata.rapid7.com
109.123.117.224/27 # opendata.rapid7.com
69.164.209.193/32 # opendata.rapid7.com
173.255.229.50/32 # opendata.rapid7.com


# https://internet-measurement.com/#ips

87.236.176.0/24 # internet-measurement.com
185.247.137.0/24 # internet-measurement.com
193.163.125.0/24 # internet-measurement.com
45.55.151.3/32 # internet-measurement.com
45.55.153.86/32 # internet-measurement.com
45.55.158.168/32 # internet-measurement.com
45.55.185.224/32 # internet-measurement.com
45.55.186.92/32 # internet-measurement.com
64.227.99.138/32 # internet-measurement.com
64.227.108.146/32 # internet-measurement.com
64.227.109.89/32 # internet-measurement.com
64.227.110.161/32 # internet-measurement.com
107.170.65.169/32 # internet-measurement.com
128.199.8.140/32 # internet-measurement.com
157.245.243.118/32 # internet-measurement.com
157.245.245.246/32 # internet-measurement.com
159.65.216.50/32 # internet-measurement.com
159.65.219.252/32 # internet-measurement.com
162.243.114.171/32 # internet-measurement.com
162.243.116.182/32 # internet-measurement.com
162.243.208.127/32 # internet-measurement.com
167.99.234.119/32 # internet-measurement.com
192.241.179.235/32 # internet-measurement.com

2a06:4880::/30 # internet-measurement.com
2604:a880:0:202a::b41:8000/124 # internet-measurement.com
2604:a880:0:202a::b41:a000/124 # internet-measurement.com
2604:a880:0:202a::b41:b000/124 # internet-measurement.com
2604:a880:0:202a::b42:d000/124 # internet-measurement.com
2604:a880:0:202a::b42:e000/124 # internet-measurement.com
2604:a880:4:1d0::2fa6:a000/124 # internet-measurement.com
2604:a880:4:1d0::2fa6:b000/124 # internet-measurement.com
2604:a880:4:1d0::2fa6:c000/124 # internet-measurement.com
2604:a880:4:1d0::2fa6:d000/124 # internet-measurement.com
2604:a880:4:1d0::2fa6:e000/124 # internet-measurement.com
2604:a880:400:d1::91e4:a000/124 # internet-measurement.com
2604:a880:400:d1::91e4:b000/124 # internet-measurement.com
2604:a880:400:d1::91e4:c000/124 # internet-measurement.com
2604:a880:400:d1::91e4:d000/124 # internet-measurement.com
2604:a880:400:d1::91e4:e000/124 # internet-measurement.com
2604:a880:800:14::5633:8000/124 # internet-measurement.com
2604:a880:800:14::5633:9000/124 # internet-measurement.com
2604:a880:800:14::5633:a000/124 # internet-measurement.com
2604:a880:800:14::5633:b000/124 # internet-measurement.com
2604:a880:800:14::5633:c000/124 # internet-measurement.com

# https://docs.censys.com/docs/opt-out-of-data-collection

66.132.159.0/24 # docs.censys.com
66.132.148.0/24 # docs.censys.com
66.132.153.0/24 # docs.censys.com
66.132.224.0/24 # docs.censys.com
66.132.186.0/24 # docs.censys.com
66.132.195.0/24 # docs.censys.com
66.132.172.0/24 # docs.censys.com
162.142.125.0/24 # docs.censys.com
167.94.138.0/24 # docs.censys.com
167.94.145.0/24 # docs.censys.com
167.94.146.0/24 # docs.censys.com
167.248.133.0/24 # docs.censys.com
199.45.154.0/24 # docs.censys.com
199.45.155.0/24 # docs.censys.com
206.168.34.0/24 # docs.censys.com
206.168.35.0/24 # docs.censys.com
2602:80d:1000:b0cc:e::/80 # docs.censys.com
2620:96:e000:b0cc:e::/80 # docs.censys.com
2602:80d:1003::/112 # docs.censys.com
2602:80d:1004::/112 # docs.censys.com
"""

# ── 1. 下載（含 retry）────────────────────────────────────────────────────────
def fetch_data(url: str, retries: int = RETRY_COUNT) -> str:
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.URLError as e:
            print(f"  ⚠ 第 {attempt} 次失敗：{e}")
            if attempt < retries:
                time.sleep(RETRY_DELAY)
    print("❌ 無法下載資料，已達最大重試次數。")
    sys.exit(1)


# ── 2. 擷取網域名稱 ───────────────────────────────────────────────────────────
def extract_domain(hostname: str) -> str:
    parts = hostname.strip().split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return hostname


# ── 3. 解析清單（支援多資料來源合併解析）──────────────────────────────────────
def parse_lines(data: str) -> tuple[list, list, dict]:
    v4_nets, v6_nets = [], []
    comments: dict = {}

    for raw in data.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        ip_str, _, comment = line.partition("#")
        ip_str = ip_str.strip()
        comment = comment.strip()

        if not ip_str: continue

        try:
            net = ipaddress.ip_network(ip_str, strict=False)
            if net.version == 4:
                v4_nets.append(net)
            else:
                v6_nets.append(net)

            if comment:
                domain = extract_domain(comment)
                comments.setdefault(net, set()).add(domain)
        except ValueError:
            continue

    return v4_nets, v6_nets, comments


# ── 4. 核心優化：二分搜尋對應註解 ─────────────────────────────────────────────
def build_collapsed_comments(collapsed: list, comments: dict, version: int) -> dict:
    if not collapsed or not comments: return {}
    keys = [net.network_address for net in collapsed]
    result: dict = {}

    for orig_net, tags in comments.items():
        if orig_net.version != version: continue
        idx = bisect.bisect_right(keys, orig_net.network_address) - 1

        for i in range(idx, max(idx - 4, -1), -1):
            if i < 0: break
            c_net = collapsed[i]
            try:
                if orig_net.subnet_of(c_net):
                    result.setdefault(c_net, set()).update(tags)
                    break
            except TypeError:
                break
    return result


# ── 5. 截斷工具 ───────────────────────────────────────────────────────────────
def truncate_comment(text: str, max_len: int = MAX_COMMENT_LEN) -> str:
    if len(text) <= max_len: return text
    return text[:max_len].rsplit(",", 1)[0].rstrip() + ", ..."


# ── 6. 輸出 RSC ───────────────────────────────────────────────────────────────
def write_rsc(filename: str, collapsed: list, comments_map: dict, is_v6: bool = False, max_comment: int = MAX_COMMENT_LEN) -> None:
    cmd_path = "/ipv6 firewall address-list" if is_v6 else "/ip firewall address-list"
    list_name = "MALTRAIL-SCANNER-V6" if is_v6 else "MALTRAIL-SCANNER"
    gen_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC+0000")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Maltrail Mass Scanner List\n")
        f.write("# Source: https://github.com/stamparm/maltrail + Local Variable List\n")
        f.write(f"# Generated on: {gen_time}\n\n")
        f.write(f"{cmd_path} remove [find list={list_name}]\n")

        for net in collapsed:
            tags = comments_map.get(net)
            comment = f"Maltrail: {truncate_comment(', '.join(sorted(tags)), max_comment)}" if tags else "Maltrail-Scanner"
            f.write(f'{cmd_path} add address={net} comment="{comment}" list={list_name}\n')


# ── 主程式 ────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        description="將 Maltrail 清單與本地變數整併為 MikroTik .rsc 格式",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--url", default=URL, help="來源清單的 URL")
    parser.add_argument("--output-v4", default=OUTPUT_V4, metavar="FILE", help="IPv4 輸出檔案名稱")
    parser.add_argument("--output-v6", default=OUTPUT_V6, metavar="FILE", help="IPv6 輸出檔案名稱")
    parser.add_argument("--max-comment", type=int, default=MAX_COMMENT_LEN, metavar="N", help="RouterOS comment 最大字元數")
    parser.add_argument("--retries", type=int, default=RETRY_COUNT, metavar="N", help="下載失敗時的最大重試次數")
    args = parser.parse_args()

    print("正在從 Maltrail 下載遠端清單...")
    remote_data = fetch_data(args.url, retries=args.retries)

    print("合併遠端清單與本地變數...")
    # 將下載的資料與你的自訂資料合為一體，中間加一個換行符號避免連在一起
    combined_data = remote_data + "\n" + LOCAL_LIST_DATA

    print("開始解析...")
    v4_nets, v6_nets, comments = parse_lines(combined_data)

    total = len(v4_nets) + len(v6_nets)
    if total == 0:
        print("❌ 錯誤：解析後沒有找到任何有效的 IP。")
        sys.exit(1)
    print(f"成功取得 {total} 筆 IP（IPv4: {len(v4_nets)}，IPv6: {len(v6_nets)}）。")

    print("合併網段中 (collapse)...")
    v4_collapsed = list(ipaddress.collapse_addresses(v4_nets))
    v6_collapsed = list(ipaddress.collapse_addresses(v6_nets))
    print(f"合併後：IPv4 {len(v4_collapsed)} 筆，IPv6 {len(v6_collapsed)} 筆。")

    print("對應註解中...")
    v4_map = build_collapsed_comments(v4_collapsed, comments, 4)
    v6_map = build_collapsed_comments(v6_collapsed, comments, 6)

    print("寫入 RSC 檔案...")
    write_rsc(args.output_v4, v4_collapsed, v4_map, is_v6=False, max_comment=args.max_comment)
    write_rsc(args.output_v6, v6_collapsed, v6_map, is_v6=True,  max_comment=args.max_comment)

    print("✅ 轉換成功！")
    print(f"   {args.output_v4}：{len(v4_collapsed) + 4} 行")
    print(f"   {args.output_v6}：{len(v6_collapsed) + 4} 行")

if __name__ == "__main__":
    main()
