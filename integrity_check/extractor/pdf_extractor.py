"""
PDF/DOCX/HTML → 纯文本 + 元数据
"""
import fitz
from pathlib import Path
from .metadata_extractor import extract_metadata


def parse_pdf(filepath: str):
    """解析文件，返回 DocumentContext"""
    from detectors.base import DocumentContext

    path = Path(filepath)
    text = ""

    if path.suffix.lower() == '.pdf':
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text()
        doc.close()
    elif path.suffix.lower() == '.docx':
        from docx import Document
        doc = Document(filepath)
        text = '\n'.join(p.text for p in doc.paragraphs)
    elif path.suffix.lower() == '.html':
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
        text = soup.get_text()
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

    context = DocumentContext(text=text)

    # 3.1 投稿元数据提取
    context.metadata = extract_metadata(text)

    return context