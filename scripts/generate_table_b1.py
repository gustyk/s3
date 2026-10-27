import csv

table_b1_data = [
    {
        "Parameter": "FTWB interval F",
        "Submitted_Manuscript_Value": "360 s",
        "Code_at_Original_Submission": "720 s (config/parameters.yaml:25 at 50bdad2)",
        "Config_Manifest_Original_Runs": "720 s (parameters.yaml at 724519f)",
        "Current_Code_Value": "720 s (config/parameters.yaml:33)",
        "Current_Results_Value": "720 s (sampled_ftwb_interval_seconds)",
        "Classification": "Reporting error (code used 720 s all along; manuscript text erroneously stated 360 s)"
    },
    {
        "Parameter": "VTWB threshold V",
        "Submitted_Manuscript_Value": "12 orders",
        "Code_at_Original_Submission": "12 orders (config/parameters.yaml:26 at 50bdad2)",
        "Config_Manifest_Original_Runs": "12 orders (manifest.json / parameters.yaml)",
        "Current_Code_Value": "12 orders (config/parameters.yaml:34)",
        "Current_Results_Value": "12 orders (sampled_vtwb_threshold_orders)",
        "Classification": "Exact match"
    },
    {
        "Parameter": "Setup time t_setup",
        "Submitted_Manuscript_Value": "30 s",
        "Code_at_Original_Submission": "180 s (config/parameters.yaml:69 at 50bdad2)",
        "Config_Manifest_Original_Runs": "180 s (parameters.yaml at 724519f)",
        "Current_Code_Value": "180 s (config/parameters.yaml:108)",
        "Current_Results_Value": "180 s (sampled_setup_time)",
        "Classification": "Reporting error (code used 180 s all along; manuscript text erroneously stated 30 s)"
    },
    {
        "Parameter": "Urgency beta",
        "Submitted_Manuscript_Value": "2",
        "Code_at_Original_Submission": "1 at 50bdad2; updated to 2 at 724519f",
        "Config_Manifest_Original_Runs": "2 (parameters.yaml at 724519f)",
        "Current_Code_Value": "2 (config/parameters.yaml:35)",
        "Current_Results_Value": "2 (sampled_urgency_beta)",
        "Classification": "Implementation change prior to freeze (canonical frozen at beta=2)"
    },
    {
        "Parameter": "Cart capacity set C",
        "Submitted_Manuscript_Value": "{100, 150, 200}",
        "Code_at_Original_Submission": "{100, 150, 200} (config/parameters.yaml:10 at 50bdad2)",
        "Config_Manifest_Original_Runs": "{100, 150, 200}",
        "Current_Code_Value": "{100, 150, 200} (config/parameters.yaml:12-15)",
        "Current_Results_Value": "{100, 150, 200} (cart_capacity)",
        "Classification": "Exact match"
    },
    {
        "Parameter": "Pick time per piece",
        "Submitted_Manuscript_Value": "5 s",
        "Code_at_Original_Submission": "3 s at 50bdad2; updated to 5 s at 724519f",
        "Config_Manifest_Original_Runs": "5 s (parameters.yaml at 724519f)",
        "Current_Code_Value": "5 s (config/parameters.yaml:106)",
        "Current_Results_Value": "5 s (sampled_picking_time_per_item)",
        "Classification": "Implementation change prior to freeze (updated to 5 s to match standard literature)"
    },
    {
        "Parameter": "Walking speed / times",
        "Submitted_Manuscript_Value": "depot=2s, between_aisles=4s, between_shelves=2s",
        "Code_at_Original_Submission": "depot=2s, between_aisles=4s, between_shelves=2s (at 50bdad2)",
        "Config_Manifest_Original_Runs": "depot=2s, between_aisles=4s, between_shelves=2s",
        "Current_Code_Value": "depot=2s, between_aisles=4s, between_shelves=2s (config/parameters.yaml:101-103)",
        "Current_Results_Value": "depot=2s, between_aisles=4s, between_shelves=2s (sampled_walking_time_multiplier=1.0)",
        "Classification": "Exact match"
    },
    {
        "Parameter": "Warm-up W",
        "Submitted_Manuscript_Value": "5,460 s (91 min)",
        "Code_at_Original_Submission": "0 s at 50bdad2 (simulation_time: 3600s, no warmup)",
        "Config_Manifest_Original_Runs": "5,460 s (outputs/welch-stable-24h-v2 pilot)",
        "Current_Code_Value": "5,460 s (config/parameters.yaml:49)",
        "Current_Results_Value": "5,460 s (warmup_seconds)",
        "Classification": "Implementation change prior to freeze (Welch warm-up introduced to eliminate initial bias)"
    },
    {
        "Parameter": "Due allowance range",
        "Submitted_Manuscript_Value": "[1,800, 7,200] s ([30, 120] min)",
        "Code_at_Original_Submission": "[1,800, 7,200] s (src/order_generator.py:38 at dd1dae0)",
        "Config_Manifest_Original_Runs": "[1,800, 7,200] s",
        "Current_Code_Value": "[1,800, 7,200] s (config/parameters.yaml:57-58)",
        "Current_Results_Value": "[1,800, 7,200] s (sampled_due_time_min/max_seconds)",
        "Classification": "Exact match"
    },
    {
        "Parameter": "Surrogate coefficients / calibration size",
        "Submitted_Manuscript_Value": "N=10,000 calibration",
        "Code_at_Original_Submission": "None (exact routing only at dd1dae0)",
        "Config_Manifest_Original_Runs": "calibration_id: seed-20260814-n-10000-config-3b55f3efad6b",
        "Current_Code_Value": "calibrated 5-feature O(1) linear surrogate (config/parameters.yaml:113-118)",
        "Current_Results_Value": "seed-20260814-n-10000-config-3b55f3efad6b (surrogate_calibration_id)",
        "Classification": "Implementation change prior to freeze (surrogate introduced for real-time MPBH feasibility check)"
    }
]

with open("results/WP0/provenance_table_B1.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(table_b1_data[0].keys()))
    writer.writeheader()
    writer.writerows(table_b1_data)

print("Saved results/WP0/provenance_table_B1.csv")
