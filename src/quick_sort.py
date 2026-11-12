"""Quick Sort (Lomuto partition, last element as pivot).

Best/average O(n log n), worst case O(n^2) on sorted or reverse-sorted input.
Implemented iteratively with an explicit stack so that the worst case does not
hit Python's recursion limit. Works on a copy of the input.
"""


def quick_sort(a):
    a = a[:]
    st = [(0, len(a) - 1)]
    while st:
        lo, hi = st.pop()
        if lo >= hi:
            continue
        p = a[hi]
        i = lo - 1
        for j in range(lo, hi):
            if a[j] <= p:
                i += 1
                a[i], a[j] = a[j], a[i]
        a[i + 1], a[hi] = a[hi], a[i + 1]
        st.append((lo, i))
        st.append((i + 2, hi))
    return a
