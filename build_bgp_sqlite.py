import subprocess
import pyasn
import sqlite3
import os
import ipaddress

def download_and_convert():
    # 保持你原本的下載與轉換邏輯
    print("Downloading latest BGP data...")
    subprocess.run(["python", "pyasn_util_download.py", "--latest", "--filename", "rib.latest.bz2"], check=True)
    print("Converting rib.latest.bz2 to rib.latest.dat...")
    subprocess.run(["python", "pyasn_util_convert.py", "--single", "rib.latest.bz2", "rib.latest.dat"], check=True)

def main():
    # 執行下載與轉換
    download_and_convert()
    
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
    
    # 建立表結構
    c.execute("CREATE TABLE bgp (asn INTEGER, prefix TEXT)")
    
    print("Extracting all prefixes and inserting to SQLite...")
    # 取得全量資料 (Prefix, ASN)
    all_prefixes = asndb.get_all_prefixes()
    
    # 雖然 SQLite 本身可以排序，但我們在寫入前可以先按你的邏輯排好，確保資料庫物理順序整齊
    # 這裡我們針對全量資料做排序 (這會花一點點時間，但在 GitHub Actions 的 7GB RAM 下沒問題)
    print("Sorting all prefixes by numerical value...")
    sorted_data = sorted(
        all_prefixes, 
        key=lambda x: (ipaddress.ip_network(x[0], strict=False).network_address, 
                       ipaddress.ip_network(x[0], strict=False).prefixlen)
    )

    # 批次寫入：轉換為 (ASN, Prefix) 存入
    c.executemany("INSERT INTO bgp VALUES (?, ?)", ((asn, prefix) for prefix, asn in sorted_data))
    
    print("Creating index for fast ASN lookup...")
    c.execute("CREATE INDEX idx_asn ON bgp(asn)")
    
    conn.commit()
    conn.close()
    print("Database build complete.")

if __name__ == "__main__":
    main()
