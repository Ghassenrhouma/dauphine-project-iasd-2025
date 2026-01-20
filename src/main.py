"""Main module for the TelecomPlus multi-agent support system."""

from src.agents import orchestrate


def answer(question: str, client_id: str = None) -> str:
    """Answer customer questions using multi-agent orchestration.
    
    This function routes questions to the appropriate agent:
    - FAQ questions → RAG agent (searches PDF documents)
    - Data questions → Data agent (queries Excel databases)
    
    Args:
        question: Customer question in French
        client_id: Optional client ID for personalized queries
    
    Returns:
        Answer string from the orchestrated agent system
    """
    return orchestrate(question, client_id)
