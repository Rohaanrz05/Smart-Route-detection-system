import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import heapq
import math
from collections import deque

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

st.markdown(
    '<div class="main-title">AI-Based Smart Route Optimization System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Professional Route Finder using BFS, DFS, A* Search and Hill Climbing</div>',
    unsafe_allow_html=True
)

locations = {
    "Home": {
        "coord": (33.6844, 73.0479),
        "desc": "Residential Area"
    },
    "Market": {
        "coord": (33.6902, 73.0551),
        "desc": "Commercial Market"
    },
    "School": {
        "coord": (33.6789, 73.0606),
        "desc": "Educational Area"
    },
    "Hospital": {
        "coord": (33.6995, 73.0363),
        "desc": "Medical Facility"
    },
    "Mall": {
        "coord": (33.7077, 73.0498),
        "desc": "Shopping Area"
    },
    "Park": {
        "coord": (33.6938, 73.0752),
        "desc": "Public Park"
    },
    "University": {
        "coord": (33.7170, 73.0712),
        "desc": "University Campus"
    },
    "Bus Stop": {
        "coord": (33.6721, 73.0448),
        "desc": "Transport Stop"
    },
    "Airport": {
        "coord": (33.6167, 73.0992),
        "desc": "Airport Route"
    },
    "Office": {
        "coord": (33.7294, 73.0931),
        "desc": "Office Area"
    }
}

graph = {
    "Home": [
        ("Market", 4, 2),
        ("School", 2, 1),
        ("Bus Stop", 5, 3)
    ],
    "Market": [
        ("Home", 4, 2),
        ("Hospital", 5, 3),
        ("Mall", 6, 4)
    ],
    "School": [
        ("Home", 2, 1),
        ("Hospital", 3, 2),
        ("Bus Stop", 4, 1),
        ("Park", 6, 2)
    ],
    "Hospital": [
        ("Market", 5, 3),
        ("School", 3, 2),
        ("University", 4, 2),
        ("Park", 3, 1)
    ],
    "Mall": [
        ("Market", 6, 4),
        ("Airport", 5, 3),
        ("University", 4, 2)
    ],
    "Park": [
        ("Hospital", 3, 1),
        ("University", 3, 1),
        ("Bus Stop", 5, 2),
        ("School", 6, 2)
    ],
    "University": [
        ("Hospital", 4, 2),
        ("Mall", 4, 2),
        ("Park", 3, 1),
        ("Office", 2, 1)
    ],
    "Bus Stop": [
        ("Home", 5, 3),
        ("School", 4, 1),
        ("Park", 5, 2),
        ("Airport", 9, 4)
    ],
    "Airport": [
        ("Mall", 5, 3),
        ("Office", 6, 4),
        ("Bus Stop", 9, 4)
    ],
    "Office": [
        ("University", 2, 1),
        ("Airport", 6, 4)
    ]
}


if "start_location" not in st.session_state:
    st.session_state.start_location = "Home"

if "destination_location" not in st.session_state:
    st.session_state.destination_location = "Office"

if "priority" not in st.session_state:
    st.session_state.priority = "Shortest Distance"

if "paths" not in st.session_state:
    st.session_state.paths = {}

if "comparison_df" not in st.session_state:
    st.session_state.comparison_df = pd.DataFrame()

if "best_algorithm" not in st.session_state:
    st.session_state.best_algorithm = None


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


def edge_cost(distance, traffic, priority):
    estimated_time = distance * 4 + traffic * 3

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
        total_time += distance * 4 + traffic * 3

    total_cost = total_distance + total_traffic

    return total_distance, total_traffic, total_time, total_cost


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
            new_path = path + [neighbor]

            heapq.heappush(open_list, (new_f, new_g, neighbor, new_path))

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
            edge_key = tuple(sorted([node, neighbor]))

            if edge_key not in added_edges:
                added_edges.add(edge_key)

                point_1 = locations[node]["coord"]
                point_2 = locations[neighbor]["coord"]

                folium.PolyLine(
                    locations=[point_1, point_2],
                    color="#64748b",
                    weight=3,
                    opacity=0.6,
                    tooltip=f"{node} to {neighbor} | Distance: {distance} km | Traffic: {traffic}"
                ).add_to(route_map)

    if path and len(path) > 1:
        route_points = [locations[node]["coord"] for node in path]

        folium.PolyLine(
            locations=route_points,
            color="#22c55e",
            weight=8,
            opacity=1,
            tooltip=algorithm_name
        ).add_to(route_map)

    start = st.session_state.start_location
    destination = st.session_state.destination_location

    for node, data in locations.items():
        coord = data["coord"]

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
            location=coord,
            popup=f"""
            <b>{node}</b><br>
            {data['desc']}<br>
            Click marker to select from map.
            """,
            tooltip=node,
            icon=folium.Icon(color=color, icon=icon, prefix="fa")
        ).add_to(route_map)

    return route_map


