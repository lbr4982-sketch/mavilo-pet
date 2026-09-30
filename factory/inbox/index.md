# factory/inbox — 사람이 쓰는 곳

여기는 **사장님만** 씁니다. AI(Routine)는 읽기만 합니다.

| 파일/폴더 | 무엇을 | 누가 읽나 |
|---|---|---|
| `messages.md` | Etsy·Shopify에서 받은 문의를 복사해 붙임(날짜, 채널, 주문번호, 원문). 구매자 이름·주소는 적지 않음 | `night-desk` → `queue/replies/` 답장 초안 |
| `custom-orders/<주문번호>.md` | 맞춤 주문의 개인화 문구(반려동물 이름·품종·나이·고민만) | `night-desk` → `queue/custom/<주문번호>/` |
| `daily-log/YYYY-MM-DD.md` | 하루 일지. `night-desk`가 빈 표를 만들어 두고 사장님이 21시에 숫자를 채움 | `weekly-report`, `night-pins`, `night-videos` |

## 체크박스 규칙

- `messages.md`의 각 문의 앞에 `☐`. 답장을 보냈으면 `☑`. `night-desk`는 `☐`만 처리합니다.
- `custom-orders/`의 파일 첫 줄에 `상태: ☐ 대기 / ☑ 전달 완료`. 전달 완료 후 7일 지나면 `weekly-report`가 `factory/queue/_archive/custom-orders/`로 옮깁니다.
- 일지는 옮기지 않습니다(리포트의 원천이므로 계속 쌓임).
