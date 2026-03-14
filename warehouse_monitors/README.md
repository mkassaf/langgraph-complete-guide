# Warehouse Monitors — Agentic AI System Monitors

Python simulation demonstrating **all 5 categories** of Agentic AI System Monitors working together in a smart warehouse robot scenario.

## Scenario

A warehouse robot agent delivers boxes to rooms. During operation, all monitors track its behavior, performance, safety, and learning in real time.

## Project Structure

```
warehouse_monitors/
├── environment.py       # Warehouse environment simulation
├── agent.py             # Robot agent with all four modules
├── monitors/
│   ├── operational.py   # Performance, Environment, Resource monitors
│   ├── ethical.py       # Goal Alignment, Bias, Safety monitors
│   ├── interaction.py   # Interaction and Communication monitors
│   ├── state_belief.py  # Internal State, Planning, Belief monitors
│   └── ancillary.py     # Explainability, Data Quality, Robustness, Learning monitors
├── monitor_manager.py   # Aggregates all monitors, system-wide tracking
├── main.py              # Runs full simulation with monitor output
└── README.md
```

## Run

From project root:

```bash
python -m warehouse_monitors.main
```

## Monitor Categories

| Category | Monitors |
|----------|----------|
| **Operational** | PerformanceMonitor, EnvironmentMonitor, ResourceUtilizationMonitor |
| **Ethical** | GoalAlignmentMonitor, BiasAndFairnessMonitor, SafetyConstraintMonitor |
| **Interaction** | InteractionMonitor, CommunicationMonitor |
| **State & Belief** | InternalStateMonitor, PlanningAndDecisionMonitor, BeliefAccuracyMonitor |
| **Ancillary** | ExplainabilityMonitor, DataQualityMonitor, RobustnessMonitor, LearningAdaptationMonitor |

## Simulation Flow

1. **Normal delivery** — Robot moves toward target
2. **Human obstacle** — Robot detours around obstacle
3. **Locked door (first)** — Robot calls human for help
4. **Locked door (after learning)** — Robot enters keypad code (learned from feedback)
5. **Adversarial event** — Sensor malfunction; monitors flag data quality issues

## Requirements

- Python 3.10+
- No external dependencies
