# queue/videos — 영상 대본 대기열

`night-videos`가 매일 02:10에 `YYYY-MM-DD/` 폴더를 만듭니다. 대본 2편(`NN-<handle>-<format>.md`, 설계서 4장 형식) + 자막 `.srt` + `frames/<handle>-pNN.png`(1080×1920, CapCut에 바로 끌어다 쓰는 PDF 페이지). 2편 중 1편만 오늘 제작하고 나머지는 토요일 몰아찍기 재료입니다.

## 날짜 폴더

| 날짜 | 대본 | 상태 |
|---|---|---|
| [2026-10-02](2026-10-02/) | 01 cat-enrichment-guide · myth, 02 puppy-training-plan · list-3 | ☐ 첫날 대기열(수동 생성) |

## 체크박스 규칙

- `☐` 아직 올리지(쓰지) 않음 → 올린 뒤 `☑`로 바꿉니다(GitHub 웹 연필 아이콘). 탈락은 `☒` + 사유 한 줄.
- 다음 밤 Routine은 이 파일을 읽어 `☐`는 재활용하고 `☑`는 다시 만들지 않습니다.
- 7일 지난 날짜 폴더는 `weekly-report`가 `factory/queue/_archive/`로 옮깁니다. 아카이브는 편집하지 않습니다.
- 날짜 폴더 이름은 **올릴 날(KST)**입니다.
