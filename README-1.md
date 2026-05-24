# 📊 Marketing Funnel & Conversion Performance Analysis

A complete end-to-end marketing analytics toolkit that ingests funnel data, computes conversion rates at every stage, identifies drop-off bottlenecks, compares channel performance, and outputs an interactive dashboard + structured JSON report — ready to deploy or embed in any BI workflow.

---

## 🗂️ Repository Structure

```
marketing-funnel-analysis/
├── data/
│   └── funnel_data.csv          # Sample 12-month, 7-channel funnel dataset
├── src/
│   ├── analysis.py              # Core Python analytics engine
│   └── utils/                   # (extensible) helper modules
├── reports/
│   └── funnel_report.json       # Auto-generated analysis output
├── public/
│   └── dashboard.html           # Interactive single-file dashboard
├── dashboard.jsx                # React dashboard component
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/your-org/marketing-funnel-analysis.git
cd marketing-funnel-analysis
pip install -r requirements.txt
```

### 2. Run the analysis

```bash
python src/analysis.py
```

Outputs a console summary and saves `reports/funnel_report.json`.

### 3. Open the dashboard

Open `public/dashboard.html` directly in any browser — no server needed.

---

## 📐 Funnel Stages Analyzed

| Stage | Description |
|-------|-------------|
| **Visitors** | Total website sessions |
| **Leads** | Form fills / sign-ups |
| **MQLs** | Marketing Qualified Leads |
| **SQLs** | Sales Qualified Leads |
| **Opportunities** | Active pipeline deals |
| **Customers** | Closed-won |

---

## 📣 Channel Coverage

- Organic Search
- Paid Search
- Social Media
- Email Marketing
- Referral / Partners
- Direct
- Display / Retargeting

---

## 📊 Key Metrics Computed

| Metric | Formula |
|--------|---------|
| Stage CVR | `next_stage / current_stage × 100` |
| Overall CVR | `customers / visitors × 100` |
| CAC | `ad_spend / customers` |
| ROAS | `revenue / ad_spend` |
| LTV:CAC | `(revenue/customers) / CAC` |
| MoM Growth | `(this_month - last_month) / last_month` |

---

## 💡 How to Use Your Own Data

Replace `data/funnel_data.csv` with your export. Required columns:

```
date, channel, campaign, visitors, leads, mqls, sqls,
opportunities, customers, revenue, ad_spend
```

Dates should be `YYYY-MM-DD`. Missing `ad_spend` can be 0.

---

## 🧩 Extending the Analysis

- **Add UTM dimensions**: extend the CSV with `utm_source`, `utm_medium`, `utm_content` and group by them in `analysis.py`
- **CRM integration**: pipe Salesforce / HubSpot exports into `data/` and re-run
- **Alerting**: wrap `analysis.py` in a cron job and email the JSON report
- **BI tools**: load `funnel_report.json` into Tableau, Metabase, or Looker

---

## 📄 License

MIT — free to use, adapt, and distribute.
