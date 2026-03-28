import streamlit as st

from src.file_loader import load_file
from src.text_chunker import chunk_text_with_metadata
from src.vector_store import create_vector_store
from src.retriever import search_chunks
from src.llm_handler import generate_answer
from src.question_utils import detect_question_type




# ---------------- MAIN APP ----------------
st.title("Subject Guide Assistant")

uploaded_files = st.file_uploader(
    "Upload your files",
    type=["pdf", "docx", "pptx"],
    accept_multiple_files=True
)

mode = st.selectbox(
    "Select Mode",
    ["Exam Mode", "Quick Answer Mode"]
)

filter_category = st.selectbox(
    "Filter by category (optional)",
    ["All", "Textbook", "Notes", "Question Paper", "Lab Material"]
)

@st.cache_resource
def build_index(texts):
    return create_vector_store(texts)

file_categories = {}

if uploaded_files:
    st.markdown("## Assign category for each file")

    for file in uploaded_files:
        file_categories[file.name] = st.selectbox(
            f"Category for {file.name}",
            ["Textbook", "Notes", "Question Paper", "Lab Material"],
            key=file.name
        )

if uploaded_files:
    all_chunks = []

    for file in uploaded_files:
        text = load_file(file)

        if text.strip() != "":
            file_chunks = chunk_text_with_metadata(
                text=text,
                source=file.name,
                category=file_categories[file.name]
            )
            all_chunks.extend(file_chunks)

    if not all_chunks:
        st.error("Could not extract text from the uploaded files.")
    else:
        texts = [chunk["text"] for chunk in all_chunks]
        index, embeddings = build_index(texts)

        st.success("Vector store created successfully ✅")
        st.write("Number of uploaded files:", len(uploaded_files))
        st.write("Number of chunks:", len(all_chunks))

        query = st.text_input("Ask a question:")

        if query:
            question_type = detect_question_type(query)

            results = search_chunks(
                query=query,
                index=index,
                all_chunks=all_chunks,
                selected_category=filter_category,
                k=3
            )

            if not results:
                st.warning("No relevant chunks found for the selected category.")
            else:
                try:
                    answer = generate_answer(
                        query=query,
                        retrieved_chunks=results,
                        question_type=question_type,
                        mode=mode
                    )

                    st.subheader("AI Answer:")
                    st.write(answer)

                    st.markdown("### 🧠 Answer Type:")
                    st.write(question_type.upper())

                    st.markdown("### ⚙️ Mode:")
                    st.write(mode)

                    confidence = min(
                        100,
                        int((len(set([r["source"] for r in results])) / 3) * 100)
                    )
                    st.markdown(f"**Confidence Score:** {confidence}%")

                    if len(results) < 2:
                        st.warning("⚠️ Answer may be limited due to low supporting sources.")

                    st.markdown("### 📚 Sources Used:")
                    unique_sources = []
                    seen = set()

                    for res in results:
                        source_label = f"{res['source']} ({res['category']})"
                        if source_label not in seen:
                            seen.add(source_label)
                            unique_sources.append(source_label)

                    for source in unique_sources:
                        st.write(f"- {source}")

                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        st.error("⚠️ Daily Gemini free limit reached. Try again later or tomorrow.")
                    else:
                        st.error("Gemini request failed")
                        st.exception(e)

                with st.expander("Show retrieved chunks"):
                    for i, res in enumerate(results, start=1):
                        st.write(f"### Result {i}")
                        st.write(res["text"])
                        st.caption(f"Source: {res['source']} | Category: {res['category']}")