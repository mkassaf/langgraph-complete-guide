"""
Warehouse Monitors — Full Simulation with All 5 Monitor Categories

Runs the warehouse robot agent through 5 delivery scenarios while all
monitors track behavior, performance, safety, and learning in real time.

Run from project root:
    python -m warehouse_monitors.main
"""

from warehouse_monitors.agent import UtilityBasedRobotAgent
from warehouse_monitors.environment import (
    ActionType,
    WarehouseEnvironment,
)
from warehouse_monitors.monitor_manager import MonitorManager


def run_simulation() -> None:
    """Run full simulation with monitor output."""
    # 1. Initialize environment with 3 rooms
    env = WarehouseEnvironment(target_room="303")

    # 2. Create agent and monitor manager
    agent = UtilityBasedRobotAgent(env)
    manager = MonitorManager(env)

    # 3. Scenario labels for display
    scenarios = [
        "Normal delivery (moving toward target)",
        "Human obstacle blocking path",
        "Locked door (first encounter → call human)",
        "Locked door (after learning → enter keypad)",
        "Adversarial event (sensor malfunction)",
    ]

    step = 0
    scenario_idx = 0

    # 4. Run 5 delivery scenarios
    while not env.task_complete and step < 15:
        step += 1

        # Inject adversarial at step 5 only
        if step == 5:
            env.inject_adversarial_event("sensor_malfunction")
            scenario_idx = 4
        elif step == 6:
            env.clear_adversarial()
            scenario_idx = 3  # Back to normal

        # Agent step
        result = agent.step()
        manager.update(agent, result)

        # 5. Print step output
        perception = result["perception"]
        decision = result["decision"]
        execution = result["execution"]

        label = scenarios[min(scenario_idx, len(scenarios) - 1)]
        if step <= 5:
            scenario_idx = step - 1

        print()
        print("═" * 50)
        print(f"STEP {step}: {label}")
        print("═" * 50)
        print(f"[PERCEPTION]   Door light indicator: {perception.light_indicator}")
        if decision.utility_scores:
            scores_str = ", ".join(f"{k}: {v:.2f}" for k, v in decision.utility_scores.items())
            print(f"[REASONING]    Utility scores: {{{scores_str}}}")
        print(f"[ACTION]       Executing: {execution.action.value}")
        learned = agent.learning_module.get_learned_solutions()
        used_learned = learned and execution.action == ActionType.ENTER_KEYPAD
        if used_learned:
            print(f"[LEARNING]     Applied learned solution: {learned}")
        elif learned:
            print(f"[LEARNING]     Learned solutions available: {learned}")
        else:
            print("[LEARNING]     No learned solutions yet")

        print()
        print("--- MONITOR REPORTS ---")
        summary = manager.get_step_summary()
        for name, msg in summary.items():
            if msg:
                print(f"  {msg}")

        print("═" * 50)

        # Advance scenario for display
        if execution.action == ActionType.TEXT_HUMAN and "locked_door" not in learned:
            scenario_idx = 2
        elif execution.action == ActionType.ENTER_KEYPAD and learned:
            scenario_idx = 3

    # 6. Final full report
    print()
    print(manager.generate_full_report())


if __name__ == "__main__":
    run_simulation()
