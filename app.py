import streamlit as st
import json, math, heapq
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Load map
with open("data/nodes_edges.json") as f:
    data = json.load(f)

nodes = data["nodes"]
base_edges = data["edges"]


# ---------------- A* Pathfinding ----------------
def heuristic(a, b):
    return math.dist((a["x"], a["y"]), (b["x"], b["y"]))

def astar(start, goal, edges):
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
            if s == cur and e not in visited:
                nxt = e
            elif e == cur and s not in visited:
                nxt = s

            if nxt:
                cost = g[cur] + heuristic(nodes[cur], nodes[nxt])
                if cost < g.get(nxt, float("inf")):
                    g[nxt] = cost; parent[nxt] = cur
                    f = cost + heuristic(nodes[nxt], nodes[goal])
                    heapq.heappush(queue, (f, nxt))
    return None


# ---------------- Turn Instruction ----------------
def turn_instruction(p1, p2, p3):
    v1 = (p2["x"] - p1["x"], p2["y"] - p1["y"])
    v2 = (p3["x"] - p2["x"], p3["y"] - p2["y"])
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    if cross > 0: return "Turn left"
    elif cross < 0: return "Turn right"
    else: return "Go straight"


# ---------------- UI ----------------
st.title("Indoor Navigation : Single floor")

# Block edges first and show map immediately
blocked = st.multiselect("Block corridor (simulate closed hallway)", base_edges, [])
edges = [e for e in base_edges if e not in blocked]

img = mpimg.imread("data/floor_map.png")

def draw_map(path=None):
    fig, ax = plt.subplots()
    ax.imshow(img, extent=[0,400,0,300])

    # draw nodes
    for name, pos in nodes.items():
        ax.scatter(pos["x"], pos["y"], color="blue")
        ax.text(pos["x"]+5, pos["y"]+5, name)

    # draw edges
    for s,e in base_edges:
        x1,y1 = nodes[s]["x"], nodes[s]["y"]
        x2,y2 = nodes[e]["x"], nodes[e]["y"]

        if [s,e] in blocked or [e,s] in blocked:
            ax.plot([x1,x2],[y1,y2],"r-",linewidth=2)   # blocked shown red
        else:
            ax.plot([x1,x2],[y1,y2],"k--",alpha=0.4)

    # highlight path if exists
    if path:
        px=[nodes[p]["x"] for p in path]
        py=[nodes[p]["y"] for p in path]
        ax.plot(px,py,"g-",linewidth=4)

    st.pyplot(fig)


# Display map initially
st.subheader("Floor Map View")
draw_map()

# User selects routing
start = st.selectbox("Start", nodes.keys())
dest = st.selectbox("Destination", nodes.keys())

if st.button("Navigate"):
    path = astar(start, dest, edges)
    if not path:
        st.error("No available path")
    else:
        st.success(" → ".join(path))

        # Turn-by-turn instructions
        st.write("Turn-by-turn:")
        steps = []
        for i in range(len(path)-2):
            steps.append(turn_instruction(nodes[path[i]],nodes[path[i+1]],nodes[path[i+2]]))
        for i,ins in enumerate(steps,1):
            st.write(f"{i}. {ins}")
        st.write(f"{len(steps)+1}. Arrive at {dest}")

        draw_map(path)
