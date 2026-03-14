# Human Feedback Loop Integration — Toy Factory QC Demo

Demonstrates the **Human Feedback Loop Integration** pattern: a quality control robot inspects toys, receives human corrections and confirmations via HMI, and improves detection accuracy over time without retraining.

## Three Rounds

1. **Round 1 (Initial):** Robot misses micro_crack and paint_bubble → 60% accuracy
2. **Round 2 (After feedback):** Robot learns cues from human corrections → 100% accuracy
3. **Round 3:** Sustained performance with improved model

## Setup

1. `pip install anthropic python-dotenv`
2. Add `ANTHROPIC_API_KEY` to `.env`

## Run

```bash
python "Agentic AI Solution Design Patterns/feedback_loop/main.py"
```

## Project Structure

```
feedback_loop/
├── config.py
├── prompts.py
├── factory/
│   ├── defect_types.py   # Defect definitions
│   └── toy_generator.py   # Toy generation
├── hmi/
│   ├── feedback_record.py  # Feedback data structures
│   └── hmi_system.py       # Human-Machine Interface
├── agent/
│   ├── detection_model.py  # DefectKnowledge, improves with feedback
│   ├── llm_client.py
│   └── controller.py
├── agent/robot_agent.py
└── main.py
```

## Key Insight

Human corrections and confirmations drive continuous learning. The robot improves from 60% to 100% accuracy through feedback—without retraining from scratch.
