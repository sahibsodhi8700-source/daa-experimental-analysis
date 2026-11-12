# Implementation and Experimental Analysis of Algorithms

**Design and Analysis of Algorithms (CIC-311), Assignment 3**
Sahib Singh Sodhi · 35914802724 · C-15 · CSE Shift 1
Submitted to: Dr. Jyoti Kaushik, Assistant Professor, CSE Department
Maharaja Agrasen Institute of Technology

This repository contains the source code, input generators, raw timing results and graphs
for the report *"Implementation and Experimental Analysis of Algorithms using an Open-Source Tool"*.
Five algorithms are implemented in Python, timed on inputs that double in size, and the
measured behaviour is compared with the theoretical time complexity.

| No. | Algorithm | Syllabus group | Expected time complexity |
|-----|-----------|----------------|--------------------------|
| 1 | Merge Sort | Sorting (Divide and Conquer) | O(n log n) in all cases |
| 2 | Quick Sort | Sorting | Best/Average O(n log n), Worst O(n²) |
| 3 | Binary Search | Divide and Conquer | Best O(1), Average/Worst O(log n) |
| 4 | Longest Common Subsequence | Dynamic Programming | Θ(n·m) in all cases |
| 5 | Breadth First Search | Graph Traversal | O(V + E) in all cases |

Comparisons: Merge Sort vs Quick Sort, and Binary Search vs Linear Search (baseline only).

## Repository layout

```
daa-experimental-analysis/
├── src/
│   ├── merge_sort.py       # Section 4.2
│   ├── quick_sort.py       # Section 5.2 (Lomuto partition, iterative)
│   ├── binary_search.py    # Section 6.2 (+ linear search baseline)
│   ├── lcs.py              # Section 7.2 (two-row DP, plus full table / traceback)
│   ├── bfs.py              # Section 8.2 (+ unit-weight Dijkstra check, graph generator)
│   └── bench_utils.py      # timing, T(2n)/T(n), log-log slope, CSV helpers (Appendix A)
├── tests/
│   └── test_algorithms.py  # correctness checks that run before any timing
├── experiments/
│   └── run_all.py          # runs every experiment, writes results/ and graphs/
├── results/                # raw timings (3 runs + average + ratio) as CSV, plus run_log.txt
├── graphs/                 # experimental-analysis plots (PNG)
├── requirements.txt
└── README.md
```

## Setup

Python 3.13 is used in the report (any recent Python 3 works).

```bash
git clone https://github.com/<username>/daa-experimental-analysis.git
cd daa-experimental-analysis
pip install -r requirements.txt
```

## Run

```bash
# 1. correctness checks
python -m unittest discover -s tests -v

# 2. all experiments (full sizes from the report; takes a few minutes)
python experiments/run_all.py

# quick check with small sizes, or only some algorithms
python experiments/run_all.py --quick
python experiments/run_all.py --only merge quick
```

`--only` accepts `merge quick binary lcs bfs`. The random seed can be set with `--seed`.

## Method

* Timing function: `time.perf_counter()`. Only the algorithm call is timed; input
  generation, graph construction and correctness checks are excluded.
* 3 runs per input size; the average is reported.
* Input size doubles at every step (5 to 10 sizes per case).
* For every case the ratio `T(2n)/T(n)` and the log-log slope (the exponent `b` in `T(n) = a·nᵇ`)
  are computed.

| Complexity | O(log n) | O(n) | O(n log n) | O(n²) | O(n³) |
|---|---|---|---|---|---|
| Expected T(2n)/T(n) | slightly above 1 | about 2 | about 2.1–2.2 | about 4 | about 8 |

## Experiments and outputs

| Experiment | Input sizes | Results file(s) | Graph |
|---|---|---|---|
| Merge sort (random / sorted / reverse) | 1000 … 64000 | `merge_sort_*.csv` | `merge_sort.png` |
| Quick sort (random) | 1000 … 64000 | `quick_sort_random.csv` | `quick_sort.png` |
| Quick sort (sorted / reverse, worst case) | 500 … 16000 | `quick_sort_sorted.csv`, `quick_sort_reverse.csv`, `quick_sort_sorted_vs_random.csv` | `quick_sort.png` |
| Merge vs Quick sort | as above | `merge_vs_quick.csv` | `merge_vs_quick.png` |
| Binary search (20,000 unsuccessful searches) | 10,000 … 1,280,000 | `binary_search_unsuccessful.csv` | `binary_search.png` |
| Linear vs binary search (2,000 searches) | 16 … 8192 | `linear_search.csv`, `binary_search_2000.csv`, `linear_vs_binary.csv` | `binary_search.png` |
| LCS (random DNA / identical / 2-letter alphabet) | 200 … 3200 | `lcs_*.csv` | `lcs.png` |
| BFS, E = 4V | V = 10,000 … 320,000 | `bfs_E4V.csv` | `bfs.png` |
| BFS, V = 20,000, E = k·V | E = 40,000 … 640,000 | `bfs_V_fixed.csv` | `bfs.png` |
| Theory vs experiment | | `summary_theory_vs_experiment.csv` | `growth_all.png` |

The console output of the last full run is saved in `results/run_log.txt`.

## Notes

* Absolute times depend on the machine (the report used Linux, Intel Xeon 2.10 GHz, 2 cores,
  7 GB RAM). Re-running gives slightly different numbers; the ratios and slopes should agree
  with theory, and small sizes are noisy because of timer resolution.
* Quick sort uses the last element as pivot, so sorted and reverse-sorted input is its
  worst case. It is written iteratively (explicit stack) to avoid Python's recursion limit.
* BFS slows down per operation on very large graphs because of cache effects; the operation
  count still scales as O(V + E) (see the fixed-V experiment).

## References

1. T. H. Cormen, C. E. Leiserson, R. L. Rivest, C. Stein, *Introduction to Algorithms*, 4th ed., MIT Press, 2022.
2. Python Software Foundation, `time` module documentation, Python 3 docs.
3. J. D. Hunter, "Matplotlib: A 2D graphics environment", *Computing in Science & Engineering*, 2007.
4. C. R. Harris et al., "Array programming with NumPy", *Nature*, 2020.
