# Leeds & York DJ search (Instagram)

Instagram blocks profile lookups from cloud servers, so the Instagram part
runs on your own computer.

## Files

- `candidates.csv` – 23 DJs whose Leeds/York base was confirmed on their
  SoundCloud or Mixcloud page (checked 2026-10-05). Instagram handles weren't
  listed on those pages; add one in `instagram_handle` if you know it.
- `ig_dj_search.py` – searches Instagram, opens each profile, checks follower
  range, DJ wording and city, and writes the table.

## Run it

1. Install Python 3 (python.org) if you don't have it.
2. Log into your spare Instagram account in Chrome, open DevTools (F12) →
   Application → Cookies → `https://www.instagram.com`, copy `sessionid`.
3. In a terminal, in this folder:
   - macOS/Linux: `export IG_SESSIONID='paste-value'`
   - Windows (cmd): `set IG_SESSIONID=paste-value`
   - then `python3 ig_dj_search.py` (Windows: `py ig_dj_search.py`)
4. It waits 20–45 s between requests, so a full run takes a few hours. Stop
   any time with Ctrl+C; progress is saved in `ig_cache.json` and the next run
   carries on. If Instagram rate-limits it, wait an hour and run again.

## Output

- `results.md` – the table (Name, @handle, City, Followers, Link, Location
  source), sorted by city then followers, plus the per-city count and date.
  Only accounts whose bio says DJ and names the city (or whose handle you put
  in `candidates.csv`) land here.
- `needs_review.csv` – accounts with a partial match (e.g. matched by name
  only, or DJ wording but no city). Open them and move real ones into
  `candidates.csv` with their handle, then re-run.

Edit the `CURRENT SEARCH` block at the top of the script to change cities,
follower range, result cap, search terms or already-found accounts.

Don't commit `ig_cache.json` or your cookie.
