def route_intent(query: str) -> dict:
    q = query.lower().strip()

    # --- Keywords per tool ---
    topic_keywords = [
        "explain", "what is", "describe", "tell me about",
        "how does", "definition of", "overview of", "what are"
    ]
    solver_keywords = [
    "solve", "find", "calculate", "write a program",
    "algorithm", "code", "prove", "derive", "evaluate",
    "question", "answer", "solution", "implement",
    "define", "list", "state", "give", "mention"  # ← add these
]
    learning_keywords = [
        "teach me", "learn", "study", "guide me",
        "step by step", "from scratch", "beginner", "practice",
        "how to understand", "roadmap", "progression"
    ]
    crossref_keywords = [
        "across", "all files", "compare across", "from all",
        "every source", "combine", "summarize all", "overall"
    ]

    # --- Score each intent ---
    scores = {
        "topic":    sum(1 for k in topic_keywords    if k in q),
        "solver":   sum(1 for k in solver_keywords   if k in q),
        "learning": sum(1 for k in learning_keywords if k in q),
        "crossref": sum(1 for k in crossref_keywords if k in q),
    }

    best = max(scores, key=scores.get)

    # Fallback: if all zero, default to topic
    if scores[best] == 0:
        best = "topic"

    return {
        "intent":  best,
        "scores":  scores,
        "query":   query,
    }