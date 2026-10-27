import pandas as pd

df1 = pd.read_csv("outputs/smoke-test-all-policies/results.csv")
df2 = pd.read_csv("outputs/final-q1-v1/full-factorial/results.csv")

row0 = df1.iloc[0]
match = df2[
    (df2["incoming_rate"] == row0["incoming_rate"]) &
    (df2["cart_capacity"] == row0["cart_capacity"]) &
    (df2["routing_policy"] == row0["routing_policy"]) &
    (df2["batching_method"] == row0["batching_method"]) &
    (df2["num_pickers"] == row0["num_pickers"]) &
    (df2["repetition"] == row0["repetition"])
]

print(f"Found matches in full factorial: {len(match)}")
merged = pd.merge(df1, match, on="trigger_method", suffixes=("_smoke", "_stored"))

all_identical = True
for idx, r in merged.iterrows():
    tm = r["trigger_method"]
    tlo_smoke = r["total_late_orders_smoke"]
    tlo_stored = r["total_late_orders_stored"]
    tp_smoke = r["throughput_per_hour_smoke"]
    tp_stored = r["throughput_per_hour_stored"]
    trips_smoke = r["trip_count_smoke"]
    trips_stored = r["trip_count_stored"]
    
    same = (tlo_smoke == tlo_stored) and (tp_smoke == tp_stored) and (trips_smoke == trips_stored)
    if not same:
        all_identical = False
    print(f"{tm:12s}: TLO ({tlo_smoke} vs {tlo_stored}), TP ({tp_smoke} vs {tp_stored}), Trips ({trips_smoke} vs {trips_stored}) => Match: {same}")

print(f"Overall bitwise identical: {all_identical}")
