# Product QnA Chatbot — Summary

> **ReAct agent** with RAG (product features) + pricing tool (CSV) + conversation memory (MemorySaver).

**Files:** [`langgraph_examples/Product QnA Agent.ipynb`](../langgraph_examples/Product%20QnA%20Agent.ipynb) | [`langgraph_examples/example8_product_qna_agent.py`](../langgraph_examples/example8_product_qna_agent.py)

---

## Architecture Diagram

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 680" font-family="Segoe UI, Arial, sans-serif" font-size="13">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#555"/>
    </marker>
    <marker id="arrow-blue" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-auto">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#2563eb"/>
    </marker>
    <filter id="shadow" x="-4%" y="-4%" width="108%" height="108%">
      <feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.10"/>
    </filter>
  </defs>
  <text x="410" y="32" text-anchor="middle" font-size="18" font-weight="bold" fill="#1e293b">Product QnA Chatbot — Architecture</text>
  <!-- USER -->
  <rect x="330" y="52" width="160" height="44" rx="22" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="410" y="79" text-anchor="middle" font-weight="600" fill="#0c4a6e">User</text>
  <line x1="410" y1="96" x2="410" y2="140" stroke="#555" stroke-width="1.5" marker-end="url(#arrow)"/>
  <text x="420" y="125" font-size="11" fill="#64748b">messages</text>
  <!-- REACT AGENT BOX -->
  <rect x="60" y="144" width="700" height="260" rx="14" fill="#f8fafc" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="6 3" filter="url(#shadow)"/>
  <text x="80" y="170" font-size="12" font-weight="700" fill="#475569">create_react_agent (ReAct loop)</text>
  <!-- Agent LLM -->
  <rect x="230" y="184" width="360" height="72" rx="10" fill="#dbeafe" stroke="#2563eb" stroke-width="1.5"/>
  <text x="410" y="210" text-anchor="middle" font-weight="700" fill="#1e40af" font-size="14">Agent (LLM)</text>
  <text x="410" y="228" text-anchor="middle" font-size="11" fill="#3b82f6">Reasons · Picks tools · Synthesizes answer</text>
  <text x="410" y="244" text-anchor="middle" font-size="11" fill="#3b82f6">Handles small talk without tools</text>
  <line x1="410" y1="256" x2="410" y2="296" stroke="#2563eb" stroke-width="1.5" marker-end="url(#arrow-blue)"/>
  <text x="420" y="282" font-size="11" fill="#2563eb">tool_calls</text>
  <!-- get_laptop_price -->
  <rect x="110" y="300" width="260" height="80" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="1.2"/>
  <text x="240" y="324" text-anchor="middle" font-weight="700" fill="#92400e">get_laptop_price</text>
  <text x="240" y="342" text-anchor="middle" font-size="11" fill="#a16207">Substring match on product name</text>
  <text x="240" y="358" text-anchor="middle" font-size="11" fill="#a16207">Returns price (int) or -1 if not found</text>
  <!-- get_product_features -->
  <rect x="450" y="300" width="260" height="80" rx="8" fill="#dcfce7" stroke="#16a34a" stroke-width="1.2"/>
  <text x="580" y="324" text-anchor="middle" font-weight="700" fill="#166534">get_product_features (RAG)</text>
  <text x="580" y="342" text-anchor="middle" font-size="11" fill="#15803d">Vector search over descriptions</text>
  <text x="580" y="358" text-anchor="middle" font-size="11" fill="#15803d">Returns top-k relevant chunks</text>
  <!-- Results loop back -->
  <path d="M 730 340 Q 760 340 760 220 Q 760 190 600 190" stroke="#2563eb" stroke-width="1.2" fill="none" stroke-dasharray="5 3" marker-end="url(#arrow-blue)"/>
  <text x="766" y="270" font-size="10" fill="#2563eb" transform="rotate(90,766,270)">results</text>
  <!-- Arrows to data -->
  <line x1="240" y1="380" x2="240" y2="434" stroke="#555" stroke-width="1.2" marker-end="url(#arrow)"/>
  <line x1="580" y1="380" x2="580" y2="434" stroke="#555" stroke-width="1.2" marker-end="url(#arrow)"/>
  <!-- CSV -->
  <rect x="130" y="438" width="220" height="60" rx="8" fill="#fff" stroke="#94a3b8" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="240" y="462" text-anchor="middle" font-weight="600" fill="#334155">laptop_pricing.csv</text>
  <text x="240" y="480" text-anchor="middle" font-size="11" fill="#64748b">Name, Price, ShippingDays</text>
  <!-- Chroma -->
  <rect x="470" y="438" width="220" height="60" rx="8" fill="#fff" stroke="#94a3b8" stroke-width="1.2" filter="url(#shadow)"/>
  <text x="580" y="462" text-anchor="middle" font-weight="600" fill="#334155">Chroma (vector store)</text>
  <text x="580" y="480" text-anchor="middle" font-size="11" fill="#64748b">laptop_descriptions.txt chunked</text>
  <!-- MEMORY -->
  <rect x="110" y="530" width="600" height="80" rx="10" fill="#faf5ff" stroke="#9333ea" stroke-width="1.5" filter="url(#shadow)"/>
  <text x="410" y="556" text-anchor="middle" font-weight="700" fill="#6b21a8" font-size="14">MemorySaver + thread_id</text>
  <text x="410" y="576" text-anchor="middle" font-size="12" fill="#7e22ce">Same thread_id → conversation history</text>
  <text x="410" y="594" text-anchor="middle" font-size="12" fill="#7e22ce">Different thread_id → separate users</text>
  <!-- Memory → Agent dashed -->
  <line x1="410" y1="530" x2="410" y2="404" stroke="#9333ea" stroke-width="1" stroke-dasharray="4 3"/>
  <line x1="410" y1="404" x2="100" y2="404" stroke="#9333ea" stroke-width="1" stroke-dasharray="4 3"/>
  <line x1="100" y1="404" x2="100" y2="220" stroke="#9333ea" stroke-width="1" stroke-dasharray="4 3"/>
  <line x1="100" y1="220" x2="230" y2="220" stroke="#9333ea" stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
  <text x="92" y="318" font-size="10" fill="#9333ea" transform="rotate(-90,92,318)">context</text>
  <!-- Answer arrow back to user -->
  <line x1="350" y1="144" x2="350" y2="96" stroke="#555" stroke-width="1.2" stroke-dasharray="5 3" marker-end="url(#arrow)"/>
  <text x="310" y="125" font-size="11" fill="#64748b">answer</text>
  <!-- LEGEND -->
  <rect x="60" y="634" width="700" height="36" rx="6" fill="#f1f5f9"/>
  <circle cx="90" cy="652" r="6" fill="#dbeafe" stroke="#2563eb"/>
  <text x="102" y="656" font-size="11" fill="#475569">Agent</text>
  <circle cx="170" cy="652" r="6" fill="#fef3c7" stroke="#d97706"/>
  <text x="182" y="656" font-size="11" fill="#475569">Pricing tool</text>
  <circle cx="280" cy="652" r="6" fill="#dcfce7" stroke="#16a34a"/>
  <text x="292" y="656" font-size="11" fill="#475569">RAG tool</text>
  <circle cx="376" cy="652" r="6" fill="#faf5ff" stroke="#9333ea"/>
  <text x="388" y="656" font-size="11" fill="#475569">Memory</text>
  <rect x="452" y="646" width="28" height="12" rx="3" fill="#fff" stroke="#94a3b8"/>
  <text x="486" y="656" font-size="11" fill="#475569">Data source</text>
  <line x1="570" y1="652" x2="600" y2="652" stroke="#555" stroke-width="1.2" stroke-dasharray="5 3"/>
  <text x="606" y="656" font-size="11" fill="#475569">Return / dashed flow</text>
</svg>

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

Or open [`langgraph_examples/Product QnA Agent.ipynb`](../langgraph_examples/Product%20QnA%20Agent.ipynb) and run the cells.
