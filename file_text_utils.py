import os
import tempfile
import docx2txt
import PyPDF2

def extract_text_from_file(file_storage):
    filename = file_storage.filename.lower()
    temp_path = None
    text = ""
    try:
        # Save file to temp
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            temp_path = tmp.name
            file_storage.save(temp_path)

        if filename.endswith('.pdf'):
            with open(temp_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join(page.extract_text() or '' for page in reader.pages)
        elif filename.endswith('.docx'):
            text = docx2txt.process(temp_path)
        elif filename.endswith('.txt'):
            with open(temp_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = ""
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
    return text.strip()
