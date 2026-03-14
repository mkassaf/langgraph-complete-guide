# The Perception Module — Explained with Examples

This document illustrates the **perception module** of an autonomous AI agent using concrete examples.

---

## What is the Perception Module?

The perception module is responsible for **taking in raw information about the agent's environment** and turning it into **meaningful perceptions** that the reasoning module can use.

```
Raw Input (percepts) → Process → Interpret → Perceptions → Reasoning Module
```

---

## Key Concepts

| Term | Definition |
|------|------------|
| **Percept** | A single piece of raw information collected by the agent (e.g., one image frame, one API response, one sensor reading) |
| **Perception** | A meaningful interpretation derived from analyzing percepts (e.g., "there is a person 2m away", "the file is a PDF") |
| **Physical sensor** | Hardware that interacts with the physical world (camera, microphone, temperature sensor) |
| **Digital input** | Data from digital sources (APIs, file systems, UI elements, streams) |
| **Spatial mapping** | Understanding where objects are in relation to the agent and to each other |

---

## Example 1: Paper Screening Agent (Digital Environment)

*Fits the context of this project's agentic screener.*

### Step 1: Collect Percepts (Raw Data)

The perception module gathers raw inputs:

```python
# Percept 1: Raw PDF bytes from a file
percept_1 = read_pdf_bytes("paper_001.pdf")

# Percept 2: Extracted text (first 15,000 chars)
percept_2 = extract_text_from_pdf(percept_1, max_pages=20)

# Percept 3: Metadata (filename, arxiv_id)
percept_3 = {"filename": "2601.22952v1.pdf", "arxiv_id": "2601.22952v1"}
```

Each of these is a **percept** — raw, uninterpreted data.

### Step 2: Process the Data

Filter and transform:

```python
# Filter: Remove non-UTF8 characters
cleaned_text = percept_2.encode("utf-8", errors="replace").decode("utf-8")

# Transform: Truncate if too long
if len(cleaned_text) > 15000:
    cleaned_text = cleaned_text[:15000] + "\n\n[... truncated ...]"
```

### Step 3: Interpret → Form Perceptions

Extract meaningful features and identify "objects":

```python
# Object identification: Extract title, abstract, authors
title = extract_first_line(cleaned_text)      # "Sifting the Noise: LLM Agents..."
abstract = extract_abstract_section(cleaned_text)
authors = extract_authors(cleaned_text)

# Spatial mapping (digital): Where does this paper sit in the corpus?
# - In folder output/pdfs/
# - Part of batch 1–100
# - Has arxiv_id 2601.22952v1
location = {"folder": "output/pdfs", "batch": 1, "arxiv_id": "2601.22952v1"}
```

### Step 4: Hand Perceptions to Reasoning Module

```python
perceptions = {
    "title": title,
    "abstract": abstract,
    "authors": authors,
    "full_text": cleaned_text,
    "metadata": percept_3,
    "location": location,
}
# → Send to reasoning module for criterion evaluation (I1, I2, E1, etc.)
```

---

## Example 2: GUI Automation Agent (Digital + Spatial)

An agent that automates tasks on a screen.

### Percepts (Raw Input)

```python
percepts = [
    get_screenshot(),           # Raw pixel data (1920×1080)
    get_accessible_tree(),      # Raw DOM/accessibility tree (XML-like)
    get_focused_element(),     # Current focus state
]
```

### Processing

```python
# Filter: Crop to relevant region
cropped = crop_to_window(percepts[0])

# Transform: Resize for model input
resized = resize(cropped, (224, 224))
```

### Interpretation → Perceptions

```python
# Object identification: What UI elements exist?
objects = [
    {"type": "button", "label": "Submit", "bounds": (100, 200, 180, 40)},
    {"type": "text_field", "label": "Email", "bounds": (100, 100, 300, 30)},
]

# Spatial mapping: Where is each element relative to others?
# - Submit button is 70px below Email field
# - Submit is in the bottom-right of the form
spatial_map = {
    "Submit": {"below": "Email", "distance_px": 70, "region": "bottom-right"},
    "Email": {"above": "Submit", "region": "top-left"},
}

perceptions = {
    "objects": objects,
    "spatial_map": spatial_map,
    "current_focus": "Email",
}
# → Reasoning module decides: "Focus Email, type value, then click Submit"
```

---

## Example 3: Robot in a Warehouse (Physical Sensors)

### Percepts (Physical Sensors)

```python
percepts = [
    camera.capture(),           # Raw image (RGB array)
    lidar.scan(),               # Distance readings (360°)
    temperature_sensor.read(),  # 22.3 °C
]
```

### Processing

```python
# Filter: Remove noise from lidar
filtered_lidar = remove_outliers(percepts[1])

# Transform: Normalize image for model
normalized_img = preprocess_for_vision_model(percepts[0])
```

### Interpretation → Perceptions

```python
# Object identification: What's in the scene?
objects = [
    {"type": "human", "confidence": 0.95},
    {"type": "box", "confidence": 0.88},
    {"type": "shelf", "confidence": 0.92},
]

# Spatial mapping: Where are they relative to the robot?
spatial_map = {
    "human": {"distance_m": 2.3, "bearing_deg": 45, "direction": "front-left"},
    "box": {"distance_m": 1.1, "bearing_deg": 0, "direction": "front"},
    "shelf": {"distance_m": 3.0, "bearing_deg": -30, "direction": "front-right"},
}

perceptions = {
    "objects": objects,
    "spatial_map": spatial_map,
    "temperature_c": 22.3,
}
# → Reasoning module: "Human 2.3m away — slow down; box in path — navigate around"
```

---

## Refining Perceptions

The perception module may **refine** before handing off:

```python
# Initial perception: "There might be a button"
# Agent collects more percepts (e.g., zoom in, get accessibility info)
# Refined perception: "Confirm: Submit button, enabled, at (100, 200)"
```

This loop (collect → process → interpret → refine?) continues until the module is confident enough to pass perceptions to the reasoning module.

---

## Summary Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERCEPTION MODULE                              │
├─────────────────────────────────────────────────────────────────┤
│  1. COLLECT PERCEPTS                                              │
│     • Physical: camera, mic, lidar, temperature                   │
│     • Digital: PDF bytes, API responses, DOM, file contents      │
│                                                                   │
│  2. PROCESS                                                       │
│     • Filter bad data                                             │
│     • Transform (resize, normalize, truncate)                     │
│                                                                   │
│  3. INTERPRET                                                     │
│     • Extract features                                            │
│     • Identify objects (human, box, button, document)              │
│     • Build spatial map (where things are)                        │
│                                                                   │
│  4. FORM PERCEPTIONS                                              │
│     • Meaningful, structured output                               │
│     • Ready for reasoning module                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    REASONING MODULE
```
