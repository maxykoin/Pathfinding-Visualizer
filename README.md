# 🧭 Pathfinding Visualizer

This project visualizes classic pathfinding algorithms on a grid using **Pygame**. It serves as an educational tool to show how algorithms like A\* and Dijkstra explore space and find the shortest path between two points.

The project is split into two modes:

* `main.py` – Modern interface with algorithm selection, comparison, and visualization
* `astar.py` / `dijkstra.py` – Standalone versions for each algorithm

---

## ✨ Features

* Interactive grid creation (add barriers, set start/end points)
* Real-time visualization of algorithm steps
* Supports multiple algorithms with comparison mode
* UI header showing selected algorithm and execution times
* Easy-to-extend structure for adding more algorithms

---

## 📁 Project Structure

```bash
📆 pathfinding-visualizer
 ├── main.py        # Unified interface with UI and comparison mode
 ├── astar.py       # Standalone A* implementation
 ├── dijkstra.py    # Standalone Dijkstra implementation
 └── README.md
```

---

## 🛠️ Technologies Used

* Python 3.12+
* [Pygame](https://www.pygame.org/)

---

## 🚀 Getting Started

### Prerequisites

Make sure you have Python and Pygame installed:

```bash
pip install pygame
```

### Running the Main Visualizer

```bash
python main.py
```

### Running Legacy Versions (Individual Files)

```bash
python astar.py
# or
python dijkstra.py
```

---

## 🎮 Controls

* 🖱️ Left Click – Place start, end, and barriers
* 🖱️ Right Click – Remove nodes
* ⌨️ 1 – Run Dijkstra's Algorithm
* ⌨️ 2 – Run A\* Algorithm
* ⌨️ 3 – Compare all algorithms
* ⌨️ C – Clear the grid

---

## 🧠 Algorithms Implemented

* ✅ A\* Search (with Manhattan heuristic)
* ✅ Dijkstra's Algorithm

### Easily Extendable

To add more algorithms:

1. Add an entry to the `ALGORITHMS` dictionary in `main.py`:

```python
ALGORITHMS = {
    "Dijkstra": {"key": pygame.K_1, "heuristic": False},
    "A*": {"key": pygame.K_2, "heuristic": True},
    "BFS": {"key": pygame.K_4, "heuristic": False},  # example
}
```

2. Use the same `runAlgorithm()` logic.

---

## 🤝 Contribution

Feel free to fork and improve this project. You can add more algorithms, improve the UI, or optimize performance. Pull requests are welcome!

---

## 📄 License

This project is open-source and available under the MIT License.