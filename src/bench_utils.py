"""Timing, ratio, slope and plotting helpers (Appendix A of the report)."""
import csv
import time

import numpy as np


def timed(f, *args, runs=3):
    """Return the list of run times (ms) and their average. Only f(*args) is timed."""
    ts = []
    for _ in range(runs):
        s = time.perf_counter()
        f(*args)
        ts.append((time.perf_counter() - s) * 1000)
    return ts, sum(ts) / runs


def experiment(name, sizes, make_input, func, runs=3):
    """Run `func` on inputs of every size. Returns rows (n, [runs], average, ratio)."""
    rows = []
    prev = None
    print(name)
    print("n, runs(ms), average(ms), T(2n)/T(n)")
    for n in sizes:
        args = make_input(n)              # input generation is NOT timed
        ts, avg = timed(func, *args, runs=runs)
        ratio = None if prev is None else avg / prev
        print(n, [round(t, 2) for t in ts], round(avg, 2),
              "-" if ratio is None else round(ratio, 2))
        rows.append((n, ts, avg, ratio))
        prev = avg
    return rows


def slope(rows):
    """Log-log slope: the exponent b in T(n) = a * n^b."""
    n = np.log([r[0] for r in rows])
    t = np.log([r[2] for r in rows])
    return float(np.polyfit(n, t, 1)[0])


def model_values(n, model):
    n = np.asarray(n, float)
    return {"nlogn": n * np.log2(n), "n2": n ** 2, "n": n, "logn": np.log2(n)}[model]


def fit_constant(rows, model):
    """Least-squares constant c such that T(n) ~ c * f(n)."""
    n = [r[0] for r in rows]
    t = np.array([r[2] for r in rows])
    f = model_values(n, model)
    return float((t * f).sum() / (f * f).sum())


def save_csv(rows, path, size_label="n"):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([size_label, "run1_ms", "run2_ms", "run3_ms", "average_ms", "T(2n)/T(n)"])
        for n, ts, avg, ratio in rows:
            w.writerow([n] + [round(t, 4) for t in ts] + [round(avg, 4),
                       "" if ratio is None else round(ratio, 4)])
