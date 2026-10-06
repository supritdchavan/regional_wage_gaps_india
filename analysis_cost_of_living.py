"""
Post 2: price-adjusted pay across India's 15 largest states.

Idea: states differ in prices. The Planning Commission's state poverty lines (2011-12) are
built from state-specific price differences, so state line / all-India line is used as a
RELATIVE PRICE INDEX (rural and urban separately). This is a rough, dated proxy.

Steps
1. Urban share of regular wage workers in a state is backed out of the PLFS table itself:
   All = (1-w)*Rural + w*Urban  ->  w = (All - Rural) / (Urban - Rural)
2. State price index = (1-w)*(rural line/816) + w*(urban line/1000)
3. Price-adjusted pay = nominal pay / price index  (all-India prices = 1)

Run:  python analysis_cost_of_living.py
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
d["urban_share"] = (d.All_Person - d.Rural_Person) / (d.Urban_Person - d.Rural_Person)
d["price_index"] = (1 - d.urban_share) * (d.PL_Rural / 816) + d.urban_share * (d.PL_Urban / 1000)
d["adjusted_pay"] = (d.All_Person / d.price_index).round(0)
d["rank_nominal"] = d.All_Person.rank(ascending=False).astype(int)
d["rank_adjusted"] = d.adjusted_pay.rank(ascending=False).astype(int)
d = d.sort_values("adjusted_pay", ascending=False).reset_index(drop=True)

print(d[["State_UT", "All_Person", "price_index", "adjusted_pay",
         "rank_nominal", "rank_adjusted"]].round(3).to_string(index=False))
print(f"\nNominal gap (max/min):  {d.All_Person.max() / d.All_Person.min():.2f}x")
print(f"Adjusted gap (max/min): {d.adjusted_pay.max() / d.adjusted_pay.min():.2f}x")
d[["State_UT", "All_Person", "price_index", "adjusted_pay", "rank_nominal", "rank_adjusted"]] \
    .to_csv(OUT / "price_adjusted_pay.csv", index=False)

# --- Chart: nominal vs price-adjusted ---------------------------------------
r = d.iloc[::-1]
fig, ax = plt.subplots(figsize=(10.8, 10.8), dpi=100)
y = range(len(r)); h = 0.38
ax.barh([i + h / 2 for i in y], r.All_Person, height=h, color="#b8c4cc", label="Nominal pay", zorder=2)
ax.barh([i - h / 2 for i in y], r.adjusted_pay, height=h, color="#1f6f8b", label="Price-adjusted pay", zorder=2)
for i, (n, a) in enumerate(zip(r.All_Person, r.adjusted_pay)):
    ax.text(n + 200, i + h / 2, f"₹{int(n):,}", va="center", fontsize=9.5, color="#555")
    ax.text(a + 200, i - h / 2, f"₹{int(a):,}", va="center", fontsize=9.5, color="#1f6f8b", fontweight="bold")
ax.set_yticks(list(y)); ax.set_yticklabels(
    [f"{s}  (#{b}→#{a})" for s, b, a in zip(r.State_UT, r.rank_nominal, r.rank_adjusted)], fontsize=11.5)
ax.set_xlim(0, 32000)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f"{int(x):,}"))
ax.set_xlabel("Average monthly pay (₹), all-India prices = 1", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.legend(loc="lower right", frameon=False, fontsize=11)
fig.suptitle("Pay vs purchasing power: how state rankings change after adjusting for prices",
             fontsize=16.5, fontweight="bold", x=0.04, ha="left", y=0.965)
fig.text(0.04, 0.915, "Regular wage/salaried workers, 15 largest states. Labels show rank: nominal → adjusted.",
         fontsize=12, color="#444")
fig.text(0.04, 0.02, "Sources: PLFS Annual Report 2025 (MoSPI), Table 38; state poverty lines 2011-12 (Planning Commission) used as a rough\n"
         "price proxy. Dated and approximate. Telangana uses undivided Andhra Pradesh's lines. See README for method.",
         fontsize=9.5, color="#555")
fig.subplots_adjust(left=0.27, right=0.96, top=0.88, bottom=0.12)
fig.savefig(OUT / "price_adjusted_pay_top15_states.png")
print("Saved outputs/")
