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
    
    # For price-related questions, retrieve both price table and product specs
    def enhanced_retriever(question: str):
        """Retrieve relevant docs, with special handling for various question types."""
        docs = vectorstore.similarity_search(question, k=TOP_K_RESULTS)
        question_lower = question.lower()
        
        # If question mentions price/euros/€ or budget, also get price table explicitly
        if any(word in question_lower for word in ['prix', 'euro', '€', 'coût', 'budget', 'cher', 'moins de']):
            price_docs = vectorstore.similarity_search("tableau prix iPhone", k=2)
            for price_doc in price_docs:
                if price_doc not in docs:
                    docs.insert(0, price_doc)
        
        # If question is about roaming/abroad/international usage
        if any(word in question_lower for word in ['étranger', 'etranger', 'roaming', 'international', 'surcoût', 'surcout', 'voyage']):
            roaming_docs = vectorstore.similarity_search("roaming tarifs Europe hors Europe pass international", k=3)
            for roaming_doc in roaming_docs:
                if roaming_doc not in docs:
                    docs.insert(0, roaming_doc)
        
        # If question is about battery/autonomy, get all iPhone battery specs
        if any(word in question_lower for word in ['autonomie', 'batterie', 'battery', 'heures', 'lecture vidéo']):
            # Get chunks with battery/autonomy info for various models
            battery_docs = vectorstore.similarity_search("autonomie jusqu'à heures de lecture vidéo", k=4)
            for battery_doc in battery_docs:
                if battery_doc not in docs:
                    docs.insert(0, battery_doc)
            # Also search for specific model battery info if models are mentioned
            import re
            models = re.findall(r'iPhone\s*(\d+)', question)
            for model in models:
                model_battery_docs = vectorstore.similarity_search(f"iPhone {model} autonomie batterie lecture vidéo", k=2)
                for doc in model_battery_docs:
                    if doc not in docs:
                        docs.insert(0, doc)
        
        return docs

    template = """You are a TelecomPlus customer support assistant. Answer the question based on the provided context from our FAQ documents.

Context:
{context}

Question: {question}

Instructions:
- Answer in French, be helpful and concise
- Use ALL information from the context - combine details from multiple paragraphs if needed

CRITICAL - For multi-criteria product searches (e.g., camera + price + storage):
1. First, scan ALL context for the price table (format: "Modèle 128GB 256GB 512GB" followed by "iPhone X - 749€")
2. Extract prices for the requested storage (e.g., 256GB column)
3. Then, scan descriptions for the technical spec (e.g., "48 Mpx", "Triple caméra 48 Mpx")
4. Match model names between table and descriptions
5. Apply ALL filters: spec requirement (e.g., >= 48 Mpx) AND budget (e.g., < 1200€) AND storage
6. List ONLY models that meet ALL criteria with their exact prices from the table

Example: "iPhone with 48 Mpx, < 1200€, 256GB"
- Find table: iPhone 15 256GB = 1099€, iPhone 16 256GB = 1149€, iPhone 17 256GB = 1299€
- Find camera: iPhone 15 has 48 Mpx, iPhone 16 has 48 Mpx, iPhone 17 has 48 Mpx
- Filter: iPhone 15 (1099€ < 1200€ ✓), iPhone 16 (1149€ < 1200€ ✓), iPhone 17 (1299€ >= 1200€ ✗)
- Answer: iPhone 15 (1099€) and iPhone 16 (1149€)

For BUDGET questions ("avec mon budget de X€"):
- Find the BEST option(s) within budget (highest price that fits)
- If a better model is slightly over budget (<10-15% over), MENTION it as an alternative
- Example: Budget 1000€ for 256GB → Recommend iPhone 14 (999€), mention iPhone 15 (1099€) slightly exceeds budget
- DO NOT list ALL cheaper models - only recommend the BEST VALUE (most expensive within budget) and ONE alternative just over budget

For battery/autonomy comparison questions:
- Look for "autonomie" or "Xh de lecture vidéo" in ALL chunks for EACH model
- Calculate the exact difference between models

For launch dates: iPhone 15 = Sept 2023, iPhone 14 = 2022, iPhone 13 = 2021
For online account: "votre espace client" on www.telecomplus.fr
For roaming/travel abroad questions ("à l'étranger", "sans surcoût"):
- EU countries: "roaming comme à la maison" = use your French plan without extra cost
- Non-EU countries: extra charges apply, recommend subscribing to "pass international" (daily or weekly) available in customer area
For family plans: TelecomPlus offers multi-line/family plans

Always synthesize across all chunks before answering."""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # Return the components for answer_faq to use
    return enhanced_retriever, prompt, llm


