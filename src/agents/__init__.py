"""RAG Agent for FAQ questions."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from src.config import GOOGLE_API_KEY, LLM_MODEL, LLM_TEMPERATURE, TOP_K_RESULTS
from src.vectorstore import get_vectorstore


def format_docs(docs):
    """Format retrieved documents into a single string."""
    return "\n\n".join(doc.page_content for doc in docs)


def get_rag_chain():
    """Create the RAG chain for FAQ questions."""
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        google_api_key=GOOGLE_API_KEY,
    )

    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K_RESULTS})

    template = """You are a TelecomPlus customer support assistant. Answer the question based on the provided context from our FAQ documents.

Context:
{context}

Question: {question}

Answer in French, be helpful and concise. Use only the information from the context."""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = (
        {
            "context": retriever | format_docs,
            "question": lambda x: x
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain


def answer_faq(question: str) -> str:
    """Answer FAQ questions using RAG."""
    chain = get_rag_chain()
    return chain.invoke(question)
