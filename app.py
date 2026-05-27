import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import heapq
import math
import random
from collections import deque

# ======================================================
# PAGE CONFIGURATION
# ======================================================

st.set_page_config(
    page_title="AI Smart Route Optimization System",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a, #1e293b);
    color: white;
}
.main-title {
    text-align: center;
    font-size: 46px;
    font-weight: 900;
    color: #38bdf8;
    margin-bottom: 5px;
}
.sub-title {
    text-align: center;
    font-size: 18px;
    color: #cbd5e1;
    margin-bottom: 30px;
}
.card {
    background: rgba(15, 23, 42, 0.95);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #334155;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.25);
    margin-bottom: 18px;
}
.route-box {
    background: #020617;
    padding: 20px;
    border-radius: 18px;
    border-left: 6px solid #22c55e;
    margin-bottom: 15px;
}
.warning-box {
    background: #020617;
    padding: 20px;
    border-radius: 18px;
    border-left: 6px solid #f97316;
    margin-bottom: 15px;
}
.info-box {
    background: #0f172a;
    padding: 18px;
    border-radius: 16px;
    border-left: 5px solid #38bdf8;
    margin-bottom: 20px;
}
.traffic-box {
    background: #020617;
    padding: 18px;
    border-radius: 16px;
    border-left: 5px solid #facc15;
    margin-bottom: 18px;
}
div[data-testid="metric-container"] {
    background-color: #020617;
    border: 1px solid #334155;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.25);
}
.stButton > button {
    background: linear-gradient(90deg, #0284c7, #22c55e);
    color: white;
    border: none;
    border-radius: 14px;
    font-weight: 700;
    height: 48px;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #0369a1, #16a34a);
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">AI-Based Smart Route Optimization System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Dynamic Traffic Simulation using BFS, DFS, A* Search and Hill Climbing</div>', unsafe_allow_html=True)

# ======================================================
# IMPROVED CITY MAP DATASET
# Distance is fixed. Traffic is dynamic/random.
# ======================================================

locations = {
    "Home": {"coord": (33.6844, 73.0479), "desc": "Residential area where the user starts"},
    "Street 1": {"coord": (33.6900, 73.0500), "desc": "Local connecting street"},
    "Market": {"coord": (33.6945, 73.0570), "desc": "Busy commercial market area"},
    "School": {"coord": (33.6789, 73.0606), "desc": "Educational area"},
    "Bus Terminal": {"coord": (33.6721, 73.0448), "desc": "Public transport hub"},
    "Hospital": {"coord": (33.6995, 73.0363), "desc": "Medical emergency facility"},
    "Park": {"coord": (33.6938, 73.0752), "desc": "Public park and open area"},
    "Mall": {"coord": (33.7077, 73.0498), "desc": "Shopping and entertainment center"},
    "University": {"coord": (33.7170, 73.0712), "desc": "University campus"},
    "Stadium": {"coord": (33.7240, 73.0600), "desc": "Sports and event area"},
    "Railway Station": {"coord": (33.7215, 73.0895), "desc": "Railway transport point"},
    "Airport": {"coord": (33.6167, 73.0992), "desc": "Airport route"},
    "Industrial Area": {"coord": (33.7335, 73.0800), "desc": "Factory and industrial zone"},
    "Office": {"coord": (33.7294, 73.0931), "desc": "Final office destination"},
}

graph = {location: [] for location in locations}
base_traffic_data = {}


def road_key(source, destination):
    """Creates one key for a two-way road."""
    return tuple(sorted([source, destination]))


def add_road(source, destination, distance, base_traffic):
    """
    Adds a two-way road.
    distance = fixed road distance in km.
    base_traffic = normal traffic before dynamic randomization.
    """
    graph[source].append([destination, distance, base_traffic])
    graph[destination].append([source, distance, base_traffic])
    base_traffic_data[road_key(source, destination)] = base_traffic


# Residential and local roads
add_road("Home", "Street 1", 2, 1)
add_road("Home", "School", 4, 2)
add_road("Home", "Market", 5, 3)

# Central city connections
add_road("Street 1", "Market", 3, 2)
add_road("Street 1", "School", 2, 1)
add_road("Street 1", "Hospital", 5, 3)

# Education and transport side
add_road("School", "Bus Terminal", 3, 2)
add_road("School", "Park", 4, 1)
add_road("Bus Terminal", "Park", 5, 2)
add_road("Bus Terminal", "Stadium", 7, 3)

# Medical and commercial side
add_road("Market", "Hospital", 4, 4)
add_road("Market", "Mall", 6, 5)
add_road("Hospital", "Park", 3, 2)
add_road("Hospital", "University", 5, 3)
add_road("Hospital", "Mall", 4, 4)

# University and city expansion
add_road("Park", "University", 4, 2)
add_road("University", "Mall", 3, 3)
add_road("University", "Stadium", 4, 1)
add_road("University", "Railway Station", 5, 3)
add_road("University", "Industrial Area", 4, 2)

# Outer city connections
add_road("Mall", "Railway Station", 4, 4)
add_road("Railway Station", "Airport", 6, 3)
add_road("Railway Station", "Office", 5, 2)
add_road("Airport", "Office", 7, 4)
add_road("Airport", "Industrial Area", 8, 3)

# Final destination connections
add_road("Industrial Area", "Office", 3, 2)
add_road("Stadium", "Industrial Area", 4, 2)
add_road("Stadium", "Office", 6, 3)

# ======================================================
# SESSION STATE
# ======================================================

if "start_location" not in st.session_state:
    st.session_state.start_location = "Home"

if "destination_location" not in st.session_state:
    st.session_state.destination_location = "Office"

if "priority" not in st.session_state:
    st.session_state.priority = "Fastest Time"

if "traffic_scenario" not in st.session_state:
    st.session_state.traffic_scenario = "Normal"

if "traffic_seed" not in st.session_state:
    st.session_state.traffic_seed = random.randint(1, 1000000)

if "traffic_values" not in st.session_state:
    st.session_state.traffic_values = {}

if "paths" not in st.session_state:
    st.session_state.paths = {}

if "comparison_df" not in st.session_state:
    st.session_state.comparison_df = pd.DataFrame()

if "best_algorithm" not in st.session_state:
    st.session_state.best_algorithm = None

# ======================================================
# DYNAMIC TRAFFIC SIMULATION
# ======================================================


def randomize_city_traffic(traffic_scenario="Normal", seed=None):
    """
    Randomizes traffic for all roads.

    Important logic:
    1. Distance is fixed because road length does not change.
    2. Traffic is dynamic because real traffic changes.
    3. Traffic is generated once per run.
    4. The same generated traffic is used for BFS, DFS, A*, and Hill Climbing.
    5. This keeps algorithm comparison fair.
    """
    scenario_effect = {
        "Low Traffic": -1,
        "Normal": 0,
        "Peak Hours": 2,
        "Rainy Weather": 3,
        "Public Event": 4,
    }

    rng = random.Random(seed)
    traffic_adjustment = scenario_effect.get(traffic_scenario, 0)
    generated_traffic = {}

    for source, edges in graph.items():
        for edge in edges:
            destination = edge[0]
            key = road_key(source, destination)

            if key not in generated_traffic:
                base_value = base_traffic_data[key]
                random_variation = rng.randint(-1, 2)
                new_traffic = base_value + traffic_adjustment + random_variation
                new_traffic = max(1, min(10, new_traffic))
                generated_traffic[key] = new_traffic

            edge[2] = generated_traffic[key]

    return generated_traffic


def create_traffic_dataframe(traffic_values):
    rows = []
    for road, traffic in traffic_values.items():
        rows.append({
            "Road": f"{road[0]} ↔ {road[1]}",
            "Current Traffic Score": traffic,
            "Traffic Level": traffic_label(traffic),
        })
    return pd.DataFrame(rows)

# ======================================================
# HELPER FUNCTIONS
# ======================================================


def distance_between_coords(lat1, lon1, lat2, lon2):
    radius = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def haversine_distance(node1, node2):
    lat1, lon1 = locations[node1]["coord"]
    lat2, lon2 = locations[node2]["coord"]
    return distance_between_coords(lat1, lon1, lat2, lon2)


def nearest_location_from_click(lat, lon):
    nearest_node = None
    nearest_distance = float("inf")
    for node, data in locations.items():
        node_lat, node_lon = data["coord"]
        dist = distance_between_coords(lat, lon, node_lat, node_lon)
        if dist < nearest_distance:
            nearest_distance = dist
            nearest_node = node
    return nearest_node


def heuristic(node, goal):
    return haversine_distance(node, goal)


def estimate_time(distance, traffic):
    return distance * 4 + traffic * 3


def edge_cost(distance, traffic, priority):
    estimated_time = estimate_time(distance, traffic)
    if priority == "Shortest Distance":
        return distance
    if priority == "Least Traffic":
        return distance + traffic * 3
    if priority == "Fastest Time":
        return estimated_time
    return distance + traffic + estimated_time / 10


def get_edge_data(source, destination):
    for neighbor, distance, traffic in graph[source]:
        if neighbor == destination:
            return distance, traffic
    return 0, 0


def calculate_path_details(path):
    if not path or len(path) < 2:
        return 0, 0, 0, 0

    total_distance = 0
    total_traffic = 0
    total_time = 0

    for i in range(len(path) - 1):
        distance, traffic = get_edge_data(path[i], path[i + 1])
        total_distance += distance
        total_traffic += traffic
        total_time += estimate_time(distance, traffic)

    total_cost = total_distance + total_traffic + total_time / 10
    return total_distance, total_traffic, total_time, round(total_cost, 2)

# ======================================================
# AI ALGORITHMS
# ======================================================


def bfs(start, goal):
    queue = deque([[start]])
    visited = set()
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor, distance, traffic in graph[node]:
                if neighbor not in visited:
                    queue.append(path + [neighbor])
    return None


def dfs(start, goal):
    stack = [[start]]
    visited = set()
    while stack:
        path = stack.pop()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor, distance, traffic in graph[node]:
                if neighbor not in visited:
                    stack.append(path + [neighbor])
    return None


def astar(start, goal, priority):
    open_list = []
    heapq.heappush(open_list, (0, 0, start, [start]))
    visited_cost = {}

    while open_list:
        f_cost, g_cost, node, path = heapq.heappop(open_list)
        if node == goal:
            return path
        if node in visited_cost and visited_cost[node] <= g_cost:
            continue
        visited_cost[node] = g_cost

        for neighbor, distance, traffic in graph[node]:
            new_g = g_cost + edge_cost(distance, traffic, priority)
            new_f = new_g + heuristic(neighbor, goal)
            heapq.heappush(open_list, (new_f, new_g, neighbor, path + [neighbor]))

    return None


def hill_climbing(start, goal, priority):
    current = start
    path = [current]
    visited = set()

    while current != goal:
        visited.add(current)
        neighbors = []
        for neighbor, distance, traffic in graph[current]:
            if neighbor not in visited:
                score = heuristic(neighbor, goal) + edge_cost(distance, traffic, priority) * 0.2
                neighbors.append((score, neighbor))
        if not neighbors:
            return path
        neighbors.sort()
        current = neighbors[0][1]
        path.append(current)
        if len(path) > len(graph):
            break
    return path

# ======================================================
# MAP AND DISPLAY FUNCTIONS
# ======================================================


def traffic_label(traffic):
    if traffic <= 3:
        return "Low"
    if traffic <= 6:
        return "Medium"
    return "High"


def traffic_color(traffic):
    if traffic <= 3:
        return "#22c55e"  # green
    if traffic <= 6:
        return "#facc15"  # yellow
    return "#ef4444"      # red


def create_route_map(path=None, algorithm_name="Route Map"):
    center_lat = sum(locations[node]["coord"][0] for node in locations) / len(locations)
    center_lon = sum(locations[node]["coord"][1] for node in locations) / len(locations)

    route_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles="CartoDB dark_matter"
    )

    added_edges = set()
    for node in graph:
        for neighbor, distance, traffic in graph[node]:
            edge_key = road_key(node, neighbor)
            if edge_key not in added_edges:
                added_edges.add(edge_key)
                point_1 = locations[node]["coord"]
                point_2 = locations[neighbor]["coord"]
                folium.PolyLine(
                    locations=[point_1, point_2],
                    color=traffic_color(traffic),
                    weight=4,
                    opacity=0.75,
                    tooltip=(
                        f"{node} to {neighbor} | "
                        f"Distance: {distance} km | "
                        f"Traffic: {traffic} ({traffic_label(traffic)}) | "
                        f"Time: {estimate_time(distance, traffic)} min"
                    )
                ).add_to(route_map)

    if path and len(path) > 1:
        route_points = [locations[node]["coord"] for node in path]
        folium.PolyLine(
            locations=route_points,
            color="#38bdf8",
            weight=9,
            opacity=1,
            tooltip=algorithm_name
        ).add_to(route_map)

    start = st.session_state.start_location
    destination = st.session_state.destination_location

    for node, data in locations.items():
        color = "blue"
        icon = "map-marker"
        if path and node in path:
            color = "green"
        if node == start:
            color = "orange"
            icon = "home"
        if node == destination:
            color = "red"
            icon = "flag"

        folium.Marker(
            location=data["coord"],
            popup=f"<b>{node}</b><br>{data['desc']}<br>Click marker to select from map.",
            tooltip=node,
            icon=folium.Icon(color=color, icon=icon, prefix="fa")
        ).add_to(route_map)

    return route_map


def run_all_algorithms(start, goal, priority, traffic_scenario, traffic_seed):
    traffic_values = randomize_city_traffic(traffic_scenario, traffic_seed)

    paths = {
        "BFS": bfs(start, goal),
        "DFS": dfs(start, goal),
        "A* Search": astar(start, goal, priority),
        "Hill Climbing": hill_climbing(start, goal, priority),
    }

    results = []
    for algorithm, path in paths.items():
        if path:
            distance, traffic, estimated_time, cost = calculate_path_details(path)
            results.append({
                "Algorithm": algorithm,
                "Route": " → ".join(path),
                "Distance km": distance,
                "Traffic Score": traffic,
                "Estimated Time min": estimated_time,
                "Total Cost": cost,
                "Reached Goal": "Yes" if path[-1] == goal else "No",
            })

    df = pd.DataFrame(results)
    best_algorithm = None
    valid_df = df[df["Reached Goal"] == "Yes"].copy()

    if not valid_df.empty:
        if priority == "Shortest Distance":
            best = valid_df.loc[valid_df["Distance km"].idxmin()]
        elif priority == "Least Traffic":
            best = valid_df.loc[valid_df["Traffic Score"].idxmin()]
        elif priority == "Fastest Time":
            best = valid_df.loc[valid_df["Estimated Time min"].idxmin()]
        else:
            best = valid_df.loc[valid_df["Total Cost"].idxmin()]
        best_algorithm = best["Algorithm"]

    return paths, df, best_algorithm, traffic_values


def show_route_result(name, path, goal):
    if not path:
        st.error("No path found.")
        return

    distance, traffic, estimated_time, cost = calculate_path_details(path)
    reached = path[-1] == goal

    st.markdown('<div class="route-box">' if reached else '<div class="warning-box">', unsafe_allow_html=True)
    st.subheader(name)
    st.write("**Route:**", " → ".join(path))
    st.write("**Total Distance:**", distance, "km")
    st.write("**Traffic Score:**", traffic)
    st.write("**Estimated Time:**", estimated_time, "minutes")
    st.write("**Total Cost:**", cost)
    st.success("Destination reached successfully.") if reached else st.warning("This algorithm stopped before reaching the destination.")
    st.markdown("</div>", unsafe_allow_html=True)

    st_folium(create_route_map(path, name), width=1200, height=520, key=f"map_{name}")

# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:
    st.title("⚙️ Route Settings")

    st.selectbox("Select Current Location", list(graph.keys()), key="start_location")
    st.selectbox("Select Destination", list(graph.keys()), key="destination_location")

    st.selectbox(
        "Select Route Priority",
        ["Shortest Distance", "Least Traffic", "Fastest Time", "Balanced Route"],
        key="priority"
    )

    st.selectbox(
        "Select Traffic Scenario",
        ["Low Traffic", "Normal", "Peak Hours", "Rainy Weather", "Public Event"],
        key="traffic_scenario"
    )

    click_mode = st.radio(
        "Map Click Mode",
        ["Set clicked place as Current Location", "Set clicked place as Destination"]
    )

    auto_calculate = st.checkbox("Auto Calculate Route", value=True)
    regenerate_traffic = st.button("Regenerate Traffic", use_container_width=True)
    calculate_button = st.button("Find Best Route", use_container_width=True)

    st.markdown("---")
    st.write("### Algorithms Used")
    st.write("✅ BFS")
    st.write("✅ DFS")
    st.write("✅ A* Search")
    st.write("✅ Hill Climbing")

    st.markdown("---")
    st.caption("Traffic color guide:")
    st.caption("🟢 Low | 🟡 Medium | 🔴 High")

if regenerate_traffic:
    st.session_state.traffic_seed = random.randint(1, 1000000)
    st.session_state.paths = {}
    st.session_state.comparison_df = pd.DataFrame()
    st.session_state.best_algorithm = None
    st.rerun()

start = st.session_state.start_location
goal = st.session_state.destination_location
priority = st.session_state.priority
traffic_scenario = st.session_state.traffic_scenario

if start != goal and (auto_calculate or calculate_button):
    paths, comparison_df, best_algorithm, traffic_values = run_all_algorithms(
        start,
        goal,
        priority,
        traffic_scenario,
        st.session_state.traffic_seed
    )
    st.session_state.paths = paths
    st.session_state.comparison_df = comparison_df
    st.session_state.best_algorithm = best_algorithm
    st.session_state.traffic_values = traffic_values

st.markdown("""
<div class="card">
<h3>Project Overview</h3>
<p>
This intelligent system finds the best route between two locations using Artificial Intelligence algorithms.
This updated version includes dynamic traffic simulation. Distance remains fixed, but traffic changes based on real-world scenarios such as Normal, Peak Hours, Rainy Weather, and Public Event.
The same generated traffic values are used by BFS, DFS, A* Search, and Hill Climbing, so the comparison remains fair.
</p>
</div>
""", unsafe_allow_html=True)

if start == goal:
    st.warning("Current location and destination cannot be the same.")

paths = st.session_state.paths
comparison_df = st.session_state.comparison_df
best_algorithm = st.session_state.best_algorithm
traffic_values = st.session_state.traffic_values

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🗺️ Select on Map",
    "🚦 Traffic",
    "🔎 BFS",
    "🌲 DFS",
    "⭐ A* Search",
    "⛰️ Hill Climbing",
    "📊 Comparison"
])

