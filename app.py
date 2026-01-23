"""Streamlit chat interface for TelecomPlus customer support."""

import streamlit as st

from src.main import answer

st.set_page_config(page_title="TelecomPlus Support", page_icon="📱")

st.title("📱 TelecomPlus - Support Client")
st.markdown("*Assistant intelligent pour répondre à vos questions*")

# Sidebar with examples
with st.sidebar:
    st.header("💡 Exemples de questions")
    st.markdown("**Questions FAQ:**")
    st.markdown("- Quels modes de paiement acceptez-vous ?")
    st.markdown("- Y a-t-il des frais de résiliation ?")
    st.markdown("- Comment fonctionne le roaming ?")
    st.markdown("- Quel est le prix de l'iPhone 16 ?")
    st.markdown("")
    st.markdown("**Questions personnelles:**")
    st.markdown("- Je m'appelle Jean Bertrand. Quelle est ma consommation ?")
    st.markdown("- Je m'appelle Pierre Richard. Ai-je un ticket en cours ?")
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
            response = answer(prompt)
        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
