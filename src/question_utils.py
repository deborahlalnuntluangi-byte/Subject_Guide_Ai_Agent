def detect_question_type(query):
    query = query.lower().strip()

    if "difference" in query or "compare" in query:
        return "comparison"
    elif "define" in query or "what is" in query:
        return "definition"
    elif "explain" in query or "describe" in query:
        return "long"
    elif "program" in query or "lab" in query or "algorithm" in query:
        return "lab"
    else:
        return "general"