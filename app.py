"""Streamlit chat interface for TelecomPlus customer support."""

import streamlit as st

from src.main import answer

st.set_page_config(page_title="TelecomPlus Support", page_icon="📱")

st.title("📱 TelecomPlus - Support Client")
st.markdown("*Assistant intelligent pour répondre à vos questions*")

# Sidebar for client ID (optional)
with st.sidebar:
    st.header("Configuration")
    client_id = st.text_input(
        "Identifiant Client (optionnel)", 
        placeholder="Ex: 1, 2, 3...",
        help="Entrez votre ID client pour des réponses personnalisées"
    )
    st.markdown("---")
    st.markdown("### Exemples de questions")
    st.markdown("**Questions FAQ:**")
    st.markdown("- Quels modes de paiement acceptez-vous ?")
    st.markdown("- Y a-t-il des frais de résiliation ?")
    st.markdown("- Comment fonctionne le roaming ?")
    st.markdown("")
    st.markdown("**Questions personnelles:**")
    st.markdown("- Quel est mon abonnement actuel ?")
    st.markdown("- Quelle est ma dernière facture ?")
    st.markdown("- Quels sont les forfaits disponibles ?")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Posez votre question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Recherche en cours..."):
            # Use client_id if provided and not empty
            cid = client_id.strip() if client_id and client_id.strip() else None
            response = answer(prompt, client_id=cid)
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
