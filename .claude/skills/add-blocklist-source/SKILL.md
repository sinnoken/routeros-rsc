---
name: add-blocklist-source
description: Add, replace or remove an upstream feed in the routeros-rsc blocklist pipeline (scripts/gen_blocklists.py urls_info, the other scripts/gen_*.py generators, rsc/ outputs, workflows, README tables). Covers the license check, preserving upstream notices, generating and verifying the .rsc, and documenting it. Use this whenever someone wants a new threat feed, IP list, country list, scanner list or ASN list published from this repo — e.g. "加一個 FireHOL 清單", "把 abuse.ch 的 IP 加進來", "新增一個國家", "換掉壞掉的來源", "這個 feed 可以用嗎" — and also when an existing source's URL breaks or moves.
---

# Adding a blocklist source to routeros-rsc

Every file in `rsc/` is republished data: routers around the world fetch it daily and drop traffic based on it. A new source therefore needs three things to be right: we are **allowed** to redistribute it, the conversion **does not lose or widen** coverage, and the update **never pushes an empty or broken list**. Follow the steps in order. Licensing comes first because it can make the rest pointless.

## Step 1 — License and terms (do this before writing code)

Run the `license-audit` skill's checklist for the new source, or at minimum answer these questions with links to the evidence:

1. **Can it be redistributed publicly?** "Free to use" is not the same as "free to redistribute". Look for the license file, a terms or FAQ page, and comment headers inside the feed itself.
2. **What must be kept?** Copyright lines, license text, timestamps, attribution wording.
3. **Rate limits?** For example, Spamhaus allows at most one automated download per hour.
4. **Data under a separate license from the code?** maltrail's code is MIT, but its threat data moved to stamparm/trails under a restrictive data license that forbids redistributed feeds without written permission.

Decide:
- Redistribution is clearly allowed → continue.
- Allowed for internal use only (e.g. stamparm/trails) → do **not** add it to `rsc/`, Releases or workflows. Offer an on-router script instead (see `util/trails-import.rsc` and the `routeros-scripting` skill), so each user downloads it for their own network.
- Unknown (e.g. ipv64.net publishes no terms) → tell the user. If they still want it, mark it "Not published" in the README license table.

## Step 2 — Add it to a generator

Most IP and CIDR feeds belong in `scripts/gen_blocklists.py` → `urls_info`:

```python
{
    "list_name": "provider-listname",   # upper-cased into the address-list name and the file name
    "source_url": "https://...",
    "comment": "Human readable label",  # becomes comment= on every entry
    "type": "IPv4",                     # informational; files are split by detected IP version
},
```

What the generator already does for you:
- Parses IPs and CIDRs, ignoring `#` comments.
- Aggregates with `ipaddress.collapse_addresses`, which never widens coverage.
- Writes a staging-swap `.rsc`, so the list is never empty during an update.
- Keeps the previous file if the new entry count drops below 50% (upstream outage guard).
- Copies the feed's leading comment block, the upstream notice, to the top of the `.rsc`.

Check these against the actual feed:
- **Comment style.** The header copier handles `#` and `;`. If the feed puts its copyright somewhere else, such as an HTTP header or a separate page, add the notice explicitly.
- **Line format.** If it isn't "address first, then whitespace", for example CSV or JSON, write a dedicated `scripts/gen_<name>.py` that follows the same output rules rather than bending the shared parser.
- **Dangerous filters.** Do not add filters that drop entries by prefix length. A `max_prefix` filter once silently removed about 92% of the Spamhaus DROP address space and most of the CN country list.

Name new scripts `scripts/gen_<name>.py`. Their output paths are relative to the repo root, where the workflows run.

## Step 3 — Generate and verify in a scratch directory

Never test by writing into the repo's `rsc/`. Copy the current `rsc/` into a scratchpad directory so the 50% guard has a baseline, then run from there:

```bash
mkdir -p "$SCRATCH/run/rsc" && cp rsc/*.rsc "$SCRATCH/run/rsc/"
cd "$SCRATCH/run" && PYTHONIOENCODING=utf-8 python <repo>/scripts/gen_blocklists.py
```

Then verify coverage with the bundled script, which exits with code 1 if any source network is missing:

```bash
python -I <skill-dir>/scripts/verify_coverage.py \
  --source https://feed.example/list.txt \
  --rsc "$SCRATCH/run/rsc/<LIST>.rsc" \
  [--rsc-old <repo>/rsc/<LIST>.rsc]
```

Report the numbers to the user: source networks, entries, the address count before and after, and anything missing. Also open the first 15 lines of the `.rsc` and confirm three things: the upstream notice is at the top, the staging-swap lines are present, and the list name is right.

## Step 4 — Wire it up and document it

- **Workflow.** `gen_blocklists.py` already runs in `.github/workflows/daily-blocklists.yml`. A new generator needs its own step there, or its own `daily-*` or `weekly-*` workflow if its schedule differs. Pin third-party actions to a version tag, never `@master`.
- **README "Available lists" table.** Add the file, address-list name, IP family, source link and refresh schedule.
- **README "Data sources and licensing" table.** Add the license or terms link and what we do to comply.
- **README update script example.** Change it only if the new file behaves differently from the existing self-replacing ones.

## Step 5 — Replacing or removing a source

- **The upstream URL moved** (e.g. maltrail moved to `data/`): update the URL, re-run Step 3, and check the license again at the new location. A move is often part of a relicensing.
- **Removing a list.** Routers keep fetching the old URL. Prefer leaving a final `.rsc` that removes the list, or announce the removal in the README, instead of deleting the file silently.
- **Never rename an existing `rsc/` file.**
