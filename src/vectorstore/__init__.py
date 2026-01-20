"""Vectorstore setup for PDF documents."""

import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    EMBEDDING_MODEL,
    PDF_DIR,
    VECTORSTORE_DIR,
)


def load_pdf_documents() -> List:
    """Load all PDF documents from the PDF directory."""
    documents = []
    for pdf_file in PDF_DIR.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_file))
        documents.extend(loader.load())
    return documents


def create_vectorstore():
    """Create and persist the vectorstore from PDF documents."""
    # Load documents
    documents = load_pdf_documents()
    print(f"Loaded {len(documents)} documents from PDFs.")

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    splits = text_splitter.split_documents(documents)
    print(f"Created {len(splits)} text chunks.")

    # Create embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
    )

    # Create and persist vectorstore
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=str(VECTORSTORE_DIR),
    )
    print(f"Vectorstore created and persisted at {VECTORSTORE_DIR}.")
    return vectorstore


def get_vectorstore(force_recreate: bool = False):
    """Load the existing vectorstore or create if not exists."""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
    )

    if VECTORSTORE_DIR.exists() and not force_recreate:
        vectorstore = Chroma(
            persist_directory=str(VECTORSTORE_DIR),
            embedding_function=embeddings,
        )
        print("Loaded existing vectorstore.")
    else:
        if VECTORSTORE_DIR.exists():
            import shutil
            shutil.rmtree(VECTORSTORE_DIR)
            print("Removed old vectorstore.")
        vectorstore = create_vectorstore()

    return vectorstore


if __name__ == "__main__":
    # Run this to set up the vectorstore
    get_vectorstore()
