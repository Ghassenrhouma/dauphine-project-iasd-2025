from pypdf import PdfReader
import re

pdf = PdfReader('data/pdfs/FAQ_Catalogue_Telephones.pdf')
text = ''.join([p.extract_text() for p in pdf.pages])

for model in ['iPhone 13', 'iPhone 14', 'iPhone 15', 'iPhone 16', 'iPhone 17']:
    # Find the description section for this model
    pattern = rf'{model}\s*Ce modèle'
    match = re.search(pattern, text)
    if match:
        chunk = text[match.start():match.start()+800]
        battery = re.search(r'(\d+)h de lecture vidéo', chunk)
        if battery:
            print(f'{model}: {battery.group(1)}h')
        else:
            print(f'{model}: battery not found in description')
    else:
        print(f'{model}: description not found')
