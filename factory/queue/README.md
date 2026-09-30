# factory/queue — 아침 대기열

밤 Routine(`factory/routines/night-*.md`, `weekly-*.md`)이 **다음 날 올릴 것**을 여기에 써 두고,
사장님이 아침에 읽고 하루 동안 직접 게시합니다. AI는 절대 게시하지 않습니다(설계서 v2 2장·4장).

## 폴더

| 폴더 | 만드는 Routine | 내용 |
|---|---|---|
| `pins/YYYY-MM-DD/` | `night-pins` (매일 01:10) | 핀 20장 `NN-<handle>-<slug>.png`(1000×1500) + `pins.json`(제목·설명·대체텍스트·링크·보드·키워드) + `index.md`(게시 순서표) |
| `videos/YYYY-MM-DD/` | `night-videos` (매일 02:10) | 대본 `NN-<handle>-<format>.md` 2편 + `.srt` + `frames/<handle>-pNN.png`(1080×1920) |
| `replies/YYYY-MM-DD.md` | `night-desk` (매일 03:10) | `factory/inbox/messages.md`의 새 문의별 영어 답장 초안 + 한국어 요약 |
| `custom/<주문번호>/` | `night-desk` | 맞춤 주문 PDF·HTML 초안 + `review.md` |
| `listings/<handle>/` | `weekly-product` (월 04:10) | 신제품 팩(`business/etsy/listings/`와 같은 형식). PR 머지 후 사람이 Etsy에 업로드 |
| `blog/YYYY-WW/` | `weekly-content` (목 04:10) | 블로그 2편 `.html` + `.md` |
| `email/YYYY-WW.md` | `weekly-content` | 이메일 1통 |
| `_archive/` | `weekly-report` (일 05:10) | 7일 지난 날짜 폴더가 여기로 옮겨짐 |

사람이 쓰는 곳은 `factory/inbox/`입니다(문의 복사, 맞춤 주문 개인화 문구, 하루 일지). AI는 거기서 읽기만 합니다.

## 아침 검토 흐름 (설계서 3장, 07:30~08:00)

1. `factory/queue/pins/<오늘>/index.md`를 엽니다. 핀 20장을 훑어 **틀린 사실·어색한 영어·잘린 글자**가 있는 것을 골라냅니다(보통 2~3장 탈락). 탈락 사유를 `index.md`에 한 줄 적습니다.
2. `factory/queue/videos/<오늘>/`의 대본 2편 중 오늘 만들 1편을 고릅니다. 안 고른 1편은 토요일 몰아찍기 재료입니다.
3. `factory/queue/replies/<오늘>.md`의 답장 초안을 확인합니다. 환불·건강 관련 표시가 있는 답은 직접 판단합니다.
4. 08:00~09:00 게시 창 1: 영상 1편(TikTok → Reels → Shorts, AI 라벨 확인) + 핀 8~10장(보드 3~4개 분산, 10~15분 간격).
5. 13:30 핀 5장, 20:00~21:00 게시 창 2: 핀 5~8장(하루 합계 15~25장).
6. 올린 것에는 `index.md`에서 `☐`를 `☑`로 바꿉니다(GitHub 웹에서 연필 아이콘). 조회·저장 수는 나중에 같은 줄에 적습니다.
7. 21:00 일지: `factory/inbox/daily-log/<오늘>.md`(밤에 AI가 빈 표를 만들어 둠)에 숫자와 한 줄 소감을 채웁니다. **이 파일이 AI 리포트의 유일한 원천**입니다.

## 체크박스 규칙

- `☐` = 아직 올리지 않음 / `☑` = 올림. 다음 밤 Routine은 이 표시를 읽어 **안 올린 것은 재활용, 올린 것은 중복 생성 금지**.
- 탈락시킨 항목은 `☒`로 바꾸고 사유 한 줄(예: `☒ 07 — 글자 잘림`). 다음 밤 같은 실수를 피하는 데 씁니다.
- 날짜는 **올릴 날(KST)** 기준입니다. Routine은 01~05시에 돌지만 폴더 이름은 그날 날짜입니다.
- 7일이 지난 폴더는 `weekly-report`가 `_archive/`로 옮깁니다. 아카이브 안 파일은 편집하지 않습니다.
- 비상 정지: 저장소 루트에 `PAUSE` 파일을 만들면 모든 Routine이 즉시 종료합니다.
