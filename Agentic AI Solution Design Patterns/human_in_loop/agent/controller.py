"""
Human-in-the-Loop — Controller

Manages the full workflow: assess → try skills → request human → learn → apply.
"""

from dataclasses import dataclass

from prompts import SITUATION_ASSESSMENT_PROMPT, LEARN_FROM_OBSERVATION_PROMPT
from environment.warehouse import WarehouseEnvironment, Door, DeliveryTask
from human.human_supervisor import HumanSupervisor, HumanAlert, HumanResponse
from human.teaching_session import HumanTeachingSession, TeachingSession
from agent.skill_library import SkillLibrary, Skill
from agent.llm_client import LLMClient


@dataclass
class AgentThought:
    thought: str
    situation_assessment: str
    can_proceed: bool
    needs_human: bool
    reason: str


@dataclass
class TaskResult:
    task_id: str
    success: bool
    method_used: str
    human_intervention: bool
    new_skill_learned: str | None
    iterations: int


class Controller:
    """
    Manages the Human-in-the-Loop workflow:
    1. Assess situation with LLM
    2. Try existing skills first
    3. If stuck → request human
    4. Learn from human demonstration
    5. Apply new skill
    6. Store skill for future use
    """

    def __init__(
        self,
        llm_client: LLMClient,
        environment: WarehouseEnvironment,
        human_supervisor: HumanSupervisor,
        skill_library: SkillLibrary,
    ):
        self.llm = llm_client
        self.env = environment
        self.human = human_supervisor
        self.skills = skill_library
        self.teaching = HumanTeachingSession()

    def assess_situation(
        self,
        percepts: dict,
        current_task: DeliveryTask,
    ) -> AgentThought:
        """LLM analyzes situation and decides next steps."""
        skills_list = ", ".join(self.skills.list_skills())
        user_msg = SITUATION_ASSESSMENT_PROMPT.format(
            task=f"Deliver {current_task.box_id} to {current_task.destination_room}",
            percepts=str(percepts),
            skills_list=skills_list,
        )
        resp = self.llm.generate("You are a warehouse robot controller.", user_msg)
        return AgentThought(
            thought=resp.raw_content[:200],
            situation_assessment=resp.raw_content[:300],
            can_proceed=resp.can_proceed,
            needs_human=resp.needs_human,
            reason="LLM assessment",
        )

    def attempt_with_existing_skills(self, situation: str, door_id: str) -> bool:
        """Try to resolve using known skills."""
        skill = self.skills.get_skill(situation)
        if not skill:
            return False
        if "open_unlocked" in skill.skill_id:
            result = self.env.attempt_open_door(door_id)
            return result.get("success", False)
        if "use_keypad" in skill.skill_id:
            door = self.env.doors.get(door_id)
            if door and door.keypad_code:
                result = self.env.apply_keypad_code(door_id, door.keypad_code)
                if result.get("success"):
                    self.env.attempt_open_door(door_id)
                return result.get("success", False)
        return False

    def request_human_intervention(self, situation: str, location: str) -> HumanResponse:
        """Send alert and wait for human response."""
        alert = HumanAlert(
            alert_id="alt_001",
            robot_id="robot_1",
            location=location,
            situation_description=situation,
            timestamp="now",
        )
        return self.human.receive_alert(alert)

    def learn_from_human(
        self,
        human_response: HumanResponse,
        door: Door,
    ) -> Skill:
        """Observe human demonstration, convert to skill, store."""
        session = self.teaching.demonstrate_keypad_entry(door, self.env)
        return self.skills.learn_new_skill(session)

    def execute_task(self, task: DeliveryTask) -> TaskResult:
        """Full task execution with Human-in-the-Loop support."""
        dest = task.destination_room
        door_id = "door_301" if "301" in dest else "door_303"
        door = self.env.doors.get(door_id)
        percepts = self.env.get_door_percepts(door_id)
        situation = "locked door with keypad" if (door and door.is_locked and door.has_keypad) else "unlocked door"
        has_skill = self.skills.has_skill_for(situation)

        # Assess (optional LLM - use heuristics if LLM fails)
        try:
            skills_list = ", ".join(self.skills.list_skills())
            prompt = SITUATION_ASSESSMENT_PROMPT.format(
                task=f"Deliver to {dest}",
                percepts=str(percepts),
                skills_list=skills_list,
            )
            self.llm.generate("You are a warehouse robot controller.", prompt)
        except Exception:
            pass  # Use heuristic logic below

        if has_skill and not (door and door.is_new):
            # Scenario 1 or 3: use existing skill
            success = self.attempt_with_existing_skills(situation, door_id)
            return TaskResult(
                task_id=task.task_id,
                success=success,
                method_used="existing_skill",
                human_intervention=False,
                new_skill_learned=None,
                iterations=1,
            )

        if door and door.is_new and not has_skill:
            # Scenario 2: need human
            human_resp = self.request_human_intervention(
                f"Blocked at {dest} - locked door with keypad. No known skill.",
                dest,
            )
            if human_resp.will_demonstrate:
                new_skill = self.learn_from_human(human_resp, door)
                success = self.attempt_with_existing_skills("keypad door", door_id)
                return TaskResult(
                    task_id=task.task_id,
                    success=success,
                    method_used="new_skill",
                    human_intervention=True,
                    new_skill_learned=new_skill.name,
                    iterations=2,
                )

        # Fallback: try anyway
        success = self.attempt_with_existing_skills(situation, door_id)
        return TaskResult(
            task_id=task.task_id,
            success=success,
            method_used="existing_skill",
            human_intervention=False,
            new_skill_learned=None,
            iterations=1,
        )
