import os
import requests
import ipaddress
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 確保輸出目錄存在
output_dir = './rsc/'
os.makedirs(output_dir, exist_ok=True)

# 設定下載的 URL 清單
urls_info = [
    {
        "list_name": "stamparm/ipsum/level-1",
        "source_url": "https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/1.txt",
        "comment": "stamparm/ipsum/level-1",
        "type": "IPv4"
    },
    {
        "list_name": "stamparm/ipsum/level-2",
        "source_url": "https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/2.txt",
        "comment": "stamparm/ipsum/level-2",
        "type": "IPv4"
    },
    {
        "list_name": "stamparm/ipsum/level-3",
        "source_url": "https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/3.txt",
        "comment": "stamparm/ipsum/level-3",
        "type": "IPv4"
    },
    {
        "list_name": "stamparm/ipsum/level-4",
        "source_url": "https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/4.txt",
        "comment": "stamparm/ipsum/level-4",
        "type": "IPv4"
    },
    {
        "list_name": "stamparm/ipsum/level-5",
        "source_url": "https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/5.txt",
        "comment": "stamparm/ipsum/level-5",
        "type": "IPv4"
    },
    {
        "list_name": "stamparm/ipsum/level-6",
        "source_url": "https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/6.txt",
        "comment": "stamparm/ipsum/level-6",
        "type": "IPv4"
    },
    {
        "list_name": "stamparm/ipsum/level-7",
        "source_url": "https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/7.txt",
        "comment": "stamparm/ipsum/level-7",
        "type": "IPv4"
    },
    {
        "list_name": "stamparm/ipsum/level-8",
        "source_url": "https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/8.txt",
        "comment": "stamparm/ipsum/level-8",
        "type": "IPv4"
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v4_JP",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v4_JP.txt",
        "comment": "Japan IPv4 blocklist",
        "type": "IPv4",
        "max_prefix": 16
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v6_JP",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v6_JP.txt",
        "comment": "Japan IPv6 blocklist",
        "type": "IPv6",
        "max_prefix": 32
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v4_KR",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v4_KR.txt",
        "comment": "South Korea IPv4 blocklist",
        "type": "IPv4",
        "max_prefix": 16
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v6_KR",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v6_KR.txt",
        "comment": "South Korea IPv6 blocklist",
        "type": "IPv6",
        "max_prefix": 32
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v4_CN",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v4_CN.txt",
        "comment": "China IPv4 blocklist",
        "type": "IPv4",
        "max_prefix": 16
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v6_CN",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v6_CN.txt",
        "comment": "China IPv6 blocklist",
        "type": "IPv6",
        "max_prefix": 32
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v4_TW",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v4_TW.txt",
        "comment": "Taiwan IPv4 blocklist",
        "type": "IPv4",
        "max_prefix": 16
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v6_TW",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v6_TW.txt",
        "comment": "Taiwan IPv6 blocklist",
        "type": "IPv6",
        "max_prefix": 32
    },
    {
        "list_name": "ipv64.net-TorExitNodes",
        "source_url": "https://ipv64.net/blocklists/ipv64_blocklist_v4_tor_exit.txt",
        "comment": "ipv64.net-TorExitNodes",
        "type": "IPv4"
    },
    {
        "list_name": "emergingthreats-Block-IPs",
        "source_url": "https://rules.emergingthreats.net/fwrules/emerging-Block-IPs.txt",
        "comment": "Emerging Threats FW Block IPs",
        "type": "IPv4",
        "max_prefix": 8
    }
]

# 預設最大前綴長度（前綴越短 = 網段越大）
# 一般黑名單 /20 = 最多封 4096 個 IP
# 國家封鎖清單 /16 = 最多封 65536 個 IP
DEFAULT_MAX_PREFIX_V4 = 20
DEFAULT_MAX_PREFIX_V6 = 48


