"""
Perception Module Demo — Paper Screening Agent

This script demonstrates the perception module concepts using the agentic
paper screener as a concrete example. Run from project root:

    python examples/"Agentic AI Architecture"/perception_module_demo.py

"""

from pathlib import Path

# Add project root to path (parent.parent.parent: Agentic AI Architecture -> examples -> project root)
import sys
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader  # type: ignore


# ─── PERCEPTION MODULE: Paper Screening Agent ──────────────────────────────────
#
# The perception module:
# 1. Collects PERCEPTS (raw data)
# 2. Processes (filter, transform)
# 3. Interprets (extract features, identify objects)
# 4. Forms PERCEPTIONS (meaningful output for reasoning)


def collect_percepts(pdf_path: Path) -> dict:
    """
    Step 1: Collect raw percepts.
    Each percept is a piece of uninterpreted data from the environment.
    """
    # Percept 1: Raw file bytes (digital input)
    raw_bytes = pdf_path.read_bytes()

    # Percept 2: Raw extracted text
    reader = PdfReader(pdf_path)
    pages = reader.pages[:20]
    raw_text = "\n\n".join(p.extract_text() or "" for p in pages)

    # Percept 3: File metadata (digital input)
    metadata = {
        "filename": pdf_path.name,
        "arxiv_id": pdf_path.stem,
        "file_size_bytes": len(raw_bytes),
    }

    return {
        "percept_raw_bytes": raw_bytes,
        "percept_raw_text": raw_text,
        "percept_metadata": metadata,
    }


def process_percepts(percepts: dict, max_chars: int = 15000) -> dict:
    """
    Step 2: Process the data.
    Filter bad data, perform transformations.
    """
    raw_text = percepts["percept_raw_text"]

    # Filter: Handle encoding issues
    cleaned = raw_text.encode("utf-8", errors="replace").decode("utf-8")
    cleaned = cleaned.strip()

    # Transform: Truncate if too long
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars] + "\n\n[... text truncated ...]"

    return {
        **percepts,
        "processed_text": cleaned,
    }


def interpret_and_form_perceptions(processed: dict) -> dict:
    """
    Step 3 & 4: Interpret data and form perceptions.
    Extract meaningful features, identify "objects", build spatial mapping.
    """
    text = processed["processed_text"]
    lines = text.split("\n")
    metadata = processed["percept_metadata"]

    # Object identification: What are the key elements?
    title = lines[0].strip() if lines else metadata["filename"]
    if len(title) > 200:
        title = title[:200] + "..."

    # Extract abstract (simplified: first substantial block after title)
    abstract = text[:3000] if len(text) > 3000 else text

    # Spatial mapping (digital): Where does this paper sit?
    # - In which folder?
    # - What is its arxiv_id?
    spatial_map = {
        "source": "output/pdfs",
        "arxiv_id": metadata["arxiv_id"],
        "identifier": metadata["filename"],
    }

    # PERCEPTIONS: Meaningful, structured output for the reasoning module
    perceptions = {
        "title": title,
        "abstract": abstract,
        "full_text": text,
        "metadata": metadata,
        "spatial_map": spatial_map,
    }

    return perceptions


def run_perception_module(pdf_path: Path) -> dict:
    """
    Full perception pipeline: percepts → process → perceptions.
    """
    print("=" * 60)
    print("PERCEPTION MODULE — Paper Screening Agent")
    print("=" * 60)

    # 1. Collect percepts
    print("\n1. COLLECT PERCEPTS (raw input)")
    percepts = collect_percepts(pdf_path)
    print(f"   • Raw bytes: {len(percepts['percept_raw_bytes'])} bytes")
    print(f"   • Raw text: {len(percepts['percept_raw_text'])} chars")
    print(f"   • Metadata: {percepts['percept_metadata']}")

    # 2. Process
    print("\n2. PROCESS (filter, transform)")
    processed = process_percepts(percepts)
    print(f"   • Cleaned text: {len(processed['processed_text'])} chars")

    # 3 & 4. Interpret → Perceptions
    print("\n3–4. INTERPRET → FORM PERCEPTIONS")
    perceptions = interpret_and_form_perceptions(processed)
    print(f"   • Title: {perceptions['title'][:60]}...")
    print(f"   • Spatial map: {perceptions['spatial_map']}")

    print("\n→ Ready to hand to REASONING MODULE (I1, I2, E1, etc.)")
    print("=" * 60)

    return perceptions


if __name__ == "__main__":
    pdf_dir = _PROJECT_ROOT / "output" / "pdfs"
    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDFs found in output/pdfs/. Add some PDFs first.")
        sys.exit(1)

    # Run on first PDF
    run_perception_module(pdf_files[0])
