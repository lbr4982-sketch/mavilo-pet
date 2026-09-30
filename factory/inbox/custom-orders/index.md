# custom-orders — 맞춤 주문 개인화 문구

파일 하나 = 주문 하나: `<주문번호>.md`

```
상태: ☐ 대기
상품: personalized-puppy-training-plan   (또는 personalized-pet-health-record-book / custom-cat-enrichment-plan)
주문일: 2026-10-05
개인화 입력(Etsy 개인화 칸 그대로):
  Puppy's name: Biscuit
  Breed: Golden Retriever
  Age: 10 weeks
  #1 challenge: potty
```

`night-desk`가 `☐ 대기`만 처리해 `factory/queue/custom/<주문번호>/`에 초안을 만듭니다.
Etsy에서 Complete order를 누른 뒤 `☑ 전달 완료`로 바꿉니다.
