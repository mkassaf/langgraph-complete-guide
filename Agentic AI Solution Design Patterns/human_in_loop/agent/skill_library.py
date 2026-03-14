"""
Skill Library — Stores skills the robot knows.

New skills added through Human-in-the-Loop teaching.
"""

from dataclasses import dataclass

from human.teaching_session import TeachingSession


@dataclass
class Skill:
    skill_id: str
    name: str
    description: str
    trigger_conditions: list[str]
    steps: list[str]
    learned_from: str
    times_used: int = 0
    success_rate: float = 1.0


class SkillLibrary:
    """
    Stores skills the robot knows how to perform.
    New skills added through Human-in-the-Loop teaching.
    """

    def __init__(self):
        self.skills: dict[str, Skill] = {
            "open_unlocked_door": Skill(
                skill_id="open_unlocked_door",
                name="Open Unlocked Door",
                description="Turn handle and push",
                trigger_conditions=["door is unlocked", "no keypad"],
                steps=["approach door", "turn handle", "push door"],
                learned_from="training",
            ),
            "navigate_hallway": Skill(
                skill_id="navigate_hallway",
                name="Navigate Hallway",
                description="Move through hallway to destination",
                trigger_conditions=["in hallway", "need to reach room"],
                steps=["locate door", "approach", "pass through"],
                learned_from="training",
            ),
            "pick_up_box": Skill(
                skill_id="pick_up_box",
                name="Pick Up Box",
                description="Pick up delivery box",
                trigger_conditions=["box at location", "delivery task"],
                steps=["approach box", "grasp", "lift"],
                learned_from="training",
            ),
        }

    def has_skill_for(self, situation: str) -> bool:
        """Check if robot has a skill matching the situation."""
        sit_lower = situation.lower()
        for skill in self.skills.values():
            for cond in skill.trigger_conditions:
                if cond.lower() in sit_lower or sit_lower in cond.lower():
                    return True
            if "keypad" in sit_lower and "use_keypad_door" in self.skills:
                return True
        return False

    def get_skill(self, situation: str) -> Skill | None:
        """Get best matching skill for situation."""
        sit_lower = situation.lower()
        if "keypad" in sit_lower and "use_keypad_door" in self.skills:
            return self.skills["use_keypad_door"]
        if "unlocked" in sit_lower or "no keypad" in sit_lower:
            return self.skills.get("open_unlocked_door")
        for skill in self.skills.values():
            for cond in skill.trigger_conditions:
                if cond.lower() in sit_lower:
                    return skill
        return None

    def learn_new_skill(self, teaching_session: TeachingSession) -> Skill:
        """Convert teaching session into a new skill. Add to library."""
        steps = [s.action for s in teaching_session.steps_observed]
        skill = Skill(
            skill_id="use_keypad_door",
            name="Use Keypad Door",
            description="Enter code on keypad to unlock door",
            trigger_conditions=["locked door", "keypad present", "door has keypad"],
            steps=steps,
            learned_from="human_teaching",
        )
        self.skills["use_keypad_door"] = skill
        return skill

    def list_skills(self) -> list[str]:
        """List all skill names."""
        return list(self.skills.keys())
