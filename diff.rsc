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

rapid7
censys
shadow
criminalip
