import urllib.request
import ipaddress
import sys
from datetime import datetime

url = "https://raw.githubusercontent.com/stamparm/maltrail/master/trails/static/mass_scanner.txt"

original_ips_v4 = []
original_ips_v6 = []
# 用來儲存 IP 與其對應的註解
ip_comments = {}

print("正在從 Maltrail 下載清單...")

try:
    # 1. 下載並解析資料與註解
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        data = response.read().decode('utf-8')
        
    lines = data.splitlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        comment = ""
        # 拆分 IP 與註解
        if '#' in line:
            parts = line.split('#', 1)
            ip_str = parts[0].strip()
            comment = parts[1].strip()
        else:
            ip_str = line

        if not ip_str:
            continue

        try:
            net = ipaddress.ip_network(ip_str, strict=False)
            if net.version == 4:
                original_ips_v4.append(net)
            elif net.version == 6:
                original_ips_v6.append(net)
                
            # 如果這行有註解，就記錄下來 (使用 set 防止重複註解)
            if comment:
                if net not in ip_comments:
                    ip_comments[net] = set()
                ip_comments[net].add(comment)
                
        except ValueError:
            continue

    if not original_ips_v4 and not original_ips_v6:
        print("❌ 錯誤：解析後沒有找到任何有效的 IP。")
        sys.exit(1)
        
    print(f"成功取得 {len(original_ips_v4) + len(original_ips_v6)} 筆 IP。")
    print("開始合併網段並整併註解...")

    original_ips_v4.sort()
    original_ips_v6.sort()
    
    # 2. 合併相鄰或重疊的網段
    ipv4_collapsed = list(ipaddress.collapse_addresses(original_ips_v4))
    ipv6_collapsed = list(ipaddress.collapse_addresses(original_ips_v6))

    # 3. 將原本的註解重新對應到合併後的網段上
    def build_collapsed_comments(original_nets, collapsed_nets, comments_map):
        result_map = {}
        for orig_net in original_nets:
            if orig_net not in comments_map:
                continue
            # 尋找這個原始 IP 被合併到了哪個新網段 (subnet_of 是 Python 3.7+ 內建功能)
            for c_net in collapsed_nets:
                if orig_net.subnet_of(c_net):
                    if c_net not in result_map:
                        result_map[c_net] = set()
                    result_map[c_net].update(comments_map[orig_net])
                    break
        return result_map

    v4_comments_map = build_collapsed_comments(original_ips_v4, ipv4_collapsed, ip_comments)
    v6_comments_map = build_collapsed_comments(original_ips_v6, ipv6_collapsed, ip_comments)

    gen_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC+0000')
    
    # 4. 定義寫入函式並輸出
    def write_rsc(filename, collapsed_list, comments_map, is_v6=False):
        cmd_path = '/ipv6 firewall address-list' if is_v6 else '/ip firewall address-list'
        list_name = 'MALTRAIL-SCANNER-V6' if is_v6 else 'MALTRAIL-SCANNER'
        
        with open(filename, 'w') as f:
            f.write(f'# Maltrail Mass Scanner List\n')
            f.write(f'# Source: https://github.com/stamparm/maltrail\n')
            f.write(f'# Generated on: {gen_time}\n\n')
            f.write(f'{cmd_path} remove [find list={list_name}]\n')
            
            for net in collapsed_list:
                # 判斷這個合併後的網段有沒有對應的註解
                if net in comments_map and comments_map[net]:
                    # 將多個註解用逗號合併，並限制長度以免 RouterOS 報錯
                    merged_comment = ", ".join(sorted(comments_map[net]))
                    if len(merged_comment) > 120:
                        merged_comment = merged_comment[:117] + "..."
                    comment_str = f'Maltrail: {merged_comment}'
                else:
                    comment_str = 'Maltrail-Scanner'
                    
                f.write(f'{cmd_path} add address={net} comment="{comment_str}" list={list_name}\n')

    write_rsc('mass_scanner.rsc', ipv4_collapsed, v4_comments_map, is_v6=False)
    write_rsc('mass_scanner_v6.rsc', ipv6_collapsed, v6_comments_map, is_v6=True)
            
    print("✅ 轉換成功！")
    print(f"IPv4 RSC 行數：{len(ipv4_collapsed) + 4}")
    print(f"IPv6 RSC 行數：{len(ipv6_collapsed) + 4}")

except Exception as e:
    print(f'❌ 錯誤: {e}')
    sys.exit(1)
