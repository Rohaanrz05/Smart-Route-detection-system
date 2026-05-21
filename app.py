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
    font-size: 45px;
    font-weight: 800;
    color: #38bdf8;
}

.sub-title {
    text-align: center;
    font-size: 18px;
    color: #cbd5e1;
    margin-bottom: 25px;
}

.card {
    background: rgba(15, 23, 42, 0.95);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #334155;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.25);
    margin-bottom: 15px;
}

.metric-card {
    background: #020617;
    padding: 18px;
    border-radius: 16px;
    border-left: 5px solid #38bdf8;
    text-align: center;
}

.result-box {
    background: #020617;
    padding: 18px;
    border-radius: 16px;
    border-left: 5px solid #22c55e;
    margin-bottom: 15px;
}

.warning-box {
    background: #020617;
    padding: 18px;
    border-radius: 16px;
    border-left: 5px solid #f97316;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">AI-Based Smart Route Optimization System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Using BFS, DFS, A* Search, and Hill Climbing</div>',
    unsafe_allow_html=True
)

locations = {
    "Home": {
        "coord": (33.6844, 73.0479),
        "desc": "Starting residential area"
    },
    "Market": {
        "coord": (33.6902, 73.0551),
        "desc": "Busy commercial market"
    },
    "School": {
        "coord": (33.6789, 73.0606),
        "desc": "Educational area"
    },
    "Hospital": {
        "coord": (33.6995, 73.0363),
        "desc": "Emergency medical facility"
    },
    "Mall": {
        "coord": (33.7077, 73.0498),
        "desc": "Shopping mall"
    },
    "Park": {
        "coord": (33.6938, 73.0752),
        "desc": "Public park"
    },
    "University": {
        "coord": (33.7170, 73.0712),
        "desc": "University campus"
    },
    "Bus Stop": {
        "coord": (33.6721, 73.0448),
        "desc": "Public transport stop"
    },
    "Airport": {
        "coord": (33.6167, 73.0992),
        "desc": "Airport route"
    },
    "Office": {
        "coord": (33.7294, 73.0931),
        "desc": "Office destination area"
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


def haversine_distance(node1, node2):
    lat1, lon1 = locations[node1]["coord"]
    lat2, lon2 = locations[node2]["coord"]

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
                new_path = path + [neighbor]
                queue.append(new_path)

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
                new_path = path + [neighbor]
                stack.append(new_path)

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
        best_neighbor = neighbors[0][1]

        current = best_neighbor
        path.append(current)

        if len(path) > len(graph):
            break

    return path


def create_map(path=None, algorithm_name="Route Map"):
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
            weight=7,
            opacity=1,
            tooltip=algorithm_name
        ).add_to(route_map)

    for node, data in locations.items():
        coord = data["coord"]

        color = "blue"

        if path and node in path:
            color = "green"

        if path and node == path[0]:
            color = "orange"

        if path and node == path[-1]:
            color = "red"

        folium.Marker(
            location=coord,
            popup=f"""
            <b>{node}</b><br>
            {data['desc']}<br>
            Latitude: {coord[0]}<br>
            Longitude: {coord[1]}
            """,
            tooltip=node,
            icon=folium.Icon(color=color, icon="map-marker")
        ).add_to(route_map)

    return route_map


def show_algorithm_result(name, path, goal):
    if not path:
        st.error("No path found.")
        return

    distance, traffic, estimated_time, cost = calculate_path_details(path)
    reached = path[-1] == goal

    if reached:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
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

    st_folium(create_map(path, name), width=1200, height=520)


with st.sidebar:
    st.title("⚙️ Route Settings")

    start = st.selectbox(
        "Select Starting Location",
        list(graph.keys()),
        index=0
    )

    goal = st.selectbox(
        "Select Destination",
        list(graph.keys()),
        index=list(graph.keys()).index("Office")
    )

    priority = st.selectbox(
        "Select Route Priority",
        [
            "Shortest Distance",
            "Least Traffic",
            "Fastest Time",
            "Balanced Route"
        ]
    )

    run_button = st.button("Find Best Route", use_container_width=True)

    st.markdown("---")
    st.write("### Algorithms Used")
    st.write("✅ BFS")
    st.write("✅ DFS")
    st.write("✅ A* Search")
    st.write("✅ Hill Climbing")


st.markdown("""
<div class="card">
<h3>Project Overview</h3>
<p>
This project is an AI-based intelligent system that finds the best route between two locations.
It uses multiple Artificial Intelligence algorithms including BFS, DFS, A* Search, and Hill Climbing.
The system compares routes based on distance, traffic, estimated time, and total cost.
</p>
</div>
""", unsafe_allow_html=True)


if start == goal:
    st.warning("Start and destination cannot be the same.")

elif run_button:
    bfs_path = bfs(start, goal)
    dfs_path = dfs(start, goal)
    astar_path = astar(start, goal, priority)
    hill_path = hill_climbing(start, goal, priority)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Full Map",
        "BFS",
        "DFS",
        "A* Search",
        "Hill Climbing",
        "Comparison"
    ])

    with tab1:
        st.subheader("Complete City Route Map")
        st_folium(create_map(), width=1200, height=550)

    with tab2:
        show_algorithm_result("Breadth First Search", bfs_path, goal)

    with tab3:
        show_algorithm_result("Depth First Search", dfs_path, goal)

    with tab4:
        show_algorithm_result("A* Search", astar_path, goal)

    with tab5:
        show_algorithm_result("Hill Climbing", hill_path, goal)

    with tab6:
        results = []

        algorithms = {
            "BFS": bfs_path,
            "DFS": dfs_path,
            "A* Search": astar_path,
            "Hill Climbing": hill_path
        }

        for algorithm, path in algorithms.items():
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

        st.subheader("Algorithm Comparison Table")
        st.dataframe(df, use_container_width=True)

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

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Best Algorithm", best["Algorithm"])

            with col2:
                st.metric("Distance", f"{best['Distance km']} km")

            with col3:
                st.metric("Traffic", best["Traffic Score"])

            with col4:
                st.metric("Time", f"{best['Estimated Time min']} min")

            st.success(f"Best Route: {best['Route']}")

            st.subheader("Best Route Map")
            best_path = algorithms[best["Algorithm"]]
            st_folium(create_map(best_path, "Best Route"), width=1200, height=550)

else:
    st.info("Select start location, destination, and priority from the sidebar. Then click Find Best Route.")
    st_folium(create_map(), width=1200, height=550)