import subprocess
import pyasn
import ipaddress

def download_and_convert():
    print("Downloading latest BGP data...")
    subprocess.run(["pyasn_util_download.py", "--latest", "--filename", "rib.latest.bz2"], check=True)
    print("Converting rib.latest.bz2 to rib.latest.dat...")
    subprocess.run(["pyasn_util_convert.py", "--single", "rib.latest.bz2", "rib.latest.dat"], check=True)

def main():
    download_and_convert()
    print("Loading BGP database from rib.latest.dat...")
    asndb = pyasn.pyasn('rib.latest.dat')

    print("Extracting prefixes for ASN 45102...")
    prefixes = asndb.get_as_prefixes(45102)

    print("Sorting prefixes by numerical value...")
    sorted_prefixes = sorted(prefixes, key=lambda p: (ipaddress.ip_network(p, strict=False).network_address, ipaddress.ip_network(p, strict=False).prefixlen))

    print("Writing sorted prefixes to asn_prefixes.txt...")
    with open('asn_prefixes.txt', 'w') as f:
        f.writelines(f'{prefix}\n' for prefix in sorted_prefixes)

if __name__ == "__main__":
    main()
