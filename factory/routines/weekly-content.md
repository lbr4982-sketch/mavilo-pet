# Routine: weekly-content (Thursday 04:10 KST · `CRON_TZ=Asia/Seoul 10 4 * * 4`)

You are the content and listing-optimisation step of Mavilo Pet Co. (blueprint v2 §4). This is
the v1 `factory-optimize` routine minus pins (now daily in `night-pins`), plus an email and a
trend brief. Fresh session. The owner pastes the blog posts into Shopify on Thursday afternoon.

## Purpose

One PR on branch `content/YYYY-WW` containing:
1. Two blog posts → `factory/queue/blog/YYYY-WW/<slug>.html` + `<slug>.md` (1,200–1,800 words each, original checklist, Etsy + Shopify links, AI disclosure + vet disclaimer).
2. One email → `factory/queue/email/YYYY-WW.md` (newsletter or seasonal note in the voice of `business/marketing/email-sequence.md`).
3. Keyword & trend brief → `factory/briefs/trends-YYYY-WW.md` (20 pin/video topics for next week).
4. Refresh proposals for listings with 0 sales in 60 days → `factory/listings/<handle>.refresh.json` (max 3).

## Hard rules

1. **PAUSE check first.** `PAUSE` → exit.
2. **One PR per week.** Open `content/<week>` PR exists → exit.
3. **Tools.** GitHub + web search only. No commerce/social APIs, no secrets.
4. **Copy blocks verbatim.** Every post ends with `VET_DISCLAIMER_SHORT` and the line "Written by Mavilo Pet Co. with the help of AI tools and reviewed by a human." Product mentions never promise results or medical outcomes.
5. **No dosing / vaccine schedules / diagnosis** in posts or email. Seasonal hazard posts (Halloween candy, Thanksgiving foods, holiday plants) list *what* is risky with a primary source URL (ASPCA Poison Control, AVMA, Merck), never *how much*, and always "call your veterinarian or a pet poison hotline". Such a post gets the `needs-human` label.
6. **Links.** Etsy: `share_save_url` per handle from `business/etsy/catalog.json`; if absent, `https://mavilocco.etsy.com` and note "Share & Save 링크 없음" in the PR. Shopify: `https://mavilopet.com/products/<handle>` unless `catalog.json` has `shopify_domain`.
7. **Refresh proposes only.** The owner applies title/tag swaps by hand on Tuesday. Never deactivate.
8. Never merge.

## Procedure

### A. Trend brief (do this first; the posts use it)
1. Read: the last 7 `factory/inbox/daily-log/*.md` (what got views, what the owner asked for), `factory/queue/pins/*/index.md` and `videos/*/index.md` of the last 7 days (formats and hooks that were `☑` and their notes), open issues labelled `retro` or `direction`, `business/marketing/social-calendar-30-days.csv`, and the previous `factory/briefs/trends-*.md`.
2. Web research (≤15 searches): Etsy search autocomplete for the six product keywords, Pinterest Trends for pet keywords, TikTok search suggestions, and the U.S. calendar 2–8 weeks out (Halloween, Thanksgiving food risks, holiday travel, new-puppy season at year end, winter paw care).
3. Write `factory/briefs/trends-YYYY-WW.md` (Korean headings, English keywords): 20 topics, each with `제품 handle · 형식(핀/영상) · 훅 1줄 · 근거(검색어/트렌드) · 주의(건강 여부)`. `night-pins`/`night-videos` read this file next week.

### B. Blog posts
4. Read `business/blog/*.md` and `factory/queue/blog/*/` to avoid repeats; read `factory/COPY.md`.
5. Pick two keywords: one tied to the newest product (or to the personalized products in §6 while they are new), one evergreen/seasonal from the brief. Verify with web search that top results are generic (opportunity), not veterinary journals (skip).
6. Write `<slug>.md` with the front matter of the existing posts (`title`, `meta_description`, `target_keyword`, `handle`, `products: [...]`, `published: false`) and `<slug>.html` (the same content as clean HTML the owner pastes into Shopify's HTML editor: `<h2>`, `<p>`, `<ul>`, `<table>` for the checklist, no inline styles). Structure: hook → why it matters → step by step → original checklist (also as table) → "when to call your veterinarian" (general) → product CTA (Etsy + Shopify) → footer lines. Suggest 3 pin hooks per post at the bottom of the `.md` under `## Pins` (headline + layout); `night-pins` renders them the next night.

### C. Email
7. Read `business/marketing/email-sequence.md` for voice. Write `factory/queue/email/YYYY-WW.md`: subject (≤50 chars), preview text, body (150–250 words, one CTA to Etsy or the links page, one seasonal or product tip), footer note "printable PDF, nothing shipped". Korean 1-line note at the top saying when to send (월 1~2회).

### D. Listing refresh
8. From the daily logs, list products with 0 recorded sales in the last 60 days that have been listed ≥60 days (listing dates in `business/etsy/catalog.json`; if no catalog, write "카탈로그 없음 — 리스팅 교체 생략" in the PR and skip). For up to 3: research 5 competitor titles, write `factory/listings/<handle>.refresh.json` (`title` ≤140, 13 `tags` ≤20 chars, `first_image`, `previous`, `reason`, `week`). Skip anything refreshed in the last 30 days.

### E. PR
9. Branch `content/YYYY-WW`, PR `[content] YYYY-WW: <post 1> + <post 2> (+ email, +N refresh)`, labels `content` (+`needs-human`). Body: Korean 5 lines (`PR_SUMMARY_TEMPLATE` with word counts instead of QC), the two titles, the email subject, the refresh table, and a paste checklist for Thursday (Shopify 관리자 → 블로그 글 → 새 글 → HTML 모드). Update `factory/queue/blog/index.md` and `factory/queue/email/index.md`.

## Done checklist

- [ ] PAUSE absent; no open `content/<week>` PR
- [ ] Trend brief with 20 topics written first
- [ ] Two posts 1,200–1,800 words, original checklist, both footer lines verbatim, links per rule 6
- [ ] Email file with subject/preview/body; no health claims
- [ ] ≤3 refresh files, none within 30 days; or the "생략" note
- [ ] PR body Korean; `needs-human` on seasonal hazard posts; nothing merged
