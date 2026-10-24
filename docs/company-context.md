# Qawafel: public context relevant to the assessment

Researched on 24 October 2026. These are first-party public product descriptions, not verified claims about internal systems. The assessment PDF remains the specification for this exercise.

## Public facts

- Qawafel describes a B2B platform connecting suppliers, manufacturers, wholesalers, and retailers, combining commerce, invoicing, collections, and analytics. Source: [official homepage](https://qawafel.sa/).
- Its commerce offering supports a business acting as both seller and buyer in one account, with orders connected to invoices and payment status. Source: [commerce product page](https://qawafel.sa/en/ecommerce/).
- Its financing page describes financing through Al Rajhi Bank, bank-controlled approval, and supplier payment following approval. Source: [financing product page](https://qawafel.sa/en/financing-en/).

## Implications for this submission (our design inferences)

- Emphasize a financing review package with traceable invoice evidence, recorded collection performance, and outstanding receivables.
- Keep the applicant's sales invoices distinct from purchase invoices and financing flows. A single business can play multiple roles.
- In the optional automation roadmap, consider authorized reuse of existing platform invoices and order/payment records before requiring repeated file uploads; actual availability and customer consent remain discovery questions.
- Leave the credit decision with the bank and the evidence review with a human.
- Use a generic Bank Partner in the technical specification. Public partnership information does not prove which bank the assessment scenario intends or what its API supports.

## Not established by this research

No verified information about Qawafel's private technology stack, internal credit policies, bank API schemas, idempotency support, or status reconciliation mechanisms. Do not invent these.
