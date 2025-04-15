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
        "list_name": "stamparm/ipsum-1",
        "source_url": "https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/1.txt",
        "comment": "Level 1 threat list",
        "type": "IPv4"  # Not specifically IPv4 or IPv6
    },
    {
        "list_name": "stamparm/ipsum-2",
        "source_url": "https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/2.txt",
        "comment": "Level 2 threat list",
        "type": "IPv4"
    },
    # ... (其他 levels 同樣結構)
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

    response = session.get(url)
    ip_list = response.text.splitlines()

    # 使用集合來去重和驗證 IP 地址
    valid_ips = set()
    for line in ip_list:
        if line and not line.startswith('#'):
            try:
                ip = ipaddress.ip_address(line.split()[0])
                valid_ips.add(ip)
            except ValueError:
                continue

    sorted_ips = sorted(valid_ips)

    # 生成 RouterOS 指令
    if ip_type == "IPv4":
        commands = [
            f'/ip firewall address-list add address={str(ip).ljust(15)} comment={comment} list={list_name}\n'
            for ip in sorted_ips if isinstance(ip, ipaddress.IPv4Address)
        ]
    elif ip_type == "IPv6":
        commands = [
            f'/ipv6 firewall address-list add address={str(ip).ljust(39)} comment={comment} list={list_name}\n'
            for ip in sorted_ips if isinstance(ip, ipaddress.IPv6Address)
        ]
    else:
        commands = []

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
            executor.map(lambda url: process_url(session, url_info), urls_info)

if __name__ == '__main__':
    main()
