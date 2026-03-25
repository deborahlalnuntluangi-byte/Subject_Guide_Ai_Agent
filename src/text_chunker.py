from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text_with_metadata(text, source, category):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    chunks = splitter.split_text(text)

    return [
        {
            "text": chunk,
            "source": source,
            "category": category
        }
        for chunk in chunks
    ]