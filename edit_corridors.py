
import streamlit as st, json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

with open("data/config.json") as f: C=json.load(f)
with open("data/nodes_edges.json") as f: D=json.load(f)
IMG=mpimg.imread("data/floor_real.png")
W_IMG,H_IMG=C["image_width"],C["image_height"]
W_DISP,H_DISP=C["display_width"],C["display_height"]
N=D["nodes"]

st.title("Polyline Corridor Editor")

if "pts" not in st.session_state: st.session_state.pts=[]
if "edges" not in st.session_state: st.session_state.edges=[]

start=st.selectbox("Start",list(N.keys()))
end=st.selectbox("End",list(N.keys()))

def disp_to_img(x,y): return int(x/W_DISP*W_IMG), int(y/H_DISP*H_IMG)

st.write("Click map, then press button below to record point")

if st.button("Add point"):
    if "last" in st.session_state:
        x,y=st.session_state.last
        ix,iy=disp_to_img(x,y)
        st.session_state.pts.append([ix,iy])

if st.button("Finish corridor") and len(st.session_state.pts)>=2:
    st.session_state.edges.append({"nodes":[start,end],"shape":st.session_state.pts.copy()})
    st.session_state.pts.clear()

if st.button("Undo point") and st.session_state.pts:
    st.session_state.pts.pop()

if st.button("Undo corridor") and st.session_state.edges:
    st.session_state.edges.pop()

if st.button("Save"):
    with open("data/edges_polyline.json","w") as f:
        json.dump(st.session_state.edges,f,indent=2)
    st.success("Saved edges_polyline.json")

fig,ax=plt.subplots(figsize=(8,6))
ax.imshow(IMG,extent=[0,W_IMG,0,H_IMG]); ax.set_xticks([]); ax.set_yticks([])
for n,p in N.items():
    x=p["x_img"]; y=p["y_img"]
    ax.scatter(x,y,c="yellow",s=80); ax.text(x+5,y+5,n,color="white")

for e in st.session_state.edges:
    xs=[x/W_IMG*W_DISP for x,y in e["shape"]]
    ys=[y/H_IMG*H_DISP for x,y in e["shape"]]
    ax.plot(xs,ys,"cyan",linewidth=3)

if st.session_state.pts:
    xs=[x/W_IMG*W_DISP for x,y in st.session_state.pts]
    ys=[y/H_IMG*H_DISP for x,y in st.session_state.pts]
    ax.plot(xs,ys,"magenta",linewidth=3)

st.pyplot(fig,clear_figure=False)

# simple click simulation helper
if st.button("Simulate click here after clicking map"):
    st.session_state.last = st.session_state.get("last",(400,300))
