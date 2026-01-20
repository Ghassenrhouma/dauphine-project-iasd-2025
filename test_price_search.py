from src.vectorstore import get_vectorstore

vs = get_vectorstore()

# Try different search queries
queries = [
    "prix iPhone 256GB",
    "tableau prix iPhone",
    "Modèle 128GB 256GB 512GB",
    "iPhone 15 1099",
]

for query in queries:
    print(f"\n{'='*80}")
    print(f"QUERY: {query}")
    print('='*80)
    results = vs.similarity_search(query, k=3)
    for i, doc in enumerate(results):
        print(f"\n--- Chunk {i+1} ---")
        text = doc.page_content[:500]
        print(text)
        if "1099" in text or "Tableau" in text:
            print(">>> FOUND PRICE TABLE! <<<")
