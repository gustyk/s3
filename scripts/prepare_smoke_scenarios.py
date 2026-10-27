import pandas as pd
import subprocess
import json

# Let's inspect stored results to pick 5 specific scenarios
df_stored = pd.read_csv('outputs/final-q1-v1/full-factorial/results.csv')

# Let's pick 5 scenarios from df_stored:
# e.g., low lambda (0.5), mid lambda (2.0), high lambda (16.0), both routings, reps 1-3
scenarios = [
    # lam, cc, routing, batching, pickers
    (0.5, 100, 'S-shape', 'FCFS', 2),
    (0.5, 200, 'Largest Gap', 'EDT', 6),
    (2.0, 150, 'S-shape', 'FCFS', 4),
    (16.0, 100, 'Largest Gap', 'FCFS', 6),
    (16.0, 200, 'S-shape', 'EDT', 12)
]

print("Selected scenarios:")
for s in scenarios:
    print(s)
