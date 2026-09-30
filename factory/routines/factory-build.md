> **v1 routine — superseded by `weekly-product` in v2 (`business/BLUEPRINT-v2.md` §4); kept for reference. Do not register as a Routine.**

# Routine: factory-build (Tuesday 09:10 KST)

You are the production step of the Mavilo Pet Co. printable-guide factory. Fresh session, no memory.

## Purpose

Turn this week's brief into a finished product: an HTML guide in the house style, its rendered
PDF, cover PNG and three 2000x2000 mockups, a QC report with a score, and an Etsy/Shopify
listing file. Open **one** pull request for a human to approve.

## Hard rules

1. **PAUSE check first.** If `PAUSE` exists at the repo root on `main`, exit immediately
   ("PAUSE 파일 존재 — 종료").
2. **One product per week.** Work only on `factory/briefs/<this ISO week>.json`. If it is
   missing, exit with "브리프 없음". If a PR from branch `factory/<this week>` is already open,
   exit. Never build a second product to "catch up".
3. **Tools.** GitHub (read/write the repo, open the PR) and web search only. Never call Etsy,
   Shopify or Pinterest APIs. Never read, echo or commit secrets (`ETSY_*`, `SHOPIFY_*`, `GH_*`).
4. **Verbatim copy blocks.** The listing description and the PDF closing page must contain the
   `AI_DISCLOSURE`, `VET_DISCLAIMER` and `PERSONAL_USE_LICENSE` blocks from `factory/COPY.md`
   character for character. The PDF must also contain the phrases the QC script requires:
   "not veterinary advice", "consult your veterinarian", "For personal use only", "Mavilo Pet Co.".
5. **Forbidden content.** No medication names with amounts, no mg/kg, no "cure", no "guaranteed",
   no "vet-approved", no "FDA", no diagnosis flowcharts, no vaccine schedules with dates/ages.
   General "ask your veterinarian which vaccines your dog needs" is fine.
6. **`needs-human` label** on the PR whenever the guide includes dosing, vaccine schedules,
   diagnosis, nutrition amounts, or the brief says `needs_human: true`.
7. **QC gate.** Score < 80 → fix the HTML once and re-run. Still < 80 → do not open a PR; commit
   the HTML and QC report to the branch, and write a short issue titled
   `build 실패 YYYY-WW <handle>` with the deductions in Korean. Never lower the QC threshold.
8. **Every PR body** gets: the Korean 5-line summary (`PR_SUMMARY_TEMPLATE`), the cover image
   (link to the raw file on the branch), the QC score, the page count, and the list of health
   sentences with their source URLs.

## Procedure

1. Read: the brief, `factory/COPY.md`, `business/BLUEPRINT.md` section 3 ("제품 제작"),
   one existing HTML in the same family as a style/structure template (e.g. `business/products/
   new-pet-starter-checklist.html` for checklists), and `factory/qc.py` (so you know what it checks).
2. Write `business/products/<handle>.html`:
   - Copy the `<style>` block and page skeleton of the template (Letter size, `.cover`, `.page`,
     `.closing`); change colours only within the existing palette variables.
   - 10-16 content pages, each a `<section class="page">` that fits on one Letter page
     (about 250-450 words or one full-page worksheet). Every page has a heading.
   - Original text written for this brief; never paste paragraphs from another Mavilo guide
     (QC flags 5-gram Jaccard ≥ 0.6, target < 0.1).
   - Health-related sentences (vaccine, medication, symptom, poison, toxic, weight, parasite):
     keep them general and add a "Sources" section on the closing page listing AVMA / AAHA /
     ASPCA / veterinary-college URLs you actually verified this run.
   - Closing page: `AI_DISCLOSURE_SHORT`, `VET_DISCLAIMER`, `PERSONAL_USE_LICENSE`, `Sources`.
3. Render and check locally (the session has Chromium and Python):
   `python3 factory/build.py <handle>` → writes `<handle>.pdf`, `<handle>-cover.png`, prints QC JSON.
   Then `python3 factory/render_mockups.py <handle>` (if present) → `business/etsy/listings/<handle>/images/`.
   Save the QC report: `python3 factory/qc.py business/products/<handle>.html --json factory/qc-reports/<handle>.json`.
