# file: langgraph_examples/pal_react_plan_execute/example_pal.py
"""
PAL — Program-Aided Language Models in LangGraph
─────────────────────────────────────────────────
PAL shifts computation from the LLM to a Python interpreter.
Instead of asking the model to "think step by step" in words (chain-of-thought),
we ask it to write Python code that solves the problem, then we EXECUTE that code.

Why this matters:
  - LLMs hallucinate arithmetic.  "23 * 47 = ?"  The model may guess wrong.
  - Python never gets 23*47 wrong.
  - PAL gets the best of both worlds: LLM for language understanding, Python for computation.

Graph:
  START → [generate_code] → [execute_code] → [format_answer] → END

State:
  question        — the math / logic word problem
  generated_code  — Python code written by the LLM
  code_output     — stdout captured after running the code
  final_answer    — human-friendly answer composed by the LLM
"""

import io
import re
import contextlib
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

load_dotenv()

# ─── State ─────────────────────────────────────────────────────────────────────
class PALState(TypedDict):
    question:       str
    generated_code: str
    code_output:    str
    final_answer:   str


# ─── LLM ───────────────────────────────────────────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ─── Node 1: generate_code ─────────────────────────────────────────────────────
# The LLM's job here is NOT to answer — it is to WRITE CODE that will answer.
CODE_GEN_PROMPT = """\
You are a Python programmer. Given a math or logic problem, write a SHORT Python
program that solves it and prints the final numeric answer.

Rules:
- Output ONLY raw Python code — no markdown fences, no explanations.
- The last line must be a print() that outputs the final answer.
- Use only the Python standard library (math is allowed).

Problem: {question}
"""

def generate_code_node(state: PALState) -> dict:
    """Ask the LLM to write Python code for the problem."""
    response = llm.invoke([HumanMessage(content=CODE_GEN_PROMPT.format(question=state["question"]))])
    code = response.content.strip()

    # Strip markdown code blocks if the model wraps the code anyway
    code = re.sub(r"^```(?:python)?\n?", "", code)
    code = re.sub(r"\n?```$", "", code)

    print("\n── Generated Code ──────────────────────────────")
    print(code)
    print("────────────────────────────────────────────────")
    return {"generated_code": code.strip()}


# ─── Node 2: execute_code ──────────────────────────────────────────────────────
# We run the generated Python program in a restricted environment.
# stdout is captured so we can read the printed answer.
SAFE_BUILTINS = {
    "print": print, "range": range, "len": len, "sum": sum,
    "int": int, "float": float, "round": round, "abs": abs,
    "min": min, "max": max, "enumerate": enumerate, "zip": zip,
    "list": list, "dict": dict, "str": str, "bool": bool,
    "math": __import__("math"),
}

def execute_code_node(state: PALState) -> dict:
    """Execute the generated code and capture stdout."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(state["generated_code"], {"__builtins__": SAFE_BUILTINS})
        output = buf.getvalue().strip()
    except Exception as exc:
        output = f"ERROR: {exc}"

    print(f"\n── Code Output ─────────────────────────────────")
    print(output)
    print("────────────────────────────────────────────────")
    return {"code_output": output}


# ─── Node 3: format_answer ─────────────────────────────────────────────────────
# The LLM now reads the code + output and writes a clean, natural-language answer.
# It does NO calculation here — it just formats what Python already computed.
def format_answer_node(state: PALState) -> dict:
    """Turn the raw code output into a friendly answer."""
    prompt = f"""\
Question: {state['question']}

The following Python code was executed:
{state['generated_code']}

The code printed: {state['code_output']}

Write a one-sentence natural language answer to the question using the printed result.
Do not recalculate — trust the code output completely."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_answer": response.content.strip()}


# ─── Graph ─────────────────────────────────────────────────────────────────────
graph = StateGraph(PALState)
graph.add_node("generate_code", generate_code_node)
graph.add_node("execute_code",  execute_code_node)
graph.add_node("format_answer", format_answer_node)

graph.add_edge(START,           "generate_code")
graph.add_edge("generate_code", "execute_code")
graph.add_edge("execute_code",  "format_answer")
graph.add_edge("format_answer", END)

app = graph.compile()


# ─── Run Examples ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    questions = [
        # Classic PAL word problem — arithmetic that LLMs often get wrong
        "A store sells apples for $1.25 each. If I buy 17 apples and pay with a $25 bill, how much change do I get?",

        # Multi-step reasoning that benefits from code
        "A train travels at 80 km/h for 2.5 hours, then at 60 km/h for 1.75 hours. What is the total distance traveled?",

        # Percentage/ratio problem
        "A class has 35 students. 60% are female. How many male students are there?",
    ]

    for i, q in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"Example {i}: {q}")
        print("="*60)
        result = app.invoke({"question": q, "generated_code": "", "code_output": "", "final_answer": ""})
        print(f"\nFinal Answer: {result['final_answer']}")
