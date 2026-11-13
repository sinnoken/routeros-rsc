# stamparm/ipsum/level-8
# Source: https://github.com/stamparm/ipsum/raw/refs/heads/master/levels/8.txt
# Converted for RouterOS by sinnoken/routeros-rsc
# WARNING: Auto-generated. Do not edit manually.
# Generated : 2026-11-13 08:56:05 UTC+0000
# Entries   : 34 raw -> 34 after CIDR aggregation (saved 0, 0.0%)

/ip firewall address-list remove [find list=STAMPARM-IPSUM-LEVEL-8-STAGING]
/ip firewall address-list add address=3.129.187.38/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=3.130.168.2/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=35.210.54.75/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=35.210.125.227/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=35.210.166.45/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.141/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.151/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.152/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=45.148.10.157/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=64.62.197.92/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.159.106/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.172.179/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.195.74/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=66.132.195.98/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=80.94.95.115/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=81.181.129.218/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=81.192.46.45/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=103.159.2.113/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=119.96.173.169/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=125.130.102.172/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=138.226.239.233/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=138.226.239.234/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=152.32.236.102/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.49/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.50/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.52/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=167.94.146.62/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=179.43.153.2/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=185.87.121.1/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.32.162.15/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=193.47.62.69/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=195.178.110.228/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=209.99.190.186/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list add address=220.80.223.144/32 comment="stamparm/ipsum/level-8" list=STAMPARM-IPSUM-LEVEL-8-STAGING
/ip firewall address-list remove [find list=STAMPARM-IPSUM-LEVEL-8]
/ip firewall address-list set [find list=STAMPARM-IPSUM-LEVEL-8-STAGING] list=STAMPARM-IPSUM-LEVEL-8
