"""
File parser service - extracts text from PDF/DOCX files.
"""
from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument


class FileParser:
    """Parse PDF and DOCX files, extract all text."""
    
    def parse_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        text_parts = []
        reader = PdfReader(str(file_path))
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    
    def parse_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        doc = DocxDocument(str(file_path))
        text_parts = []
        
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
        
        # Also extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:
                    text_parts.append(" | ".join(row_text))
        
        return "\n\n".join(text_parts)
    
    def parse_file(self, file_path: Path) -> str:
        """Parse file based on extension."""
        suffix = file_path.suffix.lower()
        
        if suffix == ".pdf":
            return self.parse_pdf(file_path)
        elif suffix in [".docx", ".doc"]:
            return self.parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")


def get_parser() -> FileParser:
    """Get FileParser instance."""
    return FileParser()
