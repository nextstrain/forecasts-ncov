#!/usr/bin/env python3
"""
Score the sliding-window backtest produced by run-backtest.py.

For each cutoff C and each location in that cutoff's model output, compute the
absolute error of the model's forecast frequencies against a retrospective
"truth" (the paper's definition: empirical variant frequency from the full data
snapshot in a short window centred on the target date), and record the location's
sequence count in the trailing `location_min_seq_days` window (the `location_min_seq`
lever) as the x-axis.

Error, per (location, cutoff, lag):
    AE = mean over the model's variants of |predicted_freq - truth_freq|
Primary lag is +30 days (forecast); +0 (nowcast) is also recorded for context.

Truth is dropped (point skipped) when the truth window holds < --truth-min-seqs
sequences, because the frequency itself is then too noisy to validate against.

Clades present in the future data but absent from that cutoff's model variant set
are folded into 'other' so labels line up with what the model actually forecast.

Writes a tidy results.csv: cutoff, location, loc_seq_150d, n_variants, lag,
target_date, truth_seqs, mae.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def load_model_json(path):
    d = json.load(open(path))
    meta = d["metadata"]
    cutoff = pd.Timestamp(meta["updated"])  # anchored to the data cutoff by --as-of-date
    variants = list(meta["variants"])
    # predicted median frequencies: {site: {(location, variant): {date: value}}}
    pred = {"freq": {}, "freq_forecast": {}}
    for r in d["data"]:
        site = r.get("site")
        if site not in pred or r.get("ps") != "median" or "date" not in r:
            continue
        loc = r["location"]
        if loc == "hierarchical":
            continue
        pred[site].setdefault((loc, r["variant"]), {})[r["date"]] = r["value"]
    locations = sorted({loc for (loc, _v) in pred["freq_forecast"].keys()})
    return cutoff, variants, locations, pred


def pred_on_date(pred_site, loc, variants, target):
    """Return {variant: freq} for a location on the exact target date, or None."""
    t = str(pd.Timestamp(target).date())
    out = {}
    found = False
    for v in variants:
        series = pred_site.get((loc, v), {})
        if t in series:
            out[v] = series[t]
            found = True
        else:
            out[v] = 0.0
    return out if found else None


def truth_on_date(full, model_variants, loc, target, half_window, min_seqs):
    """Empirical variant frequency for a location in [target±half_window]."""
    lo = pd.Timestamp(target) - pd.Timedelta(days=half_window)
    hi = pd.Timestamp(target) + pd.Timedelta(days=half_window)
    sub = full[(full.location == loc) & (full.date >= lo) & (full.date <= hi)]
    total = int(sub["sequences"].sum())
    if total < min_seqs:
        return None, total
    mapped = sub["clade"].where(sub["clade"].isin(model_variants), "other")
    freq = sub.groupby(mapped)["sequences"].sum() / total
    return freq.to_dict(), total


def mae(pred, truth, variants):
    return float(np.mean([abs(pred.get(v, 0.0) - truth.get(v, 0.0)) for v in variants]))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    here = Path(__file__).resolve().parent
    repo = here.parents[1]
    p.add_argument("--model-outputs-dir", default=str(here / "model-outputs"))
    p.add_argument("--full-seq-counts", default=str(repo / "data/open/nextstrain_clades/global.tsv.gz"))
    p.add_argument("--out-csv", default=str(here / "results.csv"))
    p.add_argument("--location-min-seq-days", type=int, default=150, help="trailing window for the x-axis count")
    p.add_argument("--truth-window-days", type=int, default=14, help="full width of the truth window centred on the target")
    p.add_argument("--truth-min-seqs", type=int, default=10, help="min sequences in the truth window to score a point")
    p.add_argument("--lags", default="30,0", help="comma-separated forecast lags in days to score")
    args = p.parse_args()

    lags = [int(x) for x in args.lags.split(",")]
    half = args.truth_window_days // 2

    full = pd.read_csv(args.full_seq_counts, sep="\t", parse_dates=["date"])

    jsons = sorted(Path(args.model_outputs_dir).glob("*_results.json"))
    if not jsons:
        raise SystemExit(f"No *_results.json in {args.model_outputs_dir}")

    rows = []
    for jpath in jsons:
        cutoff, variants, locations, pred = load_model_json(jpath)
        nvar = len(variants)
        # precompute each location's trailing-window sequence count (the lever)
        lo = cutoff - pd.Timedelta(days=args.location_min_seq_days - 1)
        win = full[(full.date >= lo) & (full.date <= cutoff)]
        loc_counts = win.groupby("location")["sequences"].sum().to_dict()

        for loc in locations:
            loc_seq = int(loc_counts.get(loc, 0))
            for lag in lags:
                target = cutoff + pd.Timedelta(days=lag)
                site = "freq_forecast" if lag > 0 else "freq"
                pr = pred_on_date(pred[site], loc, variants, target)
                if pr is None:
                    continue
                tr, tseq = truth_on_date(full, set(variants), loc, target, half, args.truth_min_seqs)
                if tr is None:
                    continue
                rows.append({
                    "cutoff": cutoff.strftime("%Y-%m-%d"),
                    "location": loc,
                    "loc_seq_150d": loc_seq,
                    "n_variants": nvar,
                    "lag": lag,
                    "target_date": target.strftime("%Y-%m-%d"),
                    "truth_seqs": tseq,
                    "mae": mae(pr, tr, variants),
                })
        print(f"  scored {jpath.name}: {len(locations)} locations")

    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False)
    print(f"\nWrote {len(df)} rows to {args.out_csv}")
    if not df.empty:
        f30 = df[df.lag == 30]
        print(f"+30d points: {len(f30)} across {f30.cutoff.nunique()} cutoffs, "
              f"{f30.location.nunique()} distinct locations")
        print(f"+30d MAE overall: median={f30.mae.median()*100:.2f}%  mean={f30.mae.mean()*100:.2f}%")


if __name__ == "__main__":
    main()
