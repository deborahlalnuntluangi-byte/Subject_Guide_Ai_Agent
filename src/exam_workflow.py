from src.gemini_client import safe_generate


def build_exam_prep_prompt(topic: str, chunks: list, mode: str) -> str:
    sources_block = ""
    for i, c in enumerate(chunks, 1):
        sources_block += f"\n[Source {i} | {c['source']} | {c['category']}]\n{c['text']}\n"

    return f"""You are a Computer Science academic assistant preparing a student for exams.

TASK: Create a complete exam preparation package for the topic below.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

## 📌 Key Concepts
List the 5 most important concepts the student must know.
One line each.

## 📝 Important Definitions
Give 3-5 definitions that are likely to appear in exams.
Format: Term: Definition

## 🔥 Most Expected Questions
List 5 questions most likely to appear in the exam.
Label each: [2 mark] [5 mark] [10 mark]

## 💡 Quick Revision Points
Give 5-8 bullet points for last minute revision.
Keep each point under 15 words.

## ⚠️ Common Mistakes to Avoid
List 3 common mistakes students make on this topic.

RULES:
- Use ONLY the provided sources
- Keep language simple and exam-focused
- Do not invent content not in sources

TOPIC: {topic}

SOURCES:
{sources_block}
"""


def generate_exam_prep(topic: str, chunks: list, mode: str = "Exam Mode") -> dict:
    prompt = build_exam_prep_prompt(topic, chunks, mode)
    result = safe_generate(prompt)

    return {
        "content": result,
        "topic": topic,
        "source_count": len(set(c["source"] for c in chunks))
    }