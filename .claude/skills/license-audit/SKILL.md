---
name: license-audit
description: Check whether the upstream data sources that routeros-rsc republishes (ipsum, maltrail, stamparm/trails, Emerging Threats, Spamhaus DROP, ipv64.net, RIPEstat, Route Views, internet-scanners) still allow what this repo does with them, and evaluate the license or terms of any new feed. Use this for periodic license reviews, when a feed URL breaks or moves (moves often come with relicensing), before adding a source, and whenever someone asks "can we use / redistribute X", "這個來源有沒有限制", "授權有沒有改", "可以轉發嗎", "上游改授權了嗎" or mentions a LICENSE change upstream.
---

# Upstream license audit for routeros-rsc

This repo republishes other people's data: `rsc/*.rsc` files and GitHub Releases are public feeds. Every source has to allow public redistribution, and each one may require us to keep certain notices. Upstreams do change their terms. In 2026, maltrail split its threat data into stamparm/trails under a license that forbids redistributed feeds without permission, and moved the scanner list to a new path. The old URL returned 404 for two months before anyone noticed.

The current baseline lives in `references/sources.json`: each source's redistribution status, the files that use it, obligations, and the license file SHA as of the last check. `scripts/check_upstream.py` compares the live sources against it.

## Periodic audit

1. Run the automated check from the repo root:
   ```bash
   python -I .claude/skills/license-audit/scripts/check_upstream.py
   ```
   It reports these problems:
   - a changed GitHub license file or SPDX id;
   - a feed that no longer downloads (moved or removed);
   - a feed header that no longer contains the copyright notice we are required to keep.
   It also lists the terms pages that need a human read.
2. For every `CHG` line, read the new license or terms in full. Don't stop at the summary, because restrictions often live in definitions and exceptions. The Trails license allows "internal defensive use" but defines redistribution to include free public feeds and converted formats. Decide whether this repo's use is still allowed.
3. Read each listed terms page. Compare it against the `obligations` field in `references/sources.json`.
4. Check that our outputs still meet the obligations. Look at the first lines of the affected `rsc/*.rsc` and the relevant generator in `scripts/`.
5. Update `references/sources.json`: new SHA, obligations, `redistribution` status and `last_verified` date. Update the README "Data sources and licensing" table if anything user-visible changed.
6. Report to the user in a table: source, status (unchanged / changed / broken), what changed, and the action needed. Clearly separate facts from interpretation, e.g. "the license text says X; I read that as Y". This is not legal advice, and the owner decides.

## Evaluating a new or changed source

Answer each question with a link to the exact place you found the answer:

| Question | Where to look |
|---|---|
| Is there a license? Code or data? | Repo `LICENSE*` and README "License" section; for data repos, look for a separate data license |
| Is public redistribution allowed, including free and converted feeds? | License definitions of "redistribution" and "derived"; FAQ / terms page |
| What must be preserved? | Copyright line, license text, timestamps, attribution wording; feed file header |
| Commercial-use or service-provider limits? | Relevant if users may run MSP/MSSP services with the lists |
| Rate limits / identification? | Terms pages, API docs (Spamhaus ≤1/hour; RIPEstat `sourceapp`) |
| Has it been relicensed recently? | `git log` of the license file (GitHub API `commits?path=LICENSE`), changelog, README |
| Old material under an older license? | Some licenses keep earlier versions under the old terms (Trails §8: pre-baseline material stays MIT) |

Classify the result with the same values used in `references/sources.json`:
- `allowed`: may go into `rsc/`.
- `allowed-with-notice`: may go into `rsc/`, as long as the generator preserves the notice. Verify that it does.
- `allowed-per-terms`: may be used, subject to operational conditions such as rate limits or identification.
- `internal-use-only`: must **not** go into `rsc/`, Releases or workflows. Offer an on-router download script instead, so each user fetches the data for their own network. See the `routeros-scripting` skill and `util/trails-import.rsc`.
- `unknown`: tell the user plainly. If they accept the risk, mark it "Not published" in the README.
- `not-verified`: we use the source but haven't checked its terms yet, such as Route Views. Flag it as a follow-up.

## Things that are easy to miss

- **The license covers the code, not the data.** maltrail's engine is MIT, but its Trails data is not.
- **Facts versus compilations.** Individual IP addresses are facts, but a curated list can be protected as a compilation or database. Licenses like Trails restrict the compilation, so converting the format does not get around them.
- **Linking is not redistribution.** Pointing users at the official source is usually fine; republishing it is not.
- **This repo's own MIT license** covers only its code, and `LICENSE` says so. Do not suggest relicensing the data.
- **Bot-blocked terms pages.** If a terms page returns 403 to automated fetches (ipv64.net does), say that you could not read it. Do not assume the absence of terms means permission.
