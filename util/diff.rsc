# 取得 address-list 中的 IP
:local currentIP [/ip firewall address-list get [find list=PPPoE-StaticIP-current] address]

# 取得 BGP connection 的現有 local.address
:local bgpID [/routing/bgp/connection find]
:local currentLocal [/routing/bgp/connection get $bgpID local.address]

# 比較兩者是否不同
:if ($currentIP != $currentLocal) do={
    :log info "Updating BGP local.address from $currentLocal to $currentIP"
    /routing/bgp/connection set $bgpID local.address=$currentIP
} else={
    :log info "BGP local.address is already up to date."
}

https://github.com/MDMCK10/internet-scanners/raw/refs/heads/main/cidr/rapid7_v4.txt
https://github.com/MDMCK10/internet-scanners/raw/refs/heads/main/cidr/rapid7_v6.txt
https://github.com/MDMCK10/internet-scanners/raw/refs/heads/main/cidr/censys_v4.txt
https://github.com/MDMCK10/internet-scanners/raw/refs/heads/main/cidr/censys_v6.txt
https://github.com/MDMCK10/internet-scanners/raw/refs/heads/main/cidr/shadowserver_v4.txt
https://github.com/MDMCK10/internet-scanners/raw/refs/heads/main/cidr/shadowserver_v6.txt
https://github.com/MDMCK10/internet-scanners/raw/refs/heads/main/cidr/criminalip_v4.txt
