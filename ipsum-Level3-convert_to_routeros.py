import os
import requests
import ipaddress
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# 確保目錄存在
output_dir = './rsc/'
os.makedirs(output_dir, exist_ok=True)

# 設定下載的 URL 清單
urls = [
    'https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/1.txt',
    'https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/2.txt',
    'https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/3.txt',
    'https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/4.txt',
    'https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/5.txt',
    'https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/6.txt',
    'https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/7.txt',
    'https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/8.txt'
]

# RouterOS 設定
comment = 'IPsum-Threat-Intelligence-Feed'

def process_url(session, url):
    """下載資料並處理 IP 地址"""
    level = url.split('/')[-1].split('.')[0].replace('level', '')
    list_name = f'HN-BLACKLIST-IPSUM-L{level}'
    output_file = os.path.join(output_dir, f'ipsum-Level{level}.rsc')

    response = session.get(url)
    ip_list = response.text.splitlines()

    # 使用集合來去重和驗證 IP 地址
    valid_ips = {ipaddress.ip_address(line.split()[0]) for line in ip_list if line and not line.startswith('#')}
    sorted_ips = sorted(valid_ips)

    # 生成 RouterOS 指令
    commands = [
        f'/ip firewall address-list add address={str(ip).ljust(15)} comment={comment} list={list_name}\n'
        for ip in sorted_ips
    ]

    # 批量寫入文件
    with open(output_file, 'w') as f:
        f.write(f"# IPsum Threat Intelligence Feed - Level {level}\n")
        f.write(f"# Source: https://github.com/stamparm/ipsum\n")
        f.write(f"# Converted for RouterOS by sinnoken/routeros-rsc\n")
        f.write(f"# WARNING: This file is auto-generated. Manual edits may be overwritten.\n")
        f.write(f"# Generated on: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z%z')}\n\n")
        f.writelines(commands)

    print(f'已儲存 {output_file}')

def main():
    """主函數，使用多線程加速處理"""
    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(lambda url: process_url(session, url), urls)

if __name__ == '__main__':
    main()
