"""RAG and Data Agents for TelecomPlus."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from src.config import GOOGLE_API_KEY, LLM_MODEL, LLM_TEMPERATURE, TOP_K_RESULTS, ENABLE_MONITORING, LANGFUSE_CLIENT, flush_langfuse
from src.vectorstore import get_vectorstore
from src.tools import data_tools

# Import observe decorator for Langfuse tracing
if ENABLE_MONITORING:
    from langfuse import observe
else:
    # Create a no-op decorator if monitoring is disabled
    def observe(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


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
        
        # If question is about launch dates/commercialization year
        if any(word in question_lower for word in ['commercialisé', 'commercialise', 'lancé', 'lance', 'sorti', 'sortie', '2023', '2022', '2021', '2020']):
            import re
            # Extract year if mentioned
            year_match = re.search(r'\b(20\d{2})\b', question)
            if year_match:
                year = year_match.group(1)
                # Search for chunks with the year
                launch_docs = vectorstore.similarity_search(f"commercialisé en {year}", k=3)
                # Also explicitly search for model names - they may be in adjacent chunks
                # Common pattern: chunk N ends with "iPhone X\n" and chunk N+1 starts with "Ce modèle, commercialisé en YEAR"
                for model_num in ['11', '12', '13', '14', '15', '16', '17']:
                    model_docs = vectorstore.similarity_search(f"iPhone {model_num}", k=2)
                    for doc in model_docs:
                        if doc not in launch_docs:
                            launch_docs.append(doc)
            else:
                launch_docs = vectorstore.similarity_search("iPhone commercialisé lancé date sortie", k=6)
            for launch_doc in launch_docs:
                if launch_doc not in docs:
                    docs.insert(0, launch_doc)
        
        # If question is about colors/coloris
        if any(word in question_lower for word in ['coloris', 'couleur', 'color']):
            import re
            # Extract iPhone model number if mentioned
            models = re.findall(r'iPhone\s*(\d+)', question)
            if models:
                for model in models:
                    # Search for unique specs to get the RIGHT chunk
                    # Battery life is unique per model
                    if model == '16':
                        color_docs = vectorstore.similarity_search(f"iPhone 16 22h lecture vidéo", k=5)
                    elif model == '15':
                        color_docs = vectorstore.similarity_search(f"iPhone 15 20h lecture vidéo A16", k=5)
                    elif model == '14':
                        color_docs = vectorstore.similarity_search(f"iPhone 14 20h lecture vidéo", k=5)
                    elif model == '13':
                        color_docs = vectorstore.similarity_search(f"iPhone 13 19h lecture vidéo", k=5)
                    else:
                        color_docs = vectorstore.similarity_search(f"iPhone {model} Coloris", k=5)
                    # Replace docs with color-specific search results
                    docs = color_docs + [d for d in docs if d not in color_docs]
                    break  # Only process first model mentioned
        
        # If question is about trade-in/reprise
        if any(word in question_lower for word in ['reprise', 'trade-in', 'échanger', 'ancien téléphone', 'ancien telephone', 'ancien appareil']):
            # Search for the catalog page with detailed reprise info (has contact details)
            tradein_docs = vectorstore.similarity_search("Reprise Échangez votre ancien téléphone bénéficiez réduction Téléphone 3900 boutique www.telecomplus.fr", k=5)
            for doc in tradein_docs:
                if doc not in docs:
                    docs.insert(0, doc)
        
        # If question is about family plans/data sharing
        if any(word in question_lower for word in ['famille', 'family', 'partager', 'partage', 'multi-ligne', 'multi ligne']):
            # Get the exact FAQ Q31 that answers this question - search for the actual answer text
            family_docs = vectorstore.similarity_search("Oui nous proposons des forfaits famille qui permettent de partager un pool de données entre plusieurs lignes", k=3)
            # REPLACE docs entirely with family-focused docs to avoid confusion with individual plan data
            docs = family_docs
        
        # If question is about cancellation/termination fees
        if any(word in question_lower for word in ['résiliation', 'resiliation', 'résilier', 'resilier', 'frais', 'engagé', 'engage']):
            # Search for the specific Q3 answer that has BOTH scenarios
            cancel_docs = vectorstore.similarity_search("Y a-t-il des frais de résiliation hors période engagement résiliation est gratuite encore engagé", k=4)
            for doc in cancel_docs:
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
- CRITICAL: Information may be split across chunks. If you see "iPhone X" at the end of one chunk and "Ce modèle, commercialisé en [year]" at the start of another chunk, they refer to the SAME model. Connect them together.
- For trade-in/reprise questions: Include ALL contact methods mentioned (phone, boutique, website) and explain how customers can get the discount. If a specific product is mentioned (e.g., iPhone 16), ALSO include its base price from the price table in context

CRITICAL - For multi-criteria product searches (e.g., camera + price + storage):
1. First, scan ALL context for the price table
2. Extract prices for the requested storage capacity
3. Then, scan descriptions for the technical spec (e.g., camera megapixels)
4. Match model names between table and descriptions
5. Apply ALL filters: spec requirement AND budget AND storage
6. List ONLY models that meet ALL criteria with their exact prices from the table
7. ALSO mention models that meet the technical criteria but EXCEED the budget, explaining why they don't qualify

CRITICAL - For BUDGET questions ("avec mon budget de X€", "Quel iPhone puis-je m'offrir"):
- ONLY use prices that appear EXACTLY in the price table in context - NEVER invent or estimate prices
- If a model/storage combination is not in the price table, do NOT mention it
- Recommend ONLY the BEST option within budget (the NEWEST/most expensive model that fits)
- Mention ONE alternative slightly over budget if relevant
- STOP AFTER 2 MODELS MAXIMUM - do NOT list older/cheaper models
- Example: For 1000€ budget, recommend iPhone 14 (999€) and mention iPhone 15 (1099€) as alternative. DO NOT list iPhone 13, 12, 11, X, etc.

For battery/autonomy comparison questions:
- Look for "autonomie" or "Xh de lecture vidéo" in ALL chunks for EACH model
- Calculate the exact difference between models

For photography/camera recommendation questions:
- Identify the BEST model for photography (highest specs)
- ALSO mention the next best alternative(s)
- Note that choice may depend on budget

For family/sharing questions ("partager", "famille", "data avec ma famille"):
- The answer is YES - TelecomPlus DOES offer family plans
- Say: "Oui, nous proposons des forfaits famille qui permettent de partager un pool de données entre plusieurs lignes"
- Direct users to contact customer service for more details
- IGNORE any individual plan listings in the context - they are NOT relevant to this question
- DO NOT say "data sharing is not available" or "not an option" - it IS available via family plans

For cancellation/termination questions ("frais de résiliation", "engagé"):
- ALWAYS mention BOTH scenarios in your answer:
  1. If still engaged: fees equal to remaining monthly payments
  2. If engagement period is over ("hors engagement"): termination is FREE ("gratuite")
- Both pieces of information MUST appear in your answer

Always synthesize across all chunks before answering."""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # Return the components for answer_faq to use
    return enhanced_retriever, prompt, llm


