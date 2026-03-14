"""
Action Module Demo — Effectors, Execution, Monitoring

Demonstrates how the action module:
- Receives decisions from the reasoning module
- Translates them into commands for effectors
- Executes via software (file system, API) or hardware (simulated)
- Monitors outcomes

Run from project root:
    python examples/"Agentic AI Architecture"/action_module_demo.py
"""

import csv
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

# Add project root (parent.parent.parent: Agentic AI Architecture -> examples -> project root)
import sys
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))


# ─── Action Module: Core Concepts ─────────────────────────────────────────────

@dataclass
class ActionDecision:
    """What the reasoning module hands to the action module."""
    action_type: str
    payload: dict
    priority: int = 0


@dataclass
class EffectorResult:
    """Outcome from an effector after execution."""
    success: bool
    message: str
    data: dict = field(default_factory=dict)
    latency_ms: float = 0


class Effector:
    """Base: recipient that carries out an action."""
    name: str = "base"

    def execute(self, command: dict) -> EffectorResult:
        raise NotImplementedError


# ─── Software Effectors ───────────────────────────────────────────────────────

class FileSystemEffector(Effector):
    """Effector: file system (write CSV, JSON)."""
    name = "file_system"

    def execute(self, command: dict) -> EffectorResult:
        start = time.perf_counter()
        path = Path(command["path"])
        data = command["data"]
        mode = command.get("mode", "csv")  # csv or json

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            if mode == "csv":
                write_header = not path.exists() or path.stat().st_size == 0
                with open(path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=data.keys(), quoting=csv.QUOTE_MINIMAL)
                    if write_header:
                        writer.writeheader()
                    writer.writerow(data)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            latency = (time.perf_counter() - start) * 1000
            return EffectorResult(success=True, message="Write complete", data={"path": str(path)}, latency_ms=latency)
        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            return EffectorResult(success=False, message=str(e), latency_ms=latency)


class MockAPIEffector(Effector):
    """Effector: API (simulated — e.g., email, notification service)."""
    name = "api"

    def execute(self, command: dict) -> EffectorResult:
        start = time.perf_counter()
        endpoint = command.get("endpoint", "")
        payload = command.get("payload", {})

        # Simulate API call
        time.sleep(0.05)
        latency = (time.perf_counter() - start) * 1000

        # Simulate success
        return EffectorResult(
            success=True,
            message=f"POST {endpoint} → 200 OK",
            data={"request_id": "req_abc123", "payload": payload},
            latency_ms=latency,
        )


# ─── Action Module: Translate, Execute, Monitor ──────────────────────────────

class ActionModule:
    """
    Action module: receives decisions, executes via effectors, monitors outcomes.
    """

    def __init__(self):
        self.effectors = {
            "file_system": FileSystemEffector(),
            "api": MockAPIEffector(),
        }
        self.monitors = []

    def translate(self, decision: ActionDecision) -> list[dict]:
        """Translate reasoning decision into commands for effectors."""
        output_dir = _PROJECT_ROOT / "output" / "examples"
        output_dir.mkdir(parents=True, exist_ok=True)

        if decision.action_type == "persist_screening_result":
            return [
                {
                    "effector": "file_system",
                    "command": {
                        "path": str(output_dir / "action_demo_results.csv"),
                        "mode": "csv",
                        "data": decision.payload,
                    },
                },
            ]
        if decision.action_type == "send_notification":
            return [
                {
                    "effector": "api",
                    "command": {
                        "endpoint": "/notify",
                        "payload": decision.payload,
                    },
                },
            ]
        if decision.action_type == "persist_and_notify":
            # Coarse-grained: two effectors, one logical action
            output_dir = _PROJECT_ROOT / "output" / "examples"
            return [
                {
                    "effector": "file_system",
                    "command": {
                        "path": str(output_dir / "action_demo_results.csv"),
                        "mode": "csv",
                        "data": decision.payload.get("result", {}),
                    },
                },
                {
                    "effector": "api",
                    "command": {
                        "endpoint": "/notify",
                        "payload": {"message": decision.payload.get("notification", "")},
                    },
                },
            ]
        return []

    def execute(self, commands: list[dict]) -> list[EffectorResult]:
        """Execute commands via effectors. Manages/coordinates multiple effectors."""
        results = []
        for cmd in commands:
            effector_name = cmd["effector"]
            effector = self.effectors.get(effector_name)
            if not effector:
                results.append(EffectorResult(success=False, message=f"Unknown effector: {effector_name}"))
                continue
            result = effector.execute(cmd["command"])
            results.append(result)
        return results

    def monitor(self, results: list[EffectorResult]) -> dict:
        """
        Monitor: verify actions succeeded.
        Uses: performance (latency), interaction (success/failure).
        """
        all_ok = all(r.success for r in results)
        max_latency = max((r.latency_ms for r in results), default=0)
        return {
            "success": all_ok,
            "performance_ok": max_latency < 5000,  # e.g., < 5s
            "results": [{"success": r.success, "message": r.message, "latency_ms": r.latency_ms} for r in results],
        }

    def run(self, decision: ActionDecision) -> dict:
        """Full pipeline: translate → execute → monitor."""
        commands = self.translate(decision)
        results = self.execute(commands)
        monitor_report = self.monitor(results)
        return {
            "decision": decision.action_type,
            "commands_executed": len(commands),
            "monitor": monitor_report,
        }


