# IPsum Threat Intelligence Feed Processor

This Python utility is designed to fetch threat intelligence data from the **IPsum project** and generate optimized firewall address list configuration files (.rsc) specifically for MikroTik RouterOS.

## Features

* **Multi-Source Fetching:** Downloads IP address lists from multiple configured URLs.
* **Validation & De-duplication:** Automatically validates IP formats and removes duplicates for a cleaner list.
* **RouterOS Optimization:** Generates ready-to-use MikroTik firewall address-list commands.
* **High Performance:** Utilizes multi-threading to significantly speed up the download and processing workflow.

## MikroTik RouterOS v6 & v7 Setup

### 1. Update Script

This script handles the downloading of the blacklist and refreshes the local address list.

```routeros
/system script add name="downloadBlackList" owner="HybridNetworks" source={
    /tool fetch url="https://github.com/sinnoken/routeros-rsc/raw/refs/heads/main/rsc/STAMPARM-IPSUM-LEVEL-3.rsc" mode=https;
    :delay 5;
    /ip firewall address-list remove [find where list="STAMPARM-IPSUM-LEVEL-3"];
    :delay 5;
    /import file-name=STAMPARM-IPSUM-LEVEL-3.rsc;
    :delay 5;
    /file remove STAMPARM-IPSUM-LEVEL-3.rsc;
}

```

### 2. Automation Scheduler

Set a schedule to automatically update the blacklist every 3 days.

```routeros
/system scheduler add comment="BlackList" interval=3d \
    name="BlackListUpdate" on-event=downloadBlackList \
    start-date=jan/01/1970 start-time=10:10:10

```

### 3. Blocking with RAW Firewall Rules

For optimal performance and lower CPU usage, use [IP Firewall RAW](https://wiki.mikrotik.com/wiki/Manual:IP/Firewall/Raw) to drop traffic.

```routeros
/ip firewall raw
add action=drop chain=prerouting comment="STAMPARM-IPSUM-LEVEL-3" \
    src-address-list=STAMPARM-IPSUM-LEVEL-3

```

---

## Usage

1. **Environment:** Ensure you have **Python 3.x** and the `requests` library installed.
2. **Clone:** Download or clone this repository to your local machine.
3. **Execute:** Run the processor script:
```bash
python script_name.py

```


4. **Output:** The generated `.rsc` configuration files will be saved in the `./rsc/` directory.

## Requirements

* Python 3.x
* `requests` library

## Important Notes

* **Compatibility:** Verify that your RouterOS version supports the generated commands (compatible with most v6 and v7 builds).
* **Customization:** You can modify the `urls` list within the script to target different IPsum threat levels (e.g., level 1 to level 8).

## Contributing

Contributions are welcome! Please feel free to submit **Issue reports**, **Feature requests**, or **Pull Requests** to improve the code.
