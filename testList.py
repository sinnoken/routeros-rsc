import os
import requests
import ipaddress
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# 確保目錄存在
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
        "comment": "Level 2 threat list",
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
        "type": "IPv4"
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v6_JP",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v6_JP.txt",
        "comment": "Japan IPv6 blocklist",
        "type": "IPv6"
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v4_KR",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v4_KR.txt",
        "comment": "South Korea IPv4 blocklist",
        "type": "IPv4"
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v6_KR",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v6_KR.txt",
        "comment": "South Korea IPv6 blocklist",
        "type": "IPv6"
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v4_CN",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v4_CN.txt",
        "comment": "China IPv4 blocklist",
        "type": "IPv4"
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v6_CN",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v6_CN.txt",
        "comment": "China IPv6 blocklist",
        "type": "IPv6"
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v4_TW",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v4_TW.txt",
        "comment": "Taiwan IPv4 blocklist",
        "type": "IPv4"
    },
    {
        "list_name": "ipv64.net-ipv64_blocklist_v6_TW",
        "source_url": "https://ipv64.net/blocklists/countries/ipv64_blocklist_v6_TW.txt",
        "comment": "Taiwan IPv6 blocklist",
        "type": "IPv6"
    }
]

def process_url(session, url_info):
    """下載資料並處理 IP 地址"""
    url = url_info['source_url']
    comment = url_info['comment']
    list_name = url_info['list_name'].replace('/', '-').upper()
    ip_type = url_info['type']

    # 確保輸出目錄存在
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{list_name}.rsc')

    try:
        response = session.get(url)
        response.raise_for_status()  # 檢查 HTTP 回應狀態碼是否為錯誤
    except requests.exceptions.RequestException as e:
        print(f"警告: 無法下載 {url}，錯誤: {e}")
        return

    ip_list = response.text.splitlines()

    # 檢查 ip_list 行數
    line_count = len(ip_list)
    print(f"從 {url} 下載到 {line_count} 行資料。")

    if line_count == 0:
        print(f"警告: {url} 沒有下載到任何資料。")
        return

    # 使用集合來去重和驗證 IP 地址和 CIDR
    valid_entries = set()
    for line in ip_list:
        if line and not line.startswith('#'):
            try:
                # 嘗試解析為單個 IP 地址
                ip = ipaddress.ip_address(line.split()[0])
                valid_entries.add(ip)
            except ValueError:
                try:
                    # 如果不是單個 IP，嘗試解析為網路地址
                    network = ipaddress.ip_network(line.split()[0], strict=False)
                    valid_entries.add(network)
                except ValueError:
                    continue

    # 排序：先按 IP 類型（IPv4, IPv6），再按數值
    sorted_entries = sorted(valid_entries, key=lambda x: (x.version, int(x.network_address) if isinstance(x, ipaddress._BaseNetwork) else int(x)))

    # 生成 RouterOS 指令
    commands = []
    for entry in sorted_entries:
        if isinstance(entry, ipaddress.IPv4Address) and ip_type == "IPv4":
            commands.append(f'/ip firewall address-list add address={str(entry).ljust(15)} comment={comment} list={list_name}\n')
        elif isinstance(entry, ipaddress.IPv6Address) and ip_type == "IPv6":
            commands.append(f'/ipv6 firewall address-list add address={str(entry).ljust(39)} comment={comment} list={list_name}\n')
        elif isinstance(entry, ipaddress.IPv4Network) and ip_type == "IPv4":
            commands.append(f'/ip firewall address-list add address={str(entry).ljust(18)} comment={comment} list={list_name}\n')
        elif isinstance(entry, ipaddress.IPv6Network) and ip_type == "IPv6":
            commands.append(f'/ipv6 firewall address-list add address={str(entry).ljust(43)} comment={comment} list={list_name}\n')

    # 批量寫入文件
    with open(output_file, 'w') as f:
        f.write(f"# {comment}\n")
        f.write(f"# Source: {url_info['source_url']}\n")
        f.write(f"# Converted for RouterOS by sinnoken/routeros-rsc\n")
        f.write(f"# WARNING: This file is auto-generated. Manual edits may be overwritten.\n")
        f.write(f"# Generated on: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')}\n\n")
        f.writelines(commands)

    print(f'已儲存 {output_file}')

def main():
    """主函數，使用多線程加速處理"""
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(lambda url_info: process_url(session, url_info), urls_info)

if __name__ == '__main__':
    main()
