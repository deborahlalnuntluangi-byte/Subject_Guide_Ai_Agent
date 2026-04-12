import streamlit as st

from src.file_loader import load_file
from src.text_chunker import chunk_text_with_metadata
from src.vector_store import create_vector_store
from src.retriever import search_chunks
from src.llm_handler import generate_answer
from src.question_utils import detect_question_type
from src.intent_router import route_intent
from src.topic_engine import explain_topic
from src.question_solver import solve_question
from src.learning_path import generate_learning_stage, STAGES
from src.cross_ref import cross_reference

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Subject Guide Assistant",
    page_icon="📘",
    layout="wide"
)

st.title("📘 Subject Guide Assistant")
st.markdown("Upload academic files and get structured AI-generated answers.")

# ── Session state ─────────────────────────────────────────────
for key in ["all_chunks", "index", "subject", "chapters"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── Sidebar: subject + chapter organization ───────────────────
with st.sidebar:
    st.header("📚 Subject Organisation")
    subject = st.text_input("Subject name", placeholder="e.g. Data Structures")
    chapter = st.text_input("Chapter / Unit", placeholder="e.g. Unit 2 - Trees")

    if subject:
        st.session_state.subject = subject

    st.markdown("---")
    mode = st.selectbox("Mode", ["Exam Mode", "Quick Answer Mode"])
    filter_category = st.selectbox(
        "Filter category",
        ["All", "Textbook", "Notes", "Question Paper", "Lab Material"]
    )

# ── File upload ───────────────────────────────────────────────
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

# ── Query section ─────────────────────────────────────────────
if st.session_state.index is not None:

    st.markdown("---")
    query = st.text_input(
        "Ask a question or enter a topic:",
        placeholder="e.g. Explain binary search trees / Write a BFS algorithm"
    )

    if query:
        # Route intent
        route = route_intent(query)
        intent = route["intent"]

        intent_labels = {
            "topic":    "📖 Topic Explanation",
            "solver":   "🧮 Question Solver",
            "learning": "🎓 Learning Path",
            "crossref": "🔗 Cross-Reference",
        }

        st.caption(f"Detected mode: **{intent_labels[intent]}**")

        # Retrieve relevant chunks
        with st.spinner("Retrieving relevant content..."):
            chunks = search_chunks(
                query=query,
                index=st.session_state.index,
                all_chunks=st.session_state.all_chunks,
                selected_category=filter_category,
                k=5
            )
        if not chunks:
            st.warning("No relevant content found. Try a different query or category.")
        else:
            try:
                # ── TOPIC EXPLANATION ──────────────────────────────
                if intent == "topic":
                    with st.spinner("Generating topic explanation..."):
                        answer = explain_topic(query, chunks, mode)
                    st.subheader("📖 Topic Explanation")
                    st.markdown(answer)

                # ── QUESTION SOLVER ────────────────────────────────
                elif intent == "solver":
                    with st.spinner("Solving question..."):
                        result = solve_question(query, chunks, mode)
                    st.subheader("🧮 Solution")
                    st.caption(f"Solution type: `{result['solution_type']}`")
                    st.markdown(result["solution"])

                # ── LEARNING PATH ──────────────────────────────────
                elif intent == "learning":
                    st.subheader("🎓 Learning Path")
                    topic_name = query.replace("teach me", "").replace("learn", "").strip()
                    tabs = st.tabs(STAGES)
                    for tab, stage in zip(tabs, STAGES):
                        with tab:
                            with st.spinner(f"Generating {stage}..."):
                                content = generate_learning_stage(topic_name, stage, chunks)
                            st.markdown(content)

                # ── CROSS REFERENCE ────────────────────────────────
                elif intent == "crossref":
                    with st.spinner("Synthesizing across all sources..."):
                        result = cross_reference(query, chunks)
                    st.subheader("🔗 Cross-Document Answer")
                    st.caption(f"Sources used: {', '.join(result['sources_used'])}")
                    st.markdown(result["answer"])

            except RuntimeError as e:
                st.error(f"⚠️ {str(e)}")  # catches "All Gemini models quota-exhausted"
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    st.error("⚠️ Daily Gemini free limit reached. Try again later or tomorrow.")
                else:
                    st.error("Something went wrong generating the answer.")
                    st.exception(e)
            # ── Sources footer ─────────────────────────────────
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
else:
    st.info("👆 Upload files and click **Process Files** to begin.")