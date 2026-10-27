import csv

input_path = 'results/WP0/provenance_table_B1.csv'
rows = []
with open(input_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for r in reader:
        rows.append(r)

printed = {
    'FTWB interval F': ('F = 360 s (p. 11, Section 4.1)', 'reporting error'),
    'VTWB threshold V': ('V = 12 orders (p. 11, Section 4.1)', 'unchanged'),
    'Setup time t_setup': ('30 s (p. 9, Section 3.2)', 'both'),
    'Urgency beta': ('beta = 2 (p. 12, Section 4.3; p. 13, Section 4.4)', 'reporting error'),
    'Cart capacity set C': ('{100, 150, 200} items (p. 9, Section 3.3)', 'unchanged'),
    'Pick time per piece': ('5 s (p. 8, Section 3.2; p. 9, Section 3.2)', 'both'),
    'Walking speed / times': ('0.5 m/s (p. 8, Section 3.2); walking times not printed', 'unchanged'),
    'Warm-up W': ("'determined by Welch method' (no numerical value printed) (p. 10, Section 3.3)", 'implementation change'),
    'Simulation length': ('28,800 s (8-hour day) (p. 10, Section 3.3)', 'reporting error'),
    'Due allowance range': ('30-120 minutes [1800, 7200] s (p. 8, Section 3.2)', 'unchanged'),
    'Travel estimation in policy': ('Regression-based O(1) approximation (p. 9, Section 3.2; p. 13, Section 4.3)', 'both'),
    'TLO definition': ('sum 1[c_i > d_i] for i=1..N over horizon T (p. 10, Section 3.4, Eq. 2)', 'both')
}

header = rows[0]
new_rows = [header]
for r in rows[1:]:
    param = r[0]
    if param in printed:
        val_printed, classification = printed[param]
        r[1] = val_printed
        r[6] = classification
    new_rows.append(r)

with open(input_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(new_rows)

print('Updated provenance_table_B1.csv successfully.')
