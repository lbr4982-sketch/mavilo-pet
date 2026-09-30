# Routine: weekly-product (Monday 04:10 KST · `CRON_TZ=Asia/Seoul 10 4 * * 1`)

You run the whole product pipeline of the Mavilo Pet Co. printable-guide factory in **one
session**: demand scan → build → self-review → one PR (blueprint v2 §4). This replaces the v1
routines `factory-scan`, `factory-build` and `factory-review`; their procedures are folded in below.
Fresh session, no memory. The owner reviews the PR on Monday and uploads the pack to Etsy by hand.

## Purpose

Exactly one new printable guide per week as a **human-upload pack** in
`factory/queue/listings/<handle>/` plus a brief in `factory/briefs/YYYY-WW.json`, on branch
`factory/YYYY-WW`, PR `[factory] YYYY-WW <Working Title>`. If self-review fails, no PR — an issue.

## Hard rules

1. **PAUSE check first.** `PAUSE` → exit ("PAUSE 파일 존재 — 종료").
2. **One product per week.** If `factory/briefs/<this ISO week>.json` exists or a `factory/<week>` PR is open → exit. Never build two to catch up.
3. **Tools.** GitHub + web search only. No Etsy/Shopify/Pinterest APIs, no secrets.
4. **Data source is the owner's logs.** Demand signals come from `factory/inbox/daily-log/*.md` (sales, views per product the owner recorded), `factory/briefs/trends-*.md`, and open issues/PR comments where the owner wrote a direction line in Korean ("다음 주: …"). **An owner direction line wins over your score.**
5. **No dosing / vaccine schedules / diagnosis / nutrition amounts.** Topics touching health are allowed as checklists or "questions to ask your vet" and get `needs_human: true` + the `needs-human` label.
6. **Verbatim copy blocks** from `factory/COPY.md` in the listing description (`LISTING_FOOTER`) and PDF closing page (`AI_DISCLOSURE_SHORT`, `VET_DISCLAIMER`, `PERSONAL_USE_LICENSE`). Diff, do not retype.
7. **QC gate ≥ 80** (`factory/qc.py`). Fix once; still < 80 → no PR, commit to the branch and open issue `build 실패 YYYY-WW <handle>` (Korean deductions). Never lower the threshold.
8. **Self-review is mandatory** and recorded in the PR body: every health-related sentence gets `confirmed <url>` / `not found` / `contradicted <url>`. Anything `contradicted` must be removed before opening the PR.
9. Never merge. Routine output is a pack a human uploads; there is no publishing Action.

## Procedure

### A. Scan (≈ v1 factory-scan)
1. Read `business/BLUEPRINT-v2.md` §6 (personalized products), §10 stop rules, `factory/COPY.md`, existing products (`business/products/*.html` titles, `business/etsy/listings/*/listing.json`, `factory/queue/listings/*`), the last 4 briefs, the latest `factory/briefs/trends-*.md`, the last 7 daily logs, and open issues labelled `direction`.
2. Personalized variants first: while any of the three §6 personalized packs (`*-personalized`) is missing from `business/etsy/listings/` and `factory/queue/listings/`, this week's product is the next one of them (build order: puppy plan → health record → cat plan; then the welcome kit after month 2). Otherwise pick a new guide:
   ~40 candidate keywords across the families (30-day plan, record book, checklist, enrichment pack, seasonal safety guide, personalized variant), 6–10 weeks ahead of U.S. seasons; research the best ~12 (etsy result counts via `site:etsy.com`, autocomplete presence, 3 competitor prices, `demand` 1–5, `saturation` 1–5, `score = demand*2 - saturation` +1 for a family that sold in the logs). Reject title overlap with existing products.
3. Write `factory/briefs/YYYY-WW.json` (schema in `factory/routines/factory-scan.md` → "Output"; keep it), with `summary_ko`.

### B. Build (≈ v1 factory-build)
4. Write `business/products/<handle>.html` in the house style (copy the `<style>` and page skeleton of the closest existing guide; 10–16 Letter pages; original text; closing page with the three copy blocks and a Sources list of URLs you verified this run). Personalized packs: the HTML is a template with `{{PET_NAME}}`-style placeholders documented at the top, plus a rendered **example** for a fictional pet ("Biscuit") — the example PDF and its images are what gets listed (Etsy requires the first image to show a finished personalized example).
5. Render: `python3 factory/build.py <handle>` → PDF, cover PNG, QC JSON; save `python3 factory/qc.py business/products/<handle>.html --json factory/qc-reports/<handle>.json`. Add an entry to `PRODUCTS` in `factory/render_mockups.py` and run it → 9 listing images 2000×2000, then move/copy them to `factory/queue/listings/<handle>/images/`.
6. Write `factory/queue/listings/<handle>/listing.json` in the same schema as `business/etsy/listings/*/listing.json` (title ≤140, exactly 13 tags ≤20 chars, price, description ending with `LISTING_FOOTER`, `images`, `file`, `shopify` block, `qc_score`, `needs_human`, `brief`). Personalized packs also carry `personalization_instructions` (the exact Etsy prompt text from §6), `when_made: "made_to_order"`, `processing_time: "Delivered within 24 hours (usually same day)"` and the §6 AI/vet/no-dosing lines in the description.

### C. Review (≈ v1 factory-review, on your own output)
7. Re-run `factory/qc.py` and confirm the score; check title/tags/price constraints; extract every sentence with vaccine/medication/symptom/poison/toxic/weight/parasite/dose/emergency and web-verify against AVMA, AAHA, ASPCA, Merck Vet Manual, university vet colleges; scan banned terms and outcome promises; check similarity `max < 0.6`; check Etsy compliance (AI disclosure present, digital download, no "handmade", no other brands in images).
8. Verdict: pass → PR. Pass with medical detail → PR + `needs-human`. Fail → fix once and repeat step 7; still failing → issue instead of PR (rule 7).

### D. PR
9. Branch `factory/YYYY-WW`, commit `weekly-product: <handle> (QC NN)`, PR `[factory] YYYY-WW <Working Title>` with labels `factory` (+`needs-human`). Body: `PR_SUMMARY_TEMPLATE` (Korean 5 lines; line 5 = "머지 후 사장님이 `factory/queue/listings/<handle>/`를 Etsy에 업로드 (3분)"), cover image, QC score, page count, the review verdict table (Korean block + English table as in `factory-review.md`), and the brief's rejected list.
10. Add the row to `factory/queue/listings/index.md`. Final message: the same Korean summary.

## Done checklist

- [ ] PAUSE absent; no brief/PR for this week existed
- [ ] Owner direction lines read and honored; personalized packs prioritized while missing
- [ ] Brief JSON valid; HTML renders; QC ≥80 saved under `factory/qc-reports/`
- [ ] Pack complete in `factory/queue/listings/<handle>/` (listing.json, 9 images 2000×2000, PDF path)
- [ ] Copy blocks verbatim; every health sentence has a verdict with URL; none contradicted
- [ ] PR body Korean 5 lines + cover + QC + review table; `needs-human` when required; nothing merged
