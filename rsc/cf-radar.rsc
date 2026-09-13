# --- 相容性優化版 ---
:local cfToken "你的_TOKEN"
:local targetLists {"PortScanner1"; "ros_service_login1"}

:foreach listName in=$targetLists do={
    :local entries [/ip/firewall/address-list find (list=$listName && (timeout>00:10:00 || timeout~"^\\\$") && comment~"^\\\$")]
    
    :foreach i in=$entries do={
        :local ipAddr [/ip/firewall/address-list get $i address]
        
        # 排除私有網段 (RFC1918)
        :if (!($ipAddr ~ "^(192\\.168|10\\.|172\\.(1[6-9]|2[0-9]|3[0-1]))")) do={
            :do {
                :local result [/tool fetch url="https://api.cloudflare.com/client/v4/radar/entities/asns/ip/$ipAddr" \
                    http-header-field="Authorization: Bearer $cfToken" as-value output=user]
                
                :if ($result->"status" = "finished") do={
                    :local rawData ($result->"data")
                    :local jsn [:deserialize jsn $rawData]
                    :local res ($jsn->"result")
                    
                    # 使用 get 確保即便欄位缺失也不會導致腳本 crash
                    :local ipI ($res->"ip")
                    :local asnI ($res->"asn")
                    
                    :local isCrawl [:tostr ($ipI->"isCrawler")]
                    :local isDC    [:tostr ($ipI->"isDatacenter")]
                    :local isBogon [:tostr ($ipI->"isBogon")]
                    :local aType   [:tostr ($asnI->"asnType")]
                    :local aName   [:tostr ($asnI->"orgName")]
                    :local ctry    [:tostr ($ipI->"countryName")]

                    :local action "CF_TRUSTED"
                    :local reason "NORMAL"

                    # 邏輯鏈：優先判定爬蟲
                    :if ($isCrawl = "true") do={
                        :set action "CF_ALLOW"; :set reason "CRAWLER"
                    } else={
                        :if ($isBogon = "true") do={
                            :set action "CF_BLOCK"; :set reason "BOGON"
                        } else={
                            :if ($isDC = "true" || $aType = "Content" || $aType = "Business") do={
                                :set action "CF_BLOCK"; :set reason "DC_BOT"
                            } else={
                                :if ([:tostr ($ipI->"isTor")] = "true" || [:tostr ($ipI->"isVpn")] = "true") do={
                                    :set action "CF_RISK"; :set reason "PROXY"
                                }
                            }
                        }
                    }

                    # 更新 Address List
                    :local finalComment "$reason|$aType|$ctry|$aName"
                    /ip/firewall/address-list add list=$action address=$ipAddr comment=$finalComment timeout=24h
                    /ip/firewall/address-list remove $i
                    :log info "CF Radar: Classified $ipAddr as $action"
                }
            } on-error={ :log warning "CF Radar: Failed to process $ipAddr" }
            :delay 300ms
        } else={
            /ip/firewall/address-list remove $i
        }
    }
}
