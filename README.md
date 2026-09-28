# bellhaven-sync
Automated CRM data synchronization pipeline, scraper, and auditing workspace for Bellhaven Senior Living.
# Bellhaven CRM Synchronization Pipeline
**Candidate:** Katherine Fahey  

An automated data reconciliation pipeline and interactive audit workspace built to sync public facility data into our CRM Sandbox while strictly enforcing corporate compliance and billing safety rails.

## 🧠 Core Engineering Architecture

### 1. Data Ingestion & Idempotency Key Engine
* Scrapes the target facility database using normalized text matching rules.
* Generates a deterministic MD5 hash based on location coordinates (Address + City + State). This hash acts as an **idempotency key**, ensuring that daily sequential execution blocks never re-propose anomalies that a human auditor has already approved or dismissed.

### 2. Corporate Ownership Alignment Matrix
The sync engine compares scraped items against live CRM records and classifies findings into a routing layout:
* **`CREATE_NEW_ACCOUNT`**: Facility exists on the web but is completely missing from the internal ledger. Initializes a clean active instance.
* **`UPDATE_OR_REP_PARENT`**: Structural metadata updates (re-branding, naming drift) mapped directly down to existing match keys.

### 3. Billing SOP & CHOW Guard Rails (Data Safety)
To ensure compliance with financial ledgers, the sync engine checks active billing metrics before proposing parent modifications:
* **The Rule**: If an account carries lifetime revenue history (`lifetime_revenue > 0`) AND outstanding debt (`outstanding_ar > 0`), direct modifications are hard-blocked.
* **The Resolution**: The script leaves the original billing profile completely untouched, seeds a brand-new facility record under the updated corporate parent, and writes the new entity pointer back to the legacy profile's `chow_current_account` key.

---

## 🤖 AI Collaboration Methodology
* Used an AI assistant to rapidly design and prototype a Python sync pipeline and interactive local Streamlit dashboard within a tight 2-hour window.
* Directed AI to isolate complex nested JSON condition maps and explicitly write automated safety switches enforcing the billing SOP logic, eliminating manual coding errors.

## 🚀 Future Roadmap Enhancements
* **Fuzzy String Metric Engine**: Implement Jaro-Winkler string tokens to automatically map spelling variations (e.g., "St." vs "Street") without requiring manual human alignment.
* **Upstream Webhooks**: Transition from daily chronological cron loops to an event-driven listener layout, instantly picking up changes the moment a location profile modifies.
