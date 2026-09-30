# Shopify store policies (paste-ready English copy)

Where to paste (Shopify admin, menu names may change):
- **Refund policy** and **Terms of service**: Settings > Policies (Legal). Paste each block into its box, Save.
- **Disclaimer page**: Online Store > Pages > Add page. Title "Disclaimer", paste the body, and in the
  right sidebar choose the theme template **`page.disclaimer`** (added by `templates/page.disclaimer.json`).
  Then add the page to the footer menu (Online Store > Navigation > Footer menu).
- Etsy: paste the Refund policy block into Shop Manager > Settings > Policy settings > Digital items
  (Etsy also generates its own digital-item policy; keep both consistent).

All blocks reuse `factory/COPY.md` wording (`REFUND_POLICY_DIGITAL`, `VET_DISCLAIMER`, `PERSONAL_USE_LICENSE`).
Replace `[support email]` and `[state]` before publishing. This is store copy, not legal advice; have a
professional review it if the business grows.

---

## Refund policy (digital products)

```
Refund Policy

Everything sold by Mavilo Pet Co. is a digital product: printable PDF guides delivered by download link immediately after payment. Nothing is shipped.

All sales are final. Because this is an instant digital download, all sales are final and we do not offer refunds, returns or exchanges once the file has been delivered. Please read the product description, page count and preview images carefully before purchasing.

We will always fix a file problem. If your file will not open, is missing pages or otherwise does not match the listing, contact us within 30 days of purchase at [support email] with your order number and we will send a corrected file or, if we cannot fix it, refund your order in full. Refunds are never withheld for a genuine file problem.

Duplicate orders. If you accidentally purchased the same guide twice, contact us and we will refund the duplicate order.

Download problems. Your download link is shown on the order confirmation page and sent by email; it does not expire. If you cannot find it, contact us and we will re-send it.

Chargebacks. Please contact us before opening a dispute with your bank or payment provider; we resolve file problems within one business day. Disputes opened without contacting us are answered with the delivery record for the order.

Processing time. Approved refunds are issued to the original payment method within 3 business days and typically appear on your statement within 3-10 business days depending on your bank.

Contact: [support email]
```

## Terms of service

```
Terms of Service

Last updated: [date]

1. Overview
These Terms of Service ("Terms") govern your use of the Mavilo Pet Co. website and your purchase of our digital products. By placing an order you agree to these Terms. If you do not agree, please do not use the site or purchase our products.

2. Digital products
All products are digital files (PDF) delivered by download link after payment. No physical goods are shipped. Product descriptions, page counts and preview images describe what you receive; minor differences in colour or layout may occur depending on your device or printer.

3. License
For personal use only. © Mavilo Pet Co. You may print this guide as many times as you like for your own household. You may not resell, share, redistribute, upload or use any part of it commercially, or use it to train AI systems. All content, designs and text remain the property of Mavilo Pet Co. and are protected by copyright. Purchasing a guide grants a limited, non-transferable license, not ownership of the content.

4. Pricing and payment
Prices are shown in U.S. dollars and may change without notice; the price at the time of your order applies. Payment is processed by third-party providers (for example PayPal); we do not store your card details. Applicable taxes are calculated at checkout where required.

5. Refunds
Our Refund Policy is part of these Terms. In short: digital sales are final, and any file that will not open or does not match the listing will be fixed or refunded within 30 days of purchase.

6. Not veterinary advice
Our guides are general educational information for pet parents and are not veterinary advice. See our Disclaimer page, which is part of these Terms. You are responsible for decisions about your pet's health and should consult a licensed veterinarian.

7. Accounts and communications
You are responsible for providing an accurate email address so we can deliver your files. By purchasing you agree to receive transactional emails about your order. Marketing emails are sent only with your consent and include an unsubscribe link.

8. Acceptable use
You agree not to use the site for any unlawful purpose, to attempt to access it in unauthorized ways, or to copy or scrape its content.

9. Limitation of liability
To the fullest extent permitted by law, Mavilo Pet Co. is not liable for any indirect, incidental or consequential damages arising from your use of the site or our products. Our total liability for any claim relating to a product is limited to the amount you paid for that product.

10. Changes
We may update these Terms from time to time. The version posted on this page at the time of your order applies to that order.

11. Governing law
These Terms are governed by the laws of [state/country], without regard to conflict-of-law rules.

12. Contact
Mavilo Pet Co., [support email]
```

## Disclaimer page (theme template `page.disclaimer`)

Page title: **Disclaimer**

```
<h2>Not veterinary advice</h2>
<p>This guide is general educational information for pet parents and is not veterinary advice. It is not a substitute for veterinary examination, diagnosis or treatment. Always consult your veterinarian about your pet's specific health, diet, vaccinations and medications, and contact an emergency veterinarian or a pet poison hotline immediately if you think your pet is sick or has swallowed something harmful.</p>
<p>Every guide sold by Mavilo Pet Co. is written for the average healthy household pet. Your pet's age, breed, weight, medical history and environment can change what is safe or appropriate. Only a licensed veterinarian who has examined your pet can give you advice for your pet.</p>

<h2>Emergencies</h2>
<p>If your pet is having trouble breathing, has collapsed, is having a seizure, has been injured, or may have eaten something toxic, do not wait and do not rely on any printed guide. Call your veterinarian or the nearest emergency animal hospital right away. In the United States you can also call the ASPCA Animal Poison Control Center at (888) 426-4435 or the Pet Poison Helpline at (855) 764-7661 (consultation fees may apply).</p>

<h2>No guarantees of results</h2>
<p>Training plans, enrichment ideas, grooming steps and checklists describe common, generally accepted approaches. Every animal is different. We cannot promise a specific outcome, timeline or behaviour change, and we are not responsible for how you apply the information to your pet.</p>

<h2>Records are yours to keep accurate</h2>
<p>Our record books and trackers are tools for organising information you receive from your veterinarian. They do not replace your clinic's official records, vaccination certificates or prescription labels. Always follow the instructions on medication labels and from your veterinarian, even if they differ from a schedule or example shown in a guide.</p>

<h2>How our guides are made</h2>
<p>Our guides were designed and written by Mavilo Pet Co. with the help of generative AI tools, under our original creative direction, and reviewed by a human before publishing. Health-related statements are checked against sources such as the American Veterinary Medical Association, the American Animal Hospital Association and the ASPCA, but information can change and errors are possible. If you spot one, please tell us.</p>

<h2>Links and third parties</h2>
<p>We may mention products, organisations or websites for convenience. We do not control them and are not responsible for their content or services. Mentions are not endorsements.</p>

<h2>License</h2>
<p>For personal use only. © Mavilo Pet Co. You may print this guide as many times as you like for your own household. You may not resell, share, redistribute, upload or use any part of it commercially, or use it to train AI systems.</p>

<h2>Questions</h2>
<p>Contact us at [support email]. For questions about your pet's health, contact your veterinarian.</p>
```
