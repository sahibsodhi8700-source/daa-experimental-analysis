"""Breadth First Search on an adjacency list, O(V + E).

Also contains a unit-weight Dijkstra used only as an independent correctness
check, and the random connected graph generator used by the experiments.
"""
import heapq
import random
from collections import deque


def bfs(adj, s):
    dist = [-1] * len(adj)
    dist[s] = 0
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if dist[v] < 0:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def dijkstra_unit(adj, s):
    """Dijkstra with all edge weights equal to 1 (reference implementation)."""
    INF = float("inf")
    dist = [INF] * len(adj)
    dist[s] = 0
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v in adj[u]:
            if d + 1 < dist[v]:
                dist[v] = d + 1
                heapq.heappush(pq, (d + 1, v))
    return [-1 if d == INF else d for d in dist]


def random_connected_graph(V, E, rng=random):
    """Random connected undirected graph: a spanning path plus random extra edges.

    Returns an adjacency list with V vertices and (about) E edges (E >= V - 1).
    Duplicate edges are avoided.
    """
    adj = [[] for _ in range(V)]
    edges = set()
    order = list(range(V))
    rng.shuffle(order)
    for k in range(V - 1):
        u, v = order[k], order[k + 1]
        edges.add((min(u, v), max(u, v)))
        adj[u].append(v)
        adj[v].append(u)
    target = min(E, V * (V - 1) // 2)
    while len(edges) < target:
        u = rng.randrange(V)
        v = rng.randrange(V)
        if u == v:
            continue
        key = (min(u, v), max(u, v))
        if key in edges:
            continue
        edges.add(key)
        adj[u].append(v)
        adj[v].append(u)
    return adj
