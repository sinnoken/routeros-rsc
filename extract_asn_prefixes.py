import subprocess
import pyasn
import ipaddress

def download_and_convert():
    # Step 1: Download the latest BGP data
    print("Downloading latest BGP data...")
    subprocess.run(["pyasn_util_download.py", "--latest", "--filename", "rib.latest.bz2"], check=True)

    # Step 2: Convert to .dat format
    print("Converting rib.latest.bz2 to rib.latest.dat...")
    subprocess.run(["pyasn_util_convert.py", "--single", "rib.latest.bz2", "rib.latest.dat"], check=True)

def main():
    # Download and convert BGP data
    download_and_convert()

    # Load BGP database
    print("Loading BGP database from rib.latest.dat...")
    asndb = pyasn.pyasn('rib.latest.dat')

    # Extract prefixes for ASN 9505
    print("Extracting prefixes for ASN 9505...")
    prefixes = asndb.get_as_prefixes(9505)

    # Sort the prefixes by numerical value
    print("Sorting prefixes by numerical value...")
    sorted_prefixes = sorted(prefixes, key=lambda p: (ipaddress.ip_network(p, strict=False).network_address, ipaddress.ip_network(p, strict=False).prefixlen))

    # Write sorted prefixes to file
    print("Writing sorted prefixes to asn9505_prefixes.txt...")
    with open('asn9505_prefixes.txt', 'w') as f:
        for prefix in sorted_prefixes:
            f.write(f'{prefix}\n')

if __name__ == "__main__":
    main()
