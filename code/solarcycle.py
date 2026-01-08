import math
import numpy as np
import pandas as pd
from math import comb



xlsx_path = "Data.xlsx"  
data = pd.read_excel(xlsx_path, sheet_name="Data")
data["Date"] = pd.to_datetime(data["Date"])

sun_col = "Sunspot Count (Normalized Value 7-day Trailing Moving Average)"

start_indices = data.index[data["Start_Flag"] == 1].tolist()
end_indices = data.index[data["End_Flag"] == 1].tolist()

if len(start_indices) != 26 or len(end_indices) != 26:

    print("Warning: expected 26 starts and 26 ends, got:",

          len(start_indices), len(end_indices))


pairs = []
end_iter = iter(end_indices)
current_end = next(end_iter)
for s in start_indices:
    while current_end < s:
        current_end = next(end_iter)
    pairs.append((s, current_end))



mid_records = []
for s, e in pairs:
    mid = (s + e) // 2
    mid_row = data.iloc[mid]
    mid_records.append({
        "Start_idx": s,
        "End_idx": e,
        "Mid_idx": mid,
        "Start_Date": data.loc[s, "Date"].date(),
        "End_Date": data.loc[e, "Date"].date(),
        "Mid_Date": mid_row["Date"].date(),
        "Sunspot_mid": mid_row[sun_col]
    })

mid_df = pd.DataFrame(mid_records)
all_sun = data[sun_col].dropna()
cycle_percentiles = []
for v in mid_df["Sunspot_mid"]:

    # fraction of weeks with sunspot <= event value
    rank = (all_sun <= v).mean()
    cycle_percentiles.append(rank)

mid_df["CyclePercentile"] = cycle_percentiles
print("Event midpoint sunspot percentiles (relative to full history):")
print(mid_df[["Mid_Date", "Sunspot_mid", "CyclePercentile"]].sort_values("Mid_Date").to_string(index=False))





# (a) Are events more likely than chance to occur above the global median?

k_above_median = (mid_df["CyclePercentile"] > 0.5).sum()
# implement two-sided binomial test under H0: p = 0.5
def binom_two_sided(k, n, p=0.5):
    probs = [comb(n, i) * (p**i) * ((1-p)**(n-i)) for i in range(n+1)]
    obs_prob = probs[k]
    # two-sided: sum of probabilities <= the observed-probability mass
    pval = sum(pr for pr in probs if pr <= obs_prob)
    return pval


n = len(mid_df)
p_above_median = binom_two_sided(k_above_median, n, 0.5)
print(f"\nCount above median (CyclePercentile > 0.5): {k_above_median} of {n}")
print(f"Binomial two-sided p-value (H0: p = 0.5): {p_above_median:.3f}")




# (b) Are events concentrated near solar maxima (top quartile)?

k_top_quartile = (mid_df["CyclePercentile"] > 0.75).sum()
def binom_upper_tail(k, n, p):
    return sum(comb(n, i) * (p**i) * ((1-p)**(n-i)) for i in range(k, n+1))

p_top_quartile = binom_upper_tail(k_top_quartile, n, 0.25)
print(f"\nCount in top quartile (CyclePercentile > 0.75): {k_top_quartile} of {n}")
print(f"Binomial upper-tail p-value (H0: p = 0.25): {p_top_quartile:.3f}")

# Summary statistics of percentiles
print("\nSummary of cycle percentiles:")
print(mid_df["CyclePercentile"].describe())