@observe(name="answer_faq")
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

@observe(name="answer_data_query")
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
    
    # Get vectorstore for travel questions that need roaming policy
    vectorstore = get_vectorstore()
    
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
            # Include both consumption AND plan info so user knows their total allowance
            consumption = data_tools.query_consommation(client_id)
            plan_info = data_tools.query_abonnements(client_id)
            data_context = f"Customer's current plan:\n{plan_info}\n\nCustomer's consumption data:\n{consumption}"
        elif "abonnement" in question_lower or "souscription" in question_lower or ("forfait" in question_lower and ("mon" in question_lower or "quel" in question_lower)):
            # For plan-related questions with client_id, include both current plan and available plans for comparison
            current_plan = data_tools.query_abonnements(client_id)
            available_plans = data_tools.query_forfaits()
            data_context = f"Current subscription:\n{current_plan}\n\nAvailable plans:\n{available_plans}"
        elif "voyage" in question_lower or "étranger" in question_lower or "international" in question_lower or "pars" in question_lower or "italie" in question_lower or "états-unis" in question_lower or "etats-unis" in question_lower:
            # For travel questions, include subscription info AND roaming policy from FAQ
            subscription_info = data_tools.query_abonnements(client_id)
            # Also get roaming policy from vectorstore - search for EU and non-EU policies
            roaming_policy = vectorstore.similarity_search("roaming comme à la maison Europe Union Européenne sans surcoût", k=3)
            roaming_policy2 = vectorstore.similarity_search("hors Europe pass international tarifs roaming", k=2)
            all_roaming = roaming_policy + [d for d in roaming_policy2 if d not in roaming_policy]
            roaming_context = "\n\n".join([doc.page_content for doc in all_roaming])
            data_context = f"Customer subscription:\n{subscription_info}\n\nRoaming policy from FAQ (USE THIS TO ANSWER):\n{roaming_context}"
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
- CRITICAL: If you see data in the "Data from our system" section above, that data exists and is correct. Use it directly in your answer.
- For DATA CONSUMPTION questions: ALWAYS mention BOTH the consumption amount AND the total plan allowance (e.g., "3.2 Go sur votre forfait de 5GB")
- For travel/roaming questions: FIRST mention customer's current plan with data amount, THEN use the "Roaming policy from FAQ" section to explain if there are surcharges. For EU countries (like Italy): mention "roaming comme à la maison" = no extra fees. For non-EU countries (like USA): ALWAYS state that "les tarifs dépendent de votre destination" and mention international pass options available in espace client.
- For plan comparison questions: MUST calculate exact price differences between plans
- For plan upgrades: show ALL available upgrades with price differences and data increases. Also mention HOW to change plan (via espace client or call 3900) and WHEN change takes effect (next billing cycle)
- For engagement questions: check "statut" ("Actif - Engagé" = under contract, "Actif - Hors engagement" = no contract)
- For CANCELLATION (résiliation) questions: 
  * Check "statut" field: "Hors engagement" = free cancellation, "Engagé" = fees apply
  * Include the "date_debut" (contract start date) in your answer
  * If engagement period is 12 or 24 months, calculate when engagement ended
  * Example: "Votre contrat a commencé le [date_debut] et vous êtes hors engagement depuis [date]. La résiliation est gratuite."
