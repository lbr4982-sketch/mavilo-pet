# factory/routines — Claude Routine 프롬프트 (v2: 밤 3개 + 주간 3개)

이 폴더의 Markdown 파일은 Claude **Routine**(예약 실행, 매번 새 세션)에 그대로 넣는 프롬프트입니다.
프롬프트 본문은 영어(실행하는 Claude용), 사장님이 보는 산출물(대기열 `index.md`·PR 요약·이슈)은 한국어입니다.
설계는 `business/BLUEPRINT-v2.md` 2장·4장. 밤 Routine은 01~05시(KST)에 돌아 **08시 전에 `factory/queue/`를 채우고**, 사장님이 아침에 읽고 직접 게시합니다.

## v2 Routine 6개

| 파일 | 실행 (KST) | cron (`create_trigger`) | 하는 일 | 산출물 |
|---|---|---|---|---|
| `night-pins.md` | 매일 01:10 | `CRON_TZ=Asia/Seoul 10 1 * * *` | 핀 20장(1000×1500) + 문안 + 게시 순서표. 어제 `index.md`의 `☑/☒`를 읽어 잘 된 형식 2배 | `factory/queue/pins/YYYY-MM-DD/` (커밋) |
| `night-videos.md` | 매일 02:10 | `CRON_TZ=Asia/Seoul 10 2 * * *` | 영상 대본 2편 + `.srt` + `frames/`(1080×1920 PDF 페이지) | `factory/queue/videos/YYYY-MM-DD/` (커밋) |
| `night-desk.md` | 매일 03:10 | `CRON_TZ=Asia/Seoul 10 3 * * *` | 고객 답장 초안, 맞춤 주문 PDF 초안 + QC, 오늘 일지 빈 표 | `queue/replies/`, `queue/custom/`, `inbox/daily-log/` (커밋) |
| `weekly-product.md` | 월 04:10 | `CRON_TZ=Asia/Seoul 10 4 * * 1` | 수요조사 → 제작 → 자체 검수를 한 세션에서. 신제품 팩 1개(사람 업로드용) | `factory/queue/listings/<handle>/` + PR `factory/YYYY-WW` |
| `weekly-content.md` | 목 04:10 | `CRON_TZ=Asia/Seoul 10 4 * * 4` | 블로그 2편 + 이메일 1통 + 키워드·트렌드 브리프 + 60일 무판매 교체안 | `queue/blog/`, `queue/email/`, `factory/briefs/trends-*.md` + PR `content/YYYY-WW` |
| `weekly-report.md` | 일 05:10 **그리고** 매월 1일 05:10 | `CRON_TZ=Asia/Seoul 10 5 * * 0` **+** `CRON_TZ=Asia/Seoul 10 5 1 * *` (같은 프롬프트로 2개 등록) | 일지 7일치 → 한국어 주간 리포트 이슈. 1일 실행분은 손익표·중단 판정 추가. 7일 지난 대기열 `_archive/`로 | 이슈 `주간 리포트 YYYY-WW`, `월간 손익 YYYY-MM` |

정각(:00)을 피해 :10으로 잡은 이유: 예약 실행이 몰리는 시각을 피하기 위함.

### v1 → v2 대응

| v1 파일 (보관, 등록 금지) | v2 |
|---|---|
| `factory-scan.md` · `factory-build.md` · `factory-review.md` | `weekly-product.md` (3개를 한 세션으로) |
| `factory-optimize.md` | 핀 부분 → `night-pins.md`(매일) / 블로그·교체안 → `weekly-content.md` |
| `factory-report.md` · `factory-finance.md` | `weekly-report.md` (데이터 원천이 Etsy API가 아니라 사장님 일지) |
| (없음) | `night-videos.md`, `night-desk.md` 신설 |

v1 파일은 첫 줄에 "superseded" 표시를 달아 그대로 두었습니다(스키마·절차를 v2가 참조함). GitHub Actions(`etsy-publish` 등)와 Etsy·Shopify 비밀키는 v2에서 쓰지 않습니다.

## 공통 규칙 (모든 프롬프트 첫 부분에 들어 있음)

1. 저장소 루트에 `PAUSE` 파일이 있으면 즉시 종료 (`weekly-report`만 "PAUSE 상태" 한 줄 리포트를 남김).
2. 도구는 GitHub(저장소 읽기·쓰기, PR/이슈)와 웹검색만. Etsy·Shopify·Pinterest·TikTok API 호출 금지, 비밀키 접근 금지.
3. **Routine은 절대 게시·머지하지 않음.** 핀·영상·리스팅·블로그는 사장님이 손으로 올립니다.
4. `factory/inbox/`는 읽기 전용(예외: `night-desk`가 오늘 일지 빈 표를 새로 만드는 것만).
5. 신제품은 **주 1개**. 밀렸다고 두 개 만들지 않음. 맞춤 상품 3종(설계서 6장)이 없으면 그것부터.
6. 투약·백신 일정·진단 없음. 관련 내용이 있으면 `needs-human` 라벨 → 사람이 본문을 읽은 뒤에만 머지.
7. AI 고지·수의사 고지는 `factory/COPY.md`의 문구를 **글자 그대로**.
8. 밤 Routine은 가볍게(5만~15만 토큰). 아침에 대기열이 비어 있으면 한도 초과 신호(`night-desk`가 일지에 ⚠ 표시).

## Routine 만드는 법 — 사장님이 채팅에 붙여 넣을 문장 (한 번에 하나씩)

