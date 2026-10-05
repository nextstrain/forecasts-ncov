#!/usr/bin/env python3
"""
Sliding-window backtest driver for choosing `location_min_seq`.

For each monthly cutoff date C over the backtest span, this:
  1. runs scripts/prepare-data.py with --max-date C and a low location-inclusion
     floor (so many countries spanning low->high sequencing volume enter the fit),
  2. runs scripts/run-mlr-model.py with --as-of-date C (so the hierarchical MLR
     forecasts exactly C+1 .. C+forecast_L rather than out to wall-clock today),
     auto-selecting the most abundant variant as the pivot (pivot choice does not
     affect frequency forecasts, which are what we score).

Model-output JSONs are written to <outdir>/model-outputs/<C>_results.json and then
scored by score-backtest.py. post_process (colours/display names) is skipped.

Cutoffs are independent and run in parallel (--jobs). Re-running skips cutoffs whose
results JSON already exists unless --force is given.
"""
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
PREPARE = REPO / "scripts" / "prepare-data.py"
RUNMLR = REPO / "scripts" / "run-mlr-model.py"


def monthly_cutoffs(start, end):
    """First-of-month timestamps from start to end inclusive."""
    return list(pd.date_range(start=start, end=end, freq="MS"))


def pick_pivot(prepared_seq_path):
    """Most abundant non-'other' variant in the prepared data (fallback: any)."""
    df = pd.read_csv(prepared_seq_path, sep="\t")
    totals = df.groupby("variant")["sequences"].sum().sort_values(ascending=False)
    for variant in totals.index:
        if variant != "other":
            return variant
    return totals.index[0]


def run_one(cutoff, args, prepared_dir, model_dir, log_dir):
    c = cutoff.strftime("%Y-%m-%d")
    results_json = model_dir / f"{c}_results.json"
    if results_json.exists() and not args.force:
        return c, "skip (exists)"

    prepared_seq = prepared_dir / f"{c}_seq.tsv"
    prepared_cases = prepared_dir / f"{c}_cases.tsv"
    log = log_dir / f"{c}.log"

    # Subprocess env: keep each jax/numpyro process lean so we can run several at once.
    env = dict(os.environ)
    env.setdefault("JAX_PLATFORMS", "cpu")
    env.setdefault("OMP_NUM_THREADS", "2")
    env.setdefault("XLA_FLAGS", "--xla_force_host_platform_device_count=1")

    with open(log, "w") as lf:
        # 1. prepare-data at cutoff C with the low inclusion floor
        prep_cmd = [
            sys.executable, str(PREPARE),
            "--seq-counts", args.seq_counts,
            "--cases", args.cases,
            "--max-date", c,
            "--included-days", str(args.included_days),
            "--location-min-seq", str(args.location_min_seq),
            "--location-min-seq-days", str(args.location_min_seq_days),
            "--clade-min-seq", str(args.clade_min_seq),
            "--clade-min-seq-days", str(args.clade_min_seq_days),
            "--output-seq-counts", str(prepared_seq),
            "--output-cases", str(prepared_cases),
        ]
        if args.excluded_locations:
            prep_cmd += ["--excluded-locations", args.excluded_locations]
        lf.write(f"$ {' '.join(prep_cmd)}\n"); lf.flush()
        r = subprocess.run(prep_cmd, stdout=lf, stderr=subprocess.STDOUT, env=env)
        if r.returncode != 0:
            return c, "FAIL prepare-data (see log)"

        pivot = pick_pivot(prepared_seq)
        lf.write(f"\n[pivot auto-selected: {pivot}]\n"); lf.flush()

        # 2. run-mlr-model with forecast horizon anchored to the cutoff
        mlr_cmd = [
            sys.executable, "-u", str(RUNMLR),
            "--config", args.mlr_config,
            "--seq-path", str(prepared_seq),
            "--export-path", str(model_dir),
            "--pivot", pivot,
            "--as-of-date", c,
            "--data-name", c,
        ]
        lf.write(f"\n$ {' '.join(mlr_cmd)}\n"); lf.flush()
        r = subprocess.run(mlr_cmd, stdout=lf, stderr=subprocess.STDOUT, env=env)
        if r.returncode != 0:
            return c, "FAIL run-mlr-model (see log)"

    return c, "ok" if results_json.exists() else "FAIL (no output json)"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seq-counts", default=str(REPO / "data/open/nextstrain_clades/global.tsv.gz"))
    p.add_argument("--cases", default=str(REPO / "data/cases/global.tsv.gz"))
    p.add_argument("--mlr-config", default=str(REPO / "config/mlr-config.yaml"))
    p.add_argument("--outdir", default=str(Path(__file__).resolve().parent))
    p.add_argument("--start", default="2023-10-01", help="first monthly cutoff (YYYY-MM-DD)")
    p.add_argument("--end", default="2026-08-01", help="last monthly cutoff (YYYY-MM-DD); needs +30d of truth after it")
    p.add_argument("--location-min-seq", type=int, default=20, help="low inclusion FLOOR for the backtest fits")
    p.add_argument("--location-min-seq-days", type=int, default=150)
    p.add_argument("--included-days", type=int, default=150)
    p.add_argument("--clade-min-seq", type=int, default=150)
    p.add_argument("--clade-min-seq-days", type=int, default=150)
    p.add_argument("--excluded-locations", default=str(REPO / "defaults/global_excluded_locations.txt"))
    p.add_argument("--jobs", type=int, default=4, help="parallel cutoffs")
    p.add_argument("--force", action="store_true", help="re-run cutoffs even if results exist")
    args = p.parse_args()

    outdir = Path(args.outdir)
    prepared_dir = outdir / "prepared"
    model_dir = outdir / "model-outputs"
    log_dir = outdir / "logs"
    for d in (prepared_dir, model_dir, log_dir):
        d.mkdir(parents=True, exist_ok=True)

    cutoffs = monthly_cutoffs(args.start, args.end)
    print(f"Backtest: {len(cutoffs)} monthly cutoffs {args.start} .. {args.end}, "
          f"floor={args.location_min_seq}/{args.location_min_seq_days}d, jobs={args.jobs}")

    results = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(run_one, c, args, prepared_dir, model_dir, log_dir): c for c in cutoffs}
        for fut in as_completed(futs):
            c, status = fut.result()
            results[c] = status
            print(f"  [{c}] {status}", flush=True)

    ok = sum(1 for s in results.values() if s in ("ok", "skip (exists)"))
    print(f"\nDone: {ok}/{len(cutoffs)} cutoffs have results. Outputs in {model_dir}")
    fails = {c: s for c, s in results.items() if s.startswith("FAIL")}
    if fails:
        print("FAILURES:", fails)
        sys.exit(1)


if __name__ == "__main__":
    main()
