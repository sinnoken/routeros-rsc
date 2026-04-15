import urllib.request
import ipaddress
import sys
from datetime import datetime

url = "https://raw.githubusercontent.com/stamparm/maltrail/master/trails/static/mass_scanner.txt"

ipv4_list = []
ipv6_list = []

print("正在從 Maltrail 下載清單...")

try:
    # 1. 下載並清理資料
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')
        
    lines = data.splitlines()
    unique_ips = set()
    
    for line in lines:
        # 移除註解
        if '#' in line:
            line = line.split('#')[0]
        # 移除首尾空白
        line = line.strip()
        # 排除空行並加入 set 確保唯一性
        if line:
            unique_ips.add(line)
            
    if not unique_ips:
        print("❌ 錯誤：下載的清單為空。")
        sys.exit(1)
        
    print(f"成功取得 {len(unique_ips)} 筆唯一的 IP/CIDR。")
    print("開始生成 RouterOS .rsc 檔案...")

    # 2. 處理 IP 格式
    for ip_str in unique_ips:
        try:
            net = ipaddress.ip_network(ip_str, strict=False)
            if net.version == 4:
                ipv4_list.append(net)
            elif net.version == 6:
                ipv6_list.append(net)
        except ValueError:
            continue

    ipv4_list.sort()
    ipv6_list.sort()
    
    # 整合相鄰或重疊的網段
    ipv4_collapsed = list(ipaddress.collapse_addresses(ipv4_list))
    ipv6_collapsed = list(ipaddress.collapse_addresses(ipv6_list))

    gen_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC+0000')
    
    # 3. 定義寫入函式並輸出
    def write_rsc(filename, cidr_list, is_v6=False):
        cmd_path = '/ipv6 firewall address-list' if is_v6 else '/ip firewall address-list'
        list_name = 'MALTRAIL-SCANNER-V6' if is_v6 else 'MALTRAIL-SCANNER'
        
        with open(filename, 'w') as f:
            f.write(f'# Maltrail Mass Scanner List\n')
            f.write(f'# Source: https://github.com/stamparm/maltrail\n')
            f.write(f'# Generated on: {gen_time}\n\n')
            f.write(f'{cmd_path} remove [find list={list_name}]\n')
            
            for net in cidr_list:
                f.write(f'{cmd_path} add address={net} comment=Maltrail-Scanner list={list_name}\n')

    write_rsc('mass_scanner.rsc', ipv4_collapsed, is_v6=False)
    write_rsc('mass_scanner_v6.rsc', ipv6_collapsed, is_v6=True)
            
    print("✅ 轉換成功！")
    # +4 是加上檔頭註解與 remove 指令的行數
    print(f"IPv4 RSC 行數：{len(ipv4_collapsed) + 4}")
    print(f"IPv6 RSC 行數：{len(ipv6_collapsed) + 4}")

except Exception as e:
    print(f'❌ 錯誤: {e}')
    sys.exit(1)
