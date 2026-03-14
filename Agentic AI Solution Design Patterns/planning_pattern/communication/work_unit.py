"""
Work unit data structures for Planning pattern.
"""

from enum import Enum
from dataclasses import dataclass, field


class WorkUnitStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkerType(Enum):
    VENUE = "venue_worker"
    REGISTRATION = "registration_worker"
    CATERING = "catering_worker"
    SPEAKERS = "speakers_worker"
    MARKETING = "marketing_worker"


@dataclass
class WorkUnit:
    """
    A unit of work delegated from Orchestrator to Worker.
    This is the core communication unit in the Planning pattern.
    """

    unit_id: str
    title: str
    description: str
    requirements: list[str]
    assigned_worker: WorkerType
    dependencies: list[str]  # unit_ids this depends on
    status: WorkUnitStatus = WorkUnitStatus.PENDING
    result: dict = field(default_factory=dict)


@dataclass
class OrchestratorPlan:
    """
    High-level plan created by Orchestrator's LLM.
    Contains all work units and their dependencies.
    """

    plan_id: str
    overall_task: str
    work_units: list[WorkUnit]
    execution_order: list[str]  # unit_ids in order


@dataclass
class WorkerResult:
    unit_id: str
    worker_type: WorkerType
    success: bool
    output: dict
    summary: str
