:local listComment "unknown"
:local listAddress
:foreach i in=[/ip/firewall/address-list find (timeout>00:10:00 || timeout~"^\$") && comment~"^\$" && list~"^(PortScanner[12]|ros_service_login[1-5])\$"] do={

    :set listAddress [/ip/firewall/address-list get $i address]
    :set listComment [/ip/firewall/address-list get $i comment]

    :put ("Address: " . $listAddress . " | Comment: " . $listComment)
}

:local listComment "unknown"
:local listAddress
:foreach i in=[/ip/firewall/address-list find (timeout>00:10:00 || timeout~"^\$") && comment~"^\$" && (list=PortScanner1 || list=PortScanner2 || list=ros_service_login1 || list=ros_service_login2 || list=ros_service_login3 || list=ros_service_login4 || list=ros_service_login5)] do={

    :set listAddress [/ip/firewall/address-list get $i address]
    :set listComment [/ip/firewall/address-list get $i comment]

    :put ("Address: " . $listAddress . " | Comment: " . $listComment)
}


/ip/firewall/address-list find (timeout>00:10:00 || timeout~"^\$") && comment~"^\$" && list~"^(PortScanner[12]|ros_service_login[1-5])\$"

/ip/firewall/address-list find (timeout>00:10:00 || timeout="") && comment="" && list~"^(PortScanner[12]|ros_service_login[1-5])\$"

/ip/firewall/address-list find (timeout>00:10:00 || timeout=[]) && comment=[] && list~"^(PortScanner[12]|ros_service_login[1-5])\$"

!comment=[]
:typeof

/ip/firewall/address-list find (timeout>00:10:00 || [:len timeout] = 0) && [:len comment] = 0 && list~"^(PortScanner[12]|ros_service_login[1-5])\$"
