import requests
import ipaddress
import sys
import os

# 將輸出路徑改為 rsc/ 內，以符合 Release 抓取規則
OUTPUT_DIR = "rsc"
OUTPUT_FILE = f"{OUTPUT_DIR}/mikrotik_as_lists.rsc"

def fetch_and_aggregate(asn):
    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"
    print(f"正在抓取 {asn} 的路由資訊...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"抓取 {asn} 失敗，跳過此 ASN。錯誤訊息: {e}")
        return [], []

    prefixes = [item['prefix'] for item in data.get('data', {}).get('prefixes', [])]
    
    ipv4_nets = [ipaddress.ip_network(p) for p in prefixes if ':' not in p]
    ipv6_nets = [ipaddress.ip_network(p) for p in prefixes if ':' in p]
    
    collapsed_v4 = list(ipaddress.collapse_addresses(ipv4_nets))
    collapsed_v6 = list(ipaddress.collapse_addresses(ipv6_nets))
    
    print(f" > {asn} 聚合完成: IPv4 共 {len(collapsed_v4)} 筆, IPv6 共 {len(collapsed_v6)} 筆")
    return collapsed_v4, collapsed_v6

def main():
    asn_list = sys.argv[1:]
    
    if not asn_list:
        print("錯誤: 未傳入任何 ASN。")
        sys.exit(1)

    all_v4_rules = []
    all_v6_rules = []
    
    for asn in asn_list:
        asn_upper = asn.upper()
        v4_nets, v6_nets = fetch_and_aggregate(asn_upper)
        
        for cidr in v4_nets:
            all_v4_rules.append(f"add list={asn_upper} address={cidr}")
            
        for cidr in v6_nets:
            all_v6_rules.append(f"add list={asn_upper} address={cidr}")
            
    # 確保輸出目錄存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"\n準備寫入至 {OUTPUT_FILE} ...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Auto-generated MikroTik Address List for {', '.join(asn_list).upper()}\n")
        f.write("# This file is automatically updated via GitHub Actions\n\n")
        
        if all_v4_rules:
            f.write("/ip firewall address-list\n")
            for rule in all_v4_rules:
                f.write(rule + "\n")
            f.write("\n")
            
        if all_v6_rules:
            f.write("/ipv6 firewall address-list\n")
            for rule in all_v6_rules:
                f.write(rule + "\n")

    print(f"成功產生檔案: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
