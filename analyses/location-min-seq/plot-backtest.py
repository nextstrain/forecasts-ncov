#!/usr/bin/env python3
"""
Figures + summary table for the location_min_seq backtest (reads results.csv).

Produces:
  figures/mae_vs_seqcount.png   - the decision plot: +30d MAE vs a location's
                                  sequences-in-trailing-150-days, with a binned-median
                                  trend and 5 / 10 / 15% reference lines.
  figures/coverage_tradeoff.png - two stacked panels sharing the threshold x-axis:
                                  (top) median & mean +30d MAE over included locations,
                                  (bottom) median # countries included per cutoff.
  summary.csv                   - per candidate threshold: MAE summaries + coverage.

Colors come from the dataviz skill's validated palette (light surface).
One axis per panel; no dual-axis charts.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# --- validated palette (light) ---
SURFACE = "#fcfcfb"; INK = "#0b0b0b"; INK2 = "#52514e"; MUTED = "#898781"
GRID = "#e1e0d9"; BASELINE = "#c3c2b7"
BLUE = "#2a78d6"; BLUE_DK = "#184f95"; BLUE_LT = "#86b6ef"; ORANGE = "#eb6834"
GOOD = "#0ca30c"; WARN = "#fab219"; CRIT = "#d03b3b"

CANDIDATES = [25, 50, 75, 100, 150, 200, 300, 500, 750, 1000]


def style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "font.family": "sans-serif", "font.size": 11,
        "axes.edgecolor": BASELINE, "axes.labelcolor": INK2, "text.color": INK,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlecolor": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "grid.color": GRID, "grid.linewidth": 0.8,
    })


def binned_stats(x, y, nbins=10):
    """Median & p90 of y within log-spaced x bins; returns centers, medians, p90s."""
    lo, hi = np.log10(max(x.min(), 1)), np.log10(x.max())
    edges = np.logspace(lo, hi, nbins + 1)
    centers, meds, p90s = [], [], []
    for a, b in zip(edges[:-1], edges[1:]):
        m = (x >= a) & (x < b)
        if m.sum() >= 3:
            centers.append(np.sqrt(a * b))
            meds.append(np.median(y[m]))
            p90s.append(np.quantile(y[m], 0.9))
    return np.array(centers), np.array(meds), np.array(p90s)


def true_coverage(full_path, excluded_path, start, end, days=150):
    """Median # countries passing each candidate threshold per cutoff, from raw data."""
    full = pd.read_csv(full_path, sep="\t", parse_dates=["date"])
    excl = set(l.strip() for l in open(excluded_path) if l.strip()) if excluded_path else set()
    cutoffs = pd.date_range(start, end, freq="MS")
    out = {T: [] for T in CANDIDATES}
    for c in cutoffs:
        w = full[(full.date >= c - pd.Timedelta(days=days - 1)) & (full.date <= c)]
        cnt = w.groupby("location")["sequences"].sum()
        cnt = cnt[~cnt.index.isin(excl)]
        for T in CANDIDATES:
            out[T].append(int((cnt >= T).sum()))
    return {T: int(np.median(v)) for T, v in out.items()}


def plot_mae_vs_seqcount(df, out):
    x = df["loc_seq_150d"].to_numpy(float)
    y = df["mae"].to_numpy(float) * 100
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.set_xscale("log")
    ax.grid(True, which="major", axis="both", alpha=0.7)
    ax.set_axisbelow(True)
    # reference bounds (status semantics: lower MAE is better), labelled directly
    for val, col, lab in [(5, GOOD, "5%"), (10, WARN, "10%"), (15, CRIT, "15%")]:
        ax.axhline(val, color=col, lw=1.4, ls="--", zorder=1)
        ax.text(x.max() * 1.02, val, f" {lab}", color=col, va="center", fontsize=9, fontweight="bold")
    # points (muted, no identity meaning -> single wash)
    ax.scatter(x, y, s=22, c=BLUE_LT, edgecolors="white", linewidths=0.4, alpha=0.7, zorder=2)
    # binned median + p90 (tail risk) trends
    cx, cmed, cp90 = binned_stats(df["loc_seq_150d"], df["mae"] * 100)
    ax.plot(cx, cmed, color=BLUE_DK, lw=2.4, marker="o", ms=5, zorder=4, label="binned median")
    ax.plot(cx, cp90, color=ORANGE, lw=2.0, ls="--", marker="s", ms=4, zorder=3, label="binned 90th pct (tail)")
    ax.set_xlabel("Sequences in trailing 150 days (the location_min_seq lever)")
    ax.set_ylabel("+30-day forecast MAE (%)")
    ax.set_ylim(0, max(16, y.max() * 1.05))
    ax.set_title("Variant-frequency forecast error vs sequencing volume (+30 days)", fontsize=12, pad=10)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    n = len(df); nc = df["cutoff"].nunique(); nl = df["location"].nunique()
    ax.text(0.0, -0.17, f"{n} country×cutoff points · {nc} monthly cutoffs · {nl} countries · "
            f"x÷5 ≈ per-30-day, x÷21.4 ≈ per-week",
            transform=ax.transAxes, fontsize=8.5, color=MUTED)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")


