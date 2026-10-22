# trails-import.rsc
# 在 RouterOS 上直接下載 stamparm/trails（及選用的 maltrail mass_scanner），
# 只取 IP / CIDR，加入 address-list。網域與 URL 路徑會略過。
#
# 需求：RouterOS 7.13 以上（使用 /file/read 分段讀取）
#
# 授權注意：
#   stamparm/trails 採 Maltrail Trails Community Data License 1.0。
#   本腳本僅供在「你自己管理的網路」上使用（授權第 3 條 Internal Defensive Use）。
#   請勿將產生的清單轉發、公開或用於代管客戶的網路（需另取得書面授權）。
#   https://github.com/stamparm/trails/blob/main/LICENSE.md
#
# 更新方式：
#   每筆條目帶 timeout，重新執行時延長已存在條目的 timeout，
#   上游移除的條目會在 timeout 到期後自然消失，更新期間清單不會被清空。
#   單一來源下載失敗時，既有條目保留到 timeout 到期。
#
# 安裝：
#   /file 上傳本檔後執行
#   /system script add name=trails-import source=[/file get trails-import.rsc contents]
#   /system scheduler add name=trails-import interval=1d start-time=04:30:00 \
#       on-event="/system script run trails-import"
#   /system scheduler add name=trails-import-boot start-time=startup \
#       on-event="/system script run trails-import"
#
# 開機後清單會是空的：帶 timeout 的條目屬於 dynamic，不會存入設定，重開機即清除
# （見官方手冊 Address lists 頁）。因此需要上面第二個排程在開機時重建。
# 開機排程執行時網路尚未就緒，腳本開頭會先等待預設路由生效（最多 5 分鐘）。
#
# 建議先觀察再封鎖（C2 清單可能混有雲端共用 IP）：
#   /ip firewall raw add chain=prerouting action=log log-prefix="TRAILS-C2" \
#       src-address-list=TRAILS-C2
#   確認無誤後再改為 action=drop
#
# 首次執行約需數分鐘（約 3 萬筆），之後每日執行主要是延長 timeout。

