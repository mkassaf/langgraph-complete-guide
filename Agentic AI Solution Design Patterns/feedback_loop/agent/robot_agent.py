"""
Human Feedback Loop — Full Inspection Robot Agent
"""

from config import MODEL, MAX_TOKENS
from factory.toy_generator import Toy, ToyGenerator
from hmi.hmi_system import HMISystem
from agent.detection_model import DefectDetectionModel
from agent.llm_client import LLMClient
from agent.controller import Controller
from hmi.feedback_record import InspectionDecision


class InspectionRobotAgent:
    """Full inspection robot agent with feedback loop support."""

    def __init__(self):
        self.llm = LLMClient(model=MODEL, max_tokens=MAX_TOKENS)
        self.model = DefectDetectionModel()
        self.controller = Controller(self.llm, self.model)
        self.hmi = HMISystem()
        self.generator = ToyGenerator()

    def inspect_toy(self, toy: Toy) -> InspectionDecision:
        """Inspect a single toy."""
        return self.controller.inspect_toy(toy)

    def process_feedback(self, feedback_list: list) -> list[str]:
        """Process human feedback batch and update model."""
        return self.controller.process_feedback_batch(feedback_list)
