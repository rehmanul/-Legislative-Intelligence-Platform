"""
Document Parser Utilities
Extracts text and metadata from various document formats
"""

from typing import Dict, Any, Optional
from pathlib import Path
import re


class DocumentParser:
    """
    Parses documents and extracts text and metadata
    """
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.docx']
    
    def parse(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Parse a document and extract text and metadata
        
        Args:
            file_path: Path to document file
            file_type: File extension (pdf, txt, docx)
            
        Returns:
            Dict with text, metadata, and sections
        """
        file_path_obj = Path(file_path)
        
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_type == 'pdf':
            return self._parse_pdf(file_path)
        elif file_type == 'txt':
            return self._parse_text(file_path)
        elif file_type == 'docx':
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Parse PDF file
        """
        try:
            # Try pdfplumber first (better for tables)
            import pdfplumber
            
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            full_text = "\n\n".join(text_parts)
            
        except ImportError:
            # Fallback to PyPDF2
            try:
                import PyPDF2
                
                text_parts = []
                with open(file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)
                
                full_text = "\n\n".join(text_parts)
            except ImportError:
                # If neither library available, return placeholder
                full_text = f"[PDF file: {Path(file_path).name} - PDF parsing libraries not installed]"
        
        return self._extract_metadata(full_text, file_path)
    
    def _parse_text(self, file_path: str) -> Dict[str, Any]:
        """
        Parse plain text file
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            full_text = f.read()
        
        return self._extract_metadata(full_text, file_path)
    
    def _parse_docx(self, file_path: str) -> Dict[str, Any]:
        """
        Parse DOCX file
        """
        try:
            from docx import Document
            
            doc = Document(file_path)
            text_parts = [paragraph.text for paragraph in doc.paragraphs]
            full_text = "\n".join(text_parts)
            
        except ImportError:
            full_text = f"[DOCX file: {Path(file_path).name} - python-docx not installed]"
        
        return self._extract_metadata(full_text, file_path)
    
    def _extract_metadata(self, text: str, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from document text
        """
        metadata = {
            "file_name": Path(file_path).name,
            "text_length": len(text),
            "word_count": len(text.split()),
        }
        
        # Try to extract filing date
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # MM/DD/YYYY
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text[:5000], re.IGNORECASE)  # Search first 5000 chars
            if match:
                metadata["filing_date"] = match.group(0)
                break
        
        # Try to extract company name (common in SEC filings)
        company_patterns = [
            r'Company Name[:\s]+([A-Z][A-Za-z\s&,\.]+)',
            r'Registrant[:\s]+([A-Z][A-Za-z\s&,\.]+)',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text[:5000], re.IGNORECASE)
            if match:
                metadata["company_name"] = match.group(1).strip()
                break
        
        # Extract sections (for SEC filings)
        sections = self._extract_sections(text)
        
        return {
            "text": text,
            "metadata": metadata,
            "sections": sections
        }
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract sections from SEC filing format
        """
        sections = {}
        
        # Common SEC filing sections
        section_patterns = {
            "Item 1": r'ITEM\s+1[\.\s]+([^\n]+(?:\n(?!ITEM\s+[2-9])[^\n]+)*)',
            "Item 7": r'ITEM\s+7[\.\s]+([^\n]+(?:\n(?!ITEM\s+[8-9])[^\n]+)*)',
            "Risk Factors": r'RISK\s+FACTORS[\.\s]*([^\n]+(?:\n(?!ITEM\s+)[^\n]+)*)',
        }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group(1)[:5000]  # Limit section size
        
        return sections
