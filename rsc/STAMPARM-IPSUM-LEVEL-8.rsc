# stamparm/ipsum/level-8
# Source: https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/8.txt
# Converted for RouterOS by sinnoken/routeros-rsc
# WARNING: Auto-generated. Do not edit manually.
# Generated : 2026-11-23 10:02:01 UTC+0000
# Entries   : 32 raw -> 32 after CIDR aggregation (saved 0, 0.0%)

/ip firewall address-list remove [find list=STAMPARM-IPSUM-LEVEL-8-STAGING]
/ip firewall address-list add address=3.129.187.38/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=18.218.118.203/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=35.210.88.112/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.61/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=46.151.178.14/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=62.60.130.148/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=62.60.130.219/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.17/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.92/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.197/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.172.217/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.186.204/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.195.48/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.195.107/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.195.210/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.224.229/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=77.239.124.181/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=77.239.124.252/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=93.174.95.106/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=102.220.45.186/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=119.204.122.94/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=125.130.102.172/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=138.226.239.233/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=138.226.239.234/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=151.243.11.108/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.58/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.32.162.15/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.47.62.69/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.187.110.158/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=199.165.159.169/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=199.165.159.193/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=209.99.190.186/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list remove [find list=STAMPARM-IPSUM-LEVEL-8]
/ip firewall address-list set [find list=STAMPARM-IPSUM-LEVEL-8-STAGING] list=STAMPARM-IPSUM-LEVEL-8
