import os
import requests
import ipaddress
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

output_dir = './rsc/'
os.makedirs(output_dir, exist_ok=True)

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
    },
    {
        "list_name": "HN-BLACKLIST-SPAMHAUS",
        "source_url": "https://www.spamhaus.org/drop/drop.txt",
        "comment": "SPAMHAUS-DROP",
        "type": "IPv4"
    },
    {
        "list_name": "spamhaus-edrop",
        "source_url": "https://www.spamhaus.org/drop/edrop.txt",
        "comment": "SPAMHAUS-DROP",
        "type": "IPv4"
    },
    {
        "list_name": "spamhaus-dropv6",
        "source_url": "https://www.spamhaus.org/drop/dropv6.txt",
        "comment": "SPAMHAUS-DROP",
        "type": "IPv6"
    }
]

DEFAULT_MAX_PREFIX_V4 = 20
DEFAULT_MAX_PREFIX_V6 = 48


def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3, backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def collapse_entries(valid_entries: set, max_prefix: int) -> list:
    networks = set()
    for entry in valid_entries:
        if isinstance(entry, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            networks.add(ipaddress.ip_network(entry))
        else:
            networks.add(entry)
    collapsed = ipaddress.collapse_addresses(networks)
    return [net for net in collapsed if net.prefixlen >= max_prefix]


def write_rsc(
    output_file: str, comment: str, url: str,
    before: int, after: int, saved: int, ratio: float,
    max_prefix: int, prefix_cmd: str,
    collapsed: list, list_name: str
) -> None:
    """將整併結果寫入 RSC 檔案"""
    now_str = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# {comment}\n")
        f.write(f"# Source: {url}\n")
        f.write("# Converted for RouterOS by sinnoken/routeros-rsc\n")
        f.write("# WARNING: Auto-generated. Do not edit manually.\n")
        f.write(f"# Generated : {now_str}\n")
        f.write(
            f"# Entries   : {before} raw -> {after} after CIDR aggregation"
            f" (saved {saved}, {ratio:.1f}%, max_prefix=/{max_prefix})\n\n"
        )
        for net in collapsed:
            f.write(
                f"{prefix_cmd} add address={net}"
                f' comment="{comment}" list={list_name}\n'
            )


def process_url(url_info: dict) -> None:
    url       = url_info['source_url']
    comment   = url_info['comment']
    list_name = url_info['list_name'].replace('/', '-').upper()

    try:
        session  = create_session()
        response = session.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[WARN] 無法下載 {url}: {e}")
        return

    ip_list = response.text.splitlines()
    print(f"[INFO] [{list_name}] 下載到 {len(ip_list)} 行")

    # ── 解析：不預設版本，直接分組 ──────────────────────────────
    v4_entries: set = set()
    v6_entries: set = set()

    for raw_line in ip_list:
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        ip_str = line.split()[0]

        # 嘗試單一 IP
        try:
            ip = ipaddress.ip_address(ip_str)
            (v4_entries if ip.version == 4 else v6_entries).add(ip)
            continue
        except ValueError:
            pass

        # 嘗試 CIDR 網段
        try:
            net = ipaddress.ip_network(ip_str, strict=False)
            (v4_entries if net.version == 4 else v6_entries).add(net)
        except ValueError:
            pass

    if not v4_entries and not v6_entries:
        print(f"[WARN] [{list_name}] 沒有有效 IP，跳過輸出")
        return

    # ── 依版本分別輸出 RSC ──────────────────────────────────────
    groups = []
    if v4_entries:
        groups.append((v4_entries, 4, "IPv4",
                       '/ip firewall address-list',
                       url_info.get('max_prefix', DEFAULT_MAX_PREFIX_V4)))
    if v6_entries:
        groups.append((v6_entries, 6, "IPv6",
                       '/ipv6 firewall address-list',
                       url_info.get('max_prefix', DEFAULT_MAX_PREFIX_V6)))

    for entries, ver, ver_label, prefix_cmd, max_prefix in groups:
        # 混合清單時檔名加版本後綴，純單版本則沿用原名
        suffix      = f"_v{ver}" if len(groups) > 1 else ""
        output_file = os.path.join(output_dir, f"{list_name}{suffix}.rsc")
        lname_out   = f"{list_name}{suffix}"

        before    = len(entries)
        collapsed = collapse_entries(entries, max_prefix)
        after     = len(collapsed)
        saved     = before - after
        ratio     = (saved / before * 100) if before > 0 else 0.0

        print(
            f"[INFO] [{lname_out}] ({ver_label}) CIDR 整併: "
            f"{before} -> {after} 條（節省 {saved} 條，{ratio:.1f}%）"
        )

        write_rsc(
            output_file, comment, url,
            before, after, saved, ratio,
            max_prefix, prefix_cmd, collapsed, lname_out
        )
        print(f"[OK]   [{lname_out}] 已儲存 {output_file}（{after} 筆）")


def main() -> None:
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
