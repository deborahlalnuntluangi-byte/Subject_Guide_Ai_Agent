# 📚 DBMS Lab & Question Assistant

An AI-powered academic assistant that helps students understand DBMS concepts, answer exam questions, and generate lab-style explanations using Retrieval-Augmented Generation (RAG).

---

## 🚀 Features

* Multi-document upload (PDF, DOCX, PPTX)
* AI-powered answers using Gemini
* Semantic search with vector database
* Category filtering (Notes, Textbook, Lab Material)
* Supports:

  * Concept explanations
  * Comparison questions (table format)
  * Lab-style answers
* Confidence score and source tracking

---

## 🛠️ Tech Stack

* Python
* Streamlit
* FAISS
* Google Gemini API
* PyPDF2, python-docx

---

## 📦 Project Structure

```
academic_assistant/
│
├── app.py
├── requirements.txt
├── src/
│   ├── file_loader.py
│   ├── text_chunker.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── llm_handler.py
│   ├── question_utils.py
│
└── README.md
```

---

## ▶️ How to Run

```
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔐 Environment Variables

Create a `.env` file:

```
GEMINI_API_KEY=your_api_key_here
```

---

## 🎯 Use Case

* Students preparing for DBMS exams
* Lab record writing assistance
* Understanding concepts from multiple sources

---

## 👩‍💻 Author

Deborah
