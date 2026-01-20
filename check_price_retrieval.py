from src.vectorstore import get_vectorstore

vs = get_vectorstore()

# Search for price-related content
results = vs.similarity_search("iPhone 15 iPhone 16 prix 256GB 1200 euros", k=8)

print("="*80)
print("SEARCHING FOR PRICE TABLE IN 8 CHUNKS")
print("="*80)

has_price_table = False
for i, doc in enumerate(results):
    content = doc.page_content
    # Check if this chunk has price information
    if '€' in content or 'prix' in content.lower():
        print(f"\n--- Chunk {i+1} (HAS PRICES) ---")
        print(content[:600])
        if 'iPhone 15' in content and '1099' in content:
            has_price_table = True
            print(">>> FOUND PRICE TABLE! <<<")
    else:
        print(f"\n--- Chunk {i+1} (no prices) ---")
        print(content[:200] + "...")

print(f"\n\nPrice table retrieved: {has_price_table}")
