# stamparm/ipsum/level-8
# Source: https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/8.txt
# Converted for RouterOS by sinnoken/routeros-rsc
# WARNING: Auto-generated. Do not edit manually.
# Generated : 2026-11-19 09:41:52 UTC+0000
# Entries   : 33 raw -> 32 after CIDR aggregation (saved 1, 3.0%)

/ip firewall address-list remove [find list=STAMPARM-IPSUM-LEVEL-8-STAGING]
/ip firewall address-list add address=2.57.121.25/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=2.57.121.112/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=3.129.187.38/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=18.218.118.203/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=35.210.240.68/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.141/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.151/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.152/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.157/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=62.60.130.148/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.2/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.92/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=65.49.1.202/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.195.110/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=77.239.124.252/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=80.94.95.115/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=80.94.95.116/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=102.220.161.170/31 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=104.244.79.113/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=118.194.228.101/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=119.204.122.94/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=125.130.102.172/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=138.226.239.233/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=138.226.239.234/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=151.243.11.145/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.57/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.59/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.61/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.32.162.15/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.46.255.86/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.187.110.160/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=199.165.159.41/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list remove [find list=STAMPARM-IPSUM-LEVEL-8]
/ip firewall address-list set [find list=STAMPARM-IPSUM-LEVEL-8-STAGING] list=STAMPARM-IPSUM-LEVEL-8
