import PyPDF2
from io import BytesIO

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text content from a given PDF file's bytes.
    
    Args:
        file_bytes (bytes): The raw bytes of the uploaded PDF file.
        
    Returns:
        str: The extracted text from all pages, or an error message if extraction fails.
    """
    try:
        pdf_file_obj = BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
        
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
                
        if not extracted_text.strip():
            return "Error: Could not extract visible text. The PDF might be image-based or empty."
            
        return extracted_text.strip()
        
    except Exception as e:
        return f"Error: Failed to parse PDF document. Details: {str(e)}"