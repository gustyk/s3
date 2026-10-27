import shutil
import os

superseded = [
    'results/WP8/backlog_triage_v2.csv',
    'results/WP8/backlog_triage_v3.csv',
    'results/WP8/all_arrivals_tlo_v2.csv',
    'results/WP8/all_arrivals_tlo_v3.csv'
]

for src in superseded:
    if os.path.exists(src):
        dst = os.path.join('results/superseded', os.path.basename(src))
        shutil.move(src, dst)
        print(f"Moved {src} to {dst}")

readme_path = 'results/superseded/README.md'
with open(readme_path, 'w', encoding='utf-8') as f:
    f.write('# Superseded Results Files\n\n')
    f.write('The files in this directory are archived developmental artifacts from earlier audit rounds and are explicitly superseded:\n\n')
    f.write('- `backlog_triage_v2.csv`, `backlog_triage_v3.csv` -> Superseded by `results/WP8/backlog_triage_v4.csv`.\n')
    f.write('- `all_arrivals_tlo_v2.csv`, `all_arrivals_tlo_v3.csv` -> Superseded by `results/WP8/all_arrivals_tlo_v4.csv`.\n\n')
    f.write('Do not use these superseded files in publication tables or manuscripts.\n')

print("Created results/superseded/README.md successfully.")