# ─── Demo Scenarios ───────────────────────────────────────────────────────────

def run_fine_grained_demo():
    """Fine-grained action: single effector (file write)."""
    print("=" * 65)
    print("ACTION MODULE — Fine-Grained Action (Single Effector)")
    print("=" * 65)

    # Simulated decision from reasoning module
    decision = ActionDecision(
        action_type="persist_screening_result",
        payload={
            "ID": 1,
            "Title": "AgentCompress: Task-Aware Compression...",
            "Decision": "Yes",
            "Reason": "All inclusion criteria met",
        },
    )

    print("\n1. INPUT: Decision from Reasoning Module")
    print(f"   Action: {decision.action_type}")
    print(f"   Payload: {list(decision.payload.keys())}")

    print("\n2. TRANSLATE: Decision → Command(s)")
    module = ActionModule()
    commands = module.translate(decision)
    print(f"   Commands: {len(commands)} (effector: {commands[0]['effector']})")

    print("\n3. EXECUTE: Send to effector")
    results = module.execute(commands)
    print(f"   Result: {results[0].message} (latency: {results[0].latency_ms:.1f}ms)")

    print("\n4. MONITOR: Verify outcome")
    report = module.monitor(results)
    print(f"   Success: {report['success']}")
    print(f"   Performance OK: {report['performance_ok']}")

    print("=" * 65)


def run_coarse_grained_demo():
    """Coarse-grained action: multiple effectors, one logical action."""
    print("\n" + "=" * 65)
    print("ACTION MODULE — Coarse-Grained Action (Multiple Effectors)")
    print("=" * 65)

    decision = ActionDecision(
        action_type="persist_and_notify",
        payload={
            "result": {
                "ID": 2,
                "Title": "CONCUR: High-Throughput Agentic Batch Inference...",
                "Decision": "Yes",
            },
            "notification": "Screening complete: 1 paper included",
        },
    )

    print("\n1. INPUT: Decision (persist + notify)")
    print("\n2. TRANSLATE: One logical action → 2 effector commands")
    print("   - file_system: write result to CSV")
    print("   - api: send notification")

    print("\n3. EXECUTE: Coordinate effectors")
    module = ActionModule()
    outcome = module.run(decision)
    for i, r in enumerate(outcome["monitor"]["results"]):
        print(f"   Effector {i+1}: {r['message']} ({r['latency_ms']:.1f}ms)")

    print("\n4. MONITOR: All effectors succeeded?")
    print(f"   {outcome['monitor']['success']}")

    print("=" * 65)


def run_warehouse_robot_demo():
    """Warehouse robot: coarse-grained action (many actuators)."""
    print("\n" + "=" * 65)
    print("ACTION MODULE — Warehouse Robot (Coarse-Grained)")
    print("=" * 65)

    print("""
Reasoning decision: "Move robot to room 303"

Action module:
  - Effectors: wheel motors, arm, gripper (hardware actuators)
  - Granularity: COARSE — one "move robot" = many coordinated commands
  - Management: Orchestrate sequence, adjust speeds, avoid obstacles
  - Monitor: Position sensors, collision detection, task completion

  (Simulated: real robot would use hardware interfaces)
""")

    # Simulate: "send notification" as the action after door-lock problem-solving
    decision = ActionDecision(
        action_type="send_notification",
        payload={"to": "warehouse_manager", "body": "Door 303 locked, need access"},
    )

    module = ActionModule()
    outcome = module.run(decision)
    print("After problem-solving (door locked), action module executes:")
    print(f"  Effector: API (messaging)")
    print(f"  Result: {outcome['monitor']['results'][0]['message']}")
    print("=" * 65)


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    run_fine_grained_demo()
    run_coarse_grained_demo()
    run_warehouse_robot_demo()
