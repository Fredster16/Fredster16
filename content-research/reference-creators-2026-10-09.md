# Reference creator research (scraped 9 Oct 2026)

Step 1 research for the Deira Clo scripts. Accounts: @official_dt_trading, @landenlevine, @lukeproof, @foadster.
Every video scored by **outlier score = views ÷ that account's median views on that platform**. All 284 scraped videos with scores are in `outliers-2026-10-09.csv`.

## Coverage and gaps

| Account | TikTok | Instagram | Used for ranking |
|---|---|---|---|
| Devin Turer | @official_dt_trading, 50 videos, 26 Jul–29 Sep, median 840.5 views | @official_dt_trading, 50 reels, 4 Aug–5 Oct, median 3,023 | both |
| Landen Levine | **@landenlevine1** (the @landenlevine handle is an empty 54-follower account), 50 videos, 21 Jul–8 Oct, median 496,650 | @landenlevine, 50 reels, 30 Jul–8 Oct, median 254,878 | both |
| Luke (lukeproof) | **none found.** @lukeproof on TikTok is a private 4-follower account; a name search found no match | @lukeproof, 35 reels returned (asked for 50), 7 Nov 2025–8 Oct 2026, median 2,475,696 | Instagram only |
| Will Fode (foadster) | @foadsterr exists but has 5 videos, too few for a median | @foadster, 49 reels, 6 Mar–3 Oct, median 175,464 | Instagram only |

Missing or changed:
- **Instagram shares and saves:** the reel scraper didn't return share counts for individual reels, so shares and saves are TikTok-only.
- **Transcripts:** TikTok's own subtitles were available for 9 of the selected videos. All 35 files were also transcribed locally with Whisper (small.en for the full video, medium.en for the opening 15s), and hooks were checked across all three sources. Lines spoken over music are lower confidence. `[brackets]` mark words the speech models couldn't agree on.
- 4 Instagram files (P2, P6, F1, F2) downloaded as video only. The separate audio track was fetched and muxed back in.
- **Excluded:** Landen's Hot Pockets paid partnership ([TikTok, 14.3M, 28.8×](https://www.tiktok.com/@landenlevine1/video/7668420533544815902)). It's a paid ad and the views are likely boosted.
- **Duplicates:** Luke's guitar video [P3](https://www.instagram.com/p/DaQOLIlx1Jz/) (1 Jul) is the same edit as [his 15 Feb upload](https://www.instagram.com/p/DUyTT4gjSPB/) (7.74M, 3.13×). It counts once, and the next distinct video (P8) moved up. Cross-posts are scored on whichever platform did better, and the other link is noted.
- **Cuts** were measured with ffmpeg scene-change detection at two thresholds. 0.3 misses same-angle jump cuts, and 0.15 counts fast camera moves as cuts, so the true figure sits between the two. I spot-checked by eye: Landen 10–16s of [L4](https://www.tiktok.com/@landenlevine1/video/7673966554962267423) has 8 shots in 6s, and Luke 60–66s of [P2](https://www.instagram.com/p/DXkFxLPAsR_/) is one held shot.
- **Re-hook timestamps** are my reading of the transcripts. I didn't measure them by machine.
- Apify spend: $1.05 of the $5 monthly allowance.

---

## 1. Devin Turer (@official_dt_trading), ~10.7k IG followers

| # | Video | Date | Len | Views | × median | First spoken line | On-screen text, 0–3s | Hook type | Words |
|---|---|---|---|---|---|---|---|---|---|
| D1 | [IG](https://www.instagram.com/p/DdZpD0UxjNZ/) | 17 Sep | 39s | 2,223,200 | 735× | "Eight hours of straight meditation." | "Day 1 of proving YOU can do anything" + word-by-word captions; laptop countdown in shot | challenge | 5 |
| D2 | [IG](https://www.instagram.com/p/DdR8sFvNF77/) ([TT](https://www.tiktok.com/@official_dt_trading/video/7685487058596449549) 143×, 257 shares) | 14 Sep | 28s | 2,056,531 | 680× | "Staring at a wall for 25 minutes and then studying for 8 hours straight." | "Day 2 of proving YOU can do anything" | challenge | 14 |
| D3 | [IG](https://www.instagram.com/p/Dc1yIbmsUuo/) | 3 Sep | 7s | 615,684 | 204× | none (trending song) | "when you registered for classes 0.1 seconds late so your stuck with Testicle Theory 101 at 2:15 am" | relatable meme | – |
| D4 | [TT](https://www.tiktok.com/@official_dt_trading/video/7670368117901561102) (IG 0.21×) | 5 Aug | 15s | 133,800 | 159× | none (music) | "Day 41 / Togi's $100k fitness challenge", physique | result-first (visual) | – |
| D5 | [IG](https://www.instagram.com/p/Dc66pYqvHV5/) | 5 Sep | 41s | 460,472 | 152× | "Boys, eight hours of straight meditation." | word captions only; laptop timer 08:00:00 | challenge | 6 |
| D6 | [IG](https://www.instagram.com/p/Dd4AdWqR961/) | 29 Sep | 23s | 38,446 | 12.7× | "Reading [Can't Hurt Me] in one sitting." | "Day 3 of proving YOU can do anything"; stopwatch 00:00.00 | challenge | 5 |
| D7 | [IG](https://www.instagram.com/p/DcxHSRlOAdc/) | 2 Sep | 28s | 36,377 | 12.0× | none (music) | "Togi's $100k fitness challenge / ANABOLIC transition incoming!" + arrow | curiosity gap (text) | – |
| D8 | [IG](https://www.instagram.com/p/DcuQdUFPN7g/) | 31 Aug | 17s | 33,295 | 11.0× | none (film-dialogue audio) | "Reading the ratemyprofessor reviews for the only professor that fits in my schedule" | relatable meme | – |

**Pacing.** Median outlier length is 25.7s. He speaks in 4 of 8 videos, at 0.64 words/sec across the talking ones. Cuts per 10s run 1.3 (0.3 threshold) to 3.2 (0.15), with an average shot of 2.7–5.6s. There's no spoken re-hook between the hook and the payoff. A countdown or stopwatch is in nearly every montage shot ([D2](https://www.instagram.com/p/DdR8sFvNF77/) puts a full-screen overlay through 05:54:27 → 03:16:55 → 00:39:23), so the number moving does the re-hooking.

**Structure** ([D1](https://www.instagram.com/p/DdZpD0UxjNZ/), 39s): 0–4 hook and series overlay → 4–25 silent timer montage (5:21:06, 2:40:32…) → ~25 turn "Anything is possible" → 30–35 payoff "this is the hardest thing I've ever done… I've reached enlightenment" (77%) → 36–39 "Drop a follow for day two. Let's go." with a picture-in-picture of the Day 2 video. The loop opens with the timer at 0s and closes when it runs out.
[D2](https://www.instagram.com/p/DdR8sFvNF77/) (28s): 0–6 hook → 6–24 countdown montage → 24–28 "pitch black outside. Follow for Day 3. Let's go." plus the text "Day 3 is gonna be CRAZY".

**Voice.** Lines are 5–14 words, selfie to camera, hype sign-offs ("Let's go", "Let's get it", "Anything is possible"). He never explains method on camera; the caption does that (D1's caption is an hour-by-hour log: "Hours 1–2: Restless… Hours 6–8: Calm, almost weightless"). Half his outliers are silent meme or physique posts.

**Endings.** A follow CTA that names the next day ("Follow for Day 3"), a tease of the next episode, and a caption question ("Best lock-in method?" on [D2](https://www.instagram.com/p/DdR8sFvNF77/)).

**Hook re-test.** [D5](https://www.instagram.com/p/Dc66pYqvHV5/) (5 Sep) and [D1](https://www.instagram.com/p/DdZpD0UxjNZ/) (17 Sep) are the same meditation footage. D1 drops "Boys," and adds the "Day 1 of proving YOU can do anything" overlay: 152× became 735×. It's not a clean test, because D1 went up three days after D2 popped.

## 2. Landen Levine (@landenlevine IG / @landenlevine1 TT), ~797k IG, ~432k TT

| # | Video | Date | Len | Views | × median | First spoken line | On-screen text, 0–3s | Hook type | Words |
|---|---|---|---|---|---|---|---|---|---|
| L1 | [IG](https://www.instagram.com/p/DbjJuQTvAgZ/) (same edit [TT](https://www.tiktok.com/@landenlevine1/video/7669518426528058655) 0.93×; IG re-upload [10.8×](https://www.instagram.com/p/DbkefrVq8kt/)) | 2 Aug | 68s | 4,333,370 | 17.0× | "It's day 24 of living in my car, and we just had by far our biggest day yet." | "Day 24 / $9,054.43/$100k" ticks to "+$55,749.67" then "$64,804.10/$100k" by 2.8s; 2–3-word subtitles | result-first | 18 |
| L2 | [IG](https://www.instagram.com/p/Dc9kw0XS8JU/) | 6 Sep | 74s | 2,574,429 | 10.1× | "After 50 days of living in my car, today, we finally did [it]." | "Day 50 / $84,489.77/$100k" ticks to "$116,997.74 +$32,498.97" | result-first | 13 |
| L3 | [TT](https://www.tiktok.com/@landenlevine1/video/7680294326072642846) (IG 6.1×), 29,600 shares | 31 Aug | 51s | 4,400,000 | 8.9× | "This is your sign to make a U-Haul slip n slide with your friends before summer ends." | "Day 47 / $80,357.41/$100k"; slide footage from frame 1 | challenge (dare) | 17 |
| L4 | [TT](https://www.tiktok.com/@landenlevine1/video/7673966554962267423) (IG 7.0×), 5,257 shares | 14 Aug | 60s | 4,000,000 | 8.1× | "Where do I park my car while I sleep in it so I don't get robbed or towed overnight?" | "Day 34 / $68,971.56/$100k" ticks "+$1,236.40" | curiosity gap | 19 |
| L5 | [TT](https://www.tiktok.com/@landenlevine1/video/7687713730158660895) (IG 3.3×) | 20 Sep | 59s | 3,200,000 | 6.4× | "After living in a car for two months, it's time to start touring houses." | "Buying a House / $122,078.77/$100k" | stakes | 14 |
| L6 | [TT](https://www.tiktok.com/@landenlevine1/video/7678844480362925342) (IG 1.9×) | 27 Aug | 54s | 2,800,000 | 5.6× | "How do you shower while living in a car?" | "Day 45 / $78,633.93/$100k" | curiosity gap | 9 |
| L7 | [TT](https://www.tiktok.com/@landenlevine1/video/7681018539167223071) (IG 0.7×), 3,022 comments | 2 Sep | 63s | 2,400,000 | 4.8× | "For the past 48 days, I've been living in a car with the goal of saving $100,000, and now I want to put it all on black." | "Day 48 / $81,628.41/$100k" | stakes | 27 |
| L8 | [IG](https://www.instagram.com/p/DcRaLf8KrWI/) | 20 Aug | 59s | 1,205,469 | 4.7× | "I went to the most dangerous water park in the world where rules don't exist." | "Day 39 / $73,334.77/$100k" | stakes | 15 |

**Pacing.** Median length is 61.8s. He narrates all 8, at **4.99 words/sec** (fastest of the four by about 2×). Cuts per 10s are 9.3–13.2, so a new shot roughly every 0.7–1.1s, with B-roll that literally shows each phrase. Spoken re-hooks come about every 8–9s: [L1](https://www.instagram.com/p/DbjJuQTvAgZ/) at 4, 11, 23, 33, 44 and 54s; [L3](https://www.tiktok.com/@landenlevine1/video/7680294326072642846) at 4, 13, 17, 26, 34 and 39s; [L4](https://www.tiktok.com/@landenlevine1/video/7673966554962267423) at 4, 10, 18, 28, 35 and 46s. The money counter changes on screen in most videos.

**Structure** ([L4](https://www.tiktok.com/@landenlevine1/video/7673966554962267423), 60s): 0–3.5 question → 3.7–12 "not as simple as I thought… they're very strict" → 12–28 the options that failed (stealth set-up, hotel car parks, a Reddit search) → 28–45 answers (Love's truck stop, rest stops), so the question closes at 47–75% → 45–55 progress on the series goal ("$100k by the beginning of next month") → 55–60 follow CTA.
[L7](https://www.tiktok.com/@landenlevine1/video/7681018539167223071) (63s): 0–6 stakes → 6–18 "Let me explain", which opens a second loop ("I named my car Anita… meant something that I was waiting to reveal until the end of the series") → 18–50 pros and cons → 50–63 he hands the decision to viewers ("I left a poll… will be reading the comments").
[L1](https://www.instagram.com/p/DbjJuQTvAgZ/) (68s): 0–8 result → 9–13 "I think I know what we gotta do… but first, after the daily backflip" (a deliberate delay) → 13–23 giveaways → 23–43 where the money came from (views, brand deals, 20% management cut, NDA) → 43–58 hidden cash and gift-card codes → 58–68 CTA.

**Voice.** Complete conversational sentences in first person, explaining to a mate. Every line carries a concrete number or place ("only like $50", "over 200 locations in California… within 30 minutes", "$390,000", "drive 20 minutes from San Diego to the border"). Self-aware asides ("because you're probably not allowed to do this"). He never shouts or hypes. It's mostly voiceover over B-roll, with only short to-camera moments (end of the first 3s of [L2](https://www.instagram.com/p/Dc9kw0XS8JU/)).

**Endings.** The CTA ties to the series goal with a percentage stat: "please join the 18% of people watching" ([L6](https://www.tiktok.com/@landenlevine1/video/7678844480362925342)), "right now 79% of you watching aren't following, but you still have a chance to follow along before we buy a house" ([L4](https://www.tiktok.com/@landenlevine1/video/7673966554962267423)). Gift-card codes hidden in the video work as rewatch and comment bait ("if you're the first to type in this Visa or Roblox gift card", [L1](https://www.instagram.com/p/DbjJuQTvAgZ/)). The poll ending on [L7](https://www.tiktok.com/@landenlevine1/video/7681018539167223071) got 3,022 comments; the other top-8 TikToks sit at 699–1,768.

**Hook test across platforms.** Same day, two cuts:
- Giveaway cut [L1](https://www.instagram.com/p/DbjJuQTvAgZ/): IG 17.0×, but its [TikTok](https://www.tiktok.com/@landenlevine1/video/7669518426528058655) did 0.93×.
- Backstory cut ("Yesterday I got the biggest payment of my life of $55,000. So you're probably wondering, why am I still living in my car?"): [IG](https://www.instagram.com/p/Dbl_0Gfy3NS/) 6.5×, [TikTok](https://www.tiktok.com/@landenlevine1/video/7669933701429480734) 6.0× (3.0M).

**The Instagram winner lost on TikTok.**

## 3. Luke (@lukeproof), ~1.42M IG, Instagram only

| # | Video | Date | Len | Views | × median | First spoken line | On-screen text, 0–3s | Hook type | Words |
|---|---|---|---|---|---|---|---|---|---|
| P1 | [IG](https://www.instagram.com/p/DaIyqCvRCq5/), 22,801 comments | 28 Jun | 144s | 25,702,695 | 10.4× | "They said the saxophone was too easy." | "Day 23 of proving you Can get good at anything"; Squidward on monitor; word captions | contrarian | 7 |
| P2 | [IG](https://www.instagram.com/p/DXkFxLPAsR_/) | 25 Apr | 132s | 11,666,941 | 4.7× | "Boys, today I'm going to become a chess master!" | "Day 22 of proving you can get good at anything"; "CHESS MASTER" shirt, board in hand | challenge | 9 |
| P3 | [IG](https://www.instagram.com/p/DaQOLIlx1Jz/) (repost of a 15 Feb edit) | 1 Jul | 128s | 9,769,137 | 3.9× | "Boys, boys, this is about to be epic." | "Day 18 of proving you can get good at anything"; unzipping a guitar case | in-medias-res | 8 |
| P4 | [IG](https://www.instagram.com/p/DeFuED_C2wi/), 9,245 comments | 4 Oct | 179s | 9,633,771 | 3.9× | "I'm dead broke. I'm not leaving this room until I make 100,000 dollars." | "Day 24 of proving you can do anything"; bank app showing -$442.52 | stakes | 13 |
| P5 | [IG](https://www.instagram.com/p/DVZDW7YEQzR/) | 2 Mar | 134s | 7,404,426 | 3.0× | "Boys, I'm about to build a brand new business and make $1,000 in a day!" | "Day 19 of proving you can do anything"; suit | challenge | 15 |
| P6 | [IG](https://www.instagram.com/p/DWwdXiujVMI/) | 5 Apr | 159s | 5,363,090 | 2.2× | "Boys, you already know I'm good with my hands." (then "Today I'm gonna get good with my toes!") | "Day 20 of proving you can get good at anything"; basketball | contrarian | 9 |
| P7 | [IG](https://www.instagram.com/p/DQ-8UweDSxi/) | 13 Nov 25 | 79s | 4,696,389 | 1.9× | "Day two of proving you can get good at literally [anything]." | kendama, word captions | challenge | 11 |
| P8 | [IG](https://www.instagram.com/p/DT3O4ozkUDh/) | 23 Jan | 179s | 4,368,471 | 1.8× | "Before you guys witness absolute greatness, if you're a grown man playing video games in 2026, wrap it up." | – | contrarian | 19 |

**Pacing.** Median length is 138.7s. He talks in all 8, at a median 2.41 words/sec (2.7 on the chess video). Cuts per 10s are 1.2–2.8, so a shot every 3.5–8s. Sync-sound bits are held long, and montages are faster. Spoken re-hooks come about every 10–15s in the talking stretches: [P2](https://www.instagram.com/p/DXkFxLPAsR_/) at 15, 22, 42, 49, 55, 58, 75, 93 and 103s. He swaps the top text mid-video for context ("Literally that game…" in P2).

**Structure** ([P2](https://www.instagram.com/p/DXkFxLPAsR_/), the chess video, 132s):
- 0–5: hook.
- 5–21: prep montage and gags ("This shirt is so tough!"), lessons, "24 hours straight".
- 22–32: comic setback ("The original plan was to enter a chess tournament… I played three eight-year-olds", then a cameo saying "Don't post it").
- 38–52: he re-states the stakes. "now it is time to see how much elo I can get in 24 hours. It started me at about 400 elo, my goal? I got no clue." Then "24 hours straight starts right now."
- 55–90: milestones climb: "One more game until a thousand elo", "992 elo… Queen sacrifice!", "Eight games in a row to get to 1,100", an opponent accuses him of engine moves.
- 93: payoff, "my final rating was 1215" (70%).
- 103–112: honesty beat. "You guys only see the [W's]… I lost so many times. I went on losing streaks multiple times."
- 113–120: "comment what I should learn next. Follow for more proof… Something big is coming."

[P4](https://www.instagram.com/p/DeFuED_C2wi/) (179s): 0–6 stakes → 11–17 struggle ("10 days and we're still on step one", back pain) → 22–32 the plan (4 businesses × $25k) → 37–48 grind montage (1,000 handwritten letters, 10,000 emails) → 49–75 rejections → 78–115 first yes → ~150 "$25,000!" (84%) → 160 "I've lost like over 20 pounds" → 168–179 giveaway to followers.

**Voice.** "Boys," opens 5 of 8. Loud, sweary, and lots of filmed reactions with friends. Comedy comes from failing first. The outros run long and sincere ([P1](https://www.instagram.com/p/DaIyqCvRCq5/)'s outro is about 18s of "if you found any inspiration…"). He never narrates the whole thing in voiceover.

**Endings.** "Comment what I should learn next" and "follow for more proof" appear in the video or the caption on all 8. Captions open with a question ("Most insane one yet?", "Is this my best work?"). [P4](https://www.instagram.com/p/DeFuED_C2wi/) gives money to followers. [P8](https://www.instagram.com/p/DT3O4ozkUDh/) adds a bonus segment after the payoff: he reads out his stats ("92% win rate… 393 total games… 19 hours and 39 minutes"), then plays a live match against a strong player.

**He reposts winners.** The same guitar edit did 7.74M ([Feb](https://www.instagram.com/p/DUyTT4gjSPB/)) and then 9.77M ([Jul](https://www.instagram.com/p/DaQOLIlx1Jz/)).

## 4. Will Fode (@foadster), ~57k IG, Instagram only

| # | Video | Date | Len | Views | × median | First spoken line | On-screen text, 0–3s | Hook type | Words |
|---|---|---|---|---|---|---|---|---|---|
| F1 | [IG](https://www.instagram.com/p/DcEQ2nYt9Gv/), 1,069 comments | 15 Aug | 18s | 8,348,249 | 47.6× | none (music) | "Scrolling for 10mins then studying for 8 hours straight or whatever"; iPad countdown 10:00 | challenge (text) | 13 (text) |
| F2 | [IG](https://www.instagram.com/p/DdEiioqN2rI/) | 9 Sep | 18s | 7,628,201 | 43.5× | none (music) | "spiking my dopamine for 8 mins then studying for 8 hours straight or something"; iPad timer | challenge (text) | 14 (text) |
| F3 | [IG](https://www.instagram.com/p/DcG7iWpNJLz/), 2,547 comments | 16 Aug | 24s | 3,029,830 | 17.3× | "I'm gonna read this book in one sitting." | word captions; Can't Hurt Me held up; stopwatch 00:01.84 | challenge | 8 |
| F4 | [IG](https://www.instagram.com/p/DZSkst_tyoG/) | 7 Jun | 78s | 2,445,273 | 13.9× | "We're gonna go on a 10 hour walk." | "WE'RE GONNA GO ON A 10 HOUR WALK" captions; phone timer being set | challenge | 8 |
| F5 | [IG](https://www.instagram.com/p/DeCZz99tZU7/) | 3 Oct | 77s | 2,165,141 | 12.3× | "I'm gonna study for eight hours straight with the first person who agrees to do it with me." | word captions; walking across campus | challenge | 18 |
| F6 | [IG](https://www.instagram.com/p/DVtuGOpD8L_/) | 10 Mar | 19s | 1,508,716 | 8.6× | none (music) | "Studying till my phone drains (10 hours)"; phone at 99% | challenge (text) | 8 (text) |
| F7 | [IG](https://www.instagram.com/p/Dbybb0WJSRw/) | 8 Aug | 66s | 955,034 | 5.4× | "We're gonna drive for 10 hours straight." | word captions; motorbikes | challenge | 7 |
| F8 | [IG](https://www.instagram.com/p/DWohONmNuYt/) | 2 Apr | 8s | 910,311 | 5.2× | none (trending audio) | "When I'm at a function but I hear some guys talking about math and physics" | relatable meme | – |

**Pacing.** Median length is 21.5s. He speaks in 4 of 8, at a median 1.65 words/sec across those. Cuts per 10s are 2.2–5.0. The two biggest outliers are silent: one text card and a timer. There's no spoken re-hook in the short ones; the clock changes every shot ([F3](https://www.instagram.com/p/DcG7iWpNJLz/): 00:05:32 → 3:43:22 → 9:58:21 → 9:59:10). [F5](https://www.instagram.com/p/DeCZz99tZU7/) uses repeated rejections as the re-hook: about 10 asks between 4s and 47s, one every 3–5s.

**Structure** ([F5](https://www.instagram.com/p/DeCZz99tZU7/), 77s): 0–4.5 hook → 4.6–47 rejection montage ("Nah, sorry, I gotta take a midterm") → 48–50 turn "You know what? I'll join in" (64%) → 52–66 study montage → 66 "we got 14 minutes left" → 70–77 payoff "I got you six Red Bulls" (91%).
[F3](https://www.instagram.com/p/DcG7iWpNJLz/) (24s): 0–2.6 hook with the stopwatch → 3–11 montage → 11–14 audio from the book → 15–20 "That was an insane experience… I'm wanting to quit" → 20.7–22 "And in case the timer wasn't enough, here are all my notes" (85%).

**Voice.** Flat and understated. The on-screen text flexes and then shrugs it off ("…or whatever", "…or something"). Spoken lines just state the task. He never explains his method on camera; the caption does that (F3's caption is a "blueprint" list from the book).

**Endings.** He finishes on proof (the timer, his notes, the battery) or a small gift. There's no spoken follow CTA in any of the 8. Comment bait sits in the caption as a question asking to be corrected: "Did I do this right?" ([F1](https://www.instagram.com/p/DcEQ2nYt9Gv/), 1,069 comments), "I heard this was a good method?" ([F2](https://www.instagram.com/p/DdEiioqN2rI/)).

---

## PATTERN SHEET

**What all four share**

1. **A progress meter on screen from frame 1 that changes every shot.** Landen's money counter ticks within 3s ([L1](https://www.instagram.com/p/DbjJuQTvAgZ/)). Devin and Foad keep a countdown or stopwatch in shot ([D2](https://www.instagram.com/p/DdR8sFvNF77/), [F3](https://www.instagram.com/p/DcG7iWpNJLz/)). Luke runs a "Day N" header and calls out his rating ("992 elo"… "1215", [P2](https://www.instagram.com/p/DXkFxLPAsR_/)). In the montage formats, the moving number is the only re-hook.
2. **Speech on frame 1, with the task stated as goal + number + time limit.** In 23 of the 24 talking outliers, speech starts within 0.4s. The median hook is 12 words, finished by about 3.7s. Examples: "Staring at a wall for 25 minutes and then studying for 8 hours straight" ([D2](https://www.instagram.com/p/DdR8sFvNF77/)), "We're gonna go on a 10 hour walk" ([F4](https://www.instagram.com/p/DZSkst_tyoG/)), "Where do I park my car while I sleep in it…" ([L4](https://www.tiktok.com/@landenlevine1/video/7673966554962267423)). Challenge is the most common hook type (15 of 32), then stakes (4), then result-first, curiosity gap and contrarian (3 each).
3. **A series frame, with the CTA selling the next episode.** "Drop a follow for day two" ([D1](https://www.instagram.com/p/DdZpD0UxjNZ/)), "join the 18% of people watching" ([L6](https://www.tiktok.com/@landenlevine1/video/7678844480362925342)), "Follow for more proof" ([P2](https://www.instagram.com/p/DXkFxLPAsR_/)). Foad is the exception: he repeats a format instead of numbering days ([F1](https://www.instagram.com/p/DcEQ2nYt9Gv/), [F2](https://www.instagram.com/p/DdEiioqN2rI/)).
4. **The loop opens in the first 5s and, in the challenge videos, closes at 70–91% with a number, followed by one honest line.** "My final rating was 1215" lands at 70% ([P2](https://www.instagram.com/p/DXkFxLPAsR_/)), "$25,000" at 84% ([P4](https://www.instagram.com/p/DeFuED_C2wi/)), the timer and notes at 85% ([F3](https://www.instagram.com/p/DcG7iWpNJLz/)). Then the struggle line: "I lost so many times" ([P2](https://www.instagram.com/p/DXkFxLPAsR_/)), "this is the hardest thing I've ever done" ([D5](https://www.instagram.com/p/Dc66pYqvHV5/)), "I'm wanting to quit" ([F3](https://www.instagram.com/p/DcG7iWpNJLz/)).
5. **Comment bait is a question, usually in the caption.** "Did I do this right?" ([F1](https://www.instagram.com/p/DcEQ2nYt9Gv/)), "Best lock-in method?" ([D2](https://www.instagram.com/p/DdR8sFvNF77/)), "comment what I should learn next" ([P2](https://www.instagram.com/p/DXkFxLPAsR_/)). Landen's spoken poll got the most comments of his eight ([L7](https://www.tiktok.com/@landenlevine1/video/7681018539167223071), 3,022).
6. **Formats move between accounts and still pop.** Foad's "N minutes of X, then 8 hours straight" (47.6× [F1](https://www.instagram.com/p/DcEQ2nYt9Gv/), 43.5× [F2](https://www.instagram.com/p/DdEiioqN2rI/)) showed up as Devin's 680× ([D2](https://www.instagram.com/p/DdR8sFvNF77/)). Foad's "book in one sitting" (17.3×, [F3](https://www.instagram.com/p/DcG7iWpNJLz/)) became Devin's 12.7× ([D6](https://www.instagram.com/p/Dd4AdWqR961/)). Devin's overlay is Luke's ([P2](https://www.instagram.com/p/DXkFxLPAsR_/)). The structure carries over even when the personality changes.

**What's unique to each**

- **Landen:** voiceover explainer at 5.0 words/sec with a new shot every 0.7–1.1s. There's a hard number in nearly every line, and a second loop opens mid-video ("I named my car Anita… reveal at the end", [L7](https://www.tiktok.com/@landenlevine1/video/7681018539167223071)). The CTA uses a "% of you aren't following" stat ([L4](https://www.tiktok.com/@landenlevine1/video/7673966554962267423)), and hidden codes reward rewatching ([L1](https://www.instagram.com/p/DbjJuQTvAgZ/)).
- **Luke:** 2–2.5 min of loud sync-sound vlog that opens on "Boys,". He fails comically before the real attempt ([P2](https://www.instagram.com/p/DXkFxLPAsR_/)), climbs through milestone callouts, and adds a bonus after the payoff ([P8](https://www.instagram.com/p/DT3O4ozkUDh/)). He reposts winners ([P3](https://www.instagram.com/p/DaQOLIlx1Jz/)).
- **Devin:** a ~25s micro-format: a 5–6-word hook, a silent timer montage, then 2–3 lines of payoff and "Follow for Day N" with a tease of the next day ([D2](https://www.instagram.com/p/DdR8sFvNF77/)). The caption tells the story the video doesn't ([D1](https://www.instagram.com/p/DdZpD0UxjNZ/)).
- **Foad:** his biggest outliers have no voice at all. The text hook ends on a shrug ("…or whatever", [F1](https://www.instagram.com/p/DcEQ2nYt9Gv/)), and the payoff is a proof object like the timer, notes or battery ([F3](https://www.instagram.com/p/DcG7iWpNJLz/), [F6](https://www.instagram.com/p/DVtuGOpD8L_/)).

**Measured pacing**

| | Median length | Words/sec (talking videos) | Spoken hook words (median) | Cuts per 10s (0.3–0.15) | Videos with speech |
|---|---|---|---|---|---|
| Devin | 25.7s | 0.64 | 5.5 | 1.3–3.2 | 4/8 |
| Landen | 61.8s | 4.99 | 16 | 9.3–13.2 | 8/8 |
| Luke | 138.7s | 2.41 | 10 | 1.2–2.8 | 8/8 |
| Foad | 21.5s | 1.65 | 8 | 2.2–5.0 | 4/8 |
| All 32 | 59.8s | 2.77 mean / 2.67 median (24 talking videos) | 12 | – | 24/32 |

**Two notes on your Trial Reels plan**

- Landen's two Day 24 cuts: the hook that won on Instagram (17.0×) did 0.93× on TikTok, and the other cut won there (6.0×) ([L1](https://www.instagram.com/p/DbjJuQTvAgZ/) / [TT](https://www.tiktok.com/@landenlevine1/video/7669518426528058655), [L1c](https://www.instagram.com/p/Dbl_0Gfy3NS/) / [TT](https://www.tiktok.com/@landenlevine1/video/7669933701429480734)). That's one case, but it's exactly the handoff the plan relies on.
- Devin re-cut a flop and it went from 152× to 735× ([D5](https://www.instagram.com/p/Dc66pYqvHV5/) → [D1](https://www.instagram.com/p/DdZpD0UxjNZ/)), and Luke reposted a winner and it gained views ([P3](https://www.instagram.com/p/DaQOLIlx1Jz/)). Neither treats a first upload as final.