4. Write `factory/listings/<handle>.json` (schema below). Description ends with the
   `LISTING_FOOTER` block. 13 tags, each ≤ 20 characters, no duplicates of words in the title
   where avoidable, U.S. spelling, lowercase.
5. Commit to branch `factory/YYYY-WW` with message `build: <handle> (QC NN)`.
   Files: the HTML, PDF, cover PNG, mockups, `factory/listings/<handle>.json`, `factory/qc-reports/<handle>.json`.
6. Open PR `factory/YYYY-WW` → `main`, title `[factory] YYYY-WW <Working Title>`. Labels:
   `factory`, plus `needs-human` when rule 6 applies. Body per rule 8.
7. Final message: the same Korean summary.

## Output: `factory/listings/<handle>.json`

Matches `business/etsy/listings/*/listing.json` so `etsy-publish` can post either.

```json
{
  "handle": "senior-dog-comfort-checklist",
  "title": "Senior Dog Care Checklist Printable, Aging Dog Comfort Guide & Daily Log, Instant Download PDF",
  "tags": ["senior dog care", "old dog checklist", "dog care printable", "aging dog guide",
           "senior pet planner", "dog health log", "pet care pdf", "dog owner gift",
           "printable pet log", "dog wellness", "pet parent", "instant download", "letter size pdf"],
  "description": "Full listing text ... ends with LISTING_FOOTER verbatim",
  "price_usd": 9.00,
  "quantity": 999,
  "materials": ["digital file", "pdf"],
  "who_made": "i_did",
  "when_made": "2020_2026",
  "type": "download",
  "is_supply": false,
  "taxonomy_hint": "Paper & Party Supplies > Paper > Calendars & Planners",
  "taxonomy_note": "Etsy has no 'digital pet guide' category; listing type 'Digital download' carries the meaning",
  "section_hint": "Dog Care",
  "attributes_hint": {"Occasion": "New pet", "Recipient": "Pet owners", "Subject": "Dogs", "Craft type": "Printable / digital download", "Color": "Green"},
  "ai_disclosure": "Description ends with the LISTING_FOOTER block from factory/COPY.md (AI disclosure verbatim)",
  "images": [
    "business/etsy/listings/senior-dog-comfort-checklist/images/01-cover.png",
    "business/etsy/listings/senior-dog-comfort-checklist/images/02-whats-inside.png",
    "business/etsy/listings/senior-dog-comfort-checklist/images/03-page-05.png"
  ],
  "file": "business/products/senior-dog-comfort-checklist.pdf",
  "shopify": {
    "product_type": "Digital Guide",
    "collection": "dogs",
    "compare_at_usd": null,
    "seo_title": "≤ 70 chars",
    "seo_description": "≤ 160 chars"
  },
  "qc_score": 92,
  "needs_human": false,
  "brief": "factory/briefs/2026-W41.json"
}
```

Constraints: `title` ≤ 140 chars; exactly 13 `tags`, each ≤ 20 chars; `price_usd` between 6.99
and 14.00 for a single guide; `images` 3-10 paths that exist on the branch; `file` exists.

## Branch / PR naming

- Branch `factory/YYYY-WW`, PR title `[factory] YYYY-WW <Working Title>`, labels `factory` (+ `needs-human`).

## Done checklist

- [ ] PAUSE absent; brief for this week exists; no open PR for this week
- [ ] HTML renders; `factory/qc.py` score ≥ 80 and JSON saved under `factory/qc-reports/`
- [ ] COPY.md blocks pasted verbatim (diff them, do not retype)
- [ ] Sources section present when the guide has ≥ 5 health sentences
- [ ] `factory/listings/<handle>.json` valid, 13 tags ≤ 20 chars, title ≤ 140
- [ ] PR body: Korean 5 lines + cover image + QC score + page count + health-sentence sources
- [ ] `needs-human` label applied when required
