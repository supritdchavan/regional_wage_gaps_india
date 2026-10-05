"""
Regional wage gaps among India's 15 most populous states.

Data: PLFS Annual Report 2025 (MoSPI), Table 38 - average monthly wage/salary
earnings (Rs) of regular wage/salaried employees (current weekly status),
January-December 2025. The table was copied into data/ as a CSV.

Run:  python analysis.py
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).parent
DATA = ROOT / "data" / "plfs2025_regular_wage_by_state.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

# 15 most populous states (Census 2011 population)
MAJOR = [
    "Uttar Pradesh", "Maharashtra", "Bihar", "West Bengal", "Madhya Pradesh",
    "Tamil Nadu", "Rajasthan", "Karnataka", "Gujarat", "Andhra Pradesh",
    "Odisha", "Telangana", "Kerala", "Jharkhand", "Assam",
]

df = pd.read_csv(DATA)
india = df.loc[df["State_UT"] == "all India", "All_Person"].iloc[0]
major = (df[df["State_UT"].isin(MAJOR)]
         .sort_values("All_Person", ascending=False)
         .reset_index(drop=True))
assert len(major) == 15, "expected 15 states"

# --- Summary numbers -------------------------------------------------------
top, bottom = major.iloc[0], major.iloc[-1]
major["vs_india_pct"] = ((major["All_Person"] / india - 1) * 100).round(1)
major["urban_rural_ratio"] = (major["Urban_Person"] / major["Rural_Person"]).round(2)
major["gender_gap_pct"] = ((major["All_Male"] - major["All_Female"]) / major["All_Male"] * 100).round(1)

print(f"All-India average: Rs {india:,}")
print(f"Highest: {top.State_UT} Rs {top.All_Person:,}")
print(f"Lowest:  {bottom.State_UT} Rs {bottom.All_Person:,}")
print(f"Gap: Rs {top.All_Person - bottom.All_Person:,} "
      f"({top.All_Person / bottom.All_Person:.2f}x)")
print(f"States below India average: {(major.All_Person < india).sum()} of 15\n")
print(major[["State_UT", "All_Person", "vs_india_pct",
             "urban_rural_ratio", "gender_gap_pct"]].to_string(index=False))
major.to_csv(OUT / "major_states_summary.csv", index=False)

# --- Chart -----------------------------------------------------------------
rev = major.iloc[::-1]
colors = ["#1f6f8b" if v >= india else "#e07a5f" for v in rev.All_Person]
fig, ax = plt.subplots(figsize=(10.8, 10.8), dpi=100)
bars = ax.barh(rev.State_UT, rev.All_Person, color=colors, height=0.72, zorder=2)
for r, v in zip(bars, rev.All_Person):
    ax.text(v - 300, r.get_y() + r.get_height() / 2, f"₹{v:,}", va="center",
            ha="right", fontsize=12, color="white", fontweight="bold", zorder=4)
ax.axvline(india, color="#222", linestyle="--", linewidth=1.4, zorder=3)
ax.text(india + 200, -0.95, f"All-India average: ₹{india:,}", fontsize=11.5, va="center")
ax.set_ylim(-1.3, len(rev) - 0.4)
ax.set_xlim(0, 31500)
ax.set_xlabel("Average monthly pay (₹)", fontsize=12)
ax.tick_params(axis="y", labelsize=13)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x):,}"))
fig.suptitle("Same job, different state: the pay gap across India's 15 largest states",
             fontsize=17.5, fontweight="bold", x=0.04, ha="left", y=0.965)
fig.text(0.04, 0.915, "Average monthly earnings of regular wage/salaried workers, "
         "Jan–Dec 2025. Maharashtra pays ~1.6× West Bengal.", fontsize=12, color="#444")
fig.text(0.04, 0.025, "Source: PLFS Annual Report 2025, MoSPI (Table 38). "
         "15 most populous states by Census 2011.\n"
         "Blue = at/above all-India average; orange = below.", fontsize=10.5, color="#555")
fig.subplots_adjust(left=0.19, right=0.96, top=0.88, bottom=0.12)
fig.savefig(OUT / "regional_wage_gap_top15_states.png")
print("\nSaved chart and summary to outputs/")