def summary_table(df, coverage):
    rows = []
    for T in CANDIDATES:
        inc = df[df["loc_seq_150d"] >= T]
        band = df[(df["loc_seq_150d"] >= T) & (df["loc_seq_150d"] < 2 * T)]
        rows.append({
            "location_min_seq": T,
            "per30d_equiv": round(T / 5),
            "perweek_equiv": round(T / 21.4, 1),
            "median_countries_shown": coverage.get(T),          # TRUE coverage (raw data)
            "n_scoreable_pts": len(inc),
            "median_mae_pct": None if inc.empty else round(inc["mae"].median() * 100, 2),
            "mean_mae_pct": None if inc.empty else round(inc["mae"].mean() * 100, 2),
            "p90_mae_pct": None if inc.empty else round(inc["mae"].quantile(0.9) * 100, 2),
            "marginal_band_median_mae_pct": None if band.empty else round(band["mae"].median() * 100, 2),
            "marginal_band_p90_mae_pct": None if band.empty else round(band["mae"].quantile(0.9) * 100, 2),
        })
    return pd.DataFrame(rows)


def plot_coverage_tradeoff(summary, out):
    s = summary.dropna(subset=["median_mae_pct"])
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6.6), sharex=True,
                                   gridspec_kw={"height_ratios": [1.3, 1]})
    for ax in (ax1, ax2):
        ax.set_xscale("log")
        ax.grid(True, axis="both", alpha=0.7); ax.set_axisbelow(True)
    # top: skill of the countries added at each threshold (two series -> legend + distinct style)
    ax1.plot(s["location_min_seq"], s["median_mae_pct"], color=BLUE, lw=2.4,
             marker="o", ms=5, label="median MAE (included)")
    ax1.plot(s["location_min_seq"], s["p90_mae_pct"], color=ORANGE, lw=2.0,
             ls="--", marker="s", ms=4, label="90th pct MAE (tail)")
    ax1.axhline(10, color=WARN, lw=1.3, ls=":")
    ax1.text(s["location_min_seq"].max(), 10, " 10%", color=WARN, va="center", fontsize=9, fontweight="bold")
    ax1.set_ylabel("+30-day MAE over\nincluded countries (%)")
    ax1.set_ylim(bottom=0)
    ax1.legend(frameon=False, fontsize=9, loc="upper right")
    ax1.set_title("Coverage vs forecast skill as location_min_seq varies", fontsize=12, pad=10)
    # bottom: true coverage (single series)
    ax2.plot(s["location_min_seq"], s["median_countries_shown"], color=BLUE_DK, lw=2.4,
             marker="o", ms=5)
    ax2.set_ylabel("median # countries\nshown per cutoff")
    ax2.set_ylim(bottom=0)
    ax2.set_xlabel("location_min_seq (sequences in trailing 150 days)")
    ax2.set_xticks(CANDIDATES)
    ax2.set_xticklabels([str(c) for c in CANDIDATES])
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")


def main():
    here = Path(__file__).resolve().parent
    repo = here.parents[1]
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", default=str(here / "results.csv"))
    p.add_argument("--figdir", default=str(here / "figures"))
    p.add_argument("--summary-csv", default=str(here / "summary.csv"))
    p.add_argument("--full-seq-counts", default=str(repo / "data/open/nextstrain_clades/global.tsv.gz"))
    p.add_argument("--excluded-locations", default=str(repo / "defaults/global_excluded_locations.txt"))
    p.add_argument("--start", default="2023-10-01")
    p.add_argument("--end", default="2026-08-01")
    args = p.parse_args()

    style()
    figdir = Path(args.figdir); figdir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.results)
    f30 = df[df.lag == 30].copy()
    if f30.empty:
        raise SystemExit("No +30d rows in results.csv")

    coverage = true_coverage(args.full_seq_counts, args.excluded_locations, args.start, args.end)
    plot_mae_vs_seqcount(f30, figdir / "mae_vs_seqcount.png")
    summary = summary_table(f30, coverage)
    summary.to_csv(args.summary_csv, index=False)
    plot_coverage_tradeoff(summary, figdir / "coverage_tradeoff.png")

    pd.set_option("display.width", 200, "display.max_columns", 20)
    print("\n=== summary by candidate location_min_seq "
          "(coverage = ALL countries passing T in raw open data) ===")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