def create_session() -> requests.Session:
    """建立帶有 Retry 機制的獨立 Session（每條執行緒各自建立）"""
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def collapse_entries(valid_entries: set, max_prefix: int) -> list:
    """
    將 IP / CIDR 統一整併，並過濾掉前綴長度小於 max_prefix 的超大網段。

    Args:
        valid_entries : 包含 ip_address / ip_network 物件的集合
        max_prefix    : 允許的最小前綴長度（越小 = 網段越大）
                        e.g. IPv4 /20 = 4096 IPs，/16 = 65536 IPs

    Returns:
        整併後且通過前綴過濾的 network 物件清單（已排序）
    """
    networks = set()
    for entry in valid_entries:
        if isinstance(entry, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            # 單一 IP 轉成 /32 或 /128
            networks.add(ipaddress.ip_network(entry))
        else:
            networks.add(entry)

    collapsed = ipaddress.collapse_addresses(networks)

    # 過濾掉超大網段，避免誤封整個 ISP
    return [net for net in collapsed if net.prefixlen >= max_prefix]


def process_url(url_info: dict) -> None:
    """下載、解析、整併並輸出單一來源的 RSC 檔案"""
    url         = url_info['source_url']
    comment     = url_info['comment']
    list_name   = url_info['list_name'].replace('/', '-').upper()
    ip_type     = url_info['type']
    output_file = os.path.join(output_dir, f'{list_name}.rsc')

    # 依 IP 版本決定預設最大前綴長度
    default_prefix = DEFAULT_MAX_PREFIX_V4 if ip_type == "IPv4" else DEFAULT_MAX_PREFIX_V6
    max_prefix = url_info.get('max_prefix', default_prefix)

    # 每條執行緒獨立 Session（避免共用 Session 的執行緒安全問題）
    try:
        session  = create_session()
        response = session.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[WARN] 無法下載 {url}: {e}")
        return

    ip_list = response.text.splitlines()
    print(f"[INFO] [{list_name}] 下載到 {len(ip_list)} 行")

    # 解析階段同時過濾 ip_type，避免浪費後續排序資源
    valid_entries = set()
    for raw_line in ip_list:
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if not parts:
            continue
        ip_str = parts[0]

        # 嘗試解析為單一 IP
        try:
            ip = ipaddress.ip_address(ip_str)
            if (ip_type == "IPv4" and ip.version == 4) or \
               (ip_type == "IPv6" and ip.version == 6):
                valid_entries.add(ip)
            continue
        except ValueError:
            pass

        # 嘗試解析為網段 CIDR
        try:
            net = ipaddress.ip_network(ip_str, strict=False)
            if (ip_type == "IPv4" and net.version == 4) or \
               (ip_type == "IPv6" and net.version == 6):
                valid_entries.add(net)
        except ValueError:
            pass  # 非合法 IP / CIDR，跳過

    if not valid_entries:
        print(f"[WARN] [{list_name}] 沒有有效 IP，跳過輸出")
        return

    # CIDR 整併
    before    = len(valid_entries)
    collapsed = collapse_entries(valid_entries, max_prefix)
    after     = len(collapsed)
    saved     = before - after
    ratio     = (saved / before * 100) if before > 0 else 0.0
    print(f"[INFO] [{list_name}] CIDR 整併: {before} -> {after} 條（節省 {saved} 條，{ratio:.1f}%）")

    # 生成 RouterOS 指令
    prefix_cmd = '/ip firewall address-list' if ip_type == "IPv4" \
                 else '/ipv6 firewall address-list'

    now_str = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# " + comment + "\n")
        f.write("# Source: " + url + "\n")
        f.write("# Converted for RouterOS by sinnoken/routeros-rsc\n")
        f.write("# WARNING: Auto-generated. Do not edit manually.\n")
        f.write("# Generated : " + now_str + "\n")
        f.write(
            "# Entries   : " + str(before) + " raw -> " + str(after) +
            " after CIDR aggregation (saved " + str(saved) +
            ", " + f"{ratio:.1f}" + "%, max_prefix=/" + str(max_prefix) + ")\n\n"
        )
        for net in collapsed:
            f.write(
                prefix_cmd + ' add address=' + str(net) +
                ' comment="' + comment + '" list=' + list_name + "\n"
            )

    print(f"[OK]   [{list_name}] 已儲存 {output_file}（{after} 筆）")


def main() -> None:
    """主函數：動態調整 worker 數，使用 as_completed 取得錯誤回報"""
    max_workers = min(len(urls_info), (os.cpu_count() or 1) * 4)
    print(f"[INFO] 啟動 {max_workers} 個 worker 處理 {len(urls_info)} 個來源...\n")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_url, u): u['list_name'] for u in urls_info}
        for future in as_completed(futures):
            name = futures[future]
            exc  = future.exception()
            if exc:
                print(f"[ERROR] [{name}] 執行時發生未預期錯誤: {exc}")

    print("\n[DONE] 全部完成！")


if __name__ == '__main__':
    main()
