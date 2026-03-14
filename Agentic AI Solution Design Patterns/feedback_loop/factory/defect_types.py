"""
Defect type definitions for toy factory quality control.
"""

from enum import Enum
from dataclasses import dataclass


class DefectSeverity(Enum):
    OBVIOUS = "obvious"  # Easy to detect
    SUBTLE = "subtle"  # Hard to detect initially
    HIDDEN = "hidden"  # Very hard, needs learning


@dataclass
class DefectType:
    id: str
    name: str
    description: str
    severity: DefectSeverity
    visual_cues: list[str]  # What to look for


DEFECT_TYPES = {
    "scratch": DefectType(
        id="scratch",
        name="Surface Scratch",
        description="Visible scratch on toy surface",
        severity=DefectSeverity.OBVIOUS,
        visual_cues=["linear mark", "surface disruption"],
    ),
    "color_fade": DefectType(
        id="color_fade",
        name="Color Fading",
        description="Uneven or faded paint",
        severity=DefectSeverity.SUBTLE,
        visual_cues=["uneven color", "pale patches"],
    ),
    "micro_crack": DefectType(
        id="micro_crack",
        name="Micro Crack",
        description="Tiny structural crack",
        severity=DefectSeverity.HIDDEN,
        visual_cues=["hairline fracture", "stress mark"],
    ),
    "misalignment": DefectType(
        id="misalignment",
        name="Part Misalignment",
        description="Component not properly aligned",
        severity=DefectSeverity.SUBTLE,
        visual_cues=["gap", "uneven seam", "offset joint"],
    ),
    "paint_bubble": DefectType(
        id="paint_bubble",
        name="Paint Bubble",
        description="Air bubble under paint",
        severity=DefectSeverity.HIDDEN,
        visual_cues=["raised surface", "bubble outline"],
    ),
}