{
# ---- 等待網路（開機排程時介面與 DHCP 可能尚未就緒）----
:local waitTries 0
:while (([:len [/ip/route/find where dst-address=0.0.0.0/0 active]] = 0) && ($waitTries < 60)) do={
  :delay 5s
  :set waitTries ($waitTries + 1)
}
:if ($waitTries > 0) do={ :log info ("trails-import: waited " . ($waitTries * 5) . "s for default route") }

# ---- 設定 ----
:local ttl 3d
:local chunkSize 32768
:local tmpFile "trails-tmp.txt"
:local base "https://raw.githubusercontent.com/stamparm/trails/main/"

# 來源：{Trails 相對路徑或完整網址; address-list 名稱; 條目註解}
# 不需要的來源在行首加 # 停用
:local sources ({})
:set ($sources->[:len $sources]) {"malicious/sliver.txt";"TRAILS-C2";"Trails: sliver"}
:set ($sources->[:len $sources]) {"malicious/metasploit.txt";"TRAILS-C2";"Trails: metasploit"}
:set ($sources->[:len $sources]) {"malicious/mythic.txt";"TRAILS-C2";"Trails: mythic"}
:set ($sources->[:len $sources]) {"malicious/havoc.txt";"TRAILS-C2";"Trails: havoc"}
:set ($sources->[:len $sources]) {"malicious/supershell_c2.txt";"TRAILS-C2";"Trails: supershell"}
:set ($sources->[:len $sources]) {"malicious/deimos_c2.txt";"TRAILS-C2";"Trails: deimos"}
:set ($sources->[:len $sources]) {"malicious/viper.txt";"TRAILS-C2";"Trails: viper"}
:set ($sources->[:len $sources]) {"malicious/adaptix_c2.txt";"TRAILS-C2";"Trails: adaptix"}
:set ($sources->[:len $sources]) {"malicious/covenant.txt";"TRAILS-C2";"Trails: covenant"}
:set ($sources->[:len $sources]) {"malicious/brc4.txt";"TRAILS-C2";"Trails: brc4"}
:set ($sources->[:len $sources]) {"malicious/nimplant.txt";"TRAILS-C2";"Trails: nimplant"}

# 選用：maltrail 掃描器清單（MIT 授權）。
# 本 repo 的 rsc/mass_scanner.rsc 已做 CIDR 聚合、筆數較少，建議優先使用該檔。
# 若改用本腳本，清單名稱刻意與 MALTRAIL-SCANNER 區隔，避免互相清除。
#:set ($sources->[:len $sources]) {"https://raw.githubusercontent.com/stamparm/maltrail/master/data/mass_scanner.txt";"MALTRAIL-SCANNER-RAW";"Maltrail-Scanner"}

# 不加入清單的保留 / 內網位址，避免誤封自己的網路
:local bogon4 {0.0.0.0/8;10.0.0.0/8;100.64.0.0/10;127.0.0.0/8;169.254.0.0/16;172.16.0.0/12;192.0.0.0/24;192.168.0.0/16;198.18.0.0/15;224.0.0.0/4;240.0.0.0/4}
:local bogon6 {::/8;fc00::/7;fe80::/10;ff00::/8;2001:db8::/32}

# ---- 載入既有條目，之後用陣列查找，避免每筆都 find ----
:local known ({})
:local loaded ({})
:foreach src in=$sources do={
  :local listName ($src->1)
  :if ([:typeof ($loaded->$listName)] = "nothing") do={
    :set ($loaded->$listName) true
    :foreach i in=[/ip firewall address-list find list=$listName] do={
      :set ($known->($listName . "|4|" . [/ip firewall address-list get $i address])) $i
    }
    :foreach i in=[/ipv6 firewall address-list find list=$listName] do={
      :set ($known->($listName . "|6|" . [/ipv6 firewall address-list get $i address])) $i
    }
  }
}

# ---- 逐一處理來源 ----
:foreach src in=$sources do={
  :local path ($src->0)
  :local listName ($src->1)
  :local tag ($src->2)
  :local url $path
  :if ([:pick $path 0 8] != "https://") do={ :set url ($base . $path) }

  :local added 0
  :local refreshed 0
  :local dup 0
  :local other 0
  :local bogon 0
  :local failed 0

  :local ok true
  :do {
    /tool fetch url=$url dst-path=$tmpFile as-value
  } on-error={
    :set ok false
    :log warning ("trails-import: download failed, keep existing entries: " . $url)
  }

  :local size 0
  :if ($ok) do={
    :delay 1s
    :do { :set size [/file get [find name=$tmpFile] size] } on-error={ :set ok false }
  }

  :if ($ok) do={
    :local off 0
    :local carry ""
    :while ($off < $size) do={
      :local chunk ([/file/read file=$tmpFile offset=$off chunk-size=$chunkSize as-value]->"data")
      :set off ($off + $chunkSize)
      # 分段邊界可能切斷一行，未結束的部分留到下一段
      :local buf ($carry . $chunk)
      :if ($off >= $size) do={ :set buf ($buf . "\n") }
      :local start 0
      :local nl [:find $buf "\n" -1]
      :while ([:typeof $nl] = "num") do={
        :local line [:pick $buf $start $nl]
        :set start ($nl + 1)
        :set nl [:find $buf "\n" $nl]

        :local lineLen [:len $line]
        :if ($lineLen > 0 && [:pick $line ($lineLen - 1)] = "\r") do={ :set line [:pick $line 0 ($lineLen - 1)] }
        :local c0 [:pick $line 0 1]

        # 跳過空行、註解、URL 路徑
        :if ([:len $line] > 0 && $c0 != "#" && $c0 != "/") do={
          # 只取第一個欄位（去掉行內註解）
          :local sp [:find $line " "]
          :if ([:typeof $sp] = "num") do={ :set line [:pick $line 0 $sp] }
          :local tb [:find $line "\t"]
          :if ([:typeof $tb] = "num") do={ :set line [:pick $line 0 $tb] }

          # 拆出 /前綴長度 或 URL 路徑
          :local host $line
          :local plen ""
          :local sl [:find $host "/"]
          :if ([:typeof $sl] = "num") do={
            :set plen [:pick $host ($sl + 1) [:len $host]]
            :set host [:pick $host 0 $sl]
          }
          # [IPv6]:port
          :if ([:pick $host 0 1] = "[") do={
            :local rb [:find $host "]"]
            :if ([:typeof $rb] = "num") do={ :set host [:pick $host 1 $rb] }
          }
          # IPv4:port
          :if ([:typeof [:find $host "."]] = "num") do={
            :local co [:find $host ":"]
            :if ([:typeof $co] = "num") do={ :set host [:pick $host 0 $co] }
          }
          :local pnum [:tonum $plen]

          :local ip4 [:toip $host]
          :local ip6 [:toip6 $host]

          # 轉回字串須與原文相同，排除 "1.2.3" 這類被寬鬆解析的字串
          :if ([:typeof $ip4] = "ip" && [:tostr $ip4] = $host) do={
            :local isBogon false
            :foreach r in=$bogon4 do={ :if ($ip4 in $r) do={ :set isBogon true } }
            :if ($isBogon) do={
              :set bogon ($bogon + 1)
            } else={
              :local addr [:tostr $ip4]
              # 只接受 /8 以上的網段，避免單筆涵蓋過大範圍
              :if ([:typeof $pnum] = "num" && $pnum >= 8 && $pnum < 32) do={ :set addr ($addr . "/" . $pnum) }
              :local key ($listName . "|4|" . $addr)
              :local cur ($known->$key)
              :if ([:typeof $cur] = "nothing") do={
                :do {
                  /ip firewall address-list add list=$listName address=$addr timeout=$ttl comment=$tag
                  :set added ($added + 1)
                } on-error={
                  :do {
                    /ip firewall address-list set [find list=$listName address=$addr] timeout=$ttl
                    :set refreshed ($refreshed + 1)
                  } on-error={ :set failed ($failed + 1) }
                }
                :set ($known->$key) "seen"
              } else={
                :if ($cur != "seen") do={
                  :do { /ip firewall address-list set $cur timeout=$ttl } on-error={ :set failed ($failed + 1) }
                  :set refreshed ($refreshed + 1)
                  :set ($known->$key) "seen"
                } else={ :set dup ($dup + 1) }
              }
            }
          } else={
            :if ([:typeof $ip6] = "ip6") do={
              :local isBogon false
              :foreach r in=$bogon6 do={ :if ($ip6 in $r) do={ :set isBogon true } }
              :if ($isBogon) do={
                :set bogon ($bogon + 1)
              } else={
                :local addr ([:tostr $ip6] . "/128")
                :if ([:typeof $pnum] = "num" && $pnum >= 16 && $pnum < 128) do={ :set addr ([:tostr $ip6] . "/" . $pnum) }
                :local key ($listName . "|6|" . $addr)
                :local cur ($known->$key)
                :if ([:typeof $cur] = "nothing") do={
                  :do {
                    /ipv6 firewall address-list add list=$listName address=$addr timeout=$ttl comment=$tag
                    :set added ($added + 1)
                  } on-error={
                    :do {
                      /ipv6 firewall address-list set [find list=$listName address=$addr] timeout=$ttl
                      :set refreshed ($refreshed + 1)
                    } on-error={ :set failed ($failed + 1) }
                  }
                  :set ($known->$key) "seen"
                } else={
                  :if ($cur != "seen") do={
                    :do { /ipv6 firewall address-list set $cur timeout=$ttl } on-error={ :set failed ($failed + 1) }
                    :set refreshed ($refreshed + 1)
                    :set ($known->$key) "seen"
                  } else={ :set dup ($dup + 1) }
                }
              }
            } else={
              # 網域等非 IP 項目
              :set other ($other + 1)
            }
          }
        }
      }
      :set carry [:pick $buf $start [:len $buf]]
    }
    :do { /file remove [find name=$tmpFile] } on-error={}
  }

  :log info ("trails-import: " . $path . " -> " . $listName . " added=" . $added . " refreshed=" . $refreshed . " dup=" . $dup . " skipped(non-ip)=" . $other . " skipped(bogon)=" . $bogon . " failed=" . $failed)
}
}
