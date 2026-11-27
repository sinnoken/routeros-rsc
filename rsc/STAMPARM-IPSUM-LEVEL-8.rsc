# stamparm/ipsum/level-8
# Source: https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/8.txt
# Converted for RouterOS by sinnoken/routeros-rsc
# WARNING: Auto-generated. Do not edit manually.
# Generated : 2026-11-27 10:21:49 UTC+0000
# Entries   : 33 raw -> 32 after CIDR aggregation (saved 1, 3.0%)

/ip firewall address-list remove [find list=STAMPARM-IPSUM-LEVEL-8-STAGING]
/ip firewall address-list add address=3.129.187.38/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=18.218.118.203/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=27.102.116.43/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=35.206.163.19/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=35.210.24.61/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.17/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.137/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.152/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.182/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.172.139/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.172.201/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.172.209/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.186.180/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.186.196/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.195.67/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.195.100/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.224.80/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=93.123.109.116/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=93.123.109.181/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=102.220.45.186/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=103.248.120.6/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=104.244.79.113/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=119.204.122.94/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=125.130.102.172/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=161.49.89.39/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.47.62.149/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.47.62.152/31 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=199.165.159.41/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=199.165.159.57/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=199.165.159.121/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=220.80.223.144/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=220.247.224.226/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list remove [find list=STAMPARM-IPSUM-LEVEL-8]
/ip firewall address-list set [find list=STAMPARM-IPSUM-LEVEL-8-STAGING] list=STAMPARM-IPSUM-LEVEL-8
