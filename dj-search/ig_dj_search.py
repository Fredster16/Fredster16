#!/usr/bin/env python3
"""Find Instagram DJ accounts in given cities within a follower range.

Run on your own computer (home connection), logged into Instagram via a
session cookie in the IG_SESSIONID environment variable. Python 3.8+, no
extra packages needed.

    export IG_SESSIONID='...'        # macOS/Linux
    set IG_SESSIONID=...             # Windows cmd
    python3 ig_dj_search.py

It reads only public profile data. It never follows, likes or messages anyone.
Requests are paced slowly; progress is cached in ig_cache.json so you can stop
(Ctrl+C) and re-run to continue.
"""
import csv
import datetime
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# ---- CURRENT SEARCH (edit each run) ----------------------------------------
CITIES = {
    # city -> words that count as "based in" that city (metro area towns)
    "Leeds": ["leeds", "lds", "headingley", "chapel allerton", "kirkstall",
              "horsforth", "pudsey", "morley", "otley", "wetherby",
              "garforth", "rothwell", "lofthouse", "yeadon", "guiseley"],
    "York": ["york", "yorks uni", "uni of york", "acomb", "haxby"],
}
MIN_FOLLOWERS = 1_000
MAX_FOLLOWERS = 30_000
MAX_RESULTS = 200
ALREADY_FOUND = set()  # e.g. {"somehandle", "otherhandle"}
SEARCH_QUERIES = [
    "dj leeds", "leeds dj", "leeds techno", "leeds house music dj",
    "leeds drum and bass dj", "leeds garage dj", "leeds dj producer",
    "dj york", "york dj", "york uk dj", "york techno", "york house dj",
    "york drum and bass",
]
# -----------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
CANDIDATES_CSV = os.path.join(HERE, "candidates.csv")
CACHE = os.path.join(HERE, "ig_cache.json")
OUT_MD = os.path.join(HERE, "results.md")
OUT_REVIEW = os.path.join(HERE, "needs_review.csv")

DJ_WORDS = re.compile(r"\bdj\b|\bdjs\b|\bdj'?ing\b|dj set|selector|\bb2b\b|"
                      r"resident\b|residency|on the decks|bookings|mixes",
                      re.I)
NOT_DJ = re.compile(r"\bvenue\b|\bclub\b(?! night)|\bbar\b|\brecords\b|"
                    r"\blabel\b|\bpromotions?\b|\bpresents\b|\bevents\b|"
                    r"\bcollective\b|\bfan ?page\b|\bagency\b|\bhire\b|"
                    r"\bweddings?\b", re.I)
BIZ_CATEGORIES = re.compile(r"night ?club|venue|bar|record label|"
                            r"event planner|promoter|agency", re.I)

session_id = os.environ.get("IG_SESSIONID", "").strip()
if not session_id:
    sys.exit("Set the IG_SESSIONID environment variable first.")

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/130 Safari/537.36"),
    "x-ig-app-id": "936619743392459",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "en-GB,en;q=0.9",
    "Cookie": f"sessionid={session_id}",
}


class RateLimited(Exception):
    pass


def fetch_json(url, referer="https://www.instagram.com/"):
    req = urllib.request.Request(url, headers={**HEADERS, "Referer": referer})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 429):
            raise RateLimited(f"HTTP {e.code}")
        if e.code == 404:
            return None
        raise
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        if "login" in body[:3000].lower():
            raise RateLimited("redirected to login - cookie expired?")
        return None


def pause():
    time.sleep(random.uniform(20, 45))


def load_cache():
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    return {"queries": {}, "profiles": {}}


def save_cache(c):
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=1)


def search(query):
    q = urllib.parse.quote(query)
    for url in (
        f"https://www.instagram.com/web/search/topsearch/?context=blended&query={q}",
        f"https://www.instagram.com/api/v1/web/search/topsearch/?context=blended&query={q}",
    ):
        data = fetch_json(url)
        if data and "users" in data:
            return [u["user"]["username"] for u in data["users"]]
    return []


def profile(username):
    data = fetch_json(
        "https://www.instagram.com/api/v1/users/web_profile_info/?username="
        + urllib.parse.quote(username),
        referer=f"https://www.instagram.com/{username}/",
    )
    u = (data or {}).get("data", {}).get("user")
    if not u:
        return None
    links = [l.get("url", "") for l in (u.get("bio_links") or [])]
    return {
        "username": u["username"],
        "full_name": u.get("full_name") or "",
        "bio": u.get("biography") or "",
        "followers": u["edge_followed_by"]["count"],
        "category": u.get("category_name") or u.get("business_category_name") or "",
        "external_url": u.get("external_url") or "",
        "links": links,
        "checked": datetime.date.today().isoformat(),
    }


