
from src.gemini_client import safe_generate
SOLUTION_STYLES = {
    "numerical": """
- Show step-by-step working
- Label each step clearly
- Box the final answer
- Mention formula used
""",
    "code": """
- Write clean, commented code
- Explain logic before the code block
- Add sample input/output at the end
""",
    "theory": """
- Answer in structured paragraphs
- Use headings where needed
- Include definition, explanation, example
""",
    "mcq": """
- State the correct option clearly
- Explain WHY it is correct
- Briefly explain why others are wrong
""",
    "short": """
- Answer in 3-5 sentences max
- Be direct and precise
""",
}


def detect_solution_type(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ["calculate", "find", "evaluate", "compute", "value of"]):
        return "numerical"
    if any(k in q for k in ["write", "code", "program", "implement", "algorithm"]):
        return "code"
    if any(k in q for k in ["a)", "b)", "c)", "d)", "which of", "mcq"]):
        return "mcq"
    if any(k in q for k in ["briefly", "short", "in one line", "in brief"]):
        return "short"
    return "theory"


def build_solver_prompt(query: str, chunks: list, solution_type: str, mode: str) -> str:
    sources_block = ""
    for i, c in enumerate(chunks, 1):
        sources_block += f"\n[Source {i} | {c['source']} | {c['category']}]\n{c['text']}\n"

    style = SOLUTION_STYLES.get(solution_type, SOLUTION_STYLES["theory"])

    verbosity = (
        "Provide a complete, exam-ready solution with all steps visible."
        if mode == "Exam Mode"
        else "Keep the solution concise and direct."
    )

    return f"""You are a Computer Science academic assistant solving exam questions.

SOLUTION TYPE: {solution_type.upper()}
{verbosity}

FORMAT RULES:
{style}

STRICT RULES:
- Use ONLY the provided sources as reference
- Do not invent formulas or facts not in sources
- If sources are insufficient, state what is missing
- Do not repeat the question back

QUESTION:
{query}

REFERENCE SOURCES:
{sources_block}
"""


def solve_question(query: str, chunks: list, mode: str = "Exam Mode") -> dict:
    solution_type = detect_solution_type(query)
    prompt = build_solver_prompt(query, chunks, solution_type, mode)

    solution = safe_generate(prompt)  # already a plain string

    return {
        "solution": solution,
        "solution_type": solution_type,
    }