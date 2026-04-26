import streamlit as st
from datetime import datetime


def init_progress():
    if "progress" not in st.session_state:
        st.session_state.progress = {
            "quiz_history": [],
            "topics_studied": [],
            "total_questions": 0,
            "total_correct": 0,
            "sessions": 0,
            "last_active": None
        }


def record_quiz_result(topic: str, score: int, total: int, weak_areas: list):
    init_progress()
    st.session_state.progress["quiz_history"].append({
        "topic": topic,
        "score": score,
        "total": total,
        "percentage": int((score / total) * 100) if total > 0 else 0,
        "weak_areas": weak_areas,
        "date": datetime.now().strftime("%d %b %Y %H:%M")
    })
    st.session_state.progress["total_questions"] += total
    st.session_state.progress["total_correct"] += score
    st.session_state.progress["last_active"] = datetime.now().strftime("%d %b %Y")


def record_topic_studied(topic: str):
    init_progress()
    if topic not in st.session_state.progress["topics_studied"]:
        st.session_state.progress["topics_studied"].append(topic)
    st.session_state.progress["sessions"] += 1


def get_overall_stats() -> dict:
    init_progress()
    p = st.session_state.progress
    total_q = p["total_questions"]
    total_c = p["total_correct"]

    return {
        "total_questions": total_q,
        "total_correct": total_c,
        "overall_percentage": int((total_c / total_q) * 100) if total_q > 0 else 0,
        "topics_studied": p["topics_studied"],
        "sessions": p["sessions"],
        "quiz_history": p["quiz_history"],
        "last_active": p["last_active"]
    }


def get_performance_level(percentage: int) -> tuple:
    if percentage >= 85:
        return "🏆 Excellent", "green"
    elif percentage >= 70:
        return "✅ Good", "blue"
    elif percentage >= 50:
        return "⚠️ Needs Improvement", "orange"
    else:
        return "❌ Weak", "red"