def run_all_algorithms(start, goal, priority):
    paths = {
        "BFS": bfs(start, goal),
        "DFS": dfs(start, goal),
        "A* Search": astar(start, goal, priority),
        "Hill Climbing": hill_climbing(start, goal, priority)
    }

    results = []

    for algorithm, path in paths.items():
        if path:
            distance, traffic, estimated_time, cost = calculate_path_details(path)
            reached = "Yes" if path[-1] == goal else "No"

            results.append({
                "Algorithm": algorithm,
                "Route": " → ".join(path),
                "Distance km": distance,
                "Traffic Score": traffic,
                "Estimated Time min": estimated_time,
                "Total Cost": cost,
                "Reached Goal": reached
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
            valid_df["Final Score"] = (
                valid_df["Distance km"]
                + valid_df["Traffic Score"]
                + valid_df["Estimated Time min"] / 10
            )
            best = valid_df.loc[valid_df["Final Score"].idxmin()]

        best_algorithm = best["Algorithm"]

    return paths, df, best_algorithm


def show_route_result(name, path, goal):
    if not path:
        st.error("No path found.")
        return

    distance, traffic, estimated_time, cost = calculate_path_details(path)
    reached = path[-1] == goal

    if reached:
        st.markdown('<div class="route-box">', unsafe_allow_html=True)
    else:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)

    st.subheader(name)
    st.write("**Route:**", " → ".join(path))
    st.write("**Total Distance:**", distance, "km")
    st.write("**Traffic Score:**", traffic)
    st.write("**Estimated Time:**", estimated_time, "minutes")
    st.write("**Total Cost:**", cost)

    if reached:
        st.success("Destination reached successfully.")
    else:
        st.warning("This algorithm stopped before reaching the destination.")

    st.markdown("</div>", unsafe_allow_html=True)

    st_folium(
        create_route_map(path, name),
        width=1200,
        height=520,
        key=f"map_{name}"
    )


with st.sidebar:
    st.title("⚙️ Route Settings")

    start_location = st.selectbox(
        "Select Current Location",
        list(graph.keys()),
        key="start_location"
    )

    destination_location = st.selectbox(
        "Select Destination",
        list(graph.keys()),
        key="destination_location"
    )

    priority = st.selectbox(
        "Select Route Priority",
        [
            "Shortest Distance",
            "Least Traffic",
            "Fastest Time",
            "Balanced Route"
        ],
        key="priority"
    )

    click_mode = st.radio(
        "Map Click Mode",
        [
            "Set clicked place as Current Location",
            "Set clicked place as Destination"
        ]
    )

    auto_calculate = st.checkbox("Auto Calculate Route", value=True)

    calculate_button = st.button("Find Best Route", use_container_width=True)

    st.markdown("---")
    st.write("### Algorithms Used")
    st.write("✅ BFS")
    st.write("✅ DFS")
    st.write("✅ A* Search")
    st.write("✅ Hill Climbing")


start = st.session_state.start_location
goal = st.session_state.destination_location
priority = st.session_state.priority

if start != goal and (auto_calculate or calculate_button):
    paths, comparison_df, best_algorithm = run_all_algorithms(start, goal, priority)

    st.session_state.paths = paths
    st.session_state.comparison_df = comparison_df
    st.session_state.best_algorithm = best_algorithm

st.markdown("""
<div class="card">
<h3>Project Overview</h3>
<p>
This intelligent system finds the best route between two locations using Artificial Intelligence algorithms.
The user can select current location and destination from the sidebar or directly from the interactive map.
The system compares BFS, DFS, A* Search, and Hill Climbing based on distance, traffic, estimated time, and total cost.
</p>
</div>
""", unsafe_allow_html=True)

if start == goal:
    st.warning("Current location and destination cannot be the same.")

paths = st.session_state.paths
comparison_df = st.session_state.comparison_df
best_algorithm = st.session_state.best_algorithm

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🗺️ Select on Map",
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
    </div>
    """, unsafe_allow_html=True)

    selected_path = None

    if best_algorithm and best_algorithm in paths:
        selected_path = paths[best_algorithm]

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
    if "BFS" in paths:
        show_route_result("Breadth First Search Result", paths["BFS"], goal)
    else:
        st.info("Select route settings and click Find Best Route.")

with tab3:
    if "DFS" in paths:
        show_route_result("Depth First Search Result", paths["DFS"], goal)
    else:
        st.info("Select route settings and click Find Best Route.")

with tab4:
    if "A* Search" in paths:
        show_route_result("A* Search Result", paths["A* Search"], goal)
    else:
        st.info("Select route settings and click Find Best Route.")

with tab5:
    if "Hill Climbing" in paths:
        show_route_result("Hill Climbing Result", paths["Hill Climbing"], goal)
    else:
        st.info("Select route settings and click Find Best Route.")

with tab6:
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

            st.markdown("### Best Route Map")
            st_folium(
                create_route_map(paths[best_algorithm], "Best Route"),
                width=1200,
                height=550,
                key="best_route_map"
            )

    else:
        st.info("Select route settings and click Find Best Route.")
