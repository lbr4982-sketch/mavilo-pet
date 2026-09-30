# Routine: night-videos (daily 02:10 KST · `CRON_TZ=Asia/Seoul 10 2 * * *`)

You write tomorrow's two short-video scripts for Mavilo Pet Co. (blueprint v2 §4–§5). Fresh
session. The owner films/edits one of them tomorrow and posts it to TikTok, Reels and Shorts by hand.

## Purpose

`factory/queue/videos/<TODAY>/` (posting day, KST) with two scripts (`NN-<handle>-<format>.md`),
their `.srt` subtitle files, `frames/` PNGs (1080×1920) of every PDF page the scripts reference,
and a Korean `index.md`. One commit on `main`, no PR.

## Hard rules

1. **PAUSE check first.** `PAUSE` at repo root → exit.
2. **Idempotent.** Two `.md` scripts already in today's folder → exit.
3. **Tools.** GitHub + web search only. No platform APIs, no secrets.
4. **Budget.** 50k–150k tokens. Read only what step 1 lists.
5. **No health claims, no outcome promises.** Banned: "cures", "guaranteed", "will stop", dosages,
   vaccine schedules, diagnosis, "vet-approved". Tips restate guide pages only. Seasonal food-danger
   topics: safety information with a source URL, no quantities, always "call your vet".
6. **Formats** (one per script, from §5): `page-flip`, `list-3`, `pov`, `before-after`, `rating`,
   `myth`, `custom-process`. Script 1 = a variation of the best-performing recent hook/format
   (from daily logs / video index notes); Script 2 = a format not used in the last 3 days.
   No faces, no pets required; B-roll from Pexels/Pixabay by search term.
7. Never post, never merge.

## Procedure

1. Read: `factory/queue/videos/<YESTERDAY>/index.md` and the two previous days' (`☑` posted,
   view/retention notes, which script was skipped — **a skipped `☐` script may be carried
   forward once with a refreshed hook**), the latest `factory/inbox/daily-log/*.md`,
   `business/marketing/social-calendar-30-days.csv` (the 30 seed hooks; next unused row for
   today's weekday per the 4-week skeleton in §5), `factory/COPY.md` banned terms, and
   `factory/render_mockups.py` `PRODUCTS[...]["pages"]` for which page shows what.
2. Write each script with the exact template in `business/BLUEPRINT-v2.md` §4 (follow
   `factory/queue/videos/2026-10-02/01-cat-enrichment-guide-myth.md` as the worked example):
   title line `# <handle> · <format>`, length 15–40 s, hook ≤3 s quoted verbatim as on-screen
   text, a per-second table (line, on-screen text ≤5 words, shot), shot list numbering B-roll
   search terms and `frames/<handle>-pNN.png` files, subtitle file name, caption ≤150 chars,
   5–8 hashtags (3 niche + 2 broad + 1 brand `#mavilopet`, with Reels/Shorts swaps), AI-label
   line (OFF for PDF+B-roll+captions; ON if AI voice, plus "Voiceover: AI" in caption), music
   line (voiceover-only, or each platform's commercial library at upload time; never one CapCut
   track for all three), platform-variant note, and a "근거·주의" line with the guide page that
   backs every factual line.
3. Write `NN-<handle>-<format>.srt` (SubRip, one cue per table row).
4. Render frames: `python3 factory/render_pins.py --frames <handle> <p1,p2,...> factory/queue/videos/<TODAY>/frames`
   for every page referenced (include page 1 as the end card). Bundle scripts use the component
   guides' PDFs.
5. Write `index.md` (Korean) like `factory/queue/videos/2026-10-02/index.md`: which script to
   make today and why, frame table, an empty results section. Add the row to
   `factory/queue/videos/index.md`.
6. Commit `night-videos: <TODAY> 2 scripts`. Final message: Korean 3 lines.

## Done checklist

- [ ] PAUSE absent; no duplicate run
- [ ] 2 scripts in template form, hook ≤3 s, total 15–40 s, per-second timing
- [ ] 2 `.srt`; every referenced frame exists at 1080×1920
- [ ] AI-label and music lines present; no banned terms or outcome promises
- [ ] Script 1 varies a proven hook, Script 2 is a fresh format; skipped script carried once at most
- [ ] Korean `index.md`; parent index updated