def answer_faq(question: str) -> str:
    """Answer FAQ questions using RAG."""
    enhanced_retriever, prompt, llm = get_rag_chain()
    
    # Get relevant docs with enhanced retrieval
    docs = enhanced_retriever(question)
    context = format_docs(docs)
    
    # Generate answer
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"context": context, "question": question})


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
    
    # Check for general plans query first (no client_id needed)
    if ("forfait" in question_lower or "plan" in question_lower or "offre" in question_lower) and not client_id:
        data_context = data_tools.query_forfaits()
    elif client_id:
        # Client-specific queries - check in priority order
        if "ticket" in question_lower or "support" in question_lower:
            data_context = data_tools.query_tickets(client_id)
        elif "facture" in question_lower or "paiement" in question_lower or "montant" in question_lower or "payer" in question_lower:
            data_context = data_tools.query_factures(client_id)
        elif ("change" in question_lower or "upgrade" in question_lower or "passer" in question_lower or "plus de data" in question_lower or "coûtera" in question_lower) and "forfait" in question_lower:
            # For plan change/upgrade questions, include both current and available plans
            current_plan = data_tools.query_abonnements(client_id)
            available_plans = data_tools.query_forfaits()
            data_context = f"Current subscription:\n{current_plan}\n\nAvailable plans:\n{available_plans}"
        elif "consommation" in question_lower or ("data" in question_lower and "combien" not in question_lower) or "usage" in question_lower or "utilisation" in question_lower:
            data_context = data_tools.query_consommation(client_id)
        elif "abonnement" in question_lower or "souscription" in question_lower or ("forfait" in question_lower and ("mon" in question_lower or "quel" in question_lower)):
            # For plan-related questions with client_id, include both current plan and available plans for comparison
            current_plan = data_tools.query_abonnements(client_id)
            available_plans = data_tools.query_forfaits()
            data_context = f"Current subscription:\n{current_plan}\n\nAvailable plans:\n{available_plans}"
        elif "voyage" in question_lower or "étranger" in question_lower or "international" in question_lower:
            # For travel questions, include subscription info to check roaming coverage
            data_context = data_tools.query_abonnements(client_id)
        elif "résili" in question_lower or "annul" in question_lower:
            # For cancellation questions, include subscription with engagement info
            data_context = data_tools.query_abonnements(client_id)
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

Instructions:
- Provide a clear, helpful answer in French
- Format the information nicely and highlight important details
- For plan comparison questions: MUST calculate exact price differences (e.g., "Confort 20GB à 15.99€ - votre Essentiel 5GB à 9.99€ = +6.00€ par mois pour 15GB de data supplémentaire")
- For plan upgrades: show ALL available upgrades with price differences and data increases
- For engagement questions: check "statut" ("Actif - Engagé" = under contract, "Actif - Hors engagement" = no contract)
- For CANCELLATION (résiliation) questions: 
  * Check "statut" field: "Hors engagement" = free cancellation, "Engagé" = fees apply
  * Include the "date_debut" (contract start date) in your answer
  * If engagement period is 12 or 24 months, calculate when engagement ended
  * Example: "Votre contrat a commencé le [date_debut] et vous êtes hors engagement depuis [date]. La résiliation est gratuite."
