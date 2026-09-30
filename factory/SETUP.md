# factory/SETUP.md — 첫 매출까지 사람이 하는 1회 설정 (클릭 가이드)

설계서(`business/BLUEPRINT.md`) 5장 1~7단계를 클릭 단위로 풀어 쓴 것입니다. 총 3~4시간, 한 번만 합니다.
메뉴 이름은 2026년 9월 기준이며 플랫폼이 자주 바꿉니다. **(메뉴 위치는 바뀔 수 있음)** 표시가 있는 항목은
확인이 안 된 부분이니 이름이 조금 달라도 비슷한 메뉴를 찾으세요.

### 절대 규칙
- **비밀키(keystring, secret, token, password)는 채팅창·이슈·PR·이메일에 절대 붙이지 않습니다.** 붙이는 곳은 오직
  GitHub 저장소의 **Settings → Secrets and variables → Actions → New repository secret** 한 곳입니다.
- AI(Claude)에게 비밀키를 알려 달라거나 보여 달라고 하지 않습니다. AI는 비밀키를 볼 필요가 없습니다.
- 정지·경고 통지가 오면 항소 전에 저장소 루트에 `PAUSE` 파일을 만듭니다(모든 자동화 정지).

### GitHub 비밀키 이름표 (최종적으로 이 11개가 있어야 합니다)

| 비밀키 이름 | 어디서 얻나 | 단계 |
|---|---|---|
| `ETSY_KEYSTRING` | Etsy 개발자 포털 → Your Apps → 앱 → Keystring | 3 |
| `ETSY_SHARED_SECRET` | 같은 화면 → Shared secret | 3 |
| `ETSY_REFRESH_TOKEN` | OAuth 동의 후 받은 refresh_token (Action이 90일마다 갱신) | 3 |
| `ETSY_SHOP_ID` | Shop Manager URL 또는 `getShopByOwnerUserId` 응답의 숫자 | 3 |
| `GH_SECRETS_PAT` | GitHub → Settings → Developer settings → Fine-grained token (Secrets: Read and write) | 3 |
| `SHOPIFY_STORE_DOMAIN` | `xxxx.myshopify.com` (Shopify 관리자 주소) | 4 |
| `SHOPIFY_CLIENT_ID` | Shopify Dev Dashboard → 앱 → Settings → Client ID | 4 |
| `SHOPIFY_CLIENT_SECRET` | 같은 화면 → Client secret | 4 |
| `SHOPIFY_CLI_THEME_TOKEN` | Theme Access 앱이 이메일로 보낸 `shptka_...` 비밀번호 | 4 |
| `SHOPIFY_FLAG_STORE` | `SHOPIFY_STORE_DOMAIN`과 같은 값 (Shopify CLI용) | 4 |
| `PINTEREST_RSS_URL` (선택) | `https://<도메인>/blogs/news?view=rss` — health Action이 200 확인 | 6 |

GitHub에 넣는 방법(공통): 저장소 페이지 → **Settings** 탭 → 왼쪽 "Security" 아래 **Secrets and variables → Actions** →
**Secrets** 탭 → **New repository secret** → Name에 위 이름을 정확히, Secret에 값 → **Add secret**.
(터미널: `gh secret set ETSY_KEYSTRING` 후 값 입력.)

---

## 1단계. Etsy 매장 개설 + Payoneer (60분) — 오늘 시작

