from src.vectorstore import get_vectorstore

vs = get_vectorstore()
results = vs.similarity_search('iPhone 13 iPhone 16 autonomie batterie', k=10)

print("Retrieved chunks for battery comparison:")
for i, r in enumerate(results):
    has_13 = 'iPhone 13' in r.page_content
    has_16 = 'iPhone 16' in r.page_content
    has_19h = '19h' in r.page_content
    has_22h = '22h' in r.page_content
    print(f"Chunk {i}: iPhone 13={has_13}, iPhone 16={has_16}, 19h={has_19h}, 22h={has_22h}")
    if has_16 and has_22h:
        print(f"  FOUND! Content preview: ...{r.page_content[r.page_content.find('iPhone 16'):r.page_content.find('iPhone 16')+300]}...")
