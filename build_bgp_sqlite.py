import os
import time
import sys
import subprocess
import pyasn
import sqlite3
import ipaddress
import json

def download_and_convert():
    target_dat = "rib.latest.dat"
    target_bz2 = "rib.latest.bz2"
    target_names = "asnames.json"
    
    # 檢查是否需要更新 (1小時內不重複下載)
    need_update = not os.path.exists(target_dat) or (time.time() - os.path.getmtime(target_dat) > 3600)
    
    if not need_update:
        print(f"Using cached data.")
        return False 

    print("Downloading/Converting BGP data & AS Names...")
    subprocess.run([sys.executable, "-m", "pyasn.scripts.pyasn_util_download", "--latest", "--filename", target_bz2], check=True)
    subprocess.run([sys.executable, "-m", "pyasn.scripts.pyasn_util_convert", "--single", target_bz2, target_dat], check=True)
    subprocess.run([sys.executable, "-m", "pyasn.scripts.pyasn_util_asnames", "-o", target_names], check=True)
    
    if os.path.exists(target_bz2): os.remove(target_bz2)
    return True

def main():
    download_and_convert()
    db_name = "bgp.sqlite"
    names_file = "asnames.json"

    print("Loading datasets...")
    asndb = pyasn.pyasn('rib.latest.dat')
    
    with open(names_file, 'r', encoding='utf-8') as f:
        as_map = json.load(f)

    if os.path.exists(db_name):
        os.remove(db_name)

    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode = OFF")
    c.execute("PRAGMA synchronous = OFF")
    
    # --- 建立兩張表 ---
    # 1. 路由表 (IP 網段)
    c.execute("CREATE TABLE bgp (asn INTEGER, prefix TEXT)")
    # 2. ASN 資訊表 (公司名稱)
    c.execute("CREATE TABLE as_info (asn INTEGER PRIMARY KEY, name TEXT)")
    
    # --- 處理 as_info 資料 ---
    print("Populating as_info table...")
    name_data = [(int(asn), name) for asn, name in as_map.items()]
    c.executemany("INSERT INTO as_info VALUES (?, ?)", name_data)

    # --- 處理 bgp 資料 ---
    print("Extracting nodes from Radix tree...")
    raw_data = []
    for node in asndb.radix.nodes():
        try:
            net = ipaddress.ip_network(node.prefix, strict=False)
            raw_data.append((int(net.network_address), net.prefixlen, node.asn, node.prefix))
        except: continue

    print(f"Sorting {len(raw_data)} records...")
    raw_data.sort(key=lambda x: (x[0], x[1]))

    print("Inserting to bgp table...")
    c.executemany("INSERT INTO bgp VALUES (?, ?)", ((item[2], item[3]) for item in raw_data))
    
    # 建立索引優化查詢速度
    c.execute("CREATE INDEX idx_bgp_asn ON bgp(asn)")
    c.execute("CREATE INDEX idx_bgp_prefix ON bgp(prefix)")

    conn.commit()
    
    print("Vacuuming...")
    conn.isolation_level = None
    conn.execute("VACUUM")
    conn.close()
    
    print(f"Done! Database '{db_name}' is ready.")

if __name__ == "__main__":
    main()
