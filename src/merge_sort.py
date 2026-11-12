"""Merge Sort: Divide and Conquer, Theta(n log n) in all cases, O(n) extra space."""


def merge_sort(a):
    if len(a) <= 1:
        return a
    m = len(a) // 2
    l = merge_sort(a[:m])
    r = merge_sort(a[m:])
    res = []
    i = j = 0
    while i < len(l) and j < len(r):
        if l[i] <= r[j]:
            res.append(l[i])
            i += 1
        else:
            res.append(r[j])
            j += 1
    res.extend(l[i:])
    res.extend(r[j:])
    return res
