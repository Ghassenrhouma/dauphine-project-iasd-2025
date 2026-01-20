from src.vectorstore import get_vectorstore
from src.agents import format_docs

vs = get_vectorstore()
results = vs.similarity_search("iPhone 48 Mpx caméra 256GB prix 1200 euros", k=8)

print("="*80)
print("WHAT THE LLM SEES (formatted docs)")
print("="*80)

formatted = format_docs(results)
print(formatted)

print("\n" + "="*80)
print("CHECKING FOR KEY DATA")
print("="*80)
print(f"Contains price table: {'iPhone 15' in formatted and '1099' in formatted}")
print(f"Contains 48 Mpx: {'48 Mpx' in formatted or '48 Mpx' in formatted}")
print(f"Contains 256GB: {'256GB' in formatted}")
