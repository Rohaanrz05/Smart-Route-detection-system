# AI-Based Smart Route Optimization System

## Project Overview

AI-Based Smart Route Optimization System is an intelligent route-finding project that helps users find the best path between two locations. The system uses multiple Artificial Intelligence algorithms to search, compare, and optimize routes based on distance, traffic score, estimated time, and total cost.

This project is developed using **Python** and **Streamlit** with an interactive map interface.

## AI Algorithms Used

This project implements four AI algorithms:

1. **Breadth First Search (BFS)**
2. **Depth First Search (DFS)**
3. **A* Search Algorithm**
4. **Hill Climbing Algorithm**

The project requirement was to use at least three AI techniques, but this system uses four algorithms.

## Features

- Select starting location
- Select destination
- Choose route priority
- Find route using BFS
- Find route using DFS
- Find optimized route using A* Search
- Find greedy optimized route using Hill Climbing
- Compare all algorithms
- Display distance, traffic score, estimated time, and cost
- Show interactive map using Folium
- Highlight selected route on the map
- Display best route according to selected priority

## Route Priorities

The user can select route priority from:

- Shortest Distance
- Least Traffic
- Fastest Time
- Balanced Route

## Technologies Used

- Python
- Streamlit
- Folium
- Streamlit-Folium
- Pandas
- Heap Queue
- Collections
- Math

## Project Structure

```text
AI-Smart-Route-Optimization/
│
├── app.py
├── requirements.txt
└── README.md
