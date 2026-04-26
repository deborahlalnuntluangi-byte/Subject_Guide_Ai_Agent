from src.gemini_client import safe_generate


def build_quiz_prompt(topic: str, chunks: list, difficulty: str, num_questions: int) -> str:
    sources_block = ""
    for i, c in enumerate(chunks, 1):
        sources_block += f"\n[Source {i} | {c['source']} | {c['category']}]\n{c['text']}\n"

    return f"""You are a Computer Science exam question generator.

TASK: Generate {num_questions} quiz questions on the topic below.
DIFFICULTY: {difficulty}

FORMAT EACH QUESTION EXACTLY LIKE THIS:
Q1. [Question text]
a) Option A
b) Option B
c) Option C
d) Option D
Answer: [correct option letter]
Explanation: [one line explanation why this is correct]

---

RULES:
- Generate exactly {num_questions} questions
- Use ONLY content from the provided sources
- Make options realistic and tricky
- Keep difficulty at {difficulty} level
- Always include Answer and Explanation

TOPIC: {topic}

SOURCES:
{sources_block}
"""


def build_evaluation_prompt(question: str, user_answer: str, correct_answer: str, explanation: str) -> str:
    return f"""You are an academic evaluator checking a student's answer.

QUESTION: {question}
CORRECT ANSWER: {correct_answer}
EXPLANATION: {explanation}
STUDENT ANSWER: {user_answer}

Evaluate the student's answer and respond in this format:

## Result
[Correct / Incorrect / Partially Correct]

## Feedback
[2-3 lines of constructive feedback]

## What to Study
[One specific topic or concept the student should review]
"""


def generate_quiz(topic: str, chunks: list, difficulty: str = "Medium", num_questions: int = 5) -> str:
    prompt = build_quiz_prompt(topic, chunks, difficulty, num_questions)
    return safe_generate(prompt)


def parse_quiz(raw_quiz: str) -> list:
    questions = []
    blocks = raw_quiz.strip().split("---")

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = [l.strip() for l in block.split("\n") if l.strip()]
        question_data = {
            "question": "",
            "options": [],
            "answer": "",
            "explanation": ""
        }

        for line in lines:
            if line.startswith("Q") and "." in line[:4]:
                question_data["question"] = line.split(".", 1)[-1].strip()
            elif line.startswith(("a)", "b)", "c)", "d)")):
                question_data["options"].append(line)
            elif line.lower().startswith("answer:"):
                question_data["answer"] = line.split(":", 1)[-1].strip()
            elif line.lower().startswith("explanation:"):
                question_data["explanation"] = line.split(":", 1)[-1].strip()

        if question_data["question"] and question_data["options"]:
            questions.append(question_data)

    return questions


def evaluate_answer(question: str, user_answer: str, correct_answer: str, explanation: str) -> str:
    prompt = build_evaluation_prompt(question, user_answer, correct_answer, explanation)
    return safe_generate(prompt)