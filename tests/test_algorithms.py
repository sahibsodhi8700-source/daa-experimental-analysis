"""Correctness checks (run before any timing). Run with:  python -m unittest discover -s tests -v"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from bfs import bfs, dijkstra_unit, random_connected_graph  # noqa: E402
from binary_search import binary_search, linear_search  # noqa: E402
from lcs import lcs, lcs_string, lcs_table  # noqa: E402
from merge_sort import merge_sort  # noqa: E402
from quick_sort import quick_sort  # noqa: E402


class TestSorting(unittest.TestCase):
    def setUp(self):
        random.seed(1)
        self.a = [random.randint(0, 10 ** 6) for _ in range(5000)]

    def test_merge_sort(self):
        self.assertEqual(merge_sort(self.a), sorted(self.a))
        self.assertEqual(merge_sort(sorted(self.a)), sorted(self.a))
        self.assertEqual(merge_sort(self.a[::-1]), sorted(self.a))

    def test_merge_sort_dry_run(self):
        self.assertEqual(merge_sort([38, 27, 43, 3, 9, 82, 10]), [3, 9, 10, 27, 38, 43, 82])

    def test_quick_sort(self):
        self.assertEqual(quick_sort(self.a), sorted(self.a))
        self.assertEqual(quick_sort(sorted(self.a)), sorted(self.a))
        self.assertEqual(quick_sort(self.a[::-1]), sorted(self.a))

    def test_quick_sort_dry_run(self):
        self.assertEqual(quick_sort([10, 80, 30, 90, 40, 50, 70]), [10, 30, 40, 50, 70, 80, 90])

    def test_quick_sort_does_not_modify_input(self):
        b = self.a[:]
        quick_sort(b)
        self.assertEqual(b, self.a)

    def test_edge_cases(self):
        for f in (merge_sort, quick_sort):
            self.assertEqual(f([]), [])
            self.assertEqual(f([5]), [5])
            self.assertEqual(f([2, 2, 2]), [2, 2, 2])


class TestSearch(unittest.TestCase):
    def test_dry_run(self):
        a = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
        self.assertEqual(binary_search(a, 23), 5)

    def test_against_linear_search(self):
        random.seed(2)
        a = sorted(random.sample(range(0, 100000), 2000))
        keys = [random.choice(a) for _ in range(1100)] + \
               [random.randint(0, 100000) for _ in range(1100)]  # 2,200 keys
        for k in keys:
            b, l = binary_search(a, k), linear_search(a, k)
            self.assertEqual(b == -1, l == -1)
            if b != -1:
                self.assertEqual(a[b], k)

    def test_empty(self):
        self.assertEqual(binary_search([], 1), -1)


class TestLCS(unittest.TestCase):
    def test_textbook_example(self):
        self.assertEqual(lcs("ABCBDAB", "BDCABA"), 4)
        self.assertEqual(lcs_table("ABCBDAB", "BDCABA")[7][6], 4)
        self.assertEqual(len(lcs_string("ABCBDAB", "BDCABA")), 4)

    def test_two_row_equals_full_table(self):
        random.seed(3)
        for _ in range(3):
            x = "".join(random.choice("ACGT") for _ in range(300))
            y = "".join(random.choice("ACGT") for _ in range(300))
            self.assertEqual(lcs(x, y), lcs_table(x, y)[300][300])

    def test_edge_cases(self):
        self.assertEqual(lcs("", "ABC"), 0)
        self.assertEqual(lcs("ABC", "ABC"), 3)
        self.assertEqual(lcs("ABC", "XYZ"), 0)


class TestBFS(unittest.TestCase):
    def test_report_graph(self):
        names = "SABCDEFG"
        idx = {c: i for i, c in enumerate(names)}
        edges = ["SA", "SB", "AC", "AD", "BD", "BE", "CF", "DF", "DG", "EG"]
        adj = [[] for _ in names]
        for e in edges:
            u, v = idx[e[0]], idx[e[1]]
            adj[u].append(v)
            adj[v].append(u)
        d = bfs(adj, idx["S"])
        self.assertEqual({names[i]: d[i] for i in range(8)},
                         {"S": 0, "A": 1, "B": 1, "C": 2, "D": 2, "E": 2, "F": 3, "G": 3})

    def test_against_dijkstra(self):
        random.seed(4)
        adj = random_connected_graph(3000, 9000)
        self.assertEqual(bfs(adj, 0), dijkstra_unit(adj, 0))

    def test_generator_is_connected(self):
        random.seed(5)
        adj = random_connected_graph(500, 1500)
        self.assertNotIn(-1, bfs(adj, 0))
        self.assertEqual(sum(len(x) for x in adj) // 2, 1500)


if __name__ == "__main__":
    unittest.main()
