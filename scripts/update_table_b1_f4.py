import csv
import hashlib

input_path = 'results/WP0/provenance_table_B1.csv'
note_text = "round-0 generator not archived; the configuration's 3,600 s horizon is inconsistent with the round-0 TLO scale (1,136.92), so this configuration may not describe the round-0 run"

rows = []
with open(input_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for r in reader:
        rows.append(r)

# Explicit classification mappings from F4:
# - F 360 / 720 / 720 -> reporting error; setup 30 / 180 / 180 -> reporting error
# - beta 2 / 1 / 2, pick time 5 / 3 / 5, horizon 28,800 / 3,600 / 28,800, warm-up "Welch, no value" / 0 / 5,460, travel estimation, TLO definition -> both
# - V, cart capacity, due allowance, walking speed -> unchanged

class_map = {
    'FTWB interval F': 'reporting error',
    'Setup time t_setup': 'reporting error',
    'Urgency beta': 'both',
    'Pick time per piece': 'both',
    'Simulation length': 'both',
    'Warm-up W': 'both',
    'Travel estimation in policy': 'both',
    'TLO definition': 'both',
    'VTWB threshold V': 'unchanged',
    'Cart capacity set C': 'unchanged',
    'Due allowance range': 'unchanged',
    'Walking speed / times': 'unchanged'
}

header = rows[0]
if len(header) == 7:
    header.append('note')
new_rows = [header]

for r in rows[1:]:
    param = r[0]
    if param in class_map:
        r[6] = class_map[param]
    if len(r) == 7:
        r.append(note_text)
    else:
        r[7] = note_text
    new_rows.append(r)

with open(input_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(new_rows)

h = hashlib.sha256(open(input_path, 'rb').read()).hexdigest()
print(f"Updated {input_path} with F4 classifications and note. Rows: {len(new_rows)}, SHA-256: {h}")
