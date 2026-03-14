"""
Collector Agent — Aggregates criterion results and makes final INCLUDE/EXCLUDE decision.
"""

from ..config import compute_decision


def collect_and_decide(criterion_results: dict[str, tuple[str, str]]) -> tuple[bool, str, dict]:
    """
    Aggregate criterion results and compute final decision.

    Args:
        criterion_results: Dict of criterion_id -> (decision: Y/N, reason: str)

    Returns:
        (include: bool, reason: str, results_dict: dict)
    """
    results_dict = {cid: dec for cid, (dec, _) in criterion_results.items()}
    include, reason = compute_decision(results_dict)
    return include, reason, results_dict
