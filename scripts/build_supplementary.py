"""Build supplement/Supplementary_Material.md and .pdf from files under results/.

Tables are copied verbatim from the source CSV files (values only rounded to
three decimals for display); no numbers are recomputed. The PDF needs
reportlab (``pip install reportlab``); it is not part of the pinned
simulation environment.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "supplement"
GEN = ROOT / "docs" / "revised-paper-assets" / "generated"
MAX_ROWS = 40

TLO = "TLO = total late orders per run (count of orders); times in seconds; arrival rate in orders/min."
CI_UNVERIFIED = (
    "The 95% CI columns are taken from the source file as stored; the estimator "
    "is not documented in the repository and is therefore not verifiable here."
)

# (id, title, [(csv path, sub-caption)], units, CI note)
TABLES = [
    ("Table S1", "Tuning surface of FTWB and VTWB parameters: global and per class (arrival rate x picker group)",
     [("results/WP5/tuning_surface_global.csv", "Global tuning surface"),
      ("results/WP5/tuning_surface_class.csv", "Per-class tuning surface"),
      ("results/WP5/selected_parameters.csv", "Selected parameters")],
     TLO + " FTWB interval and VTWB threshold per the `unit` column.",
     "No confidence intervals; std_tlo is the standard deviation across cells/replications as defined in scripts/g1_tuning_analysis.py."),
    ("Table S2", "Run-status partition (order-weighted) and tardiness summary, including conditional-late and p95",
     [("results/WP3/table4d_status_partition_exact.csv", "Status partition of cohort orders (shares)"),
      ("results/WP3/tardiness_all_policies_summary.csv", "Tardiness summary (seconds)")],
     "Shares are fractions of cohort orders; tardiness in seconds.",
     "No confidence intervals. p95 definitions (run-mean vs order-weighted) are given in the header comments of the source CSV."),
    ("Table S3", "MPBH versus canonical pool by arrival rate and picker group",
     [("results/WP9/table10_v3.csv", "MPBH vs canonical, per arrival rate x picker group")],
     TLO + " `*_pct_of_N` columns in percent of cohort orders N.", CI_UNVERIFIED),
    ("Table S4", "All-arrivals TLO and inherited backlog",
     [("results/WP8/all_arrivals_tlo_v4.csv", "All-arrivals TLO by slice"),
      ("results/WP8/backlog_triage_v4.csv", "Backlog triage by policy and class")],
     TLO + " Ages in seconds.", CI_UNVERIFIED),
    ("Table S5", "Crossed timing x composition effects per arrival rate and Shapley decomposition (canonical and tuned)",
     [("results/WP4/crossed_effects_by_lambda_ci.csv", "Canonical: crossed effects per arrival rate"),
      ("results/WP4/shapley_by_lambda.csv", "Canonical: Shapley decomposition"),
      ("results/WP5/crossed_tuned_timing_effects_by_lambda_ci.csv", "Tuned: crossed effects per arrival rate"),
      ("results/WP5/crossed_tuned_timing_shapley.csv", "Tuned: Shapley decomposition")],
     "Effects in late orders per run; shares in percent.",
     "Source files report `clusters` and `df` columns, indicating cluster-level inference; " + CI_UNVERIFIED),
    ("Table S6", "Sensitivity to setup time and to warm-up length (5,460 s vs 11,000 s)",
     [("results/WP6/setup_sensitivity_with_tuned_and_cis.csv", "Setup-time sensitivity"),
      ("results/WP6/warmup_11k_vs_5k_by_setup.csv", "Warm-up comparison by setup time"),
      ("results/WP6/warmup_11k_vs_5k_by_lambda.csv", "Warm-up comparison by setup time and arrival rate")],
     TLO + " Setup time in seconds.",
     "Warm-up files: 95% CI of the paired difference using a t critical value with df = 29 (scripts/analyze_warmup_sensitivity.py). "
     "Setup-sensitivity CIs: generating script not in the repository, not verifiable."),
    ("Table S7", "Surrogate accuracy at batch level and oracle check",
     [("results/WP7/surrogate_batch_validation.csv", "Surrogate vs exact tour time by batch size"),
      ("results/WP7/oracle_decision_mismatch.csv", "Oracle decision mismatches"),
      ("results/WP7/oracle_check_results_rerun.csv", "Oracle check results")],
     "Tour-time errors in seconds (mae, rmse, signed_bias); TLO in orders per run; mismatch rate in percent.",
     "No confidence intervals reported."),
    ("Table S8", "Single-change (one-factor-at-a-time) change ladder and combined revert",
     [("results/WP0/change_ladder_ofat.csv", "Change ladder, one change at a time"),
      ("results/WP0/combined_revert_results.csv", "Combined revert, per-run results")],
     TLO + " Commit column as stored in the source file.",
     "No confidence intervals reported."),
]

FIGURES = [
    ("Figure S1", GEN / "Figure_10_tlo_sd_by_arrival_rate.png", "Standard deviation of TLO versus arrival rate (orders/min)."),
    ("Figure S2", GEN / "Figure_11_tlo_cv_by_arrival_rate.png", "Coefficient of variation of TLO versus arrival rate (orders/min)."),
    ("Figure S3", GEN / "Figure_12_tlo_sd_by_pickers.png", "Standard deviation of TLO versus number of pickers."),
    ("Figure S4", GEN / "Figure_13_tlo_cv_by_pickers.png", "Coefficient of variation of TLO versus number of pickers."),
    ("Figure S5", OUT / "Figure_S5_latency_scaling_pinned_core.png",
     "Median decision-kernel latency (ms) with IQR bars across eight policies and order-pool sizes; 30 repeats per point, process pinned to one CPU core."),
]


def read_csv(path: Path):
    comments, rows = [], []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        for line in csv.reader(handle):
            if line and line[0].startswith("#"):
                comments.append(",".join(line).lstrip("# ").strip())
            elif line:
                rows.append(line)
    return comments, rows


def fmt(value: str) -> str:
    try:
        number = float(value)
    except ValueError:
        return value
    if re.fullmatch(r"-?\d+", value.strip()):
        return value
    return f"{number:.3f}"


def limited(rows):
    shown = rows[: MAX_ROWS + 1]
    return shown, len(rows) - 1


def build_md() -> tuple[str, list]:
    md = ["# Supplementary Material", "",
          "Order-picking batching study: supplementary tables and figures. Tables are copied from the "
          "CSV files in this repository (values rounded to three decimals for display); no numbers are recomputed. "
          f"Tables longer than {MAX_ROWS} rows show the first {MAX_ROWS} rows; the full table is in the cited file.", "",
          "## Appendix A", "", "Pseudocode of all eight batching-trigger policies: [docs/Appendix_A_pseudocode.md](../docs/Appendix_A_pseudocode.md).", "",
          "## Table B1", "", "Provenance of implementation parameters: [results/WP0/provenance_table_B1.csv](../results/WP0/provenance_table_B1.csv).", ""]
    blocks = []
    for tid, title, parts, units, ci in TABLES:
        md += [f"## {tid}. {title}", "", f"**Units.** {units}", "", f"**CI method.** {ci}", ""]
        sec = {"id": tid, "title": title, "units": units, "ci": ci, "parts": []}
        for path, cap in parts:
            comments, rows = read_csv(ROOT / path)
            shown, total = limited(rows)
            md += [f"*{cap}* — source: `{path}` ({total} rows)", ""]
            for c in comments:
                md.append(f"> {c}")
            if comments:
                md.append("")
            md.append("| " + " | ".join(shown[0]) + " |")
            md.append("|" + "---|" * len(shown[0]))
            for r in shown[1:]:
                md.append("| " + " | ".join(fmt(v) for v in r) + " |")
            if total > MAX_ROWS:
                md.append("")
                md.append(f"*Showing {MAX_ROWS} of {total} rows; complete table in `{path}`.*")
            md.append("")
            sec["parts"].append((path, cap, comments, shown, total))
        blocks.append(sec)
    for fid, img, cap in FIGURES:
        rel = img.relative_to(ROOT).as_posix()
        md += [f"## {fid}", "", f"![{fid}](../{rel})", "", f"{cap} Source image: `{rel}`.", ""]
    return "\n".join(md), blocks


def build_pdf(blocks) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    from xml.sax.saxutils import escape

    ss = getSampleStyleSheet()
    small = ss["BodyText"].clone("small", fontSize=7.5, leading=9)
    cell = ss["BodyText"].clone("cell", fontSize=6, leading=7)
    page = landscape(A4)
    width = page[0] - 20 * mm
    doc = SimpleDocTemplate(str(OUT / "Supplementary_Material.pdf"), pagesize=page, leftMargin=10 * mm,
                            rightMargin=10 * mm, topMargin=10 * mm, bottomMargin=10 * mm,
                            title="Supplementary Material", author="")
    story = [Paragraph("Supplementary Material", ss["Title"]),
             Paragraph("Tables are copied from the CSV files of the replication repository (values rounded to three "
                       f"decimals for display); no numbers are recomputed. Tables longer than {MAX_ROWS} rows show the "
                       "first rows; the full table is in the cited file.", ss["BodyText"]),
             Spacer(1, 4 * mm),
             Paragraph("Appendix A", ss["Heading2"]),
             Paragraph("Pseudocode of the eight batching-trigger policies: docs/Appendix_A_pseudocode.md", ss["BodyText"]),
             Paragraph("Table B1", ss["Heading2"]),
             Paragraph("Provenance of implementation parameters: results/WP0/provenance_table_B1.csv", ss["BodyText"])]
    max_cols = 9
    for sec in blocks:
        story += [PageBreak(), Paragraph(f"{sec['id']}. {escape(sec['title'])}", ss["Heading2"]),
                  Paragraph(f"<b>Units.</b> {escape(sec['units'])}", small),
                  Paragraph(f"<b>CI method.</b> {escape(sec['ci'])}", small), Spacer(1, 3 * mm)]
        for path, cap, comments, shown, total in sec["parts"]:
            story.append(Paragraph(f"<i>{escape(cap)}</i> — source: {escape(path)} ({total} rows)", small))
            for c in comments:
                story.append(Paragraph(escape(c), small))
            header = shown[0]
            idx = list(range(len(header)))
            chunks = [idx] if len(idx) <= max_cols else [[0] + idx[i:i + max_cols - 1] for i in range(1, len(idx), max_cols - 1)]
            for chunk in chunks:
                data = [[Paragraph(escape(header[i]), cell) for i in chunk]]
                for r in shown[1:]:
                    data.append([Paragraph(escape(fmt(r[i])), cell) for i in chunk])
                tbl = Table(data, colWidths=[width / len(chunk)] * len(chunk), repeatRows=1)
                tbl.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                                         ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                                         ("VALIGN", (0, 0), (-1, -1), "TOP")]))
                story += [tbl, Spacer(1, 3 * mm)]
            if total > MAX_ROWS:
                story.append(Paragraph(f"Showing {MAX_ROWS} of {total} rows; complete table in {escape(path)}.", small))
            story.append(Spacer(1, 3 * mm))
    for fid, img, cap in FIGURES:
        from reportlab.lib.utils import ImageReader
        w, h = ImageReader(str(img)).getSize()
        scale = min((width) / w, 150 * mm / h)
        story += [PageBreak(), Paragraph(fid, ss["Heading2"]), Image(str(img), w * scale, h * scale),
                  Paragraph(escape(cap), small)]
    doc.build(story)


def main() -> None:
    md, blocks = build_md()
    (OUT / "Supplementary_Material.md").write_text(md + "\n", encoding="utf-8", newline="\n")
    build_pdf(blocks)
    print("wrote supplement/Supplementary_Material.md and .pdf")


if __name__ == "__main__":
    main()
