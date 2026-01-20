from src.vectorstore import get_vectorstore

vs = get_vectorstore()

print("="*80)
print("TESTING VECTORSTORE RETRIEVAL")
print("="*80)

# Test battery query
print("\n1. Battery comparison query:")
results = vs.similarity_search("autonomie batterie iPhone 13 iPhone 16 différence", k=5)
for i, doc in enumerate(results):
    print(f"\n--- Chunk {i+1} ---")
    print(doc.page_content[:400])

# Test price query  
print("\n\n2. iPhone price and camera query:")
results2 = vs.similarity_search("iPhone 48 Mpx caméra 256GB prix 1200 euros", k=5)
for i, doc in enumerate(results2):
    print(f"\n--- Chunk {i+1} ---")
    print(doc.page_content[:400])

# Test direct model query
print("\n\n3. Direct iPhone 13/16 query:")
results3 = vs.similarity_search("iPhone 13 iPhone 16 caractéristiques", k=5)
for i, doc in enumerate(results3):
    print(f"\n--- Chunk {i+1} ---")
    print(doc.page_content[:400])
