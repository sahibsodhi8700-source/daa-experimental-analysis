"""Binary search (O(log n)) and linear search (O(n), used only as a baseline)."""


def binary_search(a, t):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == t:
            return mid
        if a[mid] < t:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def linear_search(a, t):
    for i in range(len(a)):
        if a[i] == t:
            return i
    return -1
