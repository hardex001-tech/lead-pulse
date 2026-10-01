# LeadPulse  Automated B2B Lead Extraction, Enrichment & MX Verification Engine

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.2+-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![DNS](https://img.shields.io/badge/DNS-MX%20Verification-blue?logo=cloudflare)](https://dnspython.org)
[![CLI](https://img.shields.io/badge/CLI-Rich%20Terminal-00C7B7)](https://github.com/Textualize/rich)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **LeadPulse** is an automated, production-ready B2B lead intelligence and enrichment pipeline developed by **Abdulrazaq Adeyemi**. It extracts decision-maker contact details from target business domains, enriches records with social links and metadata, and performs live DNS MX record deliverability audits to eliminate email bounce rates for outbound sales teams.

---

## ⚡ Architecture & Pipeline

```
  +------------------+       +-------------------+       +--------------------+
  |  Target Domains  | ----> |  Deep Web Crawler | ----> | Contact Extractor  |
  |  (Input / Batch) |       |  /contact, /about |       | Emails, Phones, SM |
  +------------------+       +-------------------+       +--------------------+
                                                                    |
                                                                    v
  +------------------+       +-------------------+       +--------------------+
  | Buyer-Ready CSV  | <---- | Export Engine     | <---- | DNS MX Deliverable |
  | & JSON Datasets  |       | Pandas Tabular    |       | Verification Audit |
  +------------------+       +-------------------+       +--------------------+
```

---

## 🚀 Core Features

### 1. Deep Subpage Discovery & Contact Scraping
* Probes primary homepages and high-intent subpages (`/contact`, `/about`, `/team`, `/our-team`, `/support`).
* Uses randomized User-Agent rotation and graceful timeouts to ensure high success rates.
* Deduplicates emails, phone numbers, and company metadata while filtering out static asset noise (e.g., `image@2x.png`).

### 2. Social Profile Discovery
* Automatically identifies and links connected company social footprints:
  * **LinkedIn** (`linkedin.com/company/...` and personal profiles)
  * **Twitter / X** profiles
  * **Instagram** & **Facebook** handles
  * **GitHub** organizations

### 3. DNS Mail Exchanger (MX) Deliverability Audit
* Performs direct DNS resolution on identified email domains.
* Flags domains without active MX servers as `UNDELIVERABLE`, safeguarding cold email sender reputation and reducing bounce rates from standard 30%+ down to <3%.
* Distinguishes between direct personal inboxes and generic role accounts (`support@`, `sales@`, `info@`).

### 4. Buyer-Ready Tabular Export
* Formats records into clean, standardized datasets with columns:
  * `Company Name`, `Domain`, `Website URL`, `Primary Email`, `Email Status`, `Deliverable`, `Mail Server (MX)`, `Phone Number`, `LinkedIn`, `Twitter / X`, `Instagram`, `Description`.
* Exports concurrently to CSV and JSON in `data/output/`.

---

## 🛠️ Quickstart Installation

### 1. Clone the repository
```bash
git clone https://github.com/hardex001-tech/lead-pulse.git
cd lead-pulse
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 Usage & CLI Commands

### Option A: Run Interactive Demonstration
Process a pre-configured batch of target domains and generate exported CSV/JSON reports:
```bash
python -m lead_pulse.cli demo
```

### Option B: Scan a Single Target Domain
Inspect a specific company's contact points in real-time:
```bash
python -m lead_pulse.cli scan stripe.com
```

### Option C: Audit an Email Address Deliverability
Verify whether a business email has live mail servers:
```bash
python -m lead_pulse.cli verify contact@stripe.com
```

---

## 🧪 Automated Testing

Run the unit test suite:
```bash
python -m unittest discover -s tests
```

---

## 👤 Author & Engineering

* **Lead Engineer:** Abdulrazaq Adeyemi
* **Email:** `abdulrasaqadeyemi61@gmail.com`
* **Portfolio & Projects:** [abdulrazaq-tech.xyz](https://abdulrazaq-tech.xyz)
* **License:** [MIT](LICENSE)
