"""
Resume parser module for extracting text from PDF and DOCX files
"""

import PyPDF2
from docx import Document
from typing import Optional, Tuple
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc_file = io.BytesIO(file_bytes)
        doc = Document(doc_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting DOCX text: {str(e)}")


def extract_text(file_bytes: bytes, filename: str) -> Tuple[bool, str, Optional[str]]:
    """
    Extract text from resume file based on extension
    Returns: (success, message, extracted_text)
    """
    try:
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            text = extract_text_from_pdf(file_bytes)
        elif filename_lower.endswith('.docx') or filename_lower.endswith('.doc'):
            text = extract_text_from_docx(file_bytes)
        else:
            return False, "Unsupported file format. Please upload PDF or DOCX files.", None
        
        if not text or len(text.strip()) < 50:
            return False, "Could not extract sufficient text from the file. Please ensure the resume contains readable text.", None
        
        return True, "Text extracted successfully", text
    
    except Exception as e:
        return False, f"Error processing file: {str(e)}", None


def validate_file_size(file_bytes: bytes, max_size_mb: int = 10) -> Tuple[bool, str]:
    """
    Validate file size
    Returns: (is_valid, message)
    """
    file_size_mb = len(file_bytes) / (1024 * 1024)
    
    if file_size_mb > max_size_mb:
        return False, f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
    
    return True, "File size is valid"


def validate_file_extension(filename: str, allowed_extensions: set) -> Tuple[bool, str]:
    """
    Validate file extension
    Returns: (is_valid, message)
    """
    filename_lower = filename.lower()
    
    for ext in allowed_extensions:
        if filename_lower.endswith(f'.{ext}'):
            return True, "Valid file type"
    
    return False, f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