with tab1:
    st.subheader("Interactive Map Selection")
    st.markdown("""
    <div class="info-box">
    Click any marker on the map. It will automatically become your current location or destination based on the selected Map Click Mode in the sidebar.
    Road colors show dynamic traffic: green means low, yellow means medium, and red means high.
    </div>
    """, unsafe_allow_html=True)

    selected_path = paths.get(best_algorithm) if best_algorithm in paths else None

    map_data = st_folium(
        create_route_map(selected_path, "Best Route"),
        width=1200,
        height=560,
        key="selection_map"
    )

    clicked_node = None
    if map_data:
        tooltip = map_data.get("last_object_clicked_tooltip")
        if tooltip in locations:
            clicked_node = tooltip
        elif map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lon = map_data["last_clicked"]["lng"]
            clicked_node = nearest_location_from_click(lat, lon)

    if clicked_node:
        if click_mode == "Set clicked place as Current Location":
            if st.session_state.start_location != clicked_node:
                st.session_state.start_location = clicked_node
                st.rerun()
        else:
            if st.session_state.destination_location != clicked_node:
                st.session_state.destination_location = clicked_node
                st.rerun()

with tab2:
    st.subheader("Dynamic Traffic Generated for This Run")
    st.markdown("""
    <div class="traffic-box">
    Distance is fixed because road length does not change. Traffic is randomized because real traffic changes.
    Traffic is generated once per run and then used equally by all algorithms for fair comparison.
    </div>
    """, unsafe_allow_html=True)

    if traffic_values:
        traffic_df = create_traffic_dataframe(traffic_values)
        st.dataframe(traffic_df, use_container_width=True)
        st.bar_chart(traffic_df.set_index("Road")[["Current Traffic Score"]])
    else:
        st.info("Click Find Best Route or enable Auto Calculate Route to generate traffic.")

