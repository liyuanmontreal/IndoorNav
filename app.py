
import streamlit as st, json, math, heapq, os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# ----- Load data (IMAGE PIXELS only) -----
with open("data/config.json") as f:
    CFG = json.load(f)
W_IMG, H_IMG = CFG["image_width"], CFG["image_height"]

with open("data/nodes_edges.json") as f:
    DATA = json.load(f)
NODES = DATA["nodes"]  # expects x_img / y_img (falls back to x/y if present)

def get_xy(p):
    # Backward compatible with old schemas
    x = p.get("x_img", p.get("x"))
    y = p.get("y_img", p.get("y"))
    return float(x), float(y)

edges_file = "data/edges_polyline.json"
EDGES = json.load(open(edges_file)) if os.path.exists(edges_file) else []

# ----- A* with edge weight = polyline length (image px) -----
def edge_length(shape):
    s = 0.0
    for i in range(len(shape)-1):
        x1,y1 = shape[i]
        x2,y2 = shape[i+1]
        s += math.dist((x1,y1),(x2,y2))
    return s

def neighbors(node):
    for e in EDGES:
        a,b = e["nodes"]
        if node == a: yield b, e
        if node == b: yield a, e

def astar(start, goal):
    g = {start: 0.0}
    parent = {}
    pq = [(0.0, start)]
    visited = set()

    # Heuristic: straight-line in image pixels
    def h(n):
        x1,y1 = get_xy(NODES[n])
        x2,y2 = get_xy(NODES[goal])
        return math.dist((x1,y1),(x2,y2))

    while pq:
        _, cur = heapq.heappop(pq)
        if cur == goal:
            path = [goal]
            while cur in parent:
                cur = parent[cur]; path.append(cur)
            return path[::-1]
        if cur in visited: 
            continue
        visited.add(cur)

        for nxt, e in neighbors(cur):
            cost = g[cur] + edge_length(e["shape"])
            if cost < g.get(nxt, float("inf")):
                g[nxt] = cost
                parent[nxt] = cur
                heapq.heappush(pq, (cost + h(nxt), nxt))
    return None

# ----- UI -----
st.title("IndoorNav — Stable Pixel-Coordinate Build")
IMG = mpimg.imread("data/floor_real.png")

# Allow corridor blocking
blocked = st.multiselect("Block corridors", [tuple(e["nodes"]) for e in EDGES], [])

def is_blocked(e):
    pair = tuple(e["nodes"])
    return pair in blocked or pair[::-1] in blocked

def draw(path=None):
    fig, ax = plt.subplots(figsize=(10, 7))
    # background floorplan in image pixel coordinates
    ax.imshow(IMG, extent=[0, W_IMG, 0, H_IMG])
    ax.set_xlim(0, W_IMG); ax.set_ylim(0, H_IMG)
    ax.set_xticks([]); ax.set_yticks([])

    # draw corridors (polylines)
    for e in EDGES:
        xs = [pt[0] for pt in e["shape"]]
        ys = [pt[1] for pt in e["shape"]]
        ax.plot(xs, ys, "r-" if is_blocked(e) else "k-", linewidth=3, alpha=0.8)

    # draw nodes
    for name, p in NODES.items():
        x,y = get_xy(p)
        ax.scatter(x, y, c="yellow", s=90, edgecolors="black")
        ax.text(x+12, y+12, name, color="white", fontsize=11, weight="bold")

    # draw path
    if path:
        xs = [get_xy(NODES[n])[0] for n in path]
        ys = [get_xy(NODES[n])[1] for n in path]
        ax.plot(xs, ys, "lime", linewidth=5)

    st.pyplot(fig, clear_figure=True)

draw()

start = st.selectbox("Start", list(NODES.keys()))
dest = st.selectbox("Destination", list(NODES.keys()))

if st.button("Navigate"):
    if not EDGES:
        st.error("No corridors yet. (data/edges_polyline.json is empty)")
    else:
        # re-build EDGES without blocked ones
        filtered = [e for e in EDGES if not is_blocked(e)]
        if not filtered:
            st.error("All corridors are blocked.")
        else:
            # Temporarily swap for path search
            global EDGES_backup
            EDGES_backup = EDGES.copy()
            try:
                EDGES[:] = filtered
                path = astar(start, dest)
            finally:
                EDGES[:] = EDGES_backup

            if not path:
                st.error("No path under current closures.")
            else:
                st.success(" → ".join(path))
                draw(path)