Routine은 Claude Code(claude.ai/code) 대화형 세션에서 `create_trigger` 도구로 만듭니다. 이 저장소가 연결된 클라우드 환경에서 열린 세션에서 아래를 그대로 붙여 넣으세요. 프롬프트는 **파일 내용**을 넣습니다(경로만 넣으면 새 세션이 못 읽을 수 있음).

```
factory/routines/night-pins.md 파일 내용을 프롬프트로 하는 Routine을 만들어 주세요. 이름 night-pins, cron "CRON_TZ=Asia/Seoul 10 1 * * *", 매번 새 세션(create_new_session_on_fire=true), initiation은 human_request, 알림은 push+email, 커넥터는 GitHub만 허용하세요.
```
```
factory/routines/night-videos.md 파일 내용을 프롬프트로 하는 Routine을 만들어 주세요. 이름 night-videos, cron "CRON_TZ=Asia/Seoul 10 2 * * *", 매번 새 세션, initiation은 human_request, 알림은 push+email, 커넥터는 GitHub만 허용하세요.
```
```
factory/routines/night-desk.md 파일 내용을 프롬프트로 하는 Routine을 만들어 주세요. 이름 night-desk, cron "CRON_TZ=Asia/Seoul 10 3 * * *", 매번 새 세션, initiation은 human_request, 알림은 push+email, 커넥터는 GitHub만 허용하세요.
```
```
factory/routines/weekly-product.md 파일 내용을 프롬프트로 하는 Routine을 만들어 주세요. 이름 weekly-product, cron "CRON_TZ=Asia/Seoul 10 4 * * 1", 매번 새 세션, initiation은 human_request, 알림은 push+email, 커넥터는 GitHub만 허용하세요.
```
```
factory/routines/weekly-content.md 파일 내용을 프롬프트로 하는 Routine을 만들어 주세요. 이름 weekly-content, cron "CRON_TZ=Asia/Seoul 10 4 * * 4", 매번 새 세션, initiation은 human_request, 알림은 push+email, 커넥터는 GitHub만 허용하세요.
```
```
factory/routines/weekly-report.md 파일 내용을 프롬프트로 하는 Routine을 만들어 주세요. 이름 weekly-report, cron "CRON_TZ=Asia/Seoul 10 5 * * 0", 매번 새 세션, initiation은 human_request, 알림은 push+email, 커넥터는 GitHub만 허용하세요.
```
```
같은 factory/routines/weekly-report.md 내용으로 Routine을 하나 더 만들어 주세요. 이름 weekly-report-monthly, cron "CRON_TZ=Asia/Seoul 10 5 1 * *", 매번 새 세션, initiation은 human_request, 알림은 push+email, 커넥터는 GitHub만 허용하세요.
```

Claude가 내부적으로 호출하는 형태(참고용):

```
create_trigger(
  name = "night-pins",
  cron_expression = "CRON_TZ=Asia/Seoul 10 1 * * *",
  create_new_session_on_fire = true,
  initiation = "human_request",
  connectors = ["GitHub"],
  notifications = {"push": true, "email": true},
  prompt = <factory/routines/night-pins.md 전문>
)
```

주의:
- 파일이 바뀌면 `update_trigger`로 프롬프트를 교체합니다(삭제 후 재생성하면 실행 기록이 사라짐).
- `list_triggers`로 7개(weekly-report 2개 포함)가 모두 `enabled`인지 확인합니다. 첫날은 대기열을 수동으로 만들어 두었으므로(`factory/queue/pins/2026-10-02/`, `videos/2026-10-02/`) `fire_trigger`는 필요 없습니다. Day 2 밤부터 자동으로 채워집니다.
- 멈추려면: 저장소 루트에 `PAUSE` 파일을 만들거나(모든 자동화 정지), `update_trigger(enabled=false)`로 개별 Routine을 끕니다.
- v1 Routine(`factory-*`)이 등록되어 있으면 `update_trigger(enabled=false)`로 끕니다. 삭제하지 않아도 됩니다.

## 파일 규약 요약

| 경로 | 만드는 주체 | 형식 |
|---|---|---|
| `factory/queue/pins/YYYY-MM-DD/{NN-<handle>-<slug>.png, pins.json, index.md}` | night-pins | `factory/render_pins.py` 스펙 (첫날 예: `2026-10-02/`) |
| `factory/queue/videos/YYYY-MM-DD/{NN-<handle>-<format>.md, .srt, frames/<handle>-pNN.png, index.md}` | night-videos | 설계서 v2 4장 대본 형식 |
| `factory/queue/replies/YYYY-MM-DD.md`, `factory/queue/custom/<주문번호>/` | night-desk | `night-desk.md` 2~3단계 |
| `factory/inbox/daily-log/YYYY-MM-DD.md` (빈 표) | night-desk (숫자는 사람) | `night-desk.md` 4단계 |
| `factory/briefs/YYYY-WW.json`, `factory/queue/listings/<handle>/` | weekly-product | 브리프 스키마는 `factory-scan.md`, 팩은 `business/etsy/listings/`와 동일 |
| `factory/queue/blog/YYYY-WW/`, `factory/queue/email/YYYY-WW.md`, `factory/briefs/trends-YYYY-WW.md`, `factory/listings/<handle>.refresh.json` | weekly-content | `weekly-content.md` |
| 이슈 `주간 리포트 YYYY-WW` / `월간 손익 YYYY-MM`, `factory/queue/_archive/` | weekly-report | `weekly-report.md` |
| 브랜치 | `factory/YYYY-WW`, `content/YYYY-WW`, `finance/YYYY-MM` | ISO 주 번호 (예: 2026-W41) |
