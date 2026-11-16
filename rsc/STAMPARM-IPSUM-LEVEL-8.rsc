# stamparm/ipsum/level-8
# Source: https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/8.txt
# Converted for RouterOS by sinnoken/routeros-rsc
# WARNING: Auto-generated. Do not edit manually.
# Generated : 2026-11-16 08:49:11 UTC+0000
# Entries   : 35 raw -> 34 after CIDR aggregation (saved 1, 2.9%)

/ip firewall address-list remove [find list=STAMPARM-IPSUM-LEVEL-8-STAGING]
/ip firewall address-list add address=3.129.187.38/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=18.218.118.203/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.5/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.141/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.151/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.152/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.157/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.32/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.77/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.92/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.137/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.172.186/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.186.206/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.195.49/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.195.112/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=77.239.124.252/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=80.94.95.115/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=80.94.95.116/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=81.181.129.218/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=109.105.210.72/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=125.130.102.172/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=138.226.239.233/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=138.226.239.234/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=152.32.236.102/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.48/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.50/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.53/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.54/31 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.58/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=170.231.237.214/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.32.162.15/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.47.62.69/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=196.189.236.67/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=199.165.159.9/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list remove [find list=STAMPARM-IPSUM-LEVEL-8]
/ip firewall address-list set [find list=STAMPARM-IPSUM-LEVEL-8-STAGING] list=STAMPARM-IPSUM-LEVEL-8