- For TRAVEL questions (voyage, États-Unis, étranger hors Europe):
  * EU destinations: "roaming comme à la maison" (included in plan)
  * Non-EU destinations (USA, Asia, etc.): Recommend "pass international journalier ou hebdomadaire" available in "espace client"
  * Mention specific pass options: daily pass or weekly pass
  * Say: "Nous recommandons un pass international. Vous pouvez souscrire à un pass journalier ou hebdomadaire dans votre espace client."
- For ticket questions: list ALL tickets, their status ("En cours" = ongoing, "Résolu" = resolved), and subjects
- Be specific with numbers: exact prices, data amounts, dates, ticket IDs
- Always answer directly - perform calculations yourself, don't ask user to check elsewhere
- If you see the data in the system output, USE IT to answer the question completely"""
    
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
- "FAQ": General questions about:
  * How things work (payment methods, account management, password reset, MMS setup, viewing invoices online)
  * Policies (cancellation, roaming, charges)
  * General product information (iPhone features, colors, specs, prices, recommendations, budget questions like "avec mon budget")
  * Technical support procedures
  * Any "comment" (how to) questions about procedures
  * Using iPhone abroad, roaming questions
  
- "DATA": Questions asking for PERSONAL/SPECIFIC data:
  * "Available plans/forfaits" (general list) - use DATA
  * Client's CURRENT subscription/abonnement (with "mon abonnement", "ma facture", "mes données")
  * Client's personal bills/factures or amounts ("ma prochaine facture")
  * Client's data usage/consommation
  * Client's support tickets
  * Questions mentioning a specific person's name ("Je m'appelle...")
  * Questions about travel WITH personal plan info ("Je pars en...")

IMPORTANT: 
- Product recommendations with "mon budget" = FAQ (not personal data)
- "Puis-je utiliser mon iPhone à l'étranger" = FAQ (general policy)

IMPORTANT: 
- "Comment" (how to) questions = FAQ (procedures)
- Product questions (iPhone price, colors, specs, recommendations) = FAQ
- Questions about "available plans" or "forfaits disponibles" = DATA
- Personal account questions ("my subscription", "Je m'appelle X") = DATA
- Questions asking "how to view/access/consult" something = FAQ

Question: {question}

Answer with ONLY one word: either "FAQ" or "DATA"."""
    
    classifier_prompt = ChatPromptTemplate.from_template(classifier_template)
    classifier_chain = classifier_prompt | llm | StrOutputParser()
    
    classification = classifier_chain.invoke({"question": question}).strip().upper()
    
    # Route to appropriate agent
    if "DATA" in classification:
        question_lower = question.lower()
        
        # Check if this is a general product/plan query or a personal query
        is_general_plan_query = ("forfait" in question_lower or "plan" in question_lower) and not any(word in question_lower for word in ["mon", "ma", "mes", "m'appelle"])
        
        # If it's just asking for available plans, no client_id needed
        if is_general_plan_query and not client_id:
            return answer_data_query(question, client_id=None)
        
        # Check if we need client_id for personal queries
        needs_client_id = any(word in question_lower for word in 
                             ["mon", "ma", "mes", "facture", "abonnement", "consommation", "usage", "ticket", "m'appelle", "résili", "resili", "annul"])
        
        if needs_client_id and not client_id:
            # Try to extract name from question ("Je m'appelle X Y")
            import re
            name_match = re.search(r"(?:je m'appelle|m'appelle)\s+([A-ZÀ-ÿa-z]+(?:\s+[A-ZÀ-ÿa-z]+)?)", question, re.IGNORECASE)
            if name_match:
                client_name = name_match.group(1).strip()
                # Look up client_id by name
                found_id = data_tools.find_client_by_name(client_name)
                if found_id:
                    client_id = found_id
            
            # Try to extract client_id from question (numbers or "client X")
            if not client_id:
                match = re.search(r'client\s+(\d+)', question_lower)
                if match:
                    client_id = match.group(1)
                else:
                    # Look for standalone numbers
                    match = re.search(r'\b(\d+)\b', question)
                    if match:
                        client_id = match.group(1)
        
        # Always return the query even if client_id not found - let the data agent handle it
        return answer_data_query(question, client_id)
    else:
        return answer_faq(question)

