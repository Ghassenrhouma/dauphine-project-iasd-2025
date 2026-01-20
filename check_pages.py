from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader('data/pdfs/FAQ_Catalogue_Telephones.pdf')
docs = loader.load()

for i, d in enumerate(docs):
    has_iphone16 = 'iPhone 16' in d.page_content
    has_22h = '22h' in d.page_content
    print(f'Page {i}: iPhone 16={has_iphone16}, 22h={has_22h}')
    if has_iphone16:
        # Find where iPhone 16 appears
        idx = d.page_content.find('iPhone 16')
        print(f'  iPhone 16 context: {d.page_content[idx:idx+200]}')
