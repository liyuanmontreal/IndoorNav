
# Indoor Navigation 

V1 (Single Floor)

A minimal indoor navigation prototype using:
- Graph-based map
- A* pathfinding
- Streamlit UI
- Matplotlib visualization
- 
- 

Features: 
overlays the navigation graph on a real-looking floor plan image
turn instructions + corridor blocking


## How to run
```
pip install -r requirements.txt
streamlit run app.py
```

## Files
- data/floor_real.png — background floor plan
- data/config.json — image and display sizes (auto from the image)
- data/nodes_edges.json — nodes in IMAGE PIXELS (x_img, y_img) and edges
- app.py — Streamlit app