def city_of(p, hint=None):
    text = " ".join([p["bio"], p["full_name"], p["category"]]).lower()
    found = [c for c, words in CITIES.items()
             if any(re.search(rf"\b{re.escape(w)}\b", text) for w in words)]
    # "york" inside "new york" doesn't count
    if "York" in found and not re.search(r"(?<!new )\byork\b", text):
        found.remove("York")
    if found:
        return found[0], "Instagram bio"
    if hint:
        return hint  # (city, source) from candidates.csv
    return None, None


def classify(p, hint=None):
    """Return (status, city, source). status: include / review / skip."""
    if p["username"].lower() in ALREADY_FOUND:
        return "skip", None, "already found"
    if not MIN_FOLLOWERS <= p["followers"] <= MAX_FOLLOWERS:
        return "skip", None, "followers out of range"
    city, source = city_of(p, hint)
    text = f'{p["full_name"]} {p["bio"]}'
    is_dj = bool(DJ_WORDS.search(text)) or (hint is not None)
    looks_org = bool(NOT_DJ.search(text) or BIZ_CATEGORIES.search(p["category"]))
    if city and is_dj and not looks_org:
        return "include", city, source
    if city or is_dj:
        return "review", city, source or ""
    return "skip", None, "no DJ/city signal"


def main():
    cache = load_cache()
    hints = {}  # username -> (city, source)
    name_queries = []
    with open(CANDIDATES_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            h = row["instagram_handle"].strip().lstrip("@")
            src = f'{row["location_source"]} ({row["source_url"]})'
            if h:
                hints[h.lower()] = (row["city"], src)
            else:
                name_queries.append((row["name"], row["city"], src))

    try:
        # 1. Platform search: generic queries + candidate names
        for q in SEARCH_QUERIES + [n for n, _, _ in name_queries]:
            if q in cache["queries"]:
                continue
            print(f"search: {q}")
            cache["queries"][q] = search(q)
            save_cache(cache)
            pause()
        # Candidate-name searches: top 3 hits inherit the candidate's city as a
        # hint, but still need DJ wording or manual review to be included.
        for n, city, src in name_queries:
            for h in cache["queries"].get(n, [])[:3]:
                hints.setdefault(h.lower(), (city, src + " - matched by name, verify"))

        usernames = list(dict.fromkeys(
            [h for h in hints] +
            [u.lower() for q in SEARCH_QUERIES for u in cache["queries"].get(q, [])]))

        # 2. Open each profile
        for u in usernames:
            if u in cache["profiles"]:
                continue
            print(f"profile: {u}")
            cache["profiles"][u] = profile(u)
            save_cache(cache)
            pause()
    except RateLimited as e:
        print(f"\nInstagram stopped answering ({e}). Progress saved - wait an "
              "hour or two and run again. If it keeps happening, refresh the "
              "IG_SESSIONID cookie.")
    except KeyboardInterrupt:
        print("\nStopped. Progress saved; run again to continue.")

    # 3. Build output from everything checked so far
    include, review = [], []
    for u, p in cache["profiles"].items():
        if not p:
            continue
        hint = hints.get(u)
        status, city, source = classify(p, hint)
        row = {**p, "city": city or "", "source": source}
        if status == "include" and not source.endswith("verify"):
            include.append(row)
        elif status in ("include", "review"):
            review.append(row)

    include.sort(key=lambda r: (r["city"], -r["followers"]))
    include = include[:MAX_RESULTS]
    today = datetime.date.today().isoformat()
    lines = ["| Name | @handle | City | Followers | Link | Location source |",
             "|---|---|---|---|---|---|"]
    for r in include:
        name = (r["full_name"] or r["username"]).replace("|", "/")
        lines.append(f'| {name} | @{r["username"]} | {r["city"]} | '
                     f'{r["followers"]:,} | https://www.instagram.com/{r["username"]}/ | '
                     f'{r["source"]} |')
    counts = ", ".join(f"{c}: {sum(r['city'] == c for r in include)}" for c in CITIES)
    dates = sorted({r["checked"] for r in include}) or [today]
    lines += ["", f"Accounts found per city - {counts}. Follower counts checked "
              f"{dates[0]}" + (f" to {dates[-1]}" if dates[-1] != dates[0] else "") + "."]
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    with open(OUT_REVIEW, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["username", "full_name", "followers", "city_guess",
                    "source", "category", "bio", "link"])
        for r in sorted(review, key=lambda r: -r["followers"]):
            w.writerow([r["username"], r["full_name"], r["followers"], r["city"],
                        r["source"], r["category"], r["bio"].replace("\n", " "),
                        f'https://www.instagram.com/{r["username"]}/'])

    print(f"\n{len(include)} confirmed -> {OUT_MD}")
    print(f"{len(review)} need a manual look -> {OUT_REVIEW}")


if __name__ == "__main__":
    main()
