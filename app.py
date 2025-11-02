
import streamlit as st
import json
import math
import heapq
import matplotlib.pyplot as plt

with open("data/nodes_edges.json") as f:
    data = json.load(f)

nodes = data["nodes"]
edges = data["edges"]

def heuristic(a, b):
    return math.dist((a["x"], a["y"]), (b["x"], b["y"]))

def astar(start, goal):
    queue = [(0, start)]
    visited = set()
    g = {start: 0}
    parent = {}

    while queue:
        _, current = heapq.heappop(queue)
        if current == goal:
            # path = []
            # while current in parent:
            #     path.append(current)
            #     current = parent[current]
            # return path[::-1] + [goal]
        
            # reconstruct path
            path = [goal]
            while current in parent:
                current = parent[current]
                path.append(current)
            return path[::-1]


        visited.add(current)

        for s, e in edges:
            neighbor = None
            if s == current and e not in visited:
                neighbor = e
            elif e == current and s not in visited:
                neighbor = s

            if neighbor:
                tentative = g[current] + heuristic(nodes[current], nodes[neighbor])
                if tentative < g.get(neighbor, float("inf")):
                    g[neighbor] = tentative
                    parent[neighbor] = current
                    heapq.heappush(queue, (tentative + heuristic(nodes[neighbor], nodes[goal]), neighbor))

    return None

st.title("Indoor Navigation  (Single Floor)")

start = st.selectbox("Select your location", list(nodes.keys()))
dest = st.selectbox("Select destination", list(nodes.keys()))

if st.button("Find Path"):
    path = astar(start, dest)
    st.write("Path:", " → ".join(path))

    fig, ax = plt.subplots()
    for name, pos in nodes.items():
        ax.scatter(pos["x"], pos["y"])
        ax.text(pos["x"]+3, pos["y"]+3, name)

    for s, e in edges:
        x1, y1 = nodes[s]["x"], nodes[s]["y"]
        x2, y2 = nodes[e]["x"], nodes[e]["y"]
        ax.plot([x1, x2], [y1, y2], linestyle="--")

    px = [nodes[p]["x"] for p in path]
    py = [nodes[p]["y"] for p in path]
    ax.plot(px, py, linewidth=3)

    st.pyplot(fig)
