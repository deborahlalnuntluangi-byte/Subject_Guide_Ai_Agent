from src.gemini_client import safe_generate


def build_study_plan_prompt(subject: str, topics: list, days: int, chunks: list) -> str:
    sources_block = ""
    for i, c in enumerate(chunks[:5], 1):
        sources_block += f"\n[Source {i} | {c['source']} | {c['category']}]\n{c['text'][:300]}\n"

    topics_block = "\n".join(f"- {t}" for t in topics) if topics else "All topics from uploaded content"

    return f"""You are an academic study planner for Indian university students.

TASK: Create a detailed {days}-day study plan for the subject below.

SUBJECT: {subject}
TOPICS TO COVER:
{topics_block}

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

## 📅 Study Plan Overview
Total days: {days}
Daily study time recommended: X hours

## 🗓️ Day-wise Schedule
### Day 1
- Topic: [topic name]
- Focus: [what to study]
- Resources: [which uploaded file to refer]
- Target: [what student should achieve by end of day]

[Repeat for each day]

## 📊 Weekly Milestones
[What should be completed by end of each week]

## 🎯 Exam Day Tips
[5 tips for the day of exam]

RULES:
- Create exactly {days} days
- Balance theory and practice days
- Include revision days before exam
- Keep Indian university exam pattern in mind
- Reference uploaded study materials where relevant

AVAILABLE CONTENT:
{sources_block}
"""


def generate_study_plan(subject: str, chunks: list, days: int = 7, topics: list = None) -> dict:
    if topics is None:
        topics = list(set(c["source"] for c in chunks))

    prompt = build_study_plan_prompt(subject, topics, days, chunks)
    plan = safe_generate(prompt)

    return {
        "plan": plan,
        "subject": subject,
        "days": days,
        "topics_count": len(topics)
    }