from src.vectorstore import get_vectorstore

vs = get_vectorstore()
all_docs = vs.get()
contents = all_docs['documents']

print("Chunks with A18 (iPhone 16):")
for i, c in enumerate(contents):
    if 'A18' in c:
        has_iphone16 = 'iPhone 16' in c
        has_22h = '22h' in c
        print(f"Chunk {i}: iPhone 16={has_iphone16}, 22h={has_22h}")
        if has_iphone16 or has_22h:
            print(f"  Content preview: {c[:200]}...")
            print()
