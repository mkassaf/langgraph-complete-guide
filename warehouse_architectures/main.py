"""
Warehouse Architectures — Compare Centralized, Decentralized, Hybrid

Runs all three architectures through 4 scenarios and prints comparison report.

Run from project root:
    python -m warehouse_architectures.main
"""

from warehouse_architectures.environment import Task, TaskStatus, WarehouseEnvironment
from warehouse_architectures.systems.centralized import CentralizedAgenticSystem
from warehouse_architectures.systems.decentralized import DecentralizedAgenticSystem
from warehouse_architectures.systems.hybrid import HybridAgenticSystem


def make_tasks() -> list[Task]:
    """Create the three standard tasks."""
    return [
        Task("T1", "deliver_box", "room303", status=TaskStatus.PENDING),
        Task("T2", "restock_shelf", "A2", status=TaskStatus.PENDING),
        Task("T3", "customer_pickup", "P1", status=TaskStatus.PENDING),
    ]


def run_scenario_1_normal(env: WarehouseEnvironment) -> dict[str, dict]:
    """Scenario 1: Normal operation — all robots complete tasks without issues."""
    results = {}
    for name, SystemClass in [
        ("Centralized", CentralizedAgenticSystem),
        ("Decentralized", DecentralizedAgenticSystem),
        ("Hybrid", HybridAgenticSystem),
    ]:
        env.reset()
        env._failed_agents = set()
        system = SystemClass(env)
        tasks = make_tasks()
        print(f"\n{'='*60}")
        print(f"SCENARIO 1 — NORMAL OPERATION ({name})")
        print(f"{'='*60}")

        if name == "Centralized":
            system.assign_tasks(tasks)
        elif name == "Decentralized":
            system.initialize_agents_with_goals(tasks)
        else:
            system.set_high_level_goals(tasks)

        for _ in range(3):
            system.run_step()

        results[name] = system.generate_report()
    return results


def run_scenario_2_conflict(env: WarehouseEnvironment) -> dict[str, dict]:
    """Scenario 2: Resource conflict — Robot_A and Robot_C need elevator."""
    results = {}
    for name, SystemClass in [
        ("Centralized", CentralizedAgenticSystem),
        ("Decentralized", DecentralizedAgenticSystem),
        ("Hybrid", HybridAgenticSystem),
    ]:
        env.reset()
        env._failed_agents = set()
        system = SystemClass(env)
        tasks = make_tasks()
        print(f"\n{'='*60}")
        print(f"SCENARIO 2 — RESOURCE CONFLICT ({name})")
        print(f"{'='*60}")

        if name == "Centralized":
            system.assign_tasks(tasks)
            conflict = env.inject_conflict("elevator")
            system.handle_conflict(conflict)
        elif name == "Decentralized":
            system.initialize_agents_with_goals(tasks)
            conflict = env.inject_conflict("elevator")
            system.handle_conflict(conflict)
        else:
            system.set_high_level_goals(tasks)
            conflict = env.inject_conflict("elevator")
            system.handle_conflict(conflict)

        system.run_step()
        results[name] = system.generate_report()
    return results


def run_scenario_3_failure(env: WarehouseEnvironment) -> dict[str, dict]:
    """Scenario 3: Agent failure — Robot_B crashes mid-task."""
    results = {}
    for name, SystemClass in [
        ("Centralized", CentralizedAgenticSystem),
        ("Decentralized", DecentralizedAgenticSystem),
        ("Hybrid", HybridAgenticSystem),
    ]:
        env.reset()
        env._failed_agents = set()
        system = SystemClass(env)
        tasks = make_tasks()
        print(f"\n{'='*60}")
        print(f"SCENARIO 3 — AGENT FAILURE ({name})")
        print(f"{'='*60}")

        if name == "Centralized":
            system.assign_tasks(tasks)
        elif name == "Decentralized":
            system.initialize_agents_with_goals(tasks)
        else:
            system.set_high_level_goals(tasks)

        system.run_step()
        system.handle_agent_failure("Robot_B")
        system.run_step()
        results[name] = system.generate_report()
    return results


