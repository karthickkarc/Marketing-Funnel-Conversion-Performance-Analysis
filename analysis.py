"""
Marketing Funnel & Conversion Performance Analysis
===================================================
Analyzes funnel data to identify drop-off points, channel performance,
and provides actionable recommendations.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path

# ── Load & Clean ──────────────────────────────────────────────────────────────

def load_and_clean(path: str = "data/funnel_data.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df.columns = df.columns.str.strip().str.lower()
    df = df.dropna(subset=["visitors", "leads", "customers"])
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    df["month_label"] = df["date"].dt.strftime("%b %Y")
    # Derived metrics
    df["cac"] = np.where(df["customers"] > 0, df["ad_spend"] / df["customers"], 0)
    df["roas"] = np.where(df["ad_spend"] > 0, df["revenue"] / df["ad_spend"], np.nan)
    df["ltv_cac"] = np.where(df["cac"] > 0, (df["revenue"] / df["customers"]) / df["cac"], np.nan)
    return df


# ── Conversion Rates ──────────────────────────────────────────────────────────

def conversion_rates(df: pd.DataFrame) -> dict:
    totals = df[["visitors","leads","mqls","sqls","opportunities","customers"]].sum()
    stages = ["visitors","leads","mqls","sqls","opportunities","customers"]
    rates = {}
    for i in range(len(stages) - 1):
        key = f"{stages[i]}_to_{stages[i+1]}"
        rates[key] = round(totals[stages[i+1]] / totals[stages[i]] * 100, 2)
    rates["visitor_to_customer"] = round(totals["customers"] / totals["visitors"] * 100, 3)
    return {"totals": totals.to_dict(), "rates": rates}


# ── Drop-Off Analysis ─────────────────────────────────────────────────────────

def dropoff_analysis(df: pd.DataFrame) -> pd.DataFrame:
    totals = df[["visitors","leads","mqls","sqls","opportunities","customers"]].sum()
    stages = ["visitors","leads","mqls","sqls","opportunities","customers"]
    labels = ["Visitors","Leads","MQLs","SQLs","Opportunities","Customers"]
    rows = []
    for i, (s, l) in enumerate(zip(stages, labels)):
        prev = totals[stages[i-1]] if i > 0 else totals[stages[0]]
        drop = prev - totals[s] if i > 0 else 0
        drop_pct = round(drop / prev * 100, 1) if prev > 0 and i > 0 else 0
        rows.append({"stage": l, "count": int(totals[s]),
                     "dropped": int(drop), "drop_rate_pct": drop_pct})
    return pd.DataFrame(rows)


# ── Channel Performance ───────────────────────────────────────────────────────

def channel_performance(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("channel").agg(
        visitors=("visitors","sum"), leads=("leads","sum"),
        mqls=("mqls","sum"), sqls=("sqls","sum"),
        opportunities=("opportunities","sum"), customers=("customers","sum"),
        revenue=("revenue","sum"), ad_spend=("ad_spend","sum")
    ).reset_index()
    grp["visitor_to_lead_pct"]  = (grp["leads"]         / grp["visitors"]      * 100).round(2)
    grp["lead_to_mql_pct"]      = (grp["mqls"]          / grp["leads"]         * 100).round(2)
    grp["mql_to_sql_pct"]       = (grp["sqls"]          / grp["mqls"]          * 100).round(2)
    grp["sql_to_opp_pct"]       = (grp["opportunities"] / grp["sqls"]          * 100).round(2)
    grp["opp_to_customer_pct"]  = (grp["customers"]     / grp["opportunities"] * 100).round(2)
    grp["overall_cvr_pct"]      = (grp["customers"]     / grp["visitors"]      * 100).round(3)
    grp["avg_deal_size"]        = (grp["revenue"] / grp["customers"]).round(0)
    grp["cac"]                  = np.where(grp["ad_spend"]>0, (grp["ad_spend"]/grp["customers"]).round(0), 0)
    grp["roas"]                 = np.where(grp["ad_spend"]>0, (grp["revenue"]/grp["ad_spend"]).round(2), np.nan)
    return grp.sort_values("overall_cvr_pct", ascending=False)


# ── Monthly Trend ─────────────────────────────────────────────────────────────

def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    m = df.groupby(["date","month_label"]).agg(
        visitors=("visitors","sum"), leads=("leads","sum"),
        customers=("customers","sum"), revenue=("revenue","sum"),
        ad_spend=("ad_spend","sum")
    ).reset_index().sort_values("date")
    m["cvr_pct"]    = (m["customers"] / m["visitors"] * 100).round(3)
    m["lead_rate"]  = (m["leads"]     / m["visitors"] * 100).round(2)
    m["mom_growth"] = m["customers"].pct_change().mul(100).round(1)
    return m


# ── Recommendations ───────────────────────────────────────────────────────────

def generate_recommendations(dropoff: pd.DataFrame, channels: pd.DataFrame) -> list[dict]:
    recs = []
    worst_stage = dropoff[dropoff["stage"] != "Visitors"].sort_values("drop_rate_pct", ascending=False).iloc[0]
    recs.append({
        "priority": "Critical",
        "area": f"Fix {worst_stage['stage']} Drop-Off ({worst_stage['drop_rate_pct']}% loss)",
        "insight": f"{worst_stage['dropped']:,} prospects lost at {worst_stage['stage']} stage.",
        "action": "A/B test landing pages, improve nurture sequences, and review qualification criteria."
    })
    best_ch = channels.sort_values("overall_cvr_pct", ascending=False).iloc[0]
    worst_ch = channels.sort_values("overall_cvr_pct").iloc[0]
    recs.append({
        "priority": "High",
        "area": f"Scale {best_ch['channel']} (CVR {best_ch['overall_cvr_pct']}%)",
        "insight": f"{best_ch['channel']} converts {best_ch['overall_cvr_pct']}% vs {worst_ch['overall_cvr_pct']}% for {worst_ch['channel']}.",
        "action": f"Reallocate 20-30% of {worst_ch['channel']} budget to {best_ch['channel']}."
    })
    high_roas = channels[channels["roas"] > 0].sort_values("roas", ascending=False).iloc[0]
    recs.append({
        "priority": "High",
        "area": f"Maximize {high_roas['channel']} ROAS ({high_roas['roas']}x)",
        "insight": f"{high_roas['channel']} returns ${high_roas['roas']:.1f} per $1 spent.",
        "action": "Increase spend incrementally, watch for diminishing returns, and test new ad creatives."
    })
    recs.append({
        "priority": "Medium",
        "area": "Improve MQL-to-SQL Qualification",
        "insight": "Misaligned ICP criteria inflate MQL counts while SQLs remain low.",
        "action": "Refine lead scoring model: add intent signals, firmographic fit, and engagement depth."
    })
    recs.append({
        "priority": "Medium",
        "area": "Reduce Opportunity-to-Close Leakage",
        "insight": "Average opp-to-customer rate indicates deal slippage in late stages.",
        "action": "Introduce deal-desk reviews, ROI calculators, and executive sponsor outreach for stalled deals."
    })
    recs.append({
        "priority": "Low",
        "area": "Activate Re-engagement Campaigns",
        "insight": "Leads that went cold represent low-CAC recovery opportunities.",
        "action": "Run 3-touch win-back email sequence targeting leads >90 days inactive."
    })
    return recs


# ── Report Export ─────────────────────────────────────────────────────────────

def export_report(out_dir: str = "reports"):
    Path(out_dir).mkdir(exist_ok=True)
    df = load_and_clean()

    conv    = conversion_rates(df)
    dropoff = dropoff_analysis(df)
    channels= channel_performance(df)
    trend   = monthly_trend(df)
    recs    = generate_recommendations(dropoff, channels)

    report = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "summary": conv,
        "dropoff": dropoff.to_dict(orient="records"),
        "channels": channels.to_dict(orient="records"),
        "monthly_trend": trend[["month_label","visitors","leads","customers","cvr_pct","mom_growth"]].to_dict(orient="records"),
        "recommendations": recs
    }

    json_path = Path(out_dir) / "funnel_report.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Console summary
    print("=" * 60)
    print("  MARKETING FUNNEL ANALYSIS REPORT")
    print("=" * 60)
    print(f"\n📊 OVERALL FUNNEL CONVERSION RATES")
    for k, v in conv["rates"].items():
        print(f"  {k.replace('_',' ').title():40s} {v:.2f}%")

    print(f"\n⚠️  TOP DROP-OFF POINTS")
    print(dropoff.to_string(index=False))

    print(f"\n📣 CHANNEL PERFORMANCE (sorted by CVR)")
    cols = ["channel","visitors","customers","overall_cvr_pct","roas"]
    print(channels[cols].to_string(index=False))

    print(f"\n💡 RECOMMENDATIONS")
    for i, r in enumerate(recs, 1):
        print(f"  [{r['priority']}] {i}. {r['area']}")
        print(f"       → {r['action']}")

    print(f"\n✅ Full report exported → {json_path}")
    return report


if __name__ == "__main__":
    export_report()
