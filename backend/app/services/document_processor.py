"""Document processor for PDF chunking."""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain.schema import Document
from typing import List, Dict, Any
from pathlib import Path
import logging
from app.core.config import settings
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing PDF documents."""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". "],
        )

    def process_pdf(self, file_path: str) -> List[Document]:
        """Load and chunk PDF file."""
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
        for i, doc in enumerate(docs):
            if "page" not in doc.metadata:
                doc.metadata["page"] = i + 1
            doc.metadata["source"] = Path(file_path).name
        return self.text_splitter.split_documents(docs)

    def process_text(self, file_path: str) -> List[Document]:
        """Load and chunk text file."""
        loader = TextLoader(file_path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["page"] = 1
            doc.metadata["source"] = Path(file_path).name
        return self.text_splitter.split_documents(docs)


document_processor = DocumentProcessor()


def process_and_upload_document(file_path: str) -> Dict[str, Any]:
    """
    Process a document and upload it to the vector store.

    Args:
        file_path: Path to the document file

    Returns:
        Dictionary with processing results

    Raises:
        ValueError: If file type is not supported
        Exception: If processing or upload fails
    """
    file_path_obj = Path(file_path)
    file_ext = file_path_obj.suffix.lower()

    # Determine file type and process accordingly
    if file_ext == ".pdf":
        docs = document_processor.process_pdf(file_path)
    elif file_ext in [".txt", ".md"]:
        docs = document_processor.process_text(file_path)
    elif file_ext in [".doc", ".docx"]:
        # For now, treat as text (you may want to add python-docx for proper parsing)
        logger.warning(
            "DOC/DOCX files treated as text. Consider adding python-docx for better parsing."
        )
        try:
            docs = document_processor.process_text(file_path)
        except Exception as e:
            raise ValueError(f"Failed to process DOC/DOCX file: {str(e)}")
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

    if not docs:
        raise ValueError("No content extracted from document")

    # Add documents to vector store
    try:
        texts = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]

        vector_store.add_texts(texts, metadatas=metadatas)

        logger.info("Successfully indexed document", file=file_path_obj.name, chunks=len(docs))

        return {
            "success": True,
            "filename": file_path_obj.name,
            "chunks": len(docs),
            "file_type": file_ext,
        }
    except Exception as e:
        logger.error(
            "Failed to upload document to vector store", file=file_path_obj.name, error=str(e)
        )
        raise Exception(f"Failed to index document: {str(e)}")
