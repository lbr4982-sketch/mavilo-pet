# Routine: factory-optimize (Friday 09:10 KST)

You are the traffic-and-listing-optimisation step of the Mavilo Pet Co. factory. Fresh session.

## Purpose

Two jobs, one PR:
1. Write **two** blog posts (1,200-1,800 words each) that answer a real search query, include an
   original checklist, and link to the matching guide on both Etsy (Share & Save link) and Shopify.
   Render three Pinterest pin images (1000x1500) per post so the RSS feed carries images.
2. Refresh under-performing Etsy listings: any active listing with **0 sales in the last 60 days**
   gets a new title, new 13 tags and a new first image proposal.

## Hard rules

1. **PAUSE check first.** `PAUSE` at repo root → exit ("PAUSE 파일 존재 — 종료").
2. **One PR per week** on branch `content/YYYY-WW`. If it already exists and is open, exit.
3. **Tools.** GitHub + web search only. No Etsy/Shopify/Pinterest API calls, no secrets.
4. **Copy blocks verbatim.** Every blog post ends with `VET_DISCLAIMER_SHORT` and a one-line AI
   disclosure: "Written by Mavilo Pet Co. with the help of AI tools and reviewed by a human."
   Product mentions in posts never claim results or medical outcomes.
5. **No dosing / vaccine schedules / diagnosis** in posts. If a topic needs it, choose another
   topic. If unavoidable (e.g. "what to ask your vet about vaccines"), keep it as questions to
   ask and label the PR `needs-human`.
6. **Links.** Etsy links use the Share & Save format recorded in `business/etsy/catalog.json`
   (`share_save_url`); if absent, use the plain listing URL and note "Share & Save 링크 없음" in
   the PR. Shopify links are `https://<store domain>/products/<handle>` (domain from
   `business/etsy/catalog.json` → `shopify_domain`, else `mavilopet.com`; never guess a different one).
7. **Kill/refresh only proposes.** Title/tag swaps are files in the PR; `etsy-publish` applies them
   after merge. Never deactivate a listing here (that is `factory-finance`).
8. PR body: Korean 5-line summary, the two post titles, the pin images, and the refresh table.

## Procedure

### A. Blog posts
1. Read `business/blog/*.md` (front-matter format: title, meta_description, target_keyword,
   handle) and the last 6 weeks of `content/*` PRs to avoid repeats. Read `factory/COPY.md`.
2. Pick two keywords: one tied to this week's product (from `factory/briefs/<week>.json` or the
   most recent brief) and one evergreen/seasonal query 4-8 weeks ahead. Verify with web search
   that the query has autocomplete presence and that the top results are generic (an
   opportunity), not veterinary journals (skip).
3. Write `business/blog/<handle>.md` with the same front matter as the existing posts plus
   `image: business/pins/<handle>/pin-01.png`, `products: [<guide handle>]`, `published: false`.
   Structure: hook → why it matters → step-by-step → original checklist (also as HTML table) →
   "when to call your veterinarian" (general) → product CTA (Etsy + Shopify links) → footer blocks.
4. Pins: create `business/pins/<handle>/pin-0{1,2,3}.html` (1000x1500, brand palette, post title +
   one takeaway each) and render with
   `chrome --headless --no-sandbox --disable-gpu --window-size=1000,1586 --screenshot=<png> <html>`
   then crop to 1000x1500 with Pillow (same trick as `factory/build.py`). Commit the PNGs.
   `shopify-publish` uploads pin-01 as the article image so the RSS `<enclosure>` carries it.

### B. Listing refresh
1. Read the newest `business/etsy/stats/*.json` and `business/etsy/catalog.json`. If stats are
   missing, skip section B and write "통계 없음 — 리스팅 최적화 생략" in the PR.
2. For each active listing with `sales_60d == 0` and `age_days >= 60`:
   - Research 5 competitor titles ranking for its primary keyword.
   - Write `factory/listings/<handle>.refresh.json`:
     ```json
     {"handle": "...", "listing_id": 123, "reason": "0 sales / 60d, 84 views",
      "title": "≤140 chars", "tags": ["13 tags ≤20 chars"],
      "first_image": "business/etsy/listings/<handle>/images/03-page-05.png",
      "previous": {"title": "...", "tags": ["..."]}, "week": "YYYY-WW"}
     ```
   - Max 3 refreshes per week (Etsy treats mass edits as spam signals).
3. Do not touch listings refreshed within the last 30 days (check `previous`/`week`).

### C. PR
- Branch `content/YYYY-WW`, PR title `[content] YYYY-WW: <post 1 short> + <post 2 short> (+N refresh)`.
- Labels: `content` (+ `needs-human` per rule 5).
- Body: Korean 5 lines (`PR_SUMMARY_TEMPLATE`, replace "QC 점수" with word counts), pin images
  inline, refresh table (handle | old title | new title | reason).

## Outputs

- `business/blog/<handle>.md` ×2, `business/pins/<handle>/pin-01..03.png` (+ .html sources)
- `factory/listings/<handle>.refresh.json` ×0-3
- PR `content/YYYY-WW`

## Done checklist

- [ ] PAUSE absent; no open `content/<week>` PR before this run
- [ ] Two posts, 1,200-1,800 words, front matter valid, original checklist in each
- [ ] Both disclaimer lines present verbatim; no dosing/vaccine schedule/diagnosis
- [ ] Etsy Share & Save + Shopify links (or the "없음" note)
- [ ] 6 pin PNGs at 1000x1500
- [ ] ≤ 3 refresh files, none for listings changed in the last 30 days
- [ ] PR body in Korean with images and table
