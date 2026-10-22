# routeros-rsc

Ready-to-import MikroTik RouterOS firewall address lists (`.rsc`), built from public threat-intelligence and scanner feeds and refreshed automatically by GitHub Actions.

Point your router at a raw file URL, import it on a schedule, and drop the matching traffic in `/ip firewall raw`.

## Available lists

All generated files live in [`rsc/`](rsc/). Raw download URL pattern:

```
https://github.com/sinnoken/routeros-rsc/raw/refs/heads/main/rsc/<FILE>.rsc
```

| File(s) | Address list name | Family | Source | Refresh |
|---|---|---|---|---|
| `STAMPARM-IPSUM-LEVEL-{1..8}.rsc` | `STAMPARM-IPSUM-LEVEL-{N}` | IPv4 | [stamparm/ipsum](https://github.com/stamparm/ipsum) | daily |
| `ipsum-Level{1..8}.rsc` | `HN-BLACKLIST-IPSUM-L{N}` | IPv4 | [stamparm/ipsum](https://github.com/stamparm/ipsum) (**deprecated**, use `STAMPARM-IPSUM-LEVEL-*`) | daily |
| `IPV64.NET-IPV64_BLOCKLIST_V4_{CN,JP,KR,TW}.rsc` | same as file name | IPv4 | [ipv64.net](https://ipv64.net/) country lists | daily |
| `IPV64.NET-IPV64_BLOCKLIST_V6_{CN,JP,KR,TW}.rsc` | same as file name | IPv6 | [ipv64.net](https://ipv64.net/) country lists | daily |
| `IPV64.NET-TOREXITNODES.rsc` | `IPV64.NET-TOREXITNODES` | IPv4 | ipv64.net Tor exit nodes | daily |
| `EMERGINGTHREATS-BLOCK-IPS.rsc` | `EMERGINGTHREATS-BLOCK-IPS` | IPv4 | [Emerging Threats](https://rules.emergingthreats.net/fwrules/) | daily |
| `HN-BLACKLIST-SPAMHAUS.rsc` | `HN-BLACKLIST-SPAMHAUS` | IPv4 | [Spamhaus DROP](https://www.spamhaus.org/drop/) | daily |
| `SPAMHAUS-DROPV6.rsc` | `SPAMHAUS-DROPV6` | IPv6 | Spamhaus DROPv6 | daily |
| `mikrotik_as_lists.rsc` | `AS<number>` (default `AS45102`) | IPv4 + IPv6 | [RIPEstat](https://stat.ripe.net/) announced prefixes | daily |
| `internet-scanners.rsc` | `internet-scanners` | IPv4 + IPv6 | [OpenFilters/internet-scanners](https://github.com/OpenFilters/internet-scanners) | daily |
| `mass_scanner.rsc` | `MALTRAIL-SCANNER` | IPv4 | [stamparm/maltrail](https://github.com/stamparm/maltrail) + local list | weekly (Mon) |
| `mass_scanner_v6.rsc` | `MALTRAIL-SCANNER-V6` | IPv6 | [stamparm/maltrail](https://github.com/stamparm/maltrail) + local list | weekly (Mon) |

Notes:

- **IPsum levels.** The level is the number of independent blacklists an IP appears on. Higher levels mean fewer entries and fewer false positives. Level 3 is a common starting point.
- **Self-replacing lists.** Every file except the deprecated `ipsum-Level*.rsc` replaces its own list when imported, so do not remove the list yourself first.
  - The `STAMPARM-*`, `IPV64.NET-*`, `EMERGINGTHREATS-*` and `*SPAMHAUS*` files import into `<LIST>-STAGING`, then swap it in for `<LIST>`. The live list stays populated while the import runs. For a short time the router holds both copies, so it needs memory for twice the list.
  - `internet-scanners.rsc`, `mass_scanner*.rsc` and `mikrotik_as_lists.rsc` remove the old list first, then re-add every entry.
  - The deprecated `ipsum-Level*.rsc` files only contain `add` commands.
- **Upstream outage protection.** If a feed returns fewer than half the entries of the previous run, the generator keeps the previous file. This stops a broken upstream from pushing an empty list to routers.
- Every successful daily run also publishes all `rsc/*.rsc` files as a GitHub Release. Only the latest two releases are kept.

## Using a list on RouterOS (v6 / v7)

The example uses `STAMPARM-IPSUM-LEVEL-3`. Substitute any file and list name from the table above. For IPv6 lists, use `/ipv6 firewall address-list` and `/ipv6 firewall raw`.

### 1. Update script

```routeros
/system script add name="downloadBlackList" source={
    /tool fetch url="https://github.com/sinnoken/routeros-rsc/raw/refs/heads/main/rsc/STAMPARM-IPSUM-LEVEL-3.rsc" mode=https;
    :delay 5;
    /import file-name=STAMPARM-IPSUM-LEVEL-3.rsc;
    :delay 5;
    /file remove STAMPARM-IPSUM-LEVEL-3.rsc;
}
```

The file replaces the list by itself, so the script does not remove the old list first. The deprecated `ipsum-Level*.rsc` files are the exception: add `/ip firewall address-list remove [find where list="HN-BLACKLIST-IPSUM-L3"];` before the `/import` line.

### 2. Scheduler

```routeros
/system scheduler add name="BlackListUpdate" comment="BlackList" interval=3d \
    on-event=downloadBlackList start-date=jan/01/1970 start-time=10:10:10
```

### 3. Drop traffic with RAW rules

[RAW](https://help.mikrotik.com/docs/display/ROS/Firewall) rules run before connection tracking. That makes them the cheapest place to drop large blocklists.

```routeros
/ip firewall raw
add action=drop chain=prerouting comment="STAMPARM-IPSUM-LEVEL-3" \
    src-address-list=STAMPARM-IPSUM-LEVEL-3
```

> Large lists, especially IPsum level 1 or 2 with tens of thousands of entries, use noticeable RAM and take a while to import on small devices. Check free memory before choosing a low level.

## Generator scripts

Each list is produced by a Python script in the repository root. The scripts need Python 3.9+.

```bash
pip install -r requirements.txt   # requests
pip install pyasn                 # only for the ASN / BGP scripts
```

| Script | Produces | Usage |
|---|---|---|
| `ros-blocklist-gen.py` | `STAMPARM-IPSUM-*`, `IPV64.NET-*`, `EMERGINGTHREATS-*`, `*SPAMHAUS*` | `python ros-blocklist-gen.py` (sources are configured in `urls_info`) |
| `ipsum-convert_to_routeros.py` | `ipsum-Level{1..8}.rsc` (deprecated) | `python ipsum-convert_to_routeros.py` |
| `ros-asn-addresslist-gen.py` | `mikrotik_as_lists.rsc` | `python ros-asn-addresslist-gen.py AS45102 AS14061` |
| `ros-internet-scanners-gen.py` | `internet-scanners.rsc` | `python ros-internet-scanners-gen.py --collapse --output rsc/internet-scanners.rsc` (clones upstream automatically, or pass `--source-dir`; `--include-inactive` also adds retired ranges) |
| `mass_scanner-extractor.py` | `mass_scanner.rsc`, `mass_scanner_v6.rsc` (written to the current directory) | `python mass_scanner-extractor.py` (see `--help`; extra ranges go in `LOCAL_LIST_DATA`) |
| `asn-prefix-extractor.py` | `asn/asn_<ASN>_prefixes.txt` | `python asn-prefix-extractor.py 45102` (downloads a full BGP RIB via pyasn) |
| `build_bgp_sqlite.py` | `bgp.sqlite` (tables `bgp(asn, prefix)` and `as_info(asn, name)`) | `python build_bgp_sqlite.py` |

The generators keep only global unicast addresses and drop private, reserved and multicast ranges. Where the script supports it, they also merge adjacent prefixes so the router has fewer entries to hold. Merging only combines addresses already in the feed, so it never widens what gets blocked.

## Automation

| Workflow | Schedule (UTC) | What it does |
|---|---|---|
| `run_ipsum-Level3-convert_to_routeros.yml` | daily 02:00 | Runs the IPsum, blocklist and ASN generators, commits, sends a Telegram notification and creates a release. When run manually it accepts a `custom_asns` input. |
| `run_internet-scanners.yml` | daily 03:00 | Regenerates `internet-scanners.rsc` and commits only if it changed |
| `run_cidr-mass_scanner-extractor.yml` | Mondays 00:00 | Regenerates the Maltrail scanner lists |
| `run_asn-prefix-extractor.yml` | manual | Rebuilds `asn/asn_45102_prefixes.txt` and the BGP SQLite database |
| `run_test.yml` | manual | Runs `ros-blocklist-gen.py` alone |

The Telegram step needs the `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` repository secrets.

## RouterOS utilities

[`util/`](util/) holds snippets for running on the router itself. They are not part of the generated lists.

- `regex.rsc`: examples of filtering `address-list` entries by list-name regex, timeout and empty comment, then printing the address and comment.
- `diff.rsc`: keeps a BGP connection's `local.address` in sync with the current PPPoE IP held in an address list. It also contains a scratch list of upstream scanner URLs.

## Repository layout

```
rsc/        generated RouterOS address lists (import these)
asn/        plain-text prefix dumps per ASN
util/       on-router helper snippets
experiments/ side scripts, not used by the workflows
*.py        list generators (see above)
.github/    scheduled GitHub Actions workflows
```

[`experiments/`](experiments/) holds side scripts that are not part of the list pipeline.

## Credits

The data comes from the upstream projects linked above. Their licenses and terms of use apply, including Spamhaus DROP usage terms. This repository only reformats their data for RouterOS.

## Contributing

Issues and pull requests are welcome: new feeds, format fixes, or RouterOS compatibility reports.
