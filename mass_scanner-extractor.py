import urllib.request
import urllib.error
import ipaddress
import sys
import time
import bisect
import argparse
from datetime import datetime, timezone

# ── 設定區 ────────────────────────────────────────────────────────────────────
URL = "https://raw.githubusercontent.com/stamparm/maltrail/master/trails/static/mass_scanner.txt"
MAX_COMMENT_LEN = 110
RETRY_COUNT = 3
RETRY_DELAY = 2  # 秒

OUTPUT_V4 = "mass_scanner.rsc"
OUTPUT_V6 = "mass_scanner_v6.rsc"


# ── 1. 下載（含 retry）────────────────────────────────────────────────────────
def fetch_data(url: str, retries: int = RETRY_COUNT) -> str:
    """下載文字資料，失敗時自動重試。"""
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


# ── 2. 解析（一次迴圈，回傳分版本的結構）────────────────────────────────────
def parse_lines(data: str) -> tuple[
    list[ipaddress.IPv4Network],
    list[ipaddress.IPv6Network],
    dict,
]:
    v4_nets, v6_nets = [], []
    comments: dict[ipaddress.IPv4Network | ipaddress.IPv6Network, set[str]] = {}

    for raw in data.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        ip_str, _, comment = line.partition("#")
        ip_str = ip_str.strip()
        comment = comment.strip()

        if not ip_str:
            continue

        try:
            net = ipaddress.ip_network(ip_str, strict=False)
        except ValueError:
            continue

        if net.version == 4:
            v4_nets.append(net)
        else:
            v6_nets.append(net)

        if comment:
            comments.setdefault(net, set()).add(comment)

    return v4_nets, v6_nets, comments


# ── 3. 核心優化：O(log N) 二分搜尋取代 O(M×N) 線性掃描 ────────────────────
def build_collapsed_comments(
    collapsed: list,
    comments: dict,
    version: int,
) -> dict:
    if not collapsed or not comments:
        return {}

    keys = [net.network_address for net in collapsed]
    result: dict = {}

    for orig_net, tags in comments.items():
        if orig_net.version != version:
            continue

        idx = bisect.bisect_right(keys, orig_net.network_address) - 1

        for i in range(idx, max(idx - 4, -1), -1):
            if i < 0:
                break
            c_net = collapsed[i]
            try:
                if orig_net.subnet_of(c_net):
                    result.setdefault(c_net, set()).update(tags)
                    break
            except TypeError:
                break

    return result


# ── 4. 截斷工具（在 token 邊界截斷）────────────────────────────────────────
def truncate_comment(text: str, max_len: int = MAX_COMMENT_LEN) -> str:
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rsplit(",", 1)[0]
    return cut.rstrip() + ", ..."


# ── 5. 輸出 RSC ───────────────────────────────────────────────────────────────
def write_rsc(
    filename: str,
    collapsed: list,
    comments_map: dict,
    is_v6: bool = False,
) -> None:
    cmd_path = "/ipv6 firewall address-list" if is_v6 else "/ip firewall address-list"
    list_name = "MALTRAIL-SCANNER-V6" if is_v6 else "MALTRAIL-SCANNER"
    gen_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC+0000")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# Maltrail Mass Scanner List\n")
        f.write("# Source: https://github.com/stamparm/maltrail\n")
        f.write(f"# Generated on: {gen_time}\n\n")
        f.write(f"{cmd_path} remove [find list={list_name}]\n")

        for net in collapsed:
            tags = comments_map.get(net)
            if tags:
                merged = ", ".join(sorted(tags))
                comment = f"Maltrail: {truncate_comment(merged)}"
            else:
                comment = "Maltrail-Scanner"

            f.write(
                f'{cmd_path} add address={net} comment="{comment}" list={list_name}\n'
            )


# ── 主程式 ────────────────────────────────────────────────────────────────────
def main() -> None:
    # ── CLI 參數 ──────────────────────────────────────────────────────────────
    parser = argparse.ArgumentParser(
        description="將 Maltrail mass_scanner 清單轉換為 MikroTik RouterOS .rsc 格式",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,  # 顯示預設值
    )
    parser.add_argument(
        "--url",
        default=URL,
        help="來源清單的 URL",
    )
    parser.add_argument(
        "--output-v4",
        default=OUTPUT_V4,
        metavar="FILE",
        help="IPv4 輸出檔案名稱",
    )
    parser.add_argument(
        "--output-v6",
        default=OUTPUT_V6,
        metavar="FILE",
        help="IPv6 輸出檔案名稱",
    )
    parser.add_argument(
        "--max-comment",
        type=int,
        default=MAX_COMMENT_LEN,
        metavar="N",
        help="RouterOS comment 最大字元數",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=RETRY_COUNT,
        metavar="N",
        help="下載失敗時的最大重試次數",
    )
    args = parser.parse_args()

    # 將 CLI 參數套用到全域常數（只影響本次執行）
    global MAX_COMMENT_LEN
    MAX_COMMENT_LEN = args.max_comment

    # ── 以下邏輯完全不變 ──────────────────────────────────────────────────────
    print("正在從 Maltrail 下載清單...")
    data = fetch_data(args.url, retries=args.retries)

    print("解析中...")
    v4_nets, v6_nets, comments = parse_lines(data)

    total = len(v4_nets) + len(v6_nets)
    if total == 0:
        print("❌ 錯誤：解析後沒有找到任何有效的 IP。")
        sys.exit(1)
    print(f"成功取得 {total} 筆 IP（IPv4: {len(v4_nets)}，IPv6: {len(v6_nets)}）。")

    print("合併網段中...")
    v4_collapsed = list(ipaddress.collapse_addresses(v4_nets))
    v6_collapsed = list(ipaddress.collapse_addresses(v6_nets))
    print(f"合併後：IPv4 {len(v4_collapsed)} 筆，IPv6 {len(v6_collapsed)} 筆。")

    print("對應註解中...")
    v4_map = build_collapsed_comments(v4_collapsed, comments, 4)
    v6_map = build_collapsed_comments(v6_collapsed, comments, 6)

    print("寫入 RSC 檔案...")
    write_rsc(args.output_v4, v4_collapsed, v4_map, is_v6=False)
    write_rsc(args.output_v6, v6_collapsed, v6_map, is_v6=True)

    print("✅ 轉換成功！")
    print(f"   {args.output_v4}：{len(v4_collapsed) + 4} 行")
    print(f"   {args.output_v6}：{len(v6_collapsed) + 4} 行")


if __name__ == "__main__":
    main()
