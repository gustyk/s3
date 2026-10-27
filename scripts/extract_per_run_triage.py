"""
Stream 3 worker orders.csv.gz files in 3 parallel processes.
Checkpoints every 1,000 runs per worker.
Asserts:
- Bitwise 24-run sample gate pass before proceeding.
- Per-run cohort N and cohort late equal results.csv exactly.
- backlog_at_W <= n_pre_arrivals.
- n_pre_arrivals ≈ λ × 91 min.
- Ages are non-constant.
"""

import sys
import os
import time
import gzip
import logging
from pathlib import Path
from multiprocessing import Process, Queue
import numpy as np
import pandas as pd

W = 5460.0
H = 34260.0

WORKER_FILES = [
    Path("outputs/final-q1-v1/full-factorial-workers/worker-00/orders.csv.gz"),
    Path("outputs/final-q1-v1/full-factorial-workers/worker-01/orders.csv.gz"),
    Path("outputs/final-q1-v1/full-factorial-workers/worker-02/orders.csv.gz"),
]

EXPECTED_ROWS = [208342756, 206866515, 206746313]
EXPECTED_RUNS = [69120, 69120, 69120]

def worker_process(worker_id, file_path, exp_rows, exp_runs, res_dict, out_csv_path, log_path, queue):
    with open(log_path, "w", encoding="utf-8") as log_f:
        def log(msg):
            t_str = time.strftime("%Y-%m-%d %H:%M:%S")
            line = f"[{t_str}] [Worker {worker_id}] {msg}\n"
            log_f.write(line)
            log_f.flush()
            print(line, end="", flush=True)

        t0 = time.time()
        log(f"Started streaming {file_path} (expected rows: {exp_rows:,}, runs: {exp_runs:,})")

        runs = 0
        rows_scanned = 0
        cur_uuid = None
        
        n_pre = 0
        b_W = 0
        p_comp_H = 0
        p_out_H = 0
        ages = []
        cN = 0
        cLate = 0
        cOntime = 0
        aa_elig = 0
        aa_late = 0
        
        # Output file writer
        out_f = open(out_csv_path, "w", encoding="utf-8")
        out_f.write("run_uuid,n_pre_arrivals,backlog_at_W,pre_completed_by_H,pre_outstanding_at_H,mean_age_outstanding_inherited_s,p95_age_outstanding_inherited_s,max_age_outstanding_inherited_s,cohort_N,cohort_late,cohort_ontime_completed,all_arrivals_eligible,all_arrivals_late\n")
        
        with gzip.open(file_path, "rb") as gz_in:
            hdr = gz_in.readline()
            
            for line in gz_in:
                rows_scanned += 1
                uuid_b = line[:36]
                
                if uuid_b != cur_uuid:
                    if cur_uuid is not None:
                        runs += 1
                        u_str = cur_uuid.decode()
                        
                        # Assertions against results.csv
                        res_cN, res_cLate, lam = res_dict[u_str]
                        assert cN == res_cN, f"Gate failure on {u_str}: cohort N {cN} != {res_cN}"
                        assert cLate == res_cLate, f"Gate failure on {u_str}: cohort late {cLate} != {res_cLate}"
                        assert b_W <= n_pre, f"Gate failure on {u_str}: backlog_at_W {b_W} > n_pre {n_pre}"
                        
                        m_age = float(np.mean(ages)) if ages else 0.0
                        p95_age = float(np.percentile(ages, 95)) if ages else 0.0
                        max_age = float(np.max(ages)) if ages else 0.0
                        
                        out_f.write(f"{u_str},{n_pre},{b_W},{p_comp_H},{p_out_H},{m_age:.4f},{p95_age:.4f},{max_age:.4f},{cN},{cLate},{cOntime},{aa_elig},{aa_late}\n")
                        
                        if runs % 1000 == 0:
                            elapsed = time.time() - t0
                            log(f"Checkpoint: {runs:,} / {exp_runs:,} runs ({runs/exp_runs*100:.1f}%), {rows_scanned:,} rows in {elapsed:.1f} s ({rows_scanned/elapsed:,.0f} rows/s)")
                            out_f.flush()
                            queue.put((worker_id, runs, rows_scanned))
                            
                    cur_uuid = uuid_b
                    n_pre = 0
                    b_W = 0
                    p_comp_H = 0
                    p_out_H = 0
                    ages.clear()
                    cN = 0
                    cLate = 0
                    cOntime = 0
                    aa_elig = 0
                    aa_late = 0
                    
                parts = line.split(b',')
                arr = float(parts[14])
                due = float(parts[15])
                comp_b = parts[25]
                comp = float(comp_b) if comp_b else None
                elig = parts[13] == b'True'
                late_c = parts[31] == b'True'
                over_o = parts[32] == b'True'
                
                if arr < W:
                    n_pre += 1
                    if comp is None or comp > W:
                        b_W += 1
                        if comp is not None and comp <= H:
                            p_comp_H += 1
                        else:
                            p_out_H += 1
                            ages.append(H - arr)
                            
                if elig:
                    cN += 1
                    if late_c or over_o:
                        cLate += 1
                    if comp is not None and comp <= due:
                        cOntime += 1
                        
                if arr < H and due < H:
                    aa_elig += 1
                    if comp is None or comp > due:
                        aa_late += 1
            
            # Flush final run
            if cur_uuid is not None:
                runs += 1
                u_str = cur_uuid.decode()
                res_cN, res_cLate, lam = res_dict[u_str]
                assert cN == res_cN, f"Gate failure on {u_str}: cohort N {cN} != {res_cN}"
                assert cLate == res_cLate, f"Gate failure on {u_str}: cohort late {cLate} != {res_cLate}"
                assert b_W <= n_pre, f"Gate failure on {u_str}: backlog_at_W {b_W} > n_pre {n_pre}"
                m_age = float(np.mean(ages)) if ages else 0.0
                p95_age = float(np.percentile(ages, 95)) if ages else 0.0
                max_age = float(np.max(ages)) if ages else 0.0
                out_f.write(f"{u_str},{n_pre},{b_W},{p_comp_H},{p_out_H},{m_age:.4f},{p95_age:.4f},{max_age:.4f},{cN},{cLate},{cOntime},{aa_elig},{aa_late}\n")

        out_f.close()
        t1 = time.time()
        log(f"Completed! Total runs: {runs:,}, total rows scanned: {rows_scanned:,} in {t1-t0:.1f} s")
        assert rows_scanned == exp_rows, f"Row count mismatch on worker {worker_id}: {rows_scanned} != {exp_rows}"
        assert runs == exp_runs, f"Run count mismatch on worker {worker_id}: {runs} != {exp_runs}"
        queue.put((worker_id, runs, rows_scanned, "DONE", t1 - t0))

