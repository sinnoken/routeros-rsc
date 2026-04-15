import ipaddress
import sys
from datetime import datetime

ipv4_list = []
ipv6_list = []

try:
    with open('raw_ips.txt', 'r') as f:
        for line in f:
            ip_str = line.strip()
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
    
    ipv4_collapsed = list(ipaddress.collapse_addresses(ipv4_list))
    ipv6_collapsed = list(ipaddress.collapse_addresses(ipv6_list))

    gen_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC+0000')
    
    # 定義寫入函式
    def write_rsc(filename, cidr_list, is_v6=False):
        cmd_path = '/ipv6 firewall address-list' if is_v6 else '/ip firewall address-list'
        list_name = 'MALTRAIL-SCANNER-V6' if is_v6 else 'MALTRAIL-SCANNER'
        
        with open(filename, 'w') as f:
            # 寫入標頭
            f.write(f'# Maltrail Mass Scanner List\n')
            f.write(f'# Source: https://github.com/stamparm/maltrail\n')
            f.write(f'# Generated on: {gen_time}\n\n')
            
            # 建議：先清空舊的清單 (可選)
            f.write(f'{cmd_path} remove [find list={list_name}]\n')
            
            # 寫入條目
            for net in cidr_list:
                f.write(f'{cmd_path} add address={net} comment=Maltrail-Scanner list={list_name}\n')

    # 執行寫入
    write_rsc('mass_scanner.rsc', ipv4_collapsed, is_v6=False)
    write_rsc('mass_scanner_v6.rsc', ipv6_collapsed, is_v6=True)
            
except Exception as e:
    print(f'❌ 錯誤: {e}')
    sys.exit(1)