1. **etsy.com → Sell on Etsy → Get started**. 매장 이름은 `Mavilocco`(개설 완료, https://mavilocco.etsy.com). 매장 국가는 대한민국.
2. 첫 리스팅을 하나 만들라고 요구하면 임시로 `business/etsy/listings/new-pet-starter-checklist/`의 팩으로 만듭니다(2단계에서 마저 채움).
3. **결제(Etsy Payments) 설정**: 한국은 **Payoneer 필수**입니다. Etsy가 "Connect your Payoneer account"를 띄우면
   - Payoneer 계정이 없으면 그 자리에서 **Create new** → 이름·주소·신분증(여권 또는 주민등록증)·**한국 은행 계좌** 등록(KYC, 1~3영업일).
   - 있으면 **Sign in** → 연결. Payoneer의 국가와 Etsy 매장 국가가 같아야 합니다.
4. **본인 인증(Persona)**: 신분증 촬영 + 셀카. 여권이 가장 무난합니다.
5. **매장 개설비**: $15(지역에 따라 최대 $29, **환불 불가**) 카드 결제.
6. **매장 통화를 USD로**: **Shop Manager → Finances → Payment settings → Currency → United States Dollar → Change Shop Currency**.
   (리스팅 통화가 USD가 아니면 매 판매에 2.5% 환전 수수료가 붙습니다.)
7. **Offsite Ads 거부**: **Shop Manager → Settings → Offsite Ads** → "Stop promoting my products" (연매출 $10,000 미만만 가능).
8. **Share & Save 참여**: **Shop Manager → Marketing → Share & Save → Join now** → 약관 동의. 이후 이 화면의 추적 링크를
   블로그·핀에 쓰면 해당 주문 수수료 4%가 환급됩니다. 링크는 `business/etsy/catalog.json`의 `share_save_url`에 기록해 두면 optimize Routine이 씁니다.
9. **매장 정책**: **Shop Manager → Settings → Policy settings** → Digital items 정책에 `business/support/policies.md`의 Refund policy 붙이기. (메뉴 위치는 바뀔 수 있음)
10. **About 섹션**: 1인 매장, 직접 기획·검토, AI 도구 활용을 솔직하게 씁니다(Creativity Standards 대응). 예: "I plan, direct and review every guide myself; I use AI writing tools as part of the process and say so in every listing."

> ⚠ 한국 신규 판매자는 개설 직후 자동 정지되는 사례가 잦습니다. 정지 메일이 오면 `business/support/replies.md` 10번 구조로 항소 1회. 60일 내 복구가 안 되면 설계서 6장 Plan B.
> 90일 미만 계정은 정산 유보가 걸리므로 첫 입금은 늦습니다. Etsy → Payoneer 입금은 매주 월요일, Payoneer → 한국 계좌 출금은 약 1.2% 수수료·2~5영업일.

## 2단계. 첫 6개 리스팅 직접 업로드 (25분)

6개 팩은 `business/etsy/listings/<handle>/`에 있습니다: `puppy-training-plan`, `new-pet-starter-checklist`,
`pet-health-record-book`, `dog-grooming-guide`, `cat-enrichment-guide`, `complete-pet-parent-bundle`.
각 폴더: `listing.json`(제목·태그·설명·가격), `images/01..10.png`(2000×2000), PDF는 `business/products/<handle>.pdf`(번들은 5개 PDF).

리스팅 하나당(약 4분):
1. **Shop Manager → Listings → Add a listing**.
2. **Photos**: `images/` 폴더의 PNG를 번호 순서대로 최대 10장 드래그. 1번이 대표 이미지.
3. **Listing details**
   - Title: `listing.json`의 `title` 그대로(140자 이내).
   - About this listing: **I did** / **A finished product** / **2020 - 2026** 선택. "What is it?" → **A finished product**.
   - Category: Paper & Party Supplies → Paper → Calendars & Planners(체크리스트·기록장) 또는 Books, Movies & Music → Books → Guides & How Tos. Etsy 추천을 따라도 됩니다.
   - **Type: Digital** 선택(물리적 배송 없음).
   - Description: `description` 전체를 붙입니다. 마지막 4개 문단(AI 고지·수의사 고지·개인 사용·환불)이 빠지지 않았는지 확인. **AI 고지 문구는 Etsy 규정상 필수입니다.**
   - Tags: `tags` 13개(각 20자 이내), Materials: `materials`.
4. **Inventory and pricing**: Price = `price_usd`, Quantity = 999.
5. **Digital files**: **Add a file** → `business/products/<handle>.pdf` (번들은 5개 PDF 각각, 파일당 20MB·최대 5개).
6. **Publish** ($0.20 리스팅 수수료). 6개 완료 후 매장 화면에서 이미지·가격을 한 번 훑어봅니다.

이 6개는 **사람이 직접** 올려서 "판매자가 직접 운영하는 매장"이라는 기록을 남기는 것이 목적입니다.

## 3단계. Etsy Seller App 등록 → OAuth → GitHub 비밀키 (10~20분)

> **⏸️ 지금은 건너뛰세요.** 이 단계는 GitHub Actions가 Etsy에 자동으로 리스팅을 올릴 때만 필요합니다. 그 자동화 코드는 아직 저장소에 없고(권한 보류), 사장님이 본업으로 매일 운영하시기로 하셨으므로 리스팅은 2단계처럼 직접 올리는 것이 Etsy 규정상으로도 더 안전합니다. 아래 내용은 나중에 자동화를 켤 때를 위해 남겨 둡니다. 3단계와 4-4, 4-5, 7단계의 `.github/workflows/`·`factory/actions/` 언급도 같은 이유로 아직 실행할 수 없습니다.

Etsy Open API v3에 접근하는 열쇠입니다. 매장이 **활성 상태이고 리스팅이 있어야** 합니다(2단계 이후).

1. **etsy.com/developers/register** 접속(매장 계정으로 로그인 상태).
2. 신청서: App name은 `Mavilo Shop Tools`처럼 **"Etsy"라는 단어를 넣지 않음**. 설명 예:
   "Automation for my own shop only: create and update my digital listings, upload files and images, and read my own sales and view counts for weekly reports. Single seller, no third parties."
   앱 종류로 **Seller App**(자기 매장 전용, 앱 1개)을 고릅니다. 옛 "Personal access"는 승인이 느리고 거절이 잦습니다. (메뉴 위치는 바뀔 수 있음)
3. 제출 즉시 **Keystring**과 **Shared secret**이 표시됩니다("YOUR KEY IS NOT YET ACTIVE" 문구가 보이면 활성화까지 기다림; Seller App은 보통 수 분, 보장은 아님).
   → GitHub 비밀키 `ETSY_KEYSTRING`, `ETSY_SHARED_SECRET`.
4. 같은 화면(**Your Apps → 앱 → Edit**)에서 **Callback URL(redirect URI)**에 `https://localhost:3003/callback`을 등록합니다(HTTPS 필수, 아래 스크립트가 쓰는 주소). (메뉴 위치는 바뀔 수 있음)
5. **OAuth 동의 1회 클릭**: 저장소의 Etsy OAuth 도우미 스크립트(`factory/actions/` 아래, 정확한 파일명은 `.github/workflows/` 문서 참조)를 로컬에서 실행하거나,
   Actions 탭 → `etsy-oauth` 워크플로 → **Run workflow**를 누르면 이슈에 **동의 링크**가 생성됩니다. 링크를 열어 Etsy 로그인 → **Grant access**.
   요청 권한(scope): `listings_r listings_w listings_d shops_r shops_w transactions_r`.
   - 로컬 실행일 때: 브라우저가 `localhost:3003/callback?code=...`로 돌아오면 스크립트가 `refresh_token`을 터미널에 **한 번만** 출력합니다.
     그 값을 `ETSY_REFRESH_TOKEN`에 붙입니다. 터미널 기록은 지웁니다(`history -c`).
   - 토큰 수명: access 1시간(Action이 매번 새로 발급), refresh 90일(Action이 갱신해 `gh secret set`으로 다시 저장 → 그래서 `GH_SECRETS_PAT`가 필요).
6. **`ETSY_SHOP_ID`**: Shop Manager 주소창의 숫자(`etsy.com/your/shops/me/...`에서는 안 보일 수 있음) 또는 매장 페이지 소스의 `shop_id`, 또는 OAuth 스크립트가 함께 출력하는 `shop_id`.
7. **`GH_SECRETS_PAT`**: GitHub → 프로필 → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
   Repository access: **Only select repositories → mavilo-pet**. Permissions → Repository permissions → **Secrets: Read and write**(그 외 없음). 만료 1년. 값을 `GH_SECRETS_PAT`에.
   (Actions 기본 `GITHUB_TOKEN`은 비밀키를 쓸 수 없어서 별도 토큰이 필요합니다.)
8. 확인: Actions 탭 → `etsy-sync` → **Run workflow**. 성공하면 `business/etsy/stats/YYYY-MM-DD.json`이 커밋됩니다. 실패 시 이슈가 열리고 팩은 `factory/etsy-queue/`에 저장됩니다(수동 업로드 3분/개).

> Etsy가 이유 없이 키를 막는 사례(2026년 7~9월)가 보고되었습니다. 그럴 때도 Routine은 계속 팩을 만들고, 사장님이 `etsy-queue/`에서 직접 올리면 됩니다.

## 4단계. Shopify 열쇠·결제·정책·PDF 첨부 (45분)

### 4-1. 요금제와 도메인
- **Settings → Plan**: Basic(연납 $29/월, 월납 $39). 처음 3개월은 프로모션 가격이 있을 수 있음.
- **Settings → Domains**: 보유 도메인 연결(없으면 `xxxx.myshopify.com`으로도 됨). `SHOPIFY_STORE_DOMAIN` = `xxxx.myshopify.com`(커스텀 도메인이 아닌 관리자 주소).

### 4-2. 결제 수단 (한국은 Shopify Payments 불가)
- **Settings → Payments → Third-party providers → Choose provider → PayPal**(PayPal Business 계정 필요) → 계정 연결·활성화.
  대안: 토스페이먼츠·KG이니시스·PortOne. Basic 요금제에서 외부 결제는 판매마다 2% 추가 수수료가 붙습니다(설계서 6장).
- PayPal Business 계정: paypal.com/kr/business → 사업자 또는 개인사업자 정보·신분증·한국 은행 계좌.

### 4-3. 정책 페이지
- **Settings → Policies**(또는 Legal): Refund policy·Terms of service 칸에 `business/support/policies.md`의 해당 블록 붙이기 → Save. (메뉴 위치는 바뀔 수 있음)
- **Online Store → Pages → Add page**: 제목 `Disclaimer`, 본문에 policies.md의 Disclaimer HTML 붙이기(에디터 `<>` 버튼으로 HTML 모드),
  오른쪽 **Theme template → `disclaimer`** 선택 → Save. **Online Store → Navigation → Footer menu**에 추가.

### 4-4. Dev Dashboard 앱 → `SHOPIFY_CLIENT_ID` / `SHOPIFY_CLIENT_SECRET`
2026년 1월부터 관리자에서 만드는 "커스텀 앱"이 없어졌습니다. 대신 **Dev Dashboard** 앱 + 24시간 토큰(client credentials)을 씁니다.
1. **dev.shopify.com/dashboard**(또는 Shopify 관리자 → Settings → Apps and sales channels → Develop apps → "Dev Dashboard"로 이동) 로그인. 매장과 **같은 조직(organization)**이어야 합니다. (메뉴 위치는 바뀔 수 있음)
2. **Create app** → 이름 `Mavilo Factory` → 만들기.
3. **Versions / Configuration → Access scopes**에 다음 5개 체크 후 **Release**: `write_products`, `write_content`, `write_files`, `read_orders`, `read_analytics`. (메뉴 위치는 바뀔 수 있음)
4. **Install** 버튼으로 본인 매장에 설치(설치해야 토큰 발급이 됩니다).
5. **Settings**(앱 설정) → **Client ID**, **Client secret** 복사 → GitHub `SHOPIFY_CLIENT_ID`, `SHOPIFY_CLIENT_SECRET`.
6. 확인: Actions → `shopify-publish` → Run workflow(dry-run 입력이 있으면 켬). 이 Action은 `POST https://<store>.myshopify.com/admin/oauth/access_token`에
   `grant_type=client_credentials`로 24시간 토큰을 매번 새로 받습니다(만료 없는 토큰을 저장하지 않음).

### 4-5. Theme Access 앱 → `SHOPIFY_CLI_THEME_TOKEN`
1. **apps.shopify.com/theme-access** → Install(무료, Shopify 공식).
2. 관리자 → **Apps → Theme Access → Create password** → 이름 `github-actions`, 이메일은 사장님 본인.
3. 이메일의 링크는 **1회·7일**만 유효 → 열어서 `shptka_...` 값을 바로 GitHub `SHOPIFY_CLI_THEME_TOKEN`에 붙입니다. `SHOPIFY_FLAG_STORE`에는 `xxxx.myshopify.com`.
4. Action은 `shopify theme push --live --allow-live`로 테마를 올립니다. 처음 한 번은 AI가 대화형 세션에서 `shopify theme push`로 올려도 됩니다(5단계).

### 4-6. Digital Products 앱 + PDF 첨부 (사람만 가능)
1. **apps.shopify.com/digital-downloads**("Shopify Digital Products", 무료) → Install.
2. 상품 6개가 먼저 있어야 합니다. 없으면 5단계(AI가 CSV로 생성)를 먼저 하고 돌아옵니다.
3. **Apps → Digital Products → 상품 선택 → Add files** → `business/products/<handle>.pdf`(번들은 5개 모두). 설정에서 **Automatically send files**(결제 후 자동 이메일)를 켭니다.
4. 이 첨부는 API가 없어 항상 사람이 합니다. 신제품은 Etsy에 먼저 올리고, 90일 킬 규칙을 넘긴 것만 월 1회 묶어서 첨부합니다(설계서 3장).

### 4-7. 환영 이메일 자동화 (Shopify Email / Messaging)
1. **Apps → Messaging**(옛 Shopify Email; **Marketing → Automations**에서도 진입) → **Automations → Create automation → Welcome new subscribers** 템플릿. (메뉴 위치는 바뀔 수 있음)
2. `business/marketing/email-sequence.md`의 3통(환영+WELCOME10, 가이드 소개, 리마인드)을 각 이메일 본문에 붙이고 간격을 0일/2일/5일로. 발신자 이름 `Mavilo Pet Co.`.
3. **Turn on**. 할인코드 `WELCOME10`은 5단계에서 AI가 만들거나 **Discounts → Create discount → Amount off order → 10%, 고객당 1회**로 직접 만듭니다.
4. 월 1만 통까지 무료. 캠페인(뉴스레터)은 API가 없으니 월 1회 붙여 넣기(선택).

## 5단계. [AI] 매장 채우기 (사람 0분, 확인만)

Shopify 커넥터가 연결된 Claude 대화형 세션에서 AI가: `shopify theme push`, `business/shopify-products-import.csv`로 상품 6개 생성·공개,
컬렉션, `WELCOME10`, 블로그 5편 `articleCreate`, RSS 피드(`/blogs/news?view=rss`) 200 확인, Disclaimer 페이지 템플릿 확인.
사장님은 끝나면 매장 첫 화면·상품 페이지·`https://<도메인>/blogs/news?view=rss`가 열리는지 한 번씩 봅니다.

## 6단계. Pinterest + 검색엔진 (20분)

### 6-1. Pinterest 비즈니스 계정 + 사이트 소유 확인
1. **business.pinterest.com** → Create account(또는 기존 개인 계정을 **Settings → Account management → Convert to business**).
2. **Settings → Claimed accounts**(일부 계정은 "Link to Pinterest") → Websites → **Claim** → **Add HTML tag** 선택 → `<meta name="p:domain_verify" content="XXXX"/>`가 표시됩니다.
3. **content="..." 안의 값(XXXX)만** 복사 → Shopify 관리자 → **Online Store → Themes → Customize → Theme settings(⚙) → SEO & verification → Pinterest site verification** 칸에 붙이고 Save.
   (테마 `layout/theme.liquid`가 이 값을 `<meta name="p:domain_verify">`로 출력합니다. theme.liquid를 직접 편집할 필요 없음.)
4. Pinterest로 돌아가 **Verify/Continue**. 도메인은 커스텀 도메인 기준(`xxxx.myshopify.com`이면 그 주소로).

### 6-2. RSS 자동 게시 (핀 자동 생성, API 없음)
1. **Settings → Bulk create Pins**(왼쪽 메뉴; 데스크톱만 표시, 웹사이트가 클레임되어야 보임) → **Auto-publish** → RSS feed URL 칸에
   **`https://<도메인>/blogs/news?view=rss`** 입력 → 보드 선택(예: "Pet Care Printables") → **Save**.
   ❗ `/blogs/news.atom`은 넣지 않습니다. Pinterest는 Atom을 거부하고 이미지 태그(`<enclosure>`)가 없어 핀이 0개 생깁니다.
2. 첫 핀은 24~48시간 뒤, 이후 새 글마다 24시간 내 생성(하루 200개 한도). 안 생기면 `https://validator.w3.org/feed/`에 URL을 넣어 RSS가 유효한지 확인하고, 글에 대표 이미지(featured image)가 있는지 확인합니다(이미지가 없는 글은 핀이 안 됩니다).
3. **Pinterest Shopify 앱**(apps.shopify.com/pinterest)은 설치만 하고 기대하지 않습니다(신규 도메인 카탈로그 미승인이 흔함).

### 6-3. Google Search Console · Bing
1. **search.google.com/search-console** → Add property → **URL prefix** `https://<도메인>/` → 확인 방법 **HTML tag** → content 값 복사.
   Shopify에는 Google 전용 테마 설정이 없으므로 **Online Store → Themes → ⋯ → Edit code → layout/theme.liquid**의 `<head>` 안 `p:domain_verify` 줄 아래에 태그를 한 줄 붙여 Save → Verify.
   (또는 Google 확인 방식으로 **Domain** 속성 + DNS TXT 레코드를 도메인 등록업체에 추가.)
2. Search Console → **Sitemaps** → `https://<도메인>/sitemap.xml` 제출.
3. **bing.com/webmasters** → **Import from Google Search Console**(원클릭) → 사이트맵이 함께 가져옵니다.

## 7단계. [AI] Routine 6개 켜기 (사람 0분)

`factory/routines/README.md`의 문장을 Claude Code 세션에 붙이면 AI가 `create_trigger`로 6개를 만들고 `factory-scan`을 1회 수동 실행해
첫 브리프(`factory/briefs/YYYY-WW.json`)를 만듭니다. 사장님은 다음 토요일 **주간 리포트 이슈**가 오는지만 확인합니다.
2주 연속 안 오면 설계서 9장(구독 한도·Routine 오류)을 확인합니다.

---

## 끝난 뒤 매주 일요일 20~30분 루틴

1. GitHub 모바일 앱 → 이슈 `주간 리포트 YYYY-WW` 읽기(3분).
2. PR `factory/…`, `content/…`: 한국어 5줄·표지·QC 점수 확인 → **Merge** 또는 **Close**. `needs-human` 라벨은 본문을 실제로 읽고 머지.
3. Etsy 메시지 → `business/support/replies.md` 복붙.
4. 이슈에 "재인증 필요"가 있으면 링크 클릭 1번. `factory/etsy-queue/`에 팩이 있으면 2단계 방식으로 업로드.
5. 월말: Shopify Digital Products에 새 PDF 묶음 첨부(4-6), Payoneer 잔액 출금.

## 참고 링크 (2026-09 확인)
- Pinterest RSS 자동 게시: help.pinterest.com/en/business/article/auto-publish-pins-from-your-rss-feed
- Pinterest 웹사이트 클레임: help.pinterest.com/en/business/article/claim-your-website
- Etsy Seller App 등록: help.etsy.com/hc/en-us/articles/41918478450967 · developer.etsy.com/documentation/essentials/authentication
- Etsy Offsite Ads: help.etsy.com/hc/en-us/articles/360000338367 · Share & Save: help.etsy.com/hc/en-us/articles/16981332744087
- Etsy 통화 설정: help.etsy.com/hc/en-us/articles/360000336747 · Payoneer 연결: help.etsy.com/hc/en-us/articles/16999319005207
- Shopify Dev Dashboard 토큰: shopify.dev/docs/apps/build/dev-dashboard/get-api-access-tokens
- Shopify Theme Access: shopify.dev/docs/storefronts/themes/tools/theme-access
- Shopify Digital Products: help.shopify.com/en/manual/products/digital-service-product/digital-downloads
- Shopify Messaging 자동화: help.shopify.com/en/manual/promoting-marketing/create-marketing/shopify-messaging/marketing-automations/create
- Shopify 사이트맵: help.shopify.com/en/manual/promoting-marketing/seo/find-site-map
- GitHub 비밀키: docs.github.com/actions/security-guides/using-secrets-in-github-actions
