import os
import shutil
from pathlib import Path
from typing import List

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Persistence directory for ChromaDB
CHROMA_PATH = "data/chroma_db"

def get_embedding_function():
    """Get the Google Generative AI Embeddings function."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)

def get_vector_store():
    """Get or create the ChromaDB vector store."""
    embedding_function = get_embedding_function()
    return Chroma(
        persist_directory=CHROMA_PATH, 
        embedding_function=embedding_function
    )

def clear_vector_store():
    """Clear the vector store by removing the persistence directory."""
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
        return True
    return False

def process_and_add_document(file_path: str):
    """
    Load a document (PDF or TXT), split it into chunks, and add to vector store.
    Returns the number of chunks added.
    """
    path = Path(file_path)
    
    # 1. Load Document
    if path.suffix.lower() == ".pdf":
        loader = PyPDFLoader(file_path)
        docs = loader.load()
    elif path.suffix.lower() == ".txt":
        loader = TextLoader(file_path)
        docs = loader.load()
    elif path.suffix.lower() == ".csv":
        import pandas as pd
        try:
            df = pd.read_csv(file_path)
            # Convert to markdown for better LLM readability
            text = f"Dataset: {path.name}\n\n" + df.to_markdown(index=False)
            docs = [Document(page_content=text, metadata={"source": file_path})]
        except Exception as e:
            raise ValueError(f"Error reading CSV: {e}")
    elif path.suffix.lower() in [".xlsx", ".xls"]:
        import pandas as pd
        try:
            df = pd.read_excel(file_path)
            text = f"Dataset: {path.name}\n\n" + df.to_markdown(index=False)
            docs = [Document(page_content=text, metadata={"source": file_path})]
        except Exception as e:
            raise ValueError(f"Error reading Excel: {e}")
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")
        
    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(docs)
    
    # 3. Add to Vector Store
    db = get_vector_store()
    db.add_documents(chunks)
    # Chroma automatically persists in newer versions, but we can access db if needed
    
    return len(chunks)

def query_rag(query: str, k: int = 3):
    """
    Query the vector store for relevant context.
    Returns a list of (document, score) tuples.
    """
    db = get_vector_store()
    results = db.similarity_search_with_score(query, k=k)
    return results
