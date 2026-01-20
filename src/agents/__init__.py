"""RAG and Data Agents for TelecomPlus."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from src.config import GOOGLE_API_KEY, LLM_MODEL, LLM_TEMPERATURE, TOP_K_RESULTS
from src.vectorstore import get_vectorstore
from src.tools import data_tools


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


# ========================================
# Data Agent - Step 4
# ========================================

def answer_data_query(question: str, client_id: str = None) -> str:
    """Answer customer-specific data questions using direct tool calls.
    
    Args:
        question: The customer's question
        client_id: Optional client ID for personalized queries
        
    Returns:
        Answer based on customer data
    """
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        google_api_key=GOOGLE_API_KEY,
    )
    
    # Determine which tool to use based on question content
    question_lower = question.lower()
    
    data_context = ""
    
    if "forfait" in question_lower or "plan" in question_lower or "offre" in question_lower:
        # Query available plans
        data_context = data_tools.query_forfaits()
    elif client_id:
        # Client-specific queries
        if "facture" in question_lower or "paiement" in question_lower or "montant" in question_lower:
            data_context = data_tools.query_factures(client_id)
        elif "abonnement" in question_lower or "souscription" in question_lower:
            data_context = data_tools.query_abonnements(client_id)
        elif "consommation" in question_lower or "data" in question_lower or "usage" in question_lower:
            data_context = data_tools.query_consommation(client_id)
        elif "ticket" in question_lower or "support" in question_lower:
            data_context = data_tools.query_tickets(client_id)
        else:
            # Default to client info
            data_context = data_tools.query_clients(client_id=client_id)
    else:
        return "Pour accéder à vos informations personnelles, veuillez fournir votre identifiant client."
    
    # Generate answer using LLM with data context
    template = """You are a TelecomPlus customer support assistant. Answer the customer's question based on the provided data.

Data from our system:
{data}

Customer question: {question}

Provide a clear, helpful answer in French. Format the information nicely and highlight important details."""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({"data": data_context, "question": question})


# ========================================
# Orchestrator - Step 5
# ========================================

def orchestrate(question: str, client_id: str = None) -> str:
    """Orchestrate between RAG and Data agents based on question type.
    
    Args:
        question: The customer's question
        client_id: Optional client ID for personalized queries
        
    Returns:
        Answer from the appropriate agent
    """
    llm = ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        temperature=0,
        google_api_key=GOOGLE_API_KEY,
    )
    
    # Classify the question
    classifier_template = """You are a question classifier for TelecomPlus customer support.

Classify the following question into one of these categories:
- "FAQ": General questions about policies, how things work, payment methods, technical support procedures, roaming info, account management processes, cancellation policies, etc.
- "DATA": Questions asking for specific data like:
  * Available plans/forfaits and their pricing
  * Client's current subscription/abonnement
  * Client's bills/factures
  * Client's data usage/consommation
  * Client's support tickets
  * Any "mon/ma/mes" (my) questions requiring personal data

Question: {question}

Answer with ONLY one word: either "FAQ" or "DATA"."""
    
    classifier_prompt = ChatPromptTemplate.from_template(classifier_template)
    classifier_chain = classifier_prompt | llm | StrOutputParser()
    
    classification = classifier_chain.invoke({"question": question}).strip().upper()
    
    # Route to appropriate agent
    if "DATA" in classification:
        # Check if we need client_id
        question_lower = question.lower()
        needs_client_id = any(word in question_lower for word in 
                             ["mon", "ma", "mes", "facture", "abonnement", "consommation", "usage", "ticket"])
        
        if needs_client_id and not client_id:
            # Try to extract client_id from question
            if "client" in question_lower or "id" in question_lower:
                # Simple extraction - look for patterns like "C001" or just numbers
                import re
                match = re.search(r'\b(\d+)\b', question)
                if match:
                    client_id = match.group(1)
        
        return answer_data_query(question, client_id)
    else:
        return answer_faq(question)

