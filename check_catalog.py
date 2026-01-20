from langchain_community.document_loaders import PyPDFLoader
import os

pdf_dir = 'data/pdfs'
for f in os.listdir(pdf_dir):
    if 'Catalogue' in f or 'Telephone' in f:
        print(f'\n{"="*80}')
        print(f'FILE: {f}')
        print("="*80)
        loader = PyPDFLoader(os.path.join(pdf_dir, f))
        docs = loader.load()
        
        full_text = "\n".join([doc.page_content for doc in docs])
        
        # Check for battery/autonomy mentions
        if 'autonomie' in full_text.lower() or 'batterie' in full_text.lower():
            print("\n[BATTERY DATA FOUND]")
            for doc in docs:
                if 'autonomie' in doc.page_content.lower() or 'batterie' in doc.page_content.lower():
                    print(doc.page_content[:600])
                    print("...")
        
        # Check for specific iPhone models
        print("\n[IPHONE MODELS FOUND]")
        for model in ['iPhone X', 'iPhone 11', 'iPhone 12', 'iPhone 13', 'iPhone 14', 'iPhone 15', 'iPhone 16', 'iPhone 17']:
            if model in full_text:
                print(f"  ✓ {model}")
                # Find context around this model
                for doc in docs:
                    if model in doc.page_content:
                        start = doc.page_content.find(model)
                        print(f"    Context: {doc.page_content[max(0,start-50):start+200]}")
                        break
