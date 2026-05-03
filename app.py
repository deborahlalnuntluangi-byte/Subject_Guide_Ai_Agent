import streamlit as st

from src.file_loader import load_file
from src.text_chunker import chunk_text_with_metadata
from src.vector_store import create_vector_store
from src.retriever import search_chunks
from src.intent_router import route_intent
from src.topic_engine import explain_topic
from src.question_solver import solve_question
from src.learning_path import generate_learning_stage, STAGES
from src.cross_ref import cross_reference
from src.exam_workflow import generate_exam_prep
from src.quiz_engine import generate_quiz, parse_quiz, evaluate_answer
from src.weak_area_detector import detect_weak_areas
from src.study_plan_generator import generate_study_plan
from src.progress_tracker import (
    init_progress, record_quiz_result,
    record_topic_studied, get_overall_stats,
    get_performance_level
)

# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Subject Guide Assistant",
    page_icon="📘",
    layout="wide"
)

# ── Session state ─────────────────────────────────────────────
for key in ["all_chunks", "index", "subject", "chapters",
            "quiz_questions", "quiz_results", "quiz_topic",
            "quiz_submitted"]:
    if key not in st.session_state:
        st.session_state[key] = None

init_progress()

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.header("📚 Subject Organisation")
    subject = st.text_input("Subject name", placeholder="e.g. DBMS")
    chapter = st.text_input("Chapter / Unit", placeholder="e.g. Unit 1")

    if subject:
        st.session_state.subject = subject

    st.markdown("---")
    mode = st.selectbox("Mode", ["Exam Mode", "Quick Answer Mode"])
    filter_category = st.selectbox(
        "Filter category",
        ["All", "Textbook", "Notes", "Question Paper", "Lab Material"]
    )

# ── File upload ───────────────────────────────────────────────
st.title("📘 Subject Guide Assistant")
st.markdown("Upload academic files and get structured AI-generated answers.")

uploaded_files = st.file_uploader(
    "Upload your files (PDF, DOCX, PPTX)",
    type=["pdf", "docx", "pptx"],
    accept_multiple_files=True
)

file_categories = {}
if uploaded_files:
    st.markdown("### Assign category for each file")
    for file in uploaded_files:
        file_categories[file.name] = st.selectbox(
            f"{file.name}",
            ["Textbook", "Notes", "Question Paper", "Lab Material"],
            key=file.name
        )

# ── Cache helpers ─────────────────────────────────────────────
@st.cache_data
def process_files(uploaded_files, file_categories):
    all_chunks = []
    for file in uploaded_files:
        text = load_file(file)
        if text.strip():
            all_chunks.extend(
                chunk_text_with_metadata(text, file.name, file_categories[file.name])
            )
    return all_chunks


@st.cache_resource
def build_index(texts):
    return create_vector_store(texts)

# ── Process button ────────────────────────────────────────────
if uploaded_files:
    if st.button("🚀 Process Files"):
        with st.spinner("Processing..."):
            all_chunks = process_files(uploaded_files, file_categories)
            if not all_chunks:
                st.error("Could not extract text from uploaded files.")
            else:
                texts = [c["text"] for c in all_chunks]
                index, _ = build_index(texts)
                st.session_state.all_chunks = all_chunks
                st.session_state.index = index
                st.success(f"✅ Ready — {len(all_chunks)} chunks from {len(uploaded_files)} file(s)")

