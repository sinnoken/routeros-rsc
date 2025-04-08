import pyasn

# 加載 BGP 資料庫
asndb = pyasn.pyasn('rib.latest.dat')

# 提取 ASN 9505 的前綴
prefixes = asndb.get_as_prefixes(9505)

# 將前綴寫入檔案
with open('asn9505_prefixes.txt', 'w') as f:
    for prefix in prefixes:
        f.write(f'{prefix}\n')
