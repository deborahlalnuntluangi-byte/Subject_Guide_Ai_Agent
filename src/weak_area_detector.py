from src.gemini_client import safe_generate


def detect_weak_areas(quiz_results: list) -> dict:
    wrong = [r for r in quiz_results if not r["is_correct"]]
    correct = [r for r in quiz_results if r["is_correct"]]

    score = len(correct)
    total = len(quiz_results)
    percentage = int((score / total) * 100) if total > 0 else 0

    weak_topics = list(set(r["question"][:50] for r in wrong))

    if not wrong:
        return {
            "score": score,
            "total": total,
            "percentage": percentage,
            "weak_topics": [],
            "recommendation": "Excellent! You have strong understanding of this topic.",
            "needs_revision": False
        }

    prompt = f"""You are an academic advisor analyzing a student's quiz performance.

STUDENT PERFORMANCE:
- Score: {score} out of {total} ({percentage}%)
- Wrong answers: {len(wrong)}
- Correct answers: {len(correct)}

QUESTIONS ANSWERED WRONGLY:
{chr(10).join(f"- {r['question']}" for r in wrong)}

Based on this performance, provide:

## Weak Areas Identified
List the specific concepts or topics the student is weak in.

## Priority Topics to Revise
Rank topics from most urgent to least urgent.

## Recommended Study Strategy
Give a 3-step study plan to improve these weak areas.

## Motivational Note
One encouraging line for the student.
"""

    recommendation = safe_generate(prompt)

    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "weak_topics": weak_topics,
        "recommendation": recommendation,
        "needs_revision": percentage < 70
    }