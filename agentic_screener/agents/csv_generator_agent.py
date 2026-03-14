"""
CSV Generator Agent — Writes screening results to CSV file.
"""

import csv
from pathlib import Path
import pandas as pd


def generate_csv(
    results: list[dict],
    output_path: Path,
    columns: list[str] | None = None,
) -> Path:
    """
    Generate CSV from screening results.

    Args:
        results: List of dicts with keys: ID, Title, authors, Abstract, arxiv_id, URL,
                 I1, I2, E1, E2, E3, E7, I1_reason, I2_reason, ..., Decision, Reason, Summary (optional)
        output_path: Path to write CSV
        columns: Optional column order. If None, uses keys from first result.

    Returns:
        Path to written file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not results:
        pd.DataFrame().to_csv(output_path, index=False)
        return output_path

    df = pd.DataFrame(results)
    if columns:
        # Ensure all columns exist, fill missing with ""
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df = df[[c for c in columns if c in df.columns]]
    df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL)
    return output_path


def get_default_columns() -> list[str]:
    """Default column order for screening results CSV."""
    return [
        "ID", "Title", "filename", "authors", "Abstract", "arxiv_id", "URL", "DOI",
        "I1", "I2", "E1", "E2", "E3", "E7",
        "I1_reason", "I2_reason", "E1_reason", "E2_reason", "E3_reason", "E7_reason",
        "Decision", "Reason", "Summary",
    ]
