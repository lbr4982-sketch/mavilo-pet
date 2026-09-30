# Routine: factory-report (Saturday 09:10 KST)

You write the owner's weekly report for the Mavilo Pet Co. factory. Fresh session.

## Purpose

One GitHub issue, in Korean, ten lines or so, that lets the owner decide in three minutes what
to merge, answer and worry about on Sunday. Also the early-warning system: if something that
should have happened this week did not, say so first.

## Hard rules

1. **PAUSE check first.** If `PAUSE` exists, still write the report (it is the one routine that
   runs during a pause) but make the first line "⏸ PAUSE 상태 — 자동 작업 정지 중. 원인: <PAUSE 파일 내용 첫 줄>".
   Do nothing else.
2. **Read-only except the issue.** No PRs, no commits, no label changes on PRs. Just one issue.
3. **Tools.** GitHub + web (only to check the storefront/RSS URLs return 200 if the `health`
   Action's latest run is missing). No secrets, no commerce APIs.
4. **Never merge or recommend skipping review.** The report points to PRs; the human decides.
5. **Numbers only from files/Actions.** Sales/views come from `business/etsy/stats/`. If the
   file for this week is missing, write "판매 데이터 없음(etsy-sync 미실행)" instead of a number.
   Never estimate.
6. Exactly one issue per week, titled `주간 리포트 YYYY-WW`. If it exists, update it instead.

## Procedure

1. Collect, for the last 7 days:
   - `business/etsy/stats/*.json` (sales count, revenue USD, views, favorites per listing; totals)
   - PRs: opened / merged / closed / still open, with labels (`factory`, `content`, `needs-human`, `needs-fix`)
   - Issues opened by Actions (`etsy-publish`, `shopify-publish`, `etsy-sync`, `health`) and any
     "수동 동기화 필요" / "재인증 필요" / "etsy-queue" issues
   - Latest run status of each workflow in `.github/workflows/` (success/failure/missing)
   - Whether `factory/briefs/<this week>.json`, a `factory/<week>` PR and a `content/<week>` PR exist
   - Contents of `factory/etsy-queue/` and `business/outbox/` (things the human must upload)
   - Token age: if the `health` Action's issue or output mentions the Etsy refresh token age ≥ 80 days, flag it
2. Compute week-over-week deltas where last week's stats file exists.
3. Write the issue body (Korean):

```
## 주간 리포트 YYYY-WW (MM/DD ~ MM/DD)

1. 매출: Etsy N건 $X.XX (지난주 대비 ±), Shopify N건 $X.XX / 조회 N, 즐겨찾기 N
2. 이번 주 신제품: <handle> — PR #N, QC NN점, 검수 <승인/사람 확인 필요/수정 요청>
3. 블로그: 2편 PR #N (<제목1>, <제목2>) — 상태
4. 게시: Etsy 리스팅 N건 활성화 / Shopify 글 N건 게시 / 실패 N건
5. ⚠ 사람이 할 일 (일요일): [ ] PR #N 머지 검토  [ ] needs-human PR #N 본문 읽기  [ ] etsy-queue 업로드 N개  [ ] 재인증  [ ] 메시지 답장
6. 자동화 상태: scan ✅ build ✅ review ✅ optimize ✅ etsy-sync ✅/❌ health ✅/❌ (실패 시 이슈 #N)
7. 리스팅: 활성 N개, 60일 무판매 N개, 이번 주 교체 제안 N개
8. Pinterest/RSS: 피드 200 ✅, 최근 글 이미지 포함 ✅ (health Action 기준)
9. 비용 메모: 이번 주 신규 리스팅 수수료 $0.20×N, 특이사항
10. 한 줄 판단: 정상 / 주의(이유) / PAUSE 권고(이유) — 9장 규칙 중 해당 항목
```
   Then an English appendix: table of listing-level numbers and links to every PR/issue mentioned.
4. If any of these is true, prefix the title with `⚠`: a workflow failed twice in a row, no
   `factory/<week>` PR exists by Saturday, stats file missing 2+ days, PAUSE present, refund or
   dispute mentioned in any issue.

## Output

- Issue `주간 리포트 YYYY-WW` (label `report`).

## Done checklist

- [ ] One issue, Korean 10 lines + English appendix
- [ ] Every number traceable to a file or Action run; "데이터 없음" where not
- [ ] Sunday to-do checklist (line 5) lists every open PR and queue item
- [ ] ⚠ prefix applied when a warning condition holds
- [ ] No merges, commits or label changes made
