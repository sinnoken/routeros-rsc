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

Each list is produced by a Python script in [`scripts/`](scripts/). Run them from the repository root, because output paths such as `rsc/` are relative to the current directory. The scripts need Python 3.9+.

```bash
pip install -r requirements.txt   # requests
pip install pyasn                 # only for the ASN / BGP scripts
```

| Script | Produces | Usage |
|---|---|---|
| `gen_blocklists.py` | `STAMPARM-IPSUM-*`, `IPV64.NET-*`, `EMERGINGTHREATS-*`, `*SPAMHAUS*` | `python scripts/gen_blocklists.py` (sources are configured in `urls_info`) |
| `gen_ipsum_legacy.py` | `ipsum-Level{1..8}.rsc` (deprecated) | `python scripts/gen_ipsum_legacy.py` |
| `gen_asn_addresslist.py` | `mikrotik_as_lists.rsc` | `python scripts/gen_asn_addresslist.py AS45102 AS14061` (an ASN that fails to fetch is skipped and keeps its existing list on the router) |
| `gen_internet_scanners.py` | `internet-scanners.rsc` | `python scripts/gen_internet_scanners.py --collapse --output rsc/internet-scanners.rsc` (clones upstream automatically, or pass `--source-dir`; `--include-inactive` also adds retired ranges) |
| `gen_mass_scanner.py` | `mass_scanner.rsc`, `mass_scanner_v6.rsc` | `python scripts/gen_mass_scanner.py --output-v4 rsc/mass_scanner.rsc --output-v6 rsc/mass_scanner_v6.rsc` (see `--help`; extra ranges go in `LOCAL_LIST_DATA`) |
| `extract_asn_prefixes.py` | `asn/asn_<ASN>_prefixes.txt` | `python scripts/extract_asn_prefixes.py 45102` (downloads a full BGP RIB via pyasn) |
| `build_bgp_sqlite.py` | `util/bgp.sqlite` (tables `bgp(asn, prefix)` and `as_info(asn, name)`) | `python scripts/build_bgp_sqlite.py` |

The generators keep only global unicast addresses and drop private, reserved and multicast ranges. Where the script supports it, they also merge adjacent prefixes so the router has fewer entries to hold. Merging only combines addresses already in the feed, so it never widens what gets blocked.

## Automation

Workflow file names start with their schedule. Every scheduled workflow can also be started by hand from the Actions tab.

| Workflow | Schedule (UTC) | What it does |
|---|---|---|
| `daily-blocklists.yml` | daily 02:00 | Runs the IPsum, blocklist and ASN generators, commits, sends a Telegram notification and creates a release. When run manually it accepts a `custom_asns` input. |
| `daily-internet-scanners.yml` | daily 03:00 | Regenerates `internet-scanners.rsc` and commits only if it changed |
| `weekly-mass-scanner.yml` | Mondays 00:00 | Regenerates the Maltrail scanner lists |
| `manual-bgp-database.yml` | manual | Rebuilds `asn/asn_45102_prefixes.txt` and the BGP SQLite database |

Automated commits use the message format `chore(lists): …` for address lists and `chore(asn): …` for BGP data.

The Telegram step needs the `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` repository secrets.

## RouterOS utilities

[`util/`](util/) holds snippets for running on the router itself. They are not part of the generated lists.

- `regex.rsc`: examples of filtering `address-list` entries by list-name regex, timeout and empty comment, then printing the address and comment.
- `diff.rsc`: keeps a BGP connection's `local.address` in sync with the current PPPoE IP held in an address list. The upstream scanner URLs at the end are commented out for reference.

## Repository layout

```
rsc/          generated RouterOS address lists (import these)
asn/          plain-text prefix dumps per ASN
scripts/      list generators (see above)
util/         on-router helper snippets and the BGP SQLite database
experiments/  side scripts, not used by the workflows
.github/      scheduled GitHub Actions workflows
```

[`experiments/`](experiments/) holds side scripts that are not part of the list pipeline.

## Data sources and licensing

The code in this repository (scripts, workflows, RouterOS snippets) is licensed under the [MIT License](LICENSE).

The generated lists in `rsc/` and `asn/` are not covered by that license. They are reformatted third-party data and remain under each provider's own license or terms. Each generated file keeps the upstream copyright and license notice in its header where the provider requires it.

| Source | License / terms | Notes |
|---|---|---|
| [stamparm/ipsum](https://github.com/stamparm/ipsum) | [The Unlicense](https://github.com/stamparm/ipsum) | Public domain |
| [OpenFilters/internet-scanners](https://github.com/OpenFilters/internet-scanners) | [The Unlicense](https://github.com/OpenFilters/internet-scanners) | Public domain |
| [stamparm/maltrail](https://github.com/stamparm/maltrail) `data/mass_scanner.txt` | [MIT](https://github.com/stamparm/maltrail/blob/master/LICENSE) | MIT notice is included in `mass_scanner*.rsc`. This repo does **not** use [stamparm/trails](https://github.com/stamparm/trails), which has a separate, more restrictive [data license](https://github.com/stamparm/trails/blob/main/LICENSE.md). |
| [Emerging Threats](https://rules.emergingthreats.net/fwrules/) | BSD-style (in the source file header) | Copyright notice, conditions and disclaimer are kept in the `.rsc` header |
| [Spamhaus DROP](https://www.spamhaus.org/drop/) | [DROP Terms of Use](https://www.spamhaus.org/drop/terms/) | Redistributed per the [DROP FAQ](https://www.spamhaus.com/faqs/drop/): Spamhaus is named as the source, and its copyright line and timestamps are kept. Fetched at most once per hour, as Spamhaus requires. |
| [ipv64.net](https://ipv64.net/) | Not published | No license or terms could be found. Check with ipv64.net before redistributing these lists further. |
| [RIPEstat](https://stat.ripe.net/) | [RIPEstat Service Terms](https://www.ripe.net/about-us/legal/ripestat-service-terms-and-conditions/) | Requests identify themselves with `sourceapp=sinnoken-routeros-rsc` |
| [University of Oregon Route Views](https://www.routeviews.org/) | Not verified | BGP RIB snapshots downloaded by [pyasn](https://github.com/hadiasghari/pyasn) (MIT) for `asn/` and `util/bgp.sqlite` |
| [CIDR Report](https://www.cidr-report.org/) | Not verified | AS names in `util/bgp.sqlite`, downloaded by pyasn |

These lists are provided as is, with no warranty. Review them before using them to drop production traffic.

## Contributing

Issues and pull requests are welcome: new feeds, format fixes, or RouterOS compatibility reports.
