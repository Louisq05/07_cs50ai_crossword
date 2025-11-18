# Crossword AI

**Generate crossword puzzles automatically using Constraint Satisfaction Problems (CSP).**

This project implements an **artificial intelligence that generates complete crossword puzzles** based on a given grid structure and a vocabulary list.  
It is part of the **CS50AI** curriculum and uses **Python 3.12**.

---

## ✨ Example Output

```
bash
python generate.py data/structure1.txt data/words1.txt output.png 
██████████████
███████M████R█ 
█INTELLIGENCE█ 
█N█████N████S█ 
█F██LOGIC███O█ 
█E█████M████L█ 
█R███SEARCH█V█ 
███████X████E█ 
██████████████
```

An image file (`output.png`) will also be generated if an output path is provided.

---
# 📚 Background

Generating a crossword puzzle can be viewed as a **Constraint Satisfaction Problem (CSP)**:

- **Variables**: Each horizontal/vertical word slot
- **Domains**: All vocabulary words of matching length
- **Unary constraints**: Word length must match the slot
- **Binary constraints**: Overlapping letters must match
- **All-different constraint**: No word may appear twice

---

# 🧠 Key Algorithms to Implement

### ✅ `enforce_node_consistency()`

Remove domain words whose length ≠ variable length.

### ✅ `revise(x, y)`

Make `x` arc-consistent with `y` by removing values that violate overlap constraints.

### ✅ `ac3(arcs=None)`

Apply the **AC-3** algorithm to all arcs (or provided arcs).

### ✅ `assignment_complete(assignment)`

Check if all variables have assigned values.

### ✅ `consistent(assignment)`

Check:

- all assigned words are unique
- all satisfy unary constraints
- all binary overlaps are respected

### ✅ `order_domain_values(var, assignment)`

Use **Least-Constraining-Value (LCV)**:  
Sort values by how few neighbors they restrict.

### ✅ `select_unassigned_variable(assignment)`

Use:

1. **Minimum Remaining Values (MRV)**
2. Tie-breaker: **Degree heuristic** (most neighbors)

### ✅ `backtrack(assignment)`

Perform recursive backtracking search  
(+ optional inference for speed).

---
# 📁 Project Structure

```bash
. 
├── crossword.py         # Provided, do not modify
├── generate.py          # Implement your AI here 
├── data/ 
│   ├── structure1.txt 
│   ├── structure2.txt 
│   ├── structure3.txt 
│   ├── words1.txt 
│   ├── words2.txt 
│   ├── words3.txt 
└── README.md
```
---

# ✔ Summary

This project teaches how to:

- Model puzzles as **Constraint Satisfaction Problems**
- Apply **AC-3**, **node consistency**, **arc consistency**
- Perform **backtracking search** with MRV, degree, and LCV heuristics
- Use Python classes to structure a solver
- Generate both textual and graphical crossword outputs
