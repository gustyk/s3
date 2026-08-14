param(
    [ValidateSet("reviewer", "full", "postprocess", "all")]
    [string]$Stage = "all",
    [string]$Python = "python",
    [string]$OutputRoot = "outputs/final-q1-v1"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $ProjectRoot

function Invoke-PythonChecked {
    param([string[]]$Arguments)
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code ${LASTEXITCODE}: $($Arguments -join ' ')"
    }
}

$ResolvedOutputRoot = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot $OutputRoot))
$ReviewerRoot = Join-Path $ResolvedOutputRoot "reviewer"
$FullRoot = Join-Path $ResolvedOutputRoot "full-factorial"
$PreflightRoot = Join-Path $ResolvedOutputRoot "preflight"
New-Item -ItemType Directory -Force -Path $PreflightRoot | Out-Null

if ($Stage -in @("reviewer", "all")) {
    Invoke-PythonChecked -Arguments @("-m", "src.preflight", "--config", "config/reviewer_ablation.yaml", "--output-dir", (Join-Path $ReviewerRoot "ablation"), "--mode", "full", "--repetitions", "30", "--require-clean", "--report", (Join-Path $PreflightRoot "reviewer-ablation.json"))
    Invoke-PythonChecked -Arguments @("-m", "src.preflight", "--config", "config/reviewer_sensitivity.yaml", "--output-dir", (Join-Path $ReviewerRoot "calibration"), "--mode", "full", "--repetitions", "30", "--require-clean", "--report", (Join-Path $PreflightRoot "reviewer-sensitivity.json"))
    Invoke-PythonChecked -Arguments @("-m", "src.preflight", "--config", "config/reviewer_sensitivity.yaml", "--output-dir", (Join-Path $ReviewerRoot "beta"), "--mode", "full", "--repetitions", "30", "--require-clean", "--report", (Join-Path $PreflightRoot "reviewer-beta.json"))
    Invoke-PythonChecked -Arguments @("-m", "src.ablation", "--config", "config/reviewer_ablation.yaml", "--output-dir", (Join-Path $ReviewerRoot "ablation"), "--repetitions", "30")
    Invoke-PythonChecked -Arguments @("-m", "src.benchmark_calibration", "--config", "config/reviewer_sensitivity.yaml", "--output-dir", (Join-Path $ReviewerRoot "calibration"), "--repetitions", "30")
    Invoke-PythonChecked -Arguments @("-m", "src.beta_sensitivity", "--config", "config/reviewer_sensitivity.yaml", "--output-dir", (Join-Path $ReviewerRoot "beta"), "--repetitions", "30")
    Invoke-PythonChecked -Arguments @("-m", "src.decision_benchmark", "--config", "config/parameters.yaml", "--output-dir", (Join-Path $ReviewerRoot "decision-benchmark"), "--repeats", "30")
}

if ($Stage -in @("full", "all")) {
    Invoke-PythonChecked -Arguments @("-m", "src.preflight", "--config", "config/parameters.yaml", "--output-dir", $FullRoot, "--mode", "full", "--repetitions", "30", "--require-clean", "--minimum-free-gib", "60", "--report", (Join-Path $PreflightRoot "full-factorial.json"))
    Invoke-PythonChecked -Arguments @("-m", "src.experiment", "--config", "config/parameters.yaml", "--output-dir", $FullRoot, "--mode", "full", "--repetitions", "30", "--log-level", "WARNING")
    Invoke-PythonChecked -Arguments @("-m", "src.audit_results", (Join-Path $FullRoot "results.csv"), "--manifest", (Join-Path $FullRoot "manifest.json"), "--report", (Join-Path $FullRoot "audit_report.json"))
}

if ($Stage -in @("postprocess", "all")) {
    Invoke-PythonChecked -Arguments @("-m", "src.audit_results", (Join-Path $FullRoot "results.csv"), "--manifest", (Join-Path $FullRoot "manifest.json"), "--report", (Join-Path $FullRoot "audit_report.json"))
    Invoke-PythonChecked -Arguments @("-m", "src.analysis_pipeline", (Join-Path $FullRoot "results.csv"), "--manifest", (Join-Path $FullRoot "manifest.json"), "--output-dir", (Join-Path $FullRoot "analysis"))
    Invoke-PythonChecked -Arguments @("-m", "src.additional_metrics", (Join-Path $FullRoot "results.csv"), (Join-Path $FullRoot "orders.csv.gz"), "--output-dir", (Join-Path $FullRoot "additional-metrics"))
    Invoke-PythonChecked -Arguments @("-m", "src.composite_score", (Join-Path $FullRoot "results.csv"), "--output-dir", (Join-Path $FullRoot "composite"))
}
