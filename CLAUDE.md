# routeros-rsc

Generates MikroTik RouterOS firewall address lists (`rsc/*.rsc`) from public threat and scanner feeds. GitHub Actions refreshes them on a schedule, and routers fetch the raw URLs and `/import` them. See README.md for the list catalogue, sources and licensing.

## Layout

- `scripts/`: Python generators (`gen_*.py`, `extract_*.py`, `build_*.py`). Run them from the repo root, because output paths such as `rsc/` are relative.
- `rsc/`: generated lists. These are public; routers fetch them by URL.
- `util/`: snippets that run on the router itself, e.g. `trails-import.rsc`.
- `.github/workflows/`: named by schedule (`daily-*`, `weekly-*`, `manual-*`).
- `.claude/skills/`: `add-blocklist-source` and `license-audit`, the repo-specific procedures.

## Rules that always apply

- **Never rename or delete a file in `rsc/`.** Every file name is a URL that routers fetch on a schedule. A rename makes them fail silently.
- **A list must never be empty, even during an update.** Keep the existing protections:
  - staging-swap output in `gen_blocklists.py`;
  - the 50% shrink guard;
  - no `remove` line for a source that failed to download;
  - timeout refresh in on-router scripts. Timeout entries are dynamic and a reboot clears them, so those scripts also need a `start-time=startup` scheduler entry that waits for the default route.
- **Never drop entries to "simplify" a list.** `ipaddress.collapse_addresses` is fine. Filtering by prefix length once removed about 92% of Spamhaus DROP.
- **Check the license before adding or changing a source.** Use the `license-audit` skill. Keep the upstream copyright, license and timestamp lines at the top of generated files.
- **stamparm/trails data is internal-use only.** It must never appear in `rsc/`, Releases or workflows; only `util/trails-import.rsc` downloads it on the user's own router.
- **Don't copy MikroTik manual text into this repo.** Link to pages on https://manual.mikrotik.com instead.
- **Pin third-party GitHub Actions to a version tag**, never `@master` or `@main`.

## Testing

- Never test by writing into the repo's `rsc/`. Copy `rsc/` to a scratch directory, run the generator there, and check coverage with `.claude/skills/add-blocklist-source/scripts/verify_coverage.py`.
- RouterOS scripts can't run here. Check their logic with a small Python port, and give the user an on-device test plan: `/import ... dry-run`, a CHR or test router, and `action=log` before `drop`.

## RouterOS references

Read the official manual for RouterOS syntax; don't rely on memory. Start from the index at https://manual.mikrotik.com/llms.txt, and append `.md` to any `/docs/...` page URL. Versioned pages live under `/docs/<version>/`.

If they are available, the account-level skills `routeros-manual` (manual lookup) and `routeros-scripting` (RouterOS script lessons) cover this. They are installed on the owner's claude.ai account, synced to Claude Code, and not stored in this repo. Without them, use the manual index above directly.

## Conventions

- Python and RouterOS comments are in Traditional Chinese, matching the existing code. README.md and commit messages are in English.
- Automated commits use `chore(lists): …` and `chore(asn): …`. Manual commits use conventional prefixes (`fix:`, `docs:`, `ci:`, `refactor:`, `chore:`).
