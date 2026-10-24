# Proposed production architecture

The Streamlit prototype implements invoice validation, analysis, anomaly review, and exports. All document workers, database entities, reconciliation, and bank services below are future production design.

## Process and trust boundaries

```mermaid
flowchart TD
    A[Authenticated applicant: consent and period] --> B[Upload invoice Excel and statement PDFs]
    B --> C[Quarantine, content checks, encrypted storage]
    C --> D[Worker: parse and retain row/page lineage]
    D --> E{Data checks pass?}
    E -- No --> F[Return specific issues for correction]
    F --> B
    E -- Yes --> G[Normalize invoices and bank transactions]
    G --> H[Propose receipt allocations]
    H --> I[Human confirms ambiguous matches and exceptions]
    I --> J[Deterministic metrics + separate AI review queue]
    J --> K[Freeze versioned evidence package]
    K --> L[Reviewer approves exact package hash]
    L --> M[Durable submission intent + bank adapter]
    M --> N{Delivery outcome known?}
    N -- No --> O[Unknown: reconcile before any resend]
    N -- Yes --> P[Store raw status observation]
    O --> P
    P --> Q{Final decision independently supported?}
    Q -- No --> R[Verification pending / manual escalation]
    Q -- Yes --> S[Publish confirmed bank decision]
```

## Entity relationships

```mermaid
erDiagram
    Business ||--o{ FinancingApplication : owns
    FinancingApplication ||--o{ Document : receives
    FinancingApplication ||--o{ Invoice : contains
    Document ||--o{ Invoice : sources
    Document ||--o{ BankTransaction : sources
    Invoice ||--o{ PaymentAllocation : settles
    BankTransaction ||--o{ PaymentAllocation : funds
    FinancingApplication ||--o{ ReviewPackage : versions
    ReviewPackage ||--o{ BankSubmission : submitted_as
    BankSubmission ||--o{ StatusObservation : receives
    FinancingApplication ||--o{ AuditEvent : records
```

## Submission state rules

- Local transport: `queued -> sending -> acknowledged` or `unknown`. A definite pre-send failure can return to `queued`; a possibly delivered request cannot.
- Observed bank statuses are append-only; `last_observed_status` is distinct from `confirmed_status`.
- A final status requires agreed authoritative evidence. Contradictory observations create a verification task rather than overwriting a confirmed decision.
- Package changes invalidate approval and require a new version; they cannot mutate an in-flight submission.
- A bank-agreed reconciliation result may resolve an unknown outcome. A second identical API response is not independent evidence if the bank's error is systematic.
