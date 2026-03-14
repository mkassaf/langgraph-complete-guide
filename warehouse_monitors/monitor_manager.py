"""
Monitor Manager — Aggregates All Monitors, System-Wide Tracking

Registers and runs all 5 categories of monitors at each agent step.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from warehouse_monitors.agent import (
    ActionExecution,
    ActionType,
    Decision,
    Perception,
    UtilityBasedRobotAgent,
)
from warehouse_monitors.environment import WarehouseEnvironment
from warehouse_monitors.monitors.operational import (
    PerformanceMonitor,
    EnvironmentMonitor,
    ResourceUtilizationMonitor,
)
from warehouse_monitors.monitors.ethical import (
    GoalAlignmentMonitor,
    BiasAndFairnessMonitor,
    SafetyConstraintMonitor,
)
from warehouse_monitors.monitors.interaction import (
    InteractionMonitor,
    CommunicationMonitor,
)
from warehouse_monitors.monitors.state_belief import (
    InternalStateMonitor,
    PlanningAndDecisionMonitor,
    BeliefAccuracyMonitor,
)
from warehouse_monitors.monitors.ancillary import (
    ExplainabilityMonitor,
    DataQualityMonitor,
    RobustnessMonitor,
    LearningAdaptationMonitor,
)


class Severity(Enum):
    """Monitor alert severity."""
    INFO = "INFO"
    WARN = "WARN"
    CRITICAL = "CRITICAL"


@dataclass
class StepRecord:
    """Record of one agent step for monitors."""
    step: int
    perception: Perception
    decision: Decision
    execution: ActionExecution
    raw_percepts: dict[str, Any]


class MonitorManager:
    """
    Aggregates all monitors, runs them at each step, generates full report.
    """

    def __init__(self, env: WarehouseEnvironment):
        self.env = env
        self._step_records: list[StepRecord] = []
        self._prev_env_state: dict[str, Any] = {}
        self._prev_belief: dict[str, Any] = {}

        # Operational
        self.performance = PerformanceMonitor()
        self.environment = EnvironmentMonitor()
        self.resource = ResourceUtilizationMonitor()

        # Ethical
        self.goal_alignment = GoalAlignmentMonitor()
        self.bias_fairness = BiasAndFairnessMonitor()
        self.safety = SafetyConstraintMonitor()

        # Interaction
        self.interaction = InteractionMonitor()
        self.communication = CommunicationMonitor()

        # State & Belief
        self.internal_state = InternalStateMonitor()
        self.planning = PlanningAndDecisionMonitor()
        self.belief_accuracy = BeliefAccuracyMonitor()

        # Ancillary
        self.explainability = ExplainabilityMonitor()
        self.data_quality = DataQualityMonitor()
        self.robustness = RobustnessMonitor()
        self.learning = LearningAdaptationMonitor()

    def update(self, agent: UtilityBasedRobotAgent, step_result: dict[str, Any]) -> None:
        """Run all monitors at each agent step."""
        perception = step_result["perception"]
        decision = step_result["decision"]
        execution = step_result["execution"]
        raw_percepts = step_result["raw_percepts"]
        step = step_result["step"]

        rec = StepRecord(
            step=step,
            perception=perception,
            decision=decision,
            execution=execution,
            raw_percepts=raw_percepts,
        )
        self._step_records.append(rec)

        # Operational
        self.performance.track_goal_progress(agent, step)
        self.performance.track_task_success_rate(self._step_records)

        after_state = {
            "task_complete": self.env.task_complete,
            "door_locked": self.env.get_room(self.env.target_room).door_locked
            if self.env.get_room(self.env.target_room) else None,
        }
        self.environment.track_state_changes(self._prev_env_state, after_state)
        self.environment.detect_new_agents(raw_percepts)
        self._prev_env_state = after_state.copy()

        self.resource.track_compute(step_result)
        self.resource.track_api_calls(execution.action)

        # Ethical
        self.goal_alignment.check_action_alignment(execution.action, ["deliver_box"])
        self.goal_alignment.flag_unintended_consequences(execution)
        self.bias_fairness.analyze_decision_patterns(agent.reasoning_module.get_decision_history())
        self.bias_fairness.flag_unfair_treatment(
            execution.action, {"obstacle_type": perception.obstacle_type}
        )
        self.safety.check_safety_limits(execution.action)
        self.safety.flag_dangerous_action(execution.action)

        # Interaction
        self.interaction.log_action_taken(execution.action, execution.feedback)
        self.interaction.log_observation_received(raw_percepts)
        self.interaction.analyze_environment_impact(self._prev_env_state, after_state)

        if execution.action == ActionType.TEXT_HUMAN:
            self.communication.track_agent_to_human_messages("Please unlock door 303")
            self.communication.evaluate_communication_effectiveness(
                "Please unlock door 303", execution.feedback
            )

        # State & Belief
        self.internal_state.snapshot_beliefs(agent)
        self.internal_state.track_intention_changes(self._prev_belief, agent.get_belief_state())
        self._prev_belief = agent.get_belief_state().copy()

        options = agent.reasoning_module.get_options_considered()
        if options:
            self.planning.log_options_considered(options[-1].get("options", []))
        self.planning.log_decision_made(decision.action, decision.rationale)
        self.planning.track_planning_depth(decision.utility_scores or {})

        belief = agent.get_belief_state()
        actual = {"task_complete": self.env.task_complete, "target_room": self.env.target_room}
        self.belief_accuracy.compare_belief_to_reality(belief, actual)

        # Ancillary
        self.explainability.explain_decision(
            decision, {"perception": perception}
        )
        self.explainability.log_reasoning_chain([decision.rationale])

        self.data_quality.check_percept_quality(raw_percepts)

        if raw_percepts.get("sensor_warning"):
            self.robustness.test_adversarial_response(agent, "sensor_malfunction")

        learned = agent.learning_module.get_learned_solutions()
        if "locked_door" in learned:
            self.learning.compare_old_vs_new_solution("text_human", "enter_keypad")

    def alert(self, severity: Severity, message: str) -> None:
        """Print WARN/CRITICAL alerts in real time."""
        prefix = "⚠️ " if severity == Severity.WARN else "🚨 "
        print(f"{prefix}{severity.value}: {message}")

    def get_step_summary(self) -> dict[str, str]:
        """Get short status for each monitor for step output."""
        def status(report: str, warn_patterns: list[str]) -> str:
            # Avoid false positives: "100%" contains "0%" but is good
            for pat in warn_patterns:
                if pat == "0%" and "0%" in report and "100%" not in report:
                    return "⚠️ "
                if pat != "0%" and pat in report:
                    return "⚠️ "
            return "✅ "

        p = self.performance.report()
        g = self.goal_alignment.report()
        s = self.safety.report()
        d = self.data_quality.report()
        b = self.belief_accuracy.report()
        e = self.explainability.report()
        l = self.learning.report()

        return {
            "Performance": f"{status(p, ['success rate 0%'])} {p}" if p else "",
            "Goal Alignment": f"{status(g, ['misaligned'])} {g}" if g else "",
            "Safety": f"{status(s, ['Violation'])} {s}" if s else "",
            "Data Quality": f"{status(d, ['issue', 'flagged'])} {d}" if d else "",
            "Belief Accuracy": f"{status(b, ['accuracy 0%'])} {b}" if b else "",
            "Explainability": f"✅ {e}" if e else "",
            "Learning": f"✅ {l}" if l else "",
        }

    def generate_full_report(self) -> str:
        """Aggregated report from all monitors."""
        lines = [
            "═══════════════════════════════════════════════════════════",
            "FULL MONITOR REPORT",
            "═══════════════════════════════════════════════════════════",
            "",
            "--- OPERATIONAL ---",
            f"Performance:     {self.performance.report()}",
            f"Environment:     {self.environment.report()}",
            f"Resource:        {self.resource.report()}",
            "",
            "--- ETHICAL ---",
            f"Goal Alignment:  {self.goal_alignment.report()}",
            f"Bias/Fairness:   {self.bias_fairness.report()}",
            f"Safety:          {self.safety.report()}",
            "",
            "--- INTERACTION ---",
            f"Interaction:     {self.interaction.report()}",
            f"Communication:   {self.communication.report()}",
            "",
            "--- STATE & BELIEF ---",
            f"Internal State:  {self.internal_state.report()}",
            f"Planning:        {self.planning.report()}",
            f"Belief Accuracy: {self.belief_accuracy.report()}",
            "",
            "--- ANCILLARY ---",
            f"Explainability:  {self.explainability.report()}",
            f"Data Quality:    {self.data_quality.report()}",
            f"Robustness:      {self.robustness.report()}",
            f"Learning:        {self.learning.report()}",
            "═══════════════════════════════════════════════════════════",
        ]
        return "\n".join(lines)
