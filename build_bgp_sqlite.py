import subprocess
import pyasn
import sqlite3
import os
import sys
import time
import ipaddress

def download_and_convert():
    target_dat = "rib.latest.dat"
    target_bz2 = "rib.latest.bz2"
    one_hour_in_seconds = 3600

    # 檢查檔案是否存在且修改時間在 1 小時內
    if os.path.exists(target_dat):
        file_age = time.time() - os.path.getmtime(target_dat)
        if file_age < one_hour_in_seconds:
            print(f"Found {target_dat} (created {int(file_age/60)} mins ago). Skipping download.")
            return
        else:
            print(f"{target_dat} is older than 1 hour. Re-downloading...")
    else:
        print(f"{target_dat} not found. Starting fresh download.")

    # 開始下載
    print("Downloading latest BGP data...")
    subprocess.run([sys.executable, "-m", "pyasn.scripts.pyasn_util_download", "--latest", "--filename", target_bz2], check=True)
    
    # 開始轉換
    print(f"Converting {target_bz2} to {target_dat}...")
    subprocess.run([sys.executable, "-m", "pyasn.scripts.pyasn_util_convert", "--single", target_bz2, target_dat], check=True)

    # 轉換完畢後，建議刪除原始壓縮檔以節省空間
    if os.path.exists(target_bz2):
        os.remove(target_bz2)
        print(f"Cleaned up {target_bz2}")

def main():
    # 執行下載與轉換
    download_and_convert()
    
    if not os.path.exists('rib.latest.dat'):
        print("Error: rib.latest.dat not found!")
        return

    print("Loading BGP database from rib.latest.dat...")
    asndb = pyasn.pyasn('rib.latest.dat')
    
    db_name = "bgp.sqlite"
    if os.path.exists(db_name):
        os.remove(db_name)

    print(f"Creating SQLite database: {db_name}")
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    
    # 效能優化設定
    c.execute("PRAGMA journal_mode = OFF")
    c.execute("PRAGMA synchronous = OFF")
    c.execute("PRAGMA cache_size = -1000000") # 使用約 1GB 記憶體快取
    
    # 建立表結構
    c.execute("CREATE TABLE bgp (asn INTEGER, prefix TEXT)")
    
    print("Extracting all prefixes from pyasn...")
    
    # 修正點：pyasn 物件本身就是一個 generator，直接迭代它
    # 格式為 (prefix, asn)
    raw_data = []
    try:
        # 遍歷所有條目
        for prefix, asn in asndb:
            raw_data.append((prefix, asn))
    except Exception as e:
        print(f"Error during extraction: {e}")

    # 排序邏輯
    print(f"Sorting {len(raw_data)} prefixes by numerical value...")
    sorted_data = sorted(
        raw_data, 
        key=lambda x: (
            int(ipaddress.ip_network(x[0], strict=False).network_address), 
            ipaddress.ip_network(x[0], strict=False).prefixlen
        )
    )

    print("Inserting data into SQLite...")
    # 批次寫入：轉換為 (ASN, Prefix) 存入
    c.executemany("INSERT INTO bgp (asn, prefix) VALUES (?, ?)", ((asn, prefix) for prefix, asn in sorted_data))
    
    print("Creating index for fast ASN lookup...")
    c.execute("CREATE INDEX idx_asn ON bgp(asn)")
    
    conn.commit()
    conn.close()
    print(f"Database build complete. Total records: {len(sorted_data)}")

if __name__ == "__main__":
    main()
