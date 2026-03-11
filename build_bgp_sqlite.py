import os
import time
import sys
import subprocess
import pyasn
import sqlite3
import ipaddress
import gzip
import shutil

def download_and_convert():
    target_dat = "rib.latest.dat"
    target_bz2 = "rib.latest.bz2"
    if os.path.exists(target_dat) and (time.time() - os.path.getmtime(target_dat) < 3600):
        print(f"Using cached {target_dat} (less than 1 hour old).")
        return False # 沒有重新下載
    
    print("Downloading/Converting latest BGP data...")
    subprocess.run([sys.executable, "-m", "pyasn.scripts.pyasn_util_download", "--latest", "--filename", target_bz2], check=True)
    subprocess.run([sys.executable, "-m", "pyasn.scripts.pyasn_util_convert", "--single", target_bz2, target_dat], check=True)
    if os.path.exists(target_bz2): os.remove(target_bz2)
    return True # 有更新

def main():
    has_updated = download_and_convert()
    db_name = "bgp.sqlite"
    gz_name = "bgp.sqlite.gz"

    # 如果沒更新且 .gz 已存在，可以選擇直接結束
    if not has_updated and os.path.exists(gz_name):
        print("No update needed.")
        return

    print("Loading BGP database...")
    asndb = pyasn.pyasn('rib.latest.dat')
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode = OFF")
    c.execute("PRAGMA synchronous = OFF")
    c.execute("CREATE TABLE bgp (asn INTEGER, prefix TEXT)")
    
    print("Extracting nodes from Radix tree...")
    raw_data = []
    # 修正後的提取邏輯
    for node in asndb.radix.nodes():
        try:
            net = ipaddress.ip_network(node.prefix, strict=False)
            raw_data.append((int(net.network_address), net.prefixlen, node.asn, node.prefix))
        except: continue

    print(f"Sorting {len(raw_data)} records...")
    raw_data.sort(key=lambda x: (x[0], x[1]))

    print("Inserting to SQLite...")
    c.executemany("INSERT INTO bgp VALUES (?, ?)", ((item[2], item[3]) for item in raw_data))
    c.execute("CREATE INDEX idx_asn ON bgp(asn)")
    
    conn.commit()
    conn.close()

    # 壓縮並清理
    print(f"Compressing to {gz_name}...")
    with open(db_name, 'rb') as f_in, gzip.open(gz_name, 'wb', compresslevel=9) as f_out:
        shutil.copyfileobj(f_in, f_out)
    
    os.remove(db_name) # 刪除巨大的原始 sqlite
    print("Process complete.")

if __name__ == "__main__":
    main()
