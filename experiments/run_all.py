"""Run all experiments from the report and write CSV results + graphs.

Usage (from the repository root):
    python experiments/run_all.py                 # full run (several minutes)
    python experiments/run_all.py --quick         # small sizes, for a fast check
    python experiments/run_all.py --only merge quick   # selected algorithms
Choices for --only: merge quick binary lcs bfs
"""
import argparse
import csv
import os
import random
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from bench_utils import (experiment, fit_constant, model_values, save_csv,  # noqa: E402
                         slope)
from bfs import bfs, random_connected_graph  # noqa: E402
from binary_search import binary_search, linear_search  # noqa: E402
from lcs import lcs  # noqa: E402
from merge_sort import merge_sort  # noqa: E402
from quick_sort import quick_sort  # noqa: E402

RESULTS = os.path.join(ROOT, "results")
GRAPHS = os.path.join(ROOT, "graphs")
SUMMARY = []  # (algorithm/case, expected, ratio_min, ratio_max, slope)


def doubling(start, count):
    return [start * 2 ** i for i in range(count)]


def record(label, expected, rows):
    ratios = [r[3] for r in rows if r[3] is not None]
    SUMMARY.append((label, expected, round(min(ratios), 2), round(max(ratios), 2),
                    round(slope(rows), 2)))
    print(f"  -> slope = {slope(rows):.2f}\n")


def panel(ax, rows, title, model=None, xlabel="Input size n"):
    n = [r[0] for r in rows]
    t = [r[2] for r in rows]
    ax.plot(n, t, "o-", label="Measured")
    if model:
        c = fit_constant(rows, model)
        ax.plot(n, c * model_values(n, model), "--", label=f"Theory (c * {model})")
    ax.set_title(title, fontsize=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Average time (ms)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)


def finish(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(GRAPHS, name), dpi=130)
    plt.close(fig)


rnd_list = lambda n: ([random.randint(0, 10 ** 6) for _ in range(n)],)   # noqa: E731
sorted_list = lambda n: (list(range(n)),)                                  # noqa: E731
rev_list = lambda n: (list(range(n, 0, -1)),)                              # noqa: E731


# ---------------------------------------------------------------- merge sort
def run_merge(quick):
    sizes = doubling(1000, 4 if quick else 7)
    out = {}
    for tag, gen, exp in (("random", rnd_list, "O(n log n)"),
                          ("sorted", sorted_list, "O(n log n)"),
                          ("reverse", rev_list, "O(n log n)")):
        rows = experiment(f"Merge sort ({tag})", sizes, gen, merge_sort)
        save_csv(rows, os.path.join(RESULTS, f"merge_sort_{tag}.csv"))
        record(f"Merge sort ({tag})", exp, rows)
        out[tag] = rows
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    panel(ax[0], out["random"], "(a) Random input", "nlogn")
    panel(ax[1], out["sorted"], "(b) Already sorted input (best case)", "nlogn")
    for tag in out:
        ax[2].plot([r[0] for r in out[tag]], [r[2] for r in out[tag]], "o-", label=tag)
    ax[2].set(title="(c) All input orders compared", xlabel="Input size n",
              ylabel="Average time (ms)")
    ax[2].legend(fontsize=8)
    ax[2].grid(True, alpha=0.3)
    fig.suptitle("Merge Sort: experimental analysis")
    finish(fig, "merge_sort.png")
    return out