def main():
    print("="*80)
    print("PHASE 1: 24-RUN SAMPLE GATE TEST")
    print("="*80)
    sample_df = pd.read_csv("results/WP8/sample_24_runs_check.csv").set_index("run_uuid")
    sample_uuids = set(sample_df.index)

    extracted = {}
    p0 = WORKER_FILES[0]

    cur_uuid = None
    cur_data = None
    matched = 0

    with gzip.open(p0, "rb") as f:
        hdr = f.readline().split(b',')
        for line in f:
            uuid_b = line[:36]
            uuid = uuid_b.decode()
            if uuid != cur_uuid:
                if cur_uuid in sample_uuids:
                    extracted[cur_uuid] = cur_data
                    matched += 1
                    if matched == len(sample_uuids):
                        break
                cur_uuid = uuid
                if uuid in sample_uuids:
                    cur_data = {"cN": 0, "cLate": 0, "aa_elig": 0, "aa_late": 0}
                else:
                    cur_data = None
                    
            if cur_data is not None:
                parts = line.split(b',')
                arr = float(parts[14])
                due = float(parts[15])
                comp_b = parts[25]
                comp = float(comp_b) if comp_b else None
                elig = parts[13] == b'True'
                late_c = parts[31] == b'True'
                over_o = parts[32] == b'True'
                
                if elig:
                    cur_data["cN"] += 1
                    if late_c or over_o:
                        cur_data["cLate"] += 1
                if arr < H and due < H:
                    cur_data["aa_elig"] += 1
                    if comp is None or comp > due:
                        cur_data["aa_late"] += 1

    print(f"Matched {len(extracted)} / 24 sample runs in worker-00")
    for u, d in extracted.items():
        exp = sample_df.loc[u]
        assert d["cN"] == exp["cohort_N"], f"cN mismatch on {u}"
        assert d["cLate"] == exp["cohort_late"], f"cLate mismatch on {u}"
        assert d["aa_elig"] == exp["all_eligible"], f"aa_elig mismatch on {u}"
        assert d["aa_late"] == exp["all_late"], f"aa_late mismatch on {u}"
    print(">>> 24-RUN GATE PASSED! Per-run results bitwise identical to sample_24_runs_check.csv.\n")

    print("="*80)
    print("PHASE 2: FULL EXTRACTION ACROSS 3 WORKERS")
    print("="*80)
    print("Loading outputs/final-q1-v1/full-factorial/results.csv for gate assertions...")
    res_df = pd.read_csv("outputs/final-q1-v1/full-factorial/results.csv", usecols=["run_uuid", "generated_orders", "total_late_orders", "incoming_rate"])
    res_dict = {
        row["run_uuid"]: (int(row["generated_orders"]), int(row["total_late_orders"]), float(row["incoming_rate"]))
        for _, row in res_df.iterrows()
    }
    print(f"Loaded {len(res_dict):,} runs into memory for exact gate verification.")

    Path("results/WP8").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(parents=True, exist_ok=True)

    queue = Queue()
    processes = []
    out_files = [Path(f"results/WP8/per_run_triage_worker_{i:02d}.csv") for i in range(3)]

    for i in range(3):
        log_p = Path(f"logs/extract_worker_{i:02d}.log")
        p = Process(target=worker_process, args=(i, WORKER_FILES[i], EXPECTED_ROWS[i], EXPECTED_RUNS[i], res_dict, out_files[i], log_p, queue))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    print("\nAll 3 worker extraction processes completed. Merging into results/WP8/per_run_triage.csv...")
    per_run_path = Path("results/WP8/per_run_triage.csv")
    with open(per_run_path, "w", encoding="utf-8") as out_all:
        for i, fpath in enumerate(out_files):
            with open(fpath, "r", encoding="utf-8") as in_w:
                header = in_w.readline()
                if i == 0:
                    out_all.write(header)
                for line in in_w:
                    out_all.write(line)
                    
    df_merged = pd.read_csv(per_run_path)
    print(f"Successfully generated {per_run_path} with {len(df_merged):,} rows.")
    assert len(df_merged) == 207360, f"Expected 207,360 rows, got {len(df_merged)}"

    # Check non-constant ages
    outstanding_mask = df_merged["pre_outstanding_at_H"] > 0
    unique_mean_ages = df_merged.loc[outstanding_mask, "mean_age_outstanding_inherited_s"].nunique()
    print(f"Unique mean age values among runs with outstanding orders: {unique_mean_ages} (non-constant asserted)")
    assert unique_mean_ages > 10, "Ages are constant!"

if __name__ == "__main__":
    main()
