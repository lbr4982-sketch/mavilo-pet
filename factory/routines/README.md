# factory/routines — Claude Routine 프롬프트 6개

이 폴더의 Markdown 파일은 Claude **Routine**(예약 실행, 매번 새 세션)에 그대로 넣는 프롬프트입니다.
프롬프트 본문은 영어(실행하는 Claude용), 사장님이 보는 산출물(PR 요약·이슈·리뷰 코멘트)은 한국어입니다.

| 파일 | 실행 시각 (KST) | cron (`create_trigger`) | 하는 일 | 산출물 |
|---|---|---|---|---|
| `factory-scan.md` | 월 09:10 | `CRON_TZ=Asia/Seoul 10 9 * * 1` | 수요 조사 → 이번 주 제품 후보 1개 | `factory/briefs/YYYY-WW.json` |
| `factory-build.md` | 화 09:10 | `CRON_TZ=Asia/Seoul 10 9 * * 2` | HTML→PDF·표지·목업, QC 점수, 리스팅 JSON | PR `factory/YYYY-WW` |
| `factory-review.md` | 수 09:10 | `CRON_TZ=Asia/Seoul 10 9 * * 3` | 사실 확인·안전·고지 문구·유사도 검수 | PR 리뷰 + 라벨 (`reviewed` / `needs-human` / `needs-fix`) |
| `factory-optimize.md` | 금 09:10 | `CRON_TZ=Asia/Seoul 10 9 * * 5` | 블로그 2편 + 핀 이미지, 60일 무판매 리스팅 교체 제안 | PR `content/YYYY-WW` |
| `factory-report.md` | 토 09:10 | `CRON_TZ=Asia/Seoul 10 9 * * 6` | 한국어 주간 리포트 | 이슈 `주간 리포트 YYYY-WW` |
| `factory-finance.md` | 매월 1일 09:10 | `CRON_TZ=Asia/Seoul 10 9 1 * *` | 손익표, 9장 중단 규칙 판정, 킬/번들/시즌 제안 | 이슈 `월간 손익 YYYY-MM` + PR `finance/YYYY-MM` |

정각(:00)을 피해 :10으로 잡은 이유: 예약 실행이 몰리는 시각을 피하기 위함(설계서 4장).

## 공통 규칙 (모든 프롬프트 첫 부분에 들어 있음)

1. 저장소 루트에 `PAUSE` 파일이 있으면 즉시 종료 (`factory-report`만 "PAUSE 상태" 한 줄 리포트를 남김).
2. 신제품은 **주 1개**. 밀렸다고 두 개 만들지 않음.
3. 도구는 GitHub(저장소 읽기·쓰기, PR/이슈)와 웹검색만. Etsy·Shopify·Pinterest API 호출 금지, 비밀키 접근 금지.
4. 모든 PR 본문: 한국어 5줄 요약 + 표지 이미지 + QC 점수 (`factory/COPY.md`의 `PR_SUMMARY_TEMPLATE`).
5. 투약·백신 일정·진단 내용이 있으면 `needs-human` 라벨 → 사람이 본문을 읽은 뒤에만 머지.
6. 상품 설명에는 `factory/COPY.md`의 AI 고지·수의사 고지 문구를 **글자 그대로** 포함.
7. Routine은 절대 머지하지 않음. 머지는 사장님 클릭만.

## Routine 만드는 법

Routine은 Claude Code(claude.ai/code) 대화형 세션에서 `create_trigger` 도구로 만듭니다. 이 저장소가 연결된
클라우드 환경(environment)에서 실행되도록, **그 환경에서 열린 세션**에서 아래를 요청하세요.

사장님이 채팅에 붙여 넣을 문장(한 번에 하나씩):

```
factory/routines/factory-scan.md 파일 내용을 프롬프트로 하는 Routine을 만들어 주세요.
이름 factory-scan, cron "CRON_TZ=Asia/Seoul 10 9 * * 1", 매번 새 세션(create_new_session_on_fire=true),
initiation은 human_request, 알림은 push+email로 켜 주세요. 커넥터는 GitHub만 허용하세요.
```

같은 식으로 `factory-build`(`10 9 * * 2`), `factory-review`(`10 9 * * 3`), `factory-optimize`(`10 9 * * 5`),
`factory-report`(`10 9 * * 6`), `factory-finance`(`10 9 1 * *`)를 만듭니다.

Claude가 내부적으로 호출하는 형태(참고용):

```
create_trigger(
  name = "factory-scan",
  cron_expression = "CRON_TZ=Asia/Seoul 10 9 * * 1",
  create_new_session_on_fire = true,
  initiation = "human_request",
  connectors = ["GitHub"],
  notifications = {"push": true, "email": true},
  prompt = <factory/routines/factory-scan.md 전문>
)
```

주의:
- 프롬프트는 파일 **내용**을 넣습니다(파일 경로만 넣으면 새 세션이 저장소를 못 읽을 수 있음). 파일이 바뀌면
  `update_trigger`로 프롬프트를 교체합니다(삭제 후 재생성하면 실행 기록이 사라짐).
- `list_triggers`로 6개가 모두 `enabled`인지 확인하고, `fire_trigger`로 `factory-scan`을 1회 수동 실행해 첫 브리프를 만듭니다(설계서 5장 7번).
- 실행 비용: 각 15만~50만 토큰. 구독 한도를 넘으면 Routine이 조용히 실패하므로 **토요일 리포트가 안 오면** 그 신호입니다.
- 멈추려면: 저장소 루트에 `PAUSE` 파일을 만들거나(모든 자동화 정지), `update_trigger(enabled=false)`로 개별 Routine을 끕니다.

## 파일 규약 요약

| 경로 | 만드는 주체 | 형식 |
|---|---|---|
| `factory/briefs/YYYY-WW.json` | scan (finance는 `YYYY-MM-bundle-*.json`, `YYYY-MM-seasonal.json`) | `factory-scan.md` 하단 스키마 |
| `factory/listings/<handle>.json` | build | `factory-build.md` 하단 스키마 (Etsy 리스팅 팩 `listing.json`과 동일 필드) |
| `factory/listings/<handle>.refresh.json` | optimize | 제목·태그·첫 이미지 교체 제안 |
| `factory/listings/<handle>.deactivate.json` | finance | 90일 킬 제안 |
| `factory/qc-reports/<handle>.json` | build (`factory/qc.py --json`) | QC 리포트 |
| `business/blog/<handle>.md`, `business/pins/<handle>/` | optimize | 블로그 글 + 핀 이미지 |
| 브랜치 | `factory/YYYY-WW`, `content/YYYY-WW`, `finance/YYYY-MM` | ISO 주 번호 (예: 2026-W41) |