# ---------------------------------------------------------------- quick sort
def run_quick(quick, merge_rows):
    sizes = doubling(1000, 4 if quick else 7)
    worst_sizes = doubling(500, 4 if quick else 6)
    r_rand = experiment("Quick sort (random)", sizes, rnd_list, quick_sort)
    save_csv(r_rand, os.path.join(RESULTS, "quick_sort_random.csv"))
    record("Quick sort (random)", "O(n log n)", r_rand)

    r_rand_small = experiment("Quick sort (random, worst-case sizes)", worst_sizes,
                              rnd_list, quick_sort)
    save_csv(r_rand_small, os.path.join(RESULTS, "quick_sort_random_small_sizes.csv"))

    r_sorted = experiment("Quick sort (sorted)", worst_sizes, sorted_list, quick_sort)
    save_csv(r_sorted, os.path.join(RESULTS, "quick_sort_sorted.csv"))
    record("Quick sort (sorted)", "O(n^2)", r_sorted)

    r_rev = experiment("Quick sort (reverse)", worst_sizes, rev_list, quick_sort)
    save_csv(r_rev, os.path.join(RESULTS, "quick_sort_reverse.csv"))
    record("Quick sort (reverse)", "O(n^2)", r_rev)

    # table (d): sorted / random on the same sizes
    with open(os.path.join(RESULTS, "quick_sort_sorted_vs_random.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "random_ms", "sorted_ms", "sorted/random"])
        for a, b in zip(r_rand_small, r_sorted):
            w.writerow([a[0], round(a[2], 4), round(b[2], 4), round(b[2] / a[2], 1)])

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    panel(ax[0], r_rand, "(a) Random input (average case)", "nlogn")
    panel(ax[1], r_sorted, "(b) Already sorted input (worst case)", "n2")
    for lab, rows in (("Random (average)", r_rand_small), ("Sorted (worst)", r_sorted),
                      ("Reverse sorted (worst)", r_rev)):
        ax[2].plot([r[0] for r in rows], [r[2] for r in rows], "o-", label=lab)
    ax[2].set(title="(c) Average vs worst cases", xlabel="Input size n",
              ylabel="Average time (ms, log scale)", yscale="log")
    ax[2].legend(fontsize=8)
    ax[2].grid(True, alpha=0.3)
    fig.suptitle("Quick Sort: experimental analysis")
    finish(fig, "quick_sort.png")

    # comparative analysis: merge vs quick
    m_rand, m_sorted = merge_rows["random"], merge_rows["sorted"]
    with open(os.path.join(RESULTS, "merge_vs_quick.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["case", "n", "merge_ms", "quick_ms", "ratio"])
        for a, b in zip(m_rand, r_rand):
            w.writerow(["random", a[0], round(a[2], 4), round(b[2], 4),
                        round(a[2] / b[2], 2)])
        for a, b in zip(m_sorted, r_sorted):
            w.writerow(["sorted", a[0], round(a[2], 4), round(b[2], 4),
                        round(b[2] / a[2], 1)])
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    ax[0].plot([r[0] for r in m_rand], [r[2] for r in m_rand], "o-", label="Merge sort")
    ax[0].plot([r[0] for r in r_rand], [r[2] for r in r_rand], "o-", label="Quick sort")
    ax[0].set(title="(a) Random input", xlabel="Input size n", ylabel="Average time (ms)")
    n_s = [r[0] for r in r_sorted]
    ax[1].plot([r[0] for r in m_sorted if r[0] in n_s],
               [r[2] for r in m_sorted if r[0] in n_s], "o-", label="Merge sort")
    ax[1].plot(n_s, [r[2] for r in r_sorted], "o-", label="Quick sort")
    ax[1].set(title="(b) Already sorted input (log scale)", xlabel="Input size n",
              ylabel="Average time (ms)", yscale="log")
    for a in ax:
        a.legend(fontsize=8)
        a.grid(True, alpha=0.3)
    fig.suptitle("Comparative analysis: Merge Sort vs Quick Sort")
    finish(fig, "merge_vs_quick.png")
    return r_rand


# -------------------------------------------------------------- binary search
def run_binary(quick):
    # (a) 20,000 unsuccessful searches in a sorted array of n elements
    sizes = [10_000 * 2 ** i for i in range(4 if quick else 8)]
    keys = 2000 if quick else 20_000

    def make(n):
        a = list(range(0, 2 * n, 2))                 # even numbers
        ks = [random.randrange(n) * 2 + 1 for _ in range(keys)]   # odd -> absent
        return (a, ks)

    def many_binary(a, ks):
        for k in ks:
            binary_search(a, k)

    rows = experiment(f"Binary search ({keys} unsuccessful searches)", sizes, make, many_binary)
    save_csv(rows, os.path.join(RESULTS, "binary_search_unsuccessful.csv"), "array_size_n")
    record("Binary search", "O(log n)", rows)

    # (b) linear vs binary search, 2,000 random keys, n = 16 .. 8192
    cmp_sizes = doubling(16, 6 if quick else 10)

    def make_cmp(n):
        a = list(range(n))
        return (a, [random.randrange(n) for _ in range(2000)])

    def many_linear(a, ks):
        for k in ks:
            linear_search(a, k)

    lin = experiment("Linear search (2000 searches)", cmp_sizes, make_cmp, many_linear)
    # re-use identical key pattern for a fair comparison: regenerate per size inside
    binr = experiment("Binary search (2000 searches)", cmp_sizes, make_cmp, many_binary)
    save_csv(lin, os.path.join(RESULTS, "linear_search.csv"), "array_size_n")
    save_csv(binr, os.path.join(RESULTS, "binary_search_2000.csv"), "array_size_n")
    with open(os.path.join(RESULTS, "linear_vs_binary.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "linear_ms", "binary_ms", "linear/binary"])
        for a, b in zip(lin, binr):
            w.writerow([a[0], round(a[2], 4), round(b[2], 4), round(a[2] / b[2], 2)])
    print(f"  -> slopes: linear {slope(lin):.2f}, binary {slope(binr):.2f}\n")

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    panel(ax[0], rows, f"(a) {keys} unsuccessful searches", "logn", "Array size n")
    ax[1].plot([r[0] for r in lin], [r[2] for r in lin], "o-", label="Linear search O(n)")
    ax[1].plot([r[0] for r in binr], [r[2] for r in binr], "o-", label="Binary search O(log n)")
    ax[1].set(title="(b) Linear vs binary search (2,000 searches)", xlabel="Array size n",
              ylabel="Average time (ms, log scale)", yscale="log")
    ax[1].legend(fontsize=8)
    ax[1].grid(True, alpha=0.3)
    ax[2].plot([r[0] for r in lin], [a[2] / b[2] for a, b in zip(lin, binr)], "o-g")
    ax[2].set(title="(c) Speed-up of binary search", xlabel="Array size n",
              ylabel="Linear time / Binary time", xscale="log", yscale="log")
    ax[2].axhline(1, color="k", ls=":")
    ax[2].grid(True, alpha=0.3)
    fig.suptitle("Binary Search: experimental analysis")
    finish(fig, "binary_search.png")


# ------------------------------------------------------------------------ LCS
def run_lcs(quick):
    sizes = doubling(200, 4 if quick else 5)
    gen = lambda alphabet: (lambda n: ("".join(random.choice(alphabet) for _ in range(n)),  # noqa: E731
                                       "".join(random.choice(alphabet) for _ in range(n))))

    def identical(n):
        s = "".join(random.choice("ACGT") for _ in range(n))
        return (s, s)

    out = {}
    for tag, mk in (("random_dna", gen("ACGT")), ("identical", identical),
                    ("binary_alphabet", gen("ab"))):
        rows = experiment(f"LCS ({tag})", sizes, mk, lcs)
        save_csv(rows, os.path.join(RESULTS, f"lcs_{tag}.csv"), "string_length_n")
        record(f"LCS ({tag})", "Theta(n^2)", rows)
        out[tag] = rows
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    panel(ax[0], out["random_dna"], "(a) Random DNA strings", "n2", "String length n")
    for tag, rows in out.items():
        ax[1].plot([r[0] for r in rows], [r[2] for r in rows], "o-", label=tag)
    ax[1].set(title="(b) Different string types", xlabel="String length n",
              ylabel="Average time (ms)")
    ax[1].legend(fontsize=8)
    ax[1].grid(True, alpha=0.3)
    rows = out["random_dna"]
    ax[2].plot([r[0] for r in rows], [r[2] * 1e6 / r[0] ** 2 for r in rows], "o-r")
    ax[2].set(title="(c) Time per table cell (flat = Theta(n^2))",
              xlabel="String length n", ylabel="ns per cell")
    ax[2].grid(True, alpha=0.3)
    fig.suptitle("Longest Common Subsequence (Dynamic Programming): experimental analysis")
    finish(fig, "lcs.png")
    return out["random_dna"]


# ------------------------------------------------------------------------ BFS
def run_bfs(quick):
    v_sizes = [10_000 * 2 ** i for i in range(3 if quick else 6)]
    rows_a = experiment("BFS (E = 4V, varying V)", v_sizes,
                        lambda V: (random_connected_graph(V, 4 * V), 0), bfs)
    save_csv(rows_a, os.path.join(RESULTS, "bfs_E4V.csv"), "vertices_V")
    record("BFS (E = 4V)", "O(V + E)", rows_a)

    V = 20_000
    ks = [2, 4, 8] if quick else [2, 4, 8, 16, 32]
    rows_b = experiment(f"BFS (V = {V}, E = k*V)", [k * V for k in ks],
                        lambda E: (random_connected_graph(V, E), 0), bfs)
    save_csv(rows_b, os.path.join(RESULTS, "bfs_V_fixed.csv"), "edges_E")
    # slope against V + E (the true work measure)
    import numpy as np
    x = np.log([V + r[0] for r in rows_b])
    y = np.log([r[2] for r in rows_b])
    s = float(np.polyfit(x, y, 1)[0])
    SUMMARY.append(("BFS (V fixed, E varying)", "O(V + E)",
                    round(min(r[3] for r in rows_b[1:]), 2),
                    round(max(r[3] for r in rows_b[1:]), 2), round(s, 2)))
    print(f"  -> slope vs (V+E) = {s:.2f}\n")

    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    ve = [(r[0], r[1], r[2], r[3]) for r in rows_a]
    n = [r[0] for r in ve]
    t = [r[2] for r in ve]
    c = sum(a * b for a, b in zip(t, [5 * v for v in n])) / sum((5 * v) ** 2 for v in n)
    ax[0].plot(n, t, "o-", label="Measured")
    ax[0].plot(n, [c * 5 * v for v in n], "--", label="Theory c*(V+E)")
    ax[0].set(title="(a) E = 4V, varying V", xlabel="Number of vertices V",
              ylabel="Average time (ms)")
    ax[0].legend(fontsize=8)
    ax[0].grid(True, alpha=0.3)
    e = [r[0] for r in rows_b]
    tb = [r[2] for r in rows_b]
    cb = sum(a * (V + b) for a, b in zip(tb, e)) / sum((V + b) ** 2 for b in e)
    ax[1].plot(e, tb, "o-", label="Measured")
    ax[1].plot(e, [cb * (V + b) for b in e], "--", label="Theory c*(V+E)")
    ax[1].set(title=f"(b) V fixed ({V}), varying E", xlabel="Number of edges E",
              ylabel="Average time (ms)")
    ax[1].legend(fontsize=8)
    ax[1].grid(True, alpha=0.3)
    ax[2].plot(n, [r[2] * 1e6 / (5 * r[0]) for r in rows_a], "o-r")
    ax[2].set(title="(c) Time per unit of (V+E) (rises: cache effect)",
              xlabel="Number of vertices V", ylabel="ns per (V+E)")
    ax[2].grid(True, alpha=0.3)
    fig.suptitle("Breadth First Search (Graph Traversal): experimental analysis")
    finish(fig, "bfs.png")
    return rows_a


# ------------------------------------------------------------------ overview
def overview(res):
    fig, ax = plt.subplots(figsize=(7.5, 5))
    for label, rows in res:
        ax.plot([r[0] for r in rows], [r[2] for r in rows], "o-",
                label=f"{label} (slope {slope(rows):.2f})")
    ax.set(xscale="log", yscale="log", xlabel="Input size n (log scale)",
           ylabel="Time in ms (log scale)", title="Growth of measured algorithms")
    ax.legend(fontsize=8)
    ax.grid(True, which="both", alpha=0.3)
    finish(fig, "growth_all.png")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="use small sizes (fast check)")
    ap.add_argument("--only", nargs="+", choices=["merge", "quick", "binary", "lcs", "bfs"])
    ap.add_argument("--seed", type=int, default=2024)
    args = ap.parse_args()
    random.seed(args.seed)
    os.makedirs(RESULTS, exist_ok=True)
    os.makedirs(GRAPHS, exist_ok=True)
    todo = set(args.only or ["merge", "quick", "binary", "lcs", "bfs"])
    if "quick" in todo:
        todo.add("merge")          # comparative analysis needs the merge sort rows

    growth = []
    merge_rows = r_quick = r_lcs = r_bfs = None
    if "merge" in todo:
        merge_rows = run_merge(args.quick)
        growth.append(("Merge sort (random)", merge_rows["random"]))
    if "quick" in todo:
        r_quick = run_quick(args.quick, merge_rows)
        growth.append(("Quick sort (random)", r_quick))
    if "binary" in todo:
        run_binary(args.quick)
    if "lcs" in todo:
        r_lcs = run_lcs(args.quick)
        growth.append(("LCS (random DNA)", r_lcs))
    if "bfs" in todo:
        r_bfs = run_bfs(args.quick)
        growth.append(("BFS (E = 4V)", r_bfs))
    if len(growth) > 1:
        overview(growth)

    with open(os.path.join(RESULTS, "summary_theory_vs_experiment.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["algorithm_case", "theoretical", "ratio_min", "ratio_max", "loglog_slope"])
        w.writerows(SUMMARY)
    print("Summary (theory vs experiment):")
    for row in SUMMARY:
        print("  ", row)


if __name__ == "__main__":
    main()