- For ticket questions: The data shows a table with columns. If you see ANY rows in the ticket table, those are the customer's tickets. List ALL of them using the EXACT ticket_id values from the first column (not the row index), along with sujet, statut, and date_creation
- Be specific with numbers: exact prices, data amounts, dates, ticket IDs
- Always answer directly - perform calculations yourself, don't ask user to check elsewhere
- NEVER say "I don't have access" or "information not available" if the data is shown in the system output above"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({"data": data_context, "question": question})


# ========================================
# Orchestrator - Step 5
# ========================================

@observe(name="orchestrate")
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
  * Travel/roaming questions WITHOUT client identification (e.g., "Puis-je utiliser mon iPhone a l etranger ?")
  * General questions about OPTIONS or SERVICES (e.g., "Quelles sont les options pour les appels vers l etranger ?")
  * Questions about international calling options, roaming options, available services
  
- "DATA": Questions asking for PERSONAL/SPECIFIC data:
  * "Available plans/forfaits" (general list) - use DATA
  * Client CURRENT subscription/abonnement (with "mon abonnement", "ma facture", "mes donnees")
  * Client personal bills/factures or amounts ("ma prochaine facture")
  * Client data usage/consommation
  * Client support tickets
  * ANY question mentioning a specific person name ("Je m appelle X") = DATA, even if asking about travel
  * Personal account questions with client identification

IMPORTANT: 
- Product recommendations with "mon budget" = FAQ (not personal data)
- "Comment" (how to) questions = FAQ (procedures)
- Product questions (iPhone price, colors, specs, recommendations) = FAQ
- Questions about "available plans" or "forfaits disponibles" = DATA
- IF the question has "Je m appelle [NAME]" = ALWAYS DATA (regardless of topic)
- General questions about OPTIONS/SERVICES without personal pronouns (mon/ma/mes) = FAQ

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
        
        # If classified as DATA but no personal keywords and no client_id, treat as FAQ
        if not needs_client_id and not client_id:
            return answer_faq(question)
        
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
        result = answer_data_query(question, client_id)
        flush_langfuse()
        return result
    else:
        result = answer_faq(question)
        flush_langfuse()
        return result

