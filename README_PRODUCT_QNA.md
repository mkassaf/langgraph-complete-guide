# Product QnA Chatbot — Summary

> **ReAct agent** with RAG (product features) + pricing tool (CSV) + conversation memory (MemorySaver).

**Files:** [`langgraph_examples/Product QnA Agent.ipynb`](langgraph_examples/Product%20QnA%20Agent.ipynb) | [`langgraph_examples/example8_product_qna_agent.py`](langgraph_examples/example8_product_qna_agent.py)

---

## Architecture Diagram

![Product QnA Chatbot Architecture](docs/product_qna_architecture.svg)

---

## What We Built

| Component | Implementation |
|-----------|----------------|
| **Agent** | `create_react_agent(model, tools, state_modifier, checkpointer)` |
| **Pricing tool** | `@tool` + pandas CSV lookup, substring match |
| **RAG tool** | TextLoader → RecursiveCharacterTextSplitter → Chroma → `create_retriever_tool` |
| **Memory** | `MemorySaver()` checkpointer; `thread_id` in config |
| **Data** | `data/laptop_pricing.csv`, `data/laptop_descriptions.txt` |

---

## Flow Summary

1. **User asks** (e.g. "What are the features and pricing for GammaAir?")
2. **Agent reasons** — May call both `get_product_features` and `get_laptop_price` in one turn
3. **Tools execute** — RAG retrieves chunks; pricing tool looks up CSV
4. **Agent synthesizes** — Combines results into a natural answer
5. **Multi-turn** — Same `thread_id` = "How much does it cost?" refers to last laptop
6. **Multi-user** — Different `thread_id` = separate conversations per user

---

## Run

```bash
pip install pandas langchain-community langchain-chroma langchain-text-splitters
python langgraph_examples/example8_product_qna_agent.py
```

Or open [`langgraph_examples/Product QnA Agent.ipynb`](langgraph_examples/Product%20QnA%20Agent.ipynb) and run the cells.
