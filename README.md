<<<<<<< HEAD
=======



>>>>>>> fb4ebf3c8020050de0784f293c106950d37f78e7
````markdown
# 🐝 Bee Hive Simulation Project

## 📌 Overview

This project simulates a bee hive and the activities of honey bees on a property, focusing on nectar collection, honey storage, and bee communication strategies. The simulation supports both interactive and batch modes, allowing users to visualize bee movements or perform parameter sweeps to compare strategies. It fulfills the requirements of the COMP1005/5005 assignment, including postgraduate-level strategy exploration.

---

## 📂 Files Description

### `beeworld.py`

- The main simulation script.
- Handles command-line arguments, loads terrain and parameters, runs the simulation, and generates visualizations:
  - `task1.png` to `task4.png`
  - `honey_trend.png` (interactive mode)
  - `parameter_sweep_results.csv`
  - `parameter_sweep_plot.png` (batch mode)

### `buzzness.py`

- Defines core classes: `Flower`, `Tree`, `Barrier`, and `Bee`.
- Manages bee behavior: movement, nectar collection, communication.
- Implements a 3x3 nectar collection area and strategy-based movement logic.

### `test_beeworld.py`

- Unit tests using Python's `unittest` framework.
- Validates bee movement, nectar collection, and communication.

### `map1.csv`

- Terrain map file for a 40x35 world grid.
- Contains:
  - Flowers in a diamond pattern around hive at `(20, 20)`
  - Tree at `(18,14)` to `(20,16)`
  - Water barrier at `(18,17)` to `(20,19)`
  - Building at `(30,30)` to `(31,31)`

### `para1.csv`

- Batch mode parameter file.
- Specifies values for:
  - `num_bees`
  - `sim_length`
  - `nectar_amount`
  - `comm_prob`
  - `strategy_type`

---

## 🔧 Dependencies

- **Python 3.x**
- Required Libraries:
  - `matplotlib`: For visualization
  - `numpy`: For grid/array operations

### Installation

```bash
pip install matplotlib numpy
```
````

---

## 🚀 How to Run the Program

> Ensure all files (`beeworld.py`, `buzzness.py`, `map1.csv`, `para1.csv`) are in the same directory.

---

### 🧑‍💻 Interactive Mode

Run the simulation with live input prompts and visualization.

```bash
python beeworld.py -i
```

#### Prompts:

- Number of bees (e.g., 50)
- Simulation length (e.g., 30)
- Map file (e.g., map1.csv)
- Communication probability (e.g., 1.0)
- Nectar per flower (e.g., 100)
- Strategy (none, random, intelligent)

#### Outputs:

- PNG files: `task1.png`–`task4.png`, `honey_trend.png`
- Console logs: bee activity & summary (e.g., `Total Honey: 130`)

#### Interactivity:

- Press `p` to pause/resume visualization

---

### 📊 Batch Mode

Automated parameter sweep to compare strategies.

```bash
python beeworld.py -f map1.csv -p para1.csv
```

#### Outputs:

- `parameter_sweep_results.csv`: Raw results
- `parameter_sweep_plot.png`: Visual comparison of strategies
- Console: Summary and strategy performance

---

## 🧪 Running Unit Tests

Run all unit tests to validate behavior.

```bash
python test_beeworld.py
```

#### Output:

```
OK
```

If all tests pass.

---

## 📌 Example Usage

### 🟢 Interactive Mode Example:

```bash
python beeworld.py -i
```

Inputs:

```
Enter number of bees: 50
Enter simulation length: 30
Enter map file (e.g., map1.csv): map1.csv
Enter communication probability (0.0 to 1.0): 1.0
Enter nectar amount per flower: 100
Enter strategy type (none, random, intelligent): intelligent
```

> This runs a simulation with 50 bees over 30 timesteps using the intelligent strategy. Outputs visualizations and console summary (e.g., `Total Honey: 130`).

---

### 🔵 Batch Mode Example:

```bash
python beeworld.py -f map1.csv -p para1.csv
```

> This performs a parameter sweep across various strategies and conditions. Results saved in `parameter_sweep_results.csv`.

---

## 📝 Notes

- Simulation uses a **40x35** world grid.
- Bees begin in the hive for 4 timesteps, then go out for 5 steps or until they find nectar.
- The **intelligent strategy** enables bees to communicate nectar locations, leading to better collection efficiency.
- Visualizations and logs provide insight into bee behavior over time.
- Ensure `matplotlib` and `numpy` are installed to avoid runtime issues.

---

Happy buzzing! 🐝

```

Let me know if you want a PDF export of this or help creating a fancy cover page for submission!
```
