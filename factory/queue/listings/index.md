# queue/listings — 신제품 팩 대기열

`weekly-product`가 월요일 04:10에 `<handle>/` 폴더로 신제품 팩을 만들고 PR을 엽니다. 형식은 `business/etsy/listings/<handle>/`와 같습니다(`listing.json` + `images/` 9장 2000×2000 + PDF 경로). **PR을 머지한 뒤** 사장님이 Etsy에 직접 업로드하고(3분/개), 업로드가 끝나면 팩을 `business/etsy/listings/`로 옮깁니다. 맞춤 상품 팩은 `<handle>-personalized/`.

## 팩 목록

| handle | PR | 상태 |
|---|---|---|
| (아직 없음) | | |

## 체크박스 규칙

- `☐` 아직 올리지(쓰지) 않음 → 올린 뒤 `☑`로 바꿉니다(GitHub 웹 연필 아이콘). 탈락은 `☒` + 사유 한 줄.
- 다음 밤 Routine은 이 파일을 읽어 `☐`는 재활용하고 `☑`는 다시 만들지 않습니다.
- 7일 지난 날짜 폴더는 `weekly-report`가 `factory/queue/_archive/`로 옮깁니다. 아카이브는 편집하지 않습니다.
- 날짜 폴더 이름은 **올릴 날(KST)**입니다.
