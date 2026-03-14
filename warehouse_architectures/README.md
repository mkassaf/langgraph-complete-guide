# Warehouse Architectures — Centralized, Decentralized, Hybrid

Python simulation comparing all three agentic AI system architectures in a smart warehouse management scenario.

## Scenario

A warehouse manages three concurrent tasks:
- **Robot A**: Deliver boxes to rooms
- **Robot B**: Restock shelves
- **Robot C**: Handle customer pickup requests

The same tasks are handled by all three architecture types for direct comparison.

## Project Structure

```
warehouse_architectures/
├── environment.py           # Shared warehouse environment
├── parent_system.py         # ParentSystem base class
├── agents/
│   ├── base_agent.py        # Abstract base agent
│   ├── simple_reflex.py     # SimpleReflexAgent
│   ├── model_based.py       # ModelBasedReflexAgent
│   ├── goal_based.py        # GoalBasedAgent
│   └── utility_based.py     # UtilityBasedAgent
├── systems/
│   ├── centralized.py       # CentralizedAgenticSystem
│   ├── decentralized.py    # DecentralizedAgenticSystem
│   └── hybrid.py           # HybridAgenticSystem
├── main.py                  # Runs and compares all three
└── README.md
```

## Run

From project root:

```bash
python -m warehouse_architectures.main
```

## Architecture Comparison

| Architecture | Deliberative Logic | Agents | Conflict Resolution |
|--------------|-------------------|--------|---------------------|
| **Centralized** | Parent holds all | Simple/Model-based reflex | Parent resolves |
| **Decentralized** | Distributed in agents | Goal/Utility-based | Self-resolve |
| **Hybrid** | Parent + agents | Mix of goal + reflex | Mixed |

## Simulation Scenarios

1. **Normal Operation** — All robots complete tasks without issues
2. **Resource Conflict** — Robot_A and Robot_C need elevator simultaneously
3. **Agent Failure** — Robot_B crashes mid-task
4. **Unexpected Event** — Power outage in section B

## Requirements

- Python 3.10+
- No external dependencies
