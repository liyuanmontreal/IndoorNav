
import streamlit as st
import json, math, heapq
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# ----- Load -----
with open("data/config.json") as f:
    CFG = json.load(f)
W_IMG, H_IMG = CFG["image_width"], CFG["image_height"]
W_DISP, H_DISP = CFG["display_width"], CFG["display_height"]

with open("data/nodes_edges.json") as f:
    DATA = json.load(f)
NODES_IMG = DATA["nodes"]
BASE_EDGES = DATA["edges"]

# Map helper: image px -> display coords
def to_display(p):
    return {"x": p["x_img"] / W_IMG * W_DISP, "y": p["y_img"] / H_IMG * H_DISP}

# Build a 'display nodes' dict on the fly
def get_display_nodes():
    return {name: to_display(p) for name, p in NODES_IMG.items()}

def heuristic(a, b):
    return math.dist((a["x"], a["y"]), (b["x"], b["y"]))

def astar(start, goal, edges):
    nodes = get_display_nodes()
    queue = [(0, start)]
    g = {start: 0}
    parent = {}
    visited = set()

    while queue:
        _, cur = heapq.heappop(queue)
        if cur == goal:
            path = [goal]
            while cur in parent:
                cur = parent[cur]
                path.append(cur)
            return path[::-1]

        visited.add(cur)
        for s, e in edges:
            nxt = None
            if s == cur and e not in visited: nxt = e
            elif e == cur and s not in visited: nxt = s
            if nxt:
                cost = g[cur] + heuristic(nodes[cur], nodes[nxt])
                if cost < g.get(nxt, float("inf")):
                    g[nxt] = cost; parent[nxt] = cur
                    f = cost + heuristic(nodes[nxt], nodes[goal])
                    heapq.heappush(queue, (f, nxt))
    return None

def turn_instruction(p1, p2, p3):
    v1=(p2["x"]-p1["x"], p2["y"]-p1["y"])
    v2=(p3["x"]-p2["x"], p3["y"]-p2["y"])
    cross = v1[0]*v2[1] - v1[1]*v2[0]
    if cross > 0: return "Turn left"
    elif cross < 0: return "Turn right"
    else: return "Go straight"

# ------------- UI -------------
st.title("Indoor Navigation v1.4 — Real Floor Map")

blocked = st.multiselect("Block corridor (simulate closure)", BASE_EDGES, [])
edges = [e for e in BASE_EDGES if e not in blocked]

# Draw map (always visible)
IMG = mpimg.imread("data/floor_real.png")

def draw_map(path=None):
    display_nodes = get_display_nodes()
    fig, ax = plt.subplots(figsize=(8, 6))
    # fit display canvas
    ax.imshow(IMG, extent=[0, W_DISP, 0, H_DISP])
    ax.set_xlim(0, W_DISP); ax.set_ylim(0, H_DISP)
    ax.set_xticks([]); ax.set_yticks([])

    # nodes
    for name, pos in display_nodes.items():
        ax.scatter(pos["x"], pos["y"], s=30)
        ax.text(pos["x"]+6, pos["y"]+6, name)

    # edges (draw all; blocked in red)
    for s,e in BASE_EDGES:
        x1,y1 = display_nodes[s]["x"], display_nodes[s]["y"]
        x2,y2 = display_nodes[e]["x"], display_nodes[e]["y"]
        if [s,e] in blocked or [e,s] in blocked:
            ax.plot([x1,x2],[y1,y2],"r-", linewidth=2, alpha=0.9)
        else:
            ax.plot([x1,x2],[y1,y2],"k--", alpha=0.5)

    # highlight path
    if path:
        px = [display_nodes[p]["x"] for p in path]
        py = [display_nodes[p]["y"] for p in path]
        ax.plot(px, py, "g-", linewidth=4)

    st.pyplot(fig, clear_figure=True)

st.subheader("Floor Map")
draw_map()

display_nodes = get_display_nodes()
start = st.selectbox("Start", list(display_nodes.keys()))
dest = st.selectbox("Destination", list(display_nodes.keys()))

if st.button("Navigate"):
    path = astar(start, dest, edges)
    if not path:
        st.error("No available path under current closures.")
    else:
        st.success(" → ".join(path))
        # turn-by-turn
        steps = []
        dn = display_nodes
        for i in range(len(path)-2):
            steps.append(turn_instruction(dn[path[i]], dn[path[i+1]], dn[path[i+2]]))
        for i, s in enumerate(steps, 1):
            st.write(f"{i}. {s}")
        st.write(f"{len(steps)+1}. Arrive at {dest}")
        draw_map(path)