def run_scenario_4_unexpected(env: WarehouseEnvironment) -> dict[str, dict]:
    """Scenario 4: Unexpected event — power outage in section B."""
    results = {}
    for name, SystemClass in [
        ("Centralized", CentralizedAgenticSystem),
        ("Decentralized", DecentralizedAgenticSystem),
        ("Hybrid", HybridAgenticSystem),
    ]:
        env.reset()
        env._failed_agents = set()
        system = SystemClass(env)
        tasks = make_tasks()
        print(f"\n{'='*60}")
        print(f"SCENARIO 4 — UNEXPECTED EVENT ({name})")
        print(f"{'='*60}")

        if name == "Centralized":
            system.assign_tasks(tasks)
        elif name == "Decentralized":
            system.initialize_agents_with_goals(tasks)
        else:
            system.set_high_level_goals(tasks)

        env.inject_unexpected_event("power_outage_section_b")
        system.run_step()
        results[name] = system.generate_report()
    return results


def print_comparison_report(all_results: dict[str, dict[str, dict]]) -> None:
    """Print final comparison report."""
    # Use scenario 1 (normal) for tasks completed; scenario 4 for other metrics
    normal = all_results.get("scenario_1", {})
    last = all_results.get("scenario_4", normal)
    central = last.get("Centralized", {})
    decent = last.get("Decentralized", {})
    hybrid = last.get("Hybrid", {})

    # Tasks completed from normal operation
    central_tasks = normal.get("Centralized", {}).get("tasks_completed", central.get("tasks_completed", "N/A"))
    decent_tasks = normal.get("Decentralized", {}).get("tasks_completed", decent.get("tasks_completed", "N/A"))
    hybrid_tasks = normal.get("Hybrid", {}).get("tasks_completed", hybrid.get("tasks_completed", "N/A"))

    print("\n")
    print("╔══════════════════════════════════════════════════════╗")
    print("║           ARCHITECTURE COMPARISON REPORT             ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║ Metric              │ Central │ Decentral │ Hybrid   ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║ Tasks Completed     │ {str(central_tasks):^7} │ {str(decent_tasks):^9} │ {str(hybrid_tasks):^8} ║")
    print(f"║ Conflict Resolution │ {central.get('conflict_resolution', 'N/A'):^7} │ {decent.get('conflict_resolution', 'N/A'):^9} │ {hybrid.get('conflict_resolution', 'N/A'):^8} ║")
    print(f"║ Failure Recovery    │ {central.get('failure_recovery', 'N/A'):^7} │ {decent.get('failure_recovery', 'N/A'):^9} │ {hybrid.get('failure_recovery', 'N/A'):^8} ║")
    print(f"║ Unexpected Events   │ {central.get('unexpected_events', 'N/A'):^7} │ {decent.get('unexpected_events', 'N/A'):^9} │ {hybrid.get('unexpected_events', 'N/A'):^8} ║")
    print(f"║ Infrastructure Need │ {central.get('infrastructure', 'N/A'):^7} │ {decent.get('infrastructure', 'N/A'):^9} │ {hybrid.get('infrastructure', 'N/A'):^8} ║")
    print(f"║ Design Complexity   │ {central.get('complexity', 'N/A'):^7} │ {decent.get('complexity', 'N/A'):^9} │ {hybrid.get('complexity', 'N/A'):^8} ║")
    print("╚══════════════════════════════════════════════════════╝")


def main() -> None:
    env = WarehouseEnvironment()
    all_results = {}

    print("\n" + "="*60)
    print("WAREHOUSE ARCHITECTURES SIMULATION")
    print("Centralized | Decentralized | Hybrid")
    print("="*60)

    all_results["scenario_1"] = run_scenario_1_normal(env)
    all_results["scenario_2"] = run_scenario_2_conflict(env)
    all_results["scenario_3"] = run_scenario_3_failure(env)
    all_results["scenario_4"] = run_scenario_4_unexpected(env)

    print_comparison_report(all_results)


if __name__ == "__main__":
    main()
