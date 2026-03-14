"""
Toy generator for factory simulation.
Generates toys with realistic defect distributions.
"""

import random
from dataclasses import dataclass, field

from factory.defect_types import DEFECT_TYPES


@dataclass
class Toy:
    toy_id: str
    name: str
    category: str  # "stuffed_animal"|"action_figure"|"puzzle"
    actual_defects: list[str]  # ground truth
    visual_description: str  # What robot sensors see
    is_defective: bool

    def get_inspection_data(self) -> dict:
        """What robot sensors provide for inspection."""
        return {
            "toy_id": self.toy_id,
            "category": self.category,
            "visual_description": self.visual_description,
            "sensor_readings": self._generate_sensor_data(),
        }

    def _generate_sensor_data(self) -> dict:
        """Simulated sensor readings."""
        cues = []
        for d in self.actual_defects:
            dt = DEFECT_TYPES.get(d)
            if dt:
                # Include some cues based on defect severity
                if random.random() < 0.7:
                    cues.extend(dt.visual_cues[:1])
        return {
            "surface_scan": "complete",
            "color_consistency": random.uniform(0.7, 1.0),
            "structural_integrity": random.uniform(0.6, 1.0),
            "detected_cues": cues if cues else ["none"],
        }


class ToyGenerator:
    """Generates toys with realistic defect distributions."""

    def __init__(self, seed: int | None = None):
        if seed is not None:
            random.seed(seed)

    def generate_batch(
        self,
        count: int,
        defect_rate: float = 0.3,
    ) -> list[Toy]:
        """
        Generate batch of toys.
        30% have defects by default.
        Defects weighted by severity (more subtle = less obvious).
        """
        toys = []
        categories = ["stuffed_animal", "action_figure", "puzzle"]
        names = {
            "stuffed_animal": ["Teddy Bear", "Bunny", "Puppy", "Kitty", "Duck"],
            "action_figure": ["Super Hero", "Space Ranger", "Robot", "Ninja", "Knight"],
            "puzzle": ["Wood Puzzle", "Block Set", "Shape Sorter", "Stacking Rings", "Maze"],
        }
        defect_ids = list(DEFECT_TYPES.keys())
        # Weight: obvious more common, hidden less common
        weights = [0.4, 0.25, 0.15, 0.12, 0.08]  # scratch, color_fade, micro_crack, misalignment, paint_bubble

        for i in range(count):
            toy_id = f"toy_{i+1}"
            cat = random.choice(categories)
            name = random.choice(names[cat])
            has_defect = random.random() < defect_rate

            if has_defect:
                defect_id = random.choices(defect_ids, weights=weights)[0]
                actual_defects = [defect_id]
                dt = DEFECT_TYPES[defect_id]
                desc = self._build_description(cat, name, dt)
            else:
                actual_defects = []
                desc = f"{name} ({cat}) - appears in good condition, no obvious defects"

            toys.append(
                Toy(
                    toy_id=toy_id,
                    name=name,
                    category=cat,
                    actual_defects=actual_defects,
                    visual_description=desc,
                    is_defective=has_defect,
                )
            )
        return toys

    def _build_description(self, category: str, name: str, defect_type) -> str:
        """Build visual description including defect cues."""
        cues = defect_type.visual_cues
        cue_str = ", ".join(cues[:2]) if cues else "anomaly"
        return f"{name} ({category}) - {defect_type.description.lower()}: {cue_str}"

    def generate_toy_with_defect(self, defect_type_id: str, toy_id: str = "test_toy") -> Toy:
        """Generate toy with specific defect for testing."""
        dt = DEFECT_TYPES.get(defect_type_id)
        if not dt:
            raise ValueError(f"Unknown defect: {defect_type_id}")
        return Toy(
            toy_id=toy_id,
            name="Test Toy",
            category="action_figure",
            actual_defects=[defect_type_id],
            visual_description=self._build_description("action_figure", "Test Toy", dt),
            is_defective=True,
        )
