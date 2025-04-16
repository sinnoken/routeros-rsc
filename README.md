# IPsum Threat Intelligence Feed Processor

這個 Python 程式用於從 IPsum 項目中下載威脅情報資料，並生成適用於 RouterOS 的防火牆地址列表配置文件。

## 功能

- 從多個 URL 下載 IP 地址清單。
- 驗證並去重 IP 地址。
- 生成 RouterOS 防火牆地址列表的配置指令。
- 支援多線程處理以加速下載和處理過程。

## Mikrotik RouterOS v6 & v7

1. Script which will download the drop list and update

```
/system script add name="downloadBlackList" owner="HybridNetworks" source={
    /tool fetch url="https://github.com/sinnoken/routeros-rsc/raw/refs/heads/main/rsc/STAMPARM-IPSUM-LEVEL-3.rsc" mode=https;
    :delay 5;
    /ip firewall address-list remove [find where list="STAMPARM-IPSUM-LEVEL-3"];
    :delay 5;
    /import file-name=HN-BLACKLIST-SPAMHAUS.rsc;
    :delay 5;
    /file remove HN-BLACKLIST-SPAMHAUS.rsc;
}
```

2. Schedule the download and application of the blacklist

```
/system scheduler add comment="BlackList" interval=3d \
    name="BlackListUpdate" on-event=downloadBlackListBox \
    start-date=jan/01/1970 start-time=10:10:10
```

3. Blacklist blocking by [RAW](https://wiki.mikrotik.com/wiki/Manual:IP/Firewall/Raw) firewall rules

```
/ip firewall raw
add action=drop chain=prerouting comment="STAMPARM-IPSUM-LEVEL-3" \
    src-address-list=STAMPARM-IPSUM-LEVEL-3
```


## 使用方法

1. 確保已安裝 Python 3.x 和 `requests` 套件。
2. 將程式碼克隆或下載到本地。
3. 執行程式：

   ```bash
   python script_name.py

4. 生成的 .rsc 配置文件將儲存在 ./rsc/ 目錄中。

## 需求

- Python 3.x
- requests 套件

## 注意事項

- 請確保目標設備的 RouterOS 版本支援生成的配置指令。
- 根據需要調整 urls 列表以匹配不同的威脅情報等級。

## 貢獻

歡迎提交問題報告和功能請求，或通過提交 Pull Request 來貢獻代碼。
