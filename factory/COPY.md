# factory/COPY.md — Verbatim copy blocks

These blocks are reused **word for word** by the Routines (`factory/routines/*.md`), the Etsy
listing packs (`business/etsy/listings/*/listing.json`), the Shopify product descriptions and
the support replies. Do not paraphrase them in generated content; copy the block exactly.
When a block changes, change it here first, then open one PR that updates every consumer.

Each block has a stable ID in the heading. Routines reference blocks by ID.

---

## AI_DISCLOSURE (Etsy Creativity Standards, required in every listing description)

```
This guide was designed and written by Mavilo Pet Co. with the help of generative AI tools, under our original creative direction, and reviewed by a human before publishing.
```

## AI_DISCLOSURE_SHORT (inside the PDF closing page, optional)

```
Created by Mavilo Pet Co. with the help of generative AI tools, under our original creative direction, and reviewed by a human before publishing.
```

## VET_DISCLAIMER (required in every listing description, product page and PDF)

```
This guide is general educational information for pet parents and is not veterinary advice. It is not a substitute for veterinary examination, diagnosis or treatment. Always consult your veterinarian about your pet's specific health, diet, vaccinations and medications, and contact an emergency veterinarian or a pet poison hotline immediately if you think your pet is sick or has swallowed something harmful.
```

## VET_DISCLAIMER_SHORT (PDF page footers, image captions)

```
Not veterinary advice. Consult your veterinarian about your pet's specific needs.
```

## PERSONAL_USE_LICENSE (PDF closing page, listing description)

```
For personal use only. © Mavilo Pet Co. You may print this guide as many times as you like for your own household. You may not resell, share, redistribute, upload or use any part of it commercially, or use it to train AI systems.
```

## DOWNLOAD_INSTRUCTIONS_ETSY (listing description, "How it works" image)

```
HOW IT WORKS
1. Complete checkout. This is a digital download; nothing will be shipped.
2. On Etsy.com: go to You > Purchases and reviews and click Download files next to this order. Files are also linked in the confirmation email Etsy sends you. (Downloads are not available in the Etsy app; please use a web browser.)
3. Open the PDF with any free PDF reader (Adobe Acrobat Reader, Preview on Mac, your phone's Files app) and print at home on US Letter paper, or use it on a tablet.
```

## DOWNLOAD_INSTRUCTIONS_SHOPIFY (product page, order confirmation)

```
HOW IT WORKS
1. Complete checkout. This is a digital download; nothing will be shipped.
2. Your download link appears on the order confirmation page and in the confirmation email within a few minutes. Check your spam or promotions folder if you do not see it.
3. Open the PDF with any free PDF reader and print at home on US Letter paper, or use it on a tablet. Your link stays active, so you can download it again later.
```

## PRINT_TIPS (support replies, FAQ)

```
PRINT TIPS
- Paper: US Letter (8.5 x 11 in). Choose "Fit to page" or "Scale: 100%" in the print dialog.
- Colour: the guide prints well in black and white; choose colour for the cover and charts.
- Trackers and logs are designed to be printed as many times as you need.
- On A4 paper choose "Fit to printable area"; the margins are wide enough that nothing is cut off.
```

## REFUND_POLICY_DIGITAL (Etsy shop policies, Shopify Refund policy, support replies)

```
Because this is an instant digital download, all sales are final and we do not offer refunds, returns or exchanges once the file has been delivered. If your file will not open, is missing pages or otherwise does not match the listing, contact us within 30 days of purchase with your order number and we will send a corrected file or, if we cannot fix it, refund your order. Refunds are never withheld for a genuine file problem.
```

## SUPPORT_SIGNATURE (all replies)

```
Warm regards,
Mavilo Pet Co.
Happy pets, practical care.
```

## LISTING_FOOTER (last lines of every Etsy / Shopify description, in this order)

```
---
This guide was designed and written by Mavilo Pet Co. with the help of generative AI tools, under our original creative direction, and reviewed by a human before publishing.

This guide is general educational information for pet parents and is not veterinary advice. It is not a substitute for veterinary examination, diagnosis or treatment. Always consult your veterinarian about your pet's specific health, diet, vaccinations and medications, and contact an emergency veterinarian or a pet poison hotline immediately if you think your pet is sick or has swallowed something harmful.

For personal use only. © Mavilo Pet Co. You may print this guide as many times as you like for your own household. You may not resell, share, redistribute, upload or use any part of it commercially, or use it to train AI systems.

Instant digital download (PDF). Nothing will be shipped. Because this is an instant digital download, all sales are final; if your file will not open or does not match the listing, message us within 30 days and we will fix it or refund you.
```

## PR_SUMMARY_TEMPLATE (Korean, 5 lines, every PR body — filled in by the Routine)

```
**한국어 요약 (5줄)**
1. 무엇: <제품/글 이름 1줄>
2. 왜: <브리프 근거 — 수요·포화도 점수 1줄>
3. 내용: <페이지 수, 핵심 섹션 1줄>
4. 안전: <건강 문장 수, 출처 유무, needs-human 여부 1줄>
5. 다음: <머지되면 일어나는 일 1줄 (Etsy 게시 / Shopify 게시 / 사람 업로드 필요)>

QC 점수: **NN / 100** (통과 기준 80)
![cover](<raw.githubusercontent.com 링크 또는 PR 첨부 이미지>)
```
