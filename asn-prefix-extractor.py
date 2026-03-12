import subprocess
import pyasn
import ipaddress
import argparse
import os
import time
import sys
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
    
    print("Downloading latest asnames data...")
    subprocess.run(["pyasn_util_asnames.py", "-o", target_names ], check=True)
    print("Downloading latest BGP data...")
    subprocess.run(["pyasn_util_download.py", "--latest", "--filename", target_bz2 ], check=True)
    print("Converting rib.latest.bz2 to rib.latest.dat...")
    subprocess.run(["pyasn_util_convert.py", "--single", "rib.latest.bz2", target_dat ], check=True)

    
    if os.path.exists(target_bz2): os.remove(target_bz2)
    return True

def main(asn):
    download_and_convert()
    print("Loading BGP database from rib.latest.dat...")
    asndb = pyasn.pyasn('rib.latest.dat')

    print(f"Extracting prefixes for ASN {asn}...")
    prefixes = asndb.get_as_prefixes(asn)

    print("Sorting prefixes by numerical value...")
    sorted_prefixes = sorted(prefixes, key=lambda p: (ipaddress.ip_network(p, strict=False).network_address, ipaddress.ip_network(p, strict=False).prefixlen))

    output_filename = f'asn_{asn}_prefixes.txt'
    print(f"Writing sorted prefixes to {output_filename}...")
    with open(output_filename, 'w') as f:
        f.writelines(f'{prefix}\n' for prefix in sorted_prefixes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process BGP data for a specific ASN.")
    parser.add_argument('asn', type=int, help='The ASN to extract prefixes for')
    args = parser.parse_args()
    main(args.asn)
