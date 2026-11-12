"""Longest Common Subsequence (dynamic programming), Theta(n*m) time.

`lcs` keeps only two rows (O(m) space). `lcs_table` builds the full table and is
used as an independent check and for tracing back the actual subsequence.
"""


def lcs(x, y):
    n, m = len(x), len(y)
    prev = [0] * (m + 1)
    for i in range(1, n + 1):
        cur = [0] * (m + 1)
        xi = x[i - 1]
        for j in range(1, m + 1):
            if xi == y[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = prev[j] if prev[j] >= cur[j - 1] else cur[j - 1]
        prev = cur
    return prev[m]


def lcs_table(x, y):
    """Full (n+1) x (m+1) table L, as in the textbook recurrence."""
    n, m = len(x), len(y)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if x[i - 1] == y[j - 1]:
                L[i][j] = L[i - 1][j - 1] + 1
            else:
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
    return L


def lcs_string(x, y):
    """Trace back through the full table to return one longest common subsequence."""
    L = lcs_table(x, y)
    i, j = len(x), len(y)
    out = []
    while i > 0 and j > 0:
        if x[i - 1] == y[j - 1]:
            out.append(x[i - 1])
            i -= 1
            j -= 1
        elif L[i - 1][j] >= L[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(out))