# ── Main tabs ─────────────────────────────────────────────────
if st.session_state.index is not None:
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 Ask Question",
        "📝 Exam Prep",
        "🧪 Quiz Mode",
        "📅 Study Plan",
        "📊 My Progress"
    ])

    # ════════════════════════════════════════════════════════
    # TAB 1 — ASK QUESTION
    # ════════════════════════════════════════════════════════
    with tab1:
        st.markdown("---")
        query = st.text_input(
            "Ask a question or enter a topic:",
            placeholder="e.g. Explain ER diagrams / List advantages of DBMS"
        )

        if query:
            route = route_intent(query)
            intent = route["intent"]

            intent_labels = {
                "topic":    "📖 Topic Explanation",
                "solver":   "🧮 Question Solver",
                "learning": "🎓 Learning Path",
                "crossref": "🔗 Cross-Reference",
            }
            st.caption(f"Detected mode: **{intent_labels[intent]}**")

            with st.spinner("Retrieving relevant content..."):
                chunks = search_chunks(
                    query=query,
                    index=st.session_state.index,
                    all_chunks=st.session_state.all_chunks,
                    selected_category=filter_category,
                    k=5
                )

            if not chunks:
                st.warning("No relevant content found.")
            else:
                try:
                    if intent == "topic":
                        with st.spinner("Generating topic explanation..."):
                            answer = explain_topic(query, chunks, mode)
                        st.subheader("📖 Topic Explanation")
                        st.markdown(answer)
                        record_topic_studied(query)

                    elif intent == "solver":
                        with st.spinner("Solving question..."):
                            result = solve_question(query, chunks, mode)
                        st.subheader("🧮 Solution")
                        st.caption(f"Solution type: `{result['solution_type']}`")
                        st.markdown(result["solution"])

                    elif intent == "learning":
                        st.subheader("🎓 Learning Path")
                        topic_name = query.replace("teach me", "").replace("learn", "").strip()
                        tabs = st.tabs(STAGES)
                        for tab, stage in zip(tabs, STAGES):
                            with tab:
                                with st.spinner(f"Generating {stage}..."):
                                    content = generate_learning_stage(topic_name, stage, chunks)
                                st.markdown(content)
                        record_topic_studied(topic_name)

                    elif intent == "crossref":
                        with st.spinner("Synthesizing across all sources..."):
                            result = cross_reference(query, chunks)
                        st.subheader("🔗 Cross-Document Answer")
                        st.caption(f"Sources used: {', '.join(result['sources_used'])}")
                        st.markdown(result["answer"])

                except RuntimeError as e:
                    st.error(f"⚠️ {str(e)}")
                except Exception as e:
                    st.error("Something went wrong.")
                    st.exception(e)

                st.markdown("---")
                with st.expander("📚 Sources used"):
                    seen = set()
                    for c in chunks:
                        label = f"{c['source']} ({c['category']})"
                        if label not in seen:
                            seen.add(label)
                            st.write(f"- {label}")

                with st.expander("🔍 Retrieved chunks"):
                    for i, c in enumerate(chunks, 1):
                        st.write(f"**{i}. {c['source']}** — {c['category']}")
                        st.write(c["text"])
                        st.markdown("---")

    # ════════════════════════════════════════════════════════
    # TAB 2 — EXAM PREP
    # ════════════════════════════════════════════════════════
    with tab2:
        st.subheader("📝 Exam Preparation")
        st.markdown("Generate a complete exam prep package for any topic.")

        exam_topic = st.text_input(
            "Enter topic for exam prep:",
            placeholder="e.g. Normalization in DBMS",
            key="exam_topic_input"
        )

        if exam_topic:
            with st.spinner("Generating exam prep package..."):
                chunks = search_chunks(
                    query=exam_topic,
                    index=st.session_state.index,
                    all_chunks=st.session_state.all_chunks,
                    selected_category=filter_category,
                    k=5
                )

            if not chunks:
                st.warning("No relevant content found for this topic.")
            else:
                try:
                    if st.button("📝 Generate Exam Prep", key="exam_prep_btn"):
                        with st.spinner("Building your exam prep package..."):
                            result = generate_exam_prep(exam_topic, chunks, mode)
                        st.markdown(result["content"])
                        st.caption(f"Based on {result['source_count']} source(s)")
                        record_topic_studied(exam_topic)
                except RuntimeError as e:
                    st.error(f"⚠️ {str(e)}")
                except Exception as e:
                    st.error("Something went wrong.")
                    st.exception(e)

    # ════════════════════════════════════════════════════════
    # TAB 3 — QUIZ MODE
    # ════════════════════════════════════════════════════════
    with tab3:
        st.subheader("🧪 Quiz Mode")
        st.markdown("Test your knowledge with AI-generated questions.")

        col1, col2, col3 = st.columns(3)
        with col1:
            quiz_topic = st.text_input(
                "Quiz topic:",
                placeholder="e.g. ER Diagrams",
                key="quiz_topic_input"
            )
        with col2:
            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard"],
                key="quiz_difficulty"
            )
        with col3:
            num_q = st.selectbox(
                "Number of questions",
                [3, 5, 10],
                key="quiz_num_q"
            )

        if st.button("🎯 Generate Quiz", key="generate_quiz_btn"):
            if not quiz_topic:
                st.warning("Please enter a quiz topic.")
            else:
                with st.spinner("Generating quiz questions..."):
                    chunks = search_chunks(
                        query=quiz_topic,
                        index=st.session_state.index,
                        all_chunks=st.session_state.all_chunks,
                        selected_category=filter_category,
                        k=5
                    )

                if not chunks:
                    st.warning("No content found for this topic.")
                else:
                    try:
                        raw_quiz = generate_quiz(quiz_topic, chunks, difficulty, num_q)
                        questions = parse_quiz(raw_quiz)

                        if questions:
                            st.session_state.quiz_questions = questions
                            st.session_state.quiz_topic = quiz_topic
                            st.session_state.quiz_results = []
                            st.session_state.quiz_submitted = False
                            st.success(f"✅ {len(questions)} questions generated!")
                        else:
                            st.warning("Could not parse quiz. Try again.")
                            st.text(raw_quiz)
                    except RuntimeError as e:
                        st.error(f"⚠️ {str(e)}")

        # ── Show quiz questions ────────────────────────────
        if st.session_state.quiz_questions and not st.session_state.quiz_submitted:
            st.markdown("---")
            st.markdown("### Answer the questions below:")

            user_answers = {}
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Q{i+1}. {q['question']}**")
                if q["options"]:
                    user_answers[i] = st.radio(
                        f"Select answer for Q{i+1}:",
                        q["options"],
                        key=f"quiz_ans_{i}",
                        label_visibility="collapsed"
                    )
                else:
                    user_answers[i] = st.text_input(
                        f"Your answer for Q{i+1}:",
                        key=f"quiz_text_{i}"
                    )
                st.markdown("---")

            if st.button("✅ Submit Quiz", key="submit_quiz_btn"):
                results = []
                for i, q in enumerate(st.session_state.quiz_questions):
                    user_ans = user_answers.get(i, "")
                    correct = q["answer"]
                    is_correct = str(user_ans).lower().startswith(correct.lower())
                    results.append({
                        "question": q["question"],
                        "user_answer": user_ans,
                        "correct_answer": correct,
                        "explanation": q["explanation"],
                        "is_correct": is_correct
                    })

                st.session_state.quiz_results = results
                st.session_state.quiz_submitted = True
                st.rerun()

        # ── Show quiz results ──────────────────────────────
        if st.session_state.quiz_submitted and st.session_state.quiz_results:
            results = st.session_state.quiz_results
            score = sum(1 for r in results if r["is_correct"])
            total = len(results)
            percentage = int((score / total) * 100)

            level, color = get_performance_level(percentage)

            st.markdown("---")
            st.subheader("📊 Quiz Results")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{score}/{total}")
            with col2:
                st.metric("Percentage", f"{percentage}%")
            with col3:
                st.metric("Performance", level)

            st.markdown("---")
            for i, r in enumerate(results):
                if r["is_correct"]:
                    st.success(f"✅ Q{i+1}: {r['question']}")
                else:
                    st.error(f"❌ Q{i+1}: {r['question']}")
                    st.write(f"Your answer: `{r['user_answer']}`")
                    st.write(f"Correct answer: `{r['correct_answer']}`")
                    st.write(f"💡 {r['explanation']}")
                st.markdown("---")

            # Detect weak areas
            with st.spinner("Analyzing your performance..."):
                weak = detect_weak_areas(results)

            st.subheader("🔍 Weak Area Analysis")
            st.markdown(weak["recommendation"])

            # Save to progress
            record_quiz_result(
                topic=st.session_state.quiz_topic,
                score=score,
                total=total,
                weak_areas=weak["weak_topics"]
            )

            if st.button("🔄 Take Another Quiz", key="retry_quiz_btn"):
                st.session_state.quiz_questions = None
                st.session_state.quiz_results = []
                st.session_state.quiz_submitted = False
                st.rerun()

    # ════════════════════════════════════════════════════════
    # TAB 4 — STUDY PLAN
    # ════════════════════════════════════════════════════════
    with tab4:
        st.subheader("📅 Custom Study Plan")
        st.markdown("Generate a personalised study plan based on your uploaded content.")

        col1, col2 = st.columns(2)
        with col1:
            plan_subject = st.text_input(
                "Subject:",
                value=st.session_state.subject or "",
                placeholder="e.g. DBMS",
                key="plan_subject"
            )
        with col2:
            plan_days = st.selectbox(
                "Days until exam:",
                [3, 5, 7, 10, 14, 30],
                index=2,
                key="plan_days"
            )

        custom_topics = st.text_area(
            "Topics to cover (one per line, or leave blank to auto-detect):",
            placeholder="Normalization\nER Diagrams\nTransaction Management",
            key="plan_topics"
        )

        if st.button("📅 Generate Study Plan", key="study_plan_btn"):
            if not plan_subject:
                st.warning("Please enter a subject name.")
            else:
                topics = [t.strip() for t in custom_topics.split("\n") if t.strip()]

                with st.spinner("Creating your personalised study plan..."):
                    chunks = st.session_state.all_chunks[:20]
                    try:
                        result = generate_study_plan(
                            subject=plan_subject,
                            chunks=chunks,
                            days=plan_days,
                            topics=topics if topics else None
                        )
                        st.markdown(result["plan"])
                        st.caption(
                            f"Plan covers {result['days']} days "
                            f"across {result['topics_count']} topic(s)"
                        )
                    except RuntimeError as e:
                        st.error(f"⚠️ {str(e)}")
                    except Exception as e:
                        st.error("Something went wrong.")
                        st.exception(e)

    # ════════════════════════════════════════════════════════
    # TAB 5 — MY PROGRESS
    # ════════════════════════════════════════════════════════
    with tab5:
        st.subheader("📊 My Progress")
        stats = get_overall_stats()

        if stats["total_questions"] == 0:
            st.info("👆 Take a quiz to start tracking your progress!")
        else:
            # ── Overall stats ──────────────────────────────
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Questions", stats["total_questions"])
            with col2:
                st.metric("Correct Answers", stats["total_correct"])
            with col3:
                st.metric("Overall Score", f"{stats['overall_percentage']}%")
            with col4:
                level, _ = get_performance_level(stats["overall_percentage"])
                st.metric("Level", level)

            st.markdown("---")

            # ── Topics studied ─────────────────────────────
            if stats["topics_studied"]:
                st.markdown("### 📚 Topics Studied")
                for topic in stats["topics_studied"]:
                    st.write(f"✅ {topic}")

            st.markdown("---")

            # ── Quiz history ───────────────────────────────
            if stats["quiz_history"]:
                st.markdown("### 🧪 Quiz History")
                for i, quiz in enumerate(reversed(stats["quiz_history"]), 1):
                    level, _ = get_performance_level(quiz["percentage"])
                    with st.expander(
                        f"Quiz {i} — {quiz['topic']} — {quiz['percentage']}% {level}"
                    ):
                        st.write(f"Score: {quiz['score']}/{quiz['total']}")
                        st.write(f"Date: {quiz['date']}")
                        if quiz["weak_areas"]:
                            st.write("Weak areas:")
                            for area in quiz["weak_areas"]:
                                st.write(f"  - {area}")

            st.markdown("---")
            st.caption(f"Last active: {stats['last_active']}")

else:
    st.info("👆 Upload files and click **Process Files** to begin.")