# Etsy 리스팅 팩 (business/etsy/)

기존 5개 제품 + 번들 1개를 Etsy에 **사람이 직접 올릴 때** 쓰는 붙여넣기용 팩입니다. (설계서 5장 0~2단계. Etsy Seller App API가 승인되면 같은 JSON을 `etsy-publish` Action이 읽습니다.)

```
business/etsy/
├── README.md                       ← 이 문서
└── listings/<handle>/
    ├── listing.json                ← 제목·태그 13개·설명·가격·카테고리·속성 힌트
    └── images/01-*.png … 09-*.png  ← 2000×2000 리스팅 이미지 9장 (순서대로 업로드)
```

이미지 재생성: `python3 factory/render_mockups.py <handle>` 또는 `--all` (PDF → pymupdf → HTML → 헤드리스 Chromium, 약 15초/제품).

## 업로드 순서 (리스팅 1개당 약 3분)

Etsy 판매자 화면 → **Listings → Add a listing**. `listing.json`을 텍스트 편집기로 열어 두고 항목별로 붙여넣습니다.

| Etsy 폼 항목 | 넣을 값 (listing.json 키) |
|---|---|
| **Photos** | `images/` 폴더의 01 → 09 순서로 9장 모두 드래그. 01이 썸네일이 됩니다 |
| **Video** | 비움 |
| **Title** | `title` (140자 이내로 검증됨) |
| **About this listing** → Who made it? | **I did** (`who_made`) |
| → What is it? | **A finished product** (`is_supply: false`) |
| → When did you make it? | **2020 - 2026** (`when_made`) |
| **Category** | `taxonomy_hint` 경로를 검색창에 입력해 선택. 없으면 `taxonomy_note`의 대안 |
| **Type** | **Digital files** (`type: download`) — 이걸 골라야 Digital files 업로드란이 생김 |
| **Description** | `description` 전체 복사·붙여넣기. 줄바꿈이 그대로 살아야 함. "MADE WITH CARE" 단락(생성형 AI 사용 고지 + 사람 검토 + 수의학적 조언 아님)은 **절대 지우지 말 것** — Etsy Creativity Standards 요건 |
| **Attributes** (Occasion, Recipient 등) | `attributes_hint` 참고. 없는 값은 건너뜀 |
| **Tags** | `tags` 13개를 하나씩 입력 (각 20자 이내로 검증됨) |
| **Materials** | `digital file`, `pdf` |
| **Price** | `price_usd` (매장 통화 USD 기준) |
| **Quantity** | 999 |
| **Digital files** | `file` 경로의 PDF 업로드. 번들은 PDF 5개 모두 (Etsy는 파일 5개·각 20MB까지 허용) |
| **Personalization** | 끔 |
| **Section** | `section_hint`의 섹션 선택 (아래 참고, 없으면 새로 만들기) |
| **Renewal options** | Automatic (판매 시 자동 갱신, $0.20) |
| **Publish** | 리스팅당 $0.20 청구 |

발행 전 미리보기에서 확인할 것: (1) 첫 이미지가 잘리지 않는지 (2) 설명의 AI 고지 단락이 있는지 (3) 디지털 파일이 붙어 있는지.

## 권장 매장 섹션 (Shop sections)

Etsy는 섹션 20개까지 허용합니다. 처음엔 6개만 만듭니다.

| 섹션 이름 | 들어가는 리스팅 |
|---|---|
| **Dog Training** | puppy-training-plan (이후 주간 신제품: 30일 플랜 계열) |
| **Dog Care** | dog-grooming-guide (그루밍·계절 안전 계열) |
| **Cat Care** | cat-enrichment-guide (놀이팩·고양이 계열) |
| **Pet Health** | pet-health-record-book (기록장 계열) |
| **New Pet Essentials** | new-pet-starter-checklist (체크리스트 계열) |
| **Bundles** | complete-pet-parent-bundle (월 1회 번들 제안 PR로 추가) |

## 주의

- 6개는 사람이 직접 올려서 "판매자가 직접 만든 매장" 기록을 남기는 것이 목적입니다(설계서 5장 2단계). API 자동화는 7번째 제품부터.
- 태그·제목을 바꿀 땐 `listing.json`을 먼저 고치고 Etsy에 반영하세요. 60일 무판매 리스팅 최적화 PR이 이 파일을 기준으로 diff를 냅니다.
- 판매 통계는 `business/etsy/stats/`에 월 1회 CSV로 내려받아 두면 월요일 수요조사 Routine이 참고합니다.