with tab3:
    show_route_result("Breadth First Search Result", paths.get("BFS"), goal) if "BFS" in paths else st.info("Select route settings and click Find Best Route.")

with tab4:
    show_route_result("Depth First Search Result", paths.get("DFS"), goal) if "DFS" in paths else st.info("Select route settings and click Find Best Route.")

with tab5:
    show_route_result("A* Search Result", paths.get("A* Search"), goal) if "A* Search" in paths else st.info("Select route settings and click Find Best Route.")

with tab6:
    show_route_result("Hill Climbing Result", paths.get("Hill Climbing"), goal) if "Hill Climbing" in paths else st.info("Select route settings and click Find Best Route.")

with tab7:
    st.subheader("Algorithm Comparison")

    if not comparison_df.empty:
        st.dataframe(comparison_df, use_container_width=True)
        valid_df = comparison_df[comparison_df["Reached Goal"] == "Yes"].copy()

        if best_algorithm and not valid_df.empty:
            best_row = valid_df[valid_df["Algorithm"] == best_algorithm].iloc[0]

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Best Algorithm", best_row["Algorithm"])
            with col2:
                st.metric("Distance", f"{best_row['Distance km']} km")
            with col3:
                st.metric("Traffic", best_row["Traffic Score"])
            with col4:
                st.metric("Time", f"{best_row['Estimated Time min']} min")

            st.success(f"Best Route: {best_row['Route']}")

            chart_df = comparison_df.set_index("Algorithm")
            st.markdown("### Distance Comparison")
            st.bar_chart(chart_df[["Distance km"]])
            st.markdown("### Traffic Comparison")
            st.bar_chart(chart_df[["Traffic Score"]])
            st.markdown("### Estimated Time Comparison")
            st.bar_chart(chart_df[["Estimated Time min"]])
            st.markdown("### Total Cost Comparison")
            st.bar_chart(chart_df[["Total Cost"]])

            st.markdown("### Best Route Map")
            st_folium(
                create_route_map(paths[best_algorithm], "Best Route"),
                width=1200,
                height=550,
                key="best_route_map"
            )
    else:
        st.info("Select route settings and click Find Best Route.")
