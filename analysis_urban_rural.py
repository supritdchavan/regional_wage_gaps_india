"""
Post 3: urban vs rural pay for regular wage/salaried workers, 15 largest states.

Nominal ratio = urban pay / rural pay (PLFS 2025, Table 38).
Price-adjusted ratio = nominal ratio / (urban poverty line / rural poverty line), using the
2011-12 state poverty lines as a rough, dated price proxy (see analysis_cost_of_living.py).

Run:  python analysis_urban_rural.py
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).parent
OUT = ROOT / "outputs"; OUT.mkdir(exist_ok=True)
wage = pd.read_csv(ROOT / "data" / "plfs2025_regular_wage_by_state.csv")
pl = pd.read_csv(ROOT / "data" / "state_poverty_lines_2011_12_selected.csv")
d = pl.merge(wage, on="State_UT")
assert len(d) == 15
india = wage[wage.State_UT == "all India"].iloc[0]

d["urban_premium_ratio"] = (d.Urban_Person / d.Rural_Person).round(2)
d["urban_rural_price_ratio"] = (d.PL_Urban / d.PL_Rural).round(2)
d["price_adjusted_ratio"] = (d.urban_premium_ratio / d.urban_rural_price_ratio).round(2)
d["gap_rs"] = d.Urban_Person - d.Rural_Person
d = d.sort_values("urban_premium_ratio", ascending=False).reset_index(drop=True)
print(d[["State_UT", "Rural_Person", "Urban_Person", "urban_premium_ratio",
         "urban_rural_price_ratio", "price_adjusted_ratio", "gap_rs"]].to_string(index=False))
print(f"\nAll-India: rural Rs {india.Rural_Person:,.0f}, urban Rs {india.Urban_Person:,.0f}, "
      f"ratio {india.Urban_Person / india.Rural_Person:.2f}x")
d[["State_UT", "Rural_Person", "Urban_Person", "urban_premium_ratio",
   "urban_rural_price_ratio", "price_adjusted_ratio", "gap_rs"]].to_csv(OUT / "urban_rural_pay.csv", index=False)

# --- Chart: rural vs urban dots, joined ------------------------------------
r = d.iloc[::-1].reset_index(drop=True)
fig, ax = plt.subplots(figsize=(10.8, 10.8), dpi=100)
for i, row in r.iterrows():
    ax.plot([row.Rural_Person, row.Urban_Person], [i, i], color="#c9d3d9", linewidth=3, zorder=1)
ax.scatter(r.Rural_Person, range(len(r)), color="#e07a5f", s=110, zorder=3, label="Rural")
ax.scatter(r.Urban_Person, range(len(r)), color="#1f6f8b", s=110, zorder=3, label="Urban")
for i, row in r.iterrows():
    ax.text(row.Urban_Person + 500, i, f"{row.urban_premium_ratio:.2f}×", va="center",
            fontsize=12, fontweight="bold", color="#1f6f8b")
ax.set_yticks(range(len(r))); ax.set_yticklabels(r.State_UT, fontsize=12.5)
ax.set_xlim(10000, 36000)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"₹{int(x):,}"))
ax.set_xlabel("Average monthly pay, regular wage/salaried workers (₹)", fontsize=11)
ax.grid(axis="x", color="#eee", zorder=0)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.legend(loc="lower right", frameon=False, fontsize=12)
fig.suptitle("The urban pay premium: how much more city jobs pay than rural ones",
             fontsize=17, fontweight="bold", x=0.04, ha="left", y=0.965)
fig.text(0.04, 0.915, "15 largest states, Jan–Dec 2025. Label = urban pay ÷ rural pay. All-India: 1.47×.",
         fontsize=12, color="#444")
fig.text(0.04, 0.02, "Source: PLFS Annual Report 2025, MoSPI (Table 38). Nominal pay; not adjusted for the higher cost of living in cities.",
         fontsize=9.5, color="#555")
fig.subplots_adjust(left=0.18, right=0.96, top=0.88, bottom=0.1)
fig.savefig(OUT / "urban_rural_pay_top15_states.png")
print("Saved outputs/")
