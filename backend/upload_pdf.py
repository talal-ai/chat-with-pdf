"""Script to upload PDF to Pinecone."""
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.services.document_processor import document_processor
from app.services.vector_store import vector_store

def upload_pdf(pdf_path: str):
    """Process and upload PDF to Pinecone."""
    try:
        print(f"Processing PDF: {pdf_path}")
        chunks = document_processor.process_pdf(pdf_path)
        print(f"Created {len(chunks)} chunks")
        
        print("Uploading to Pinecone...")
        ids = vector_store.add_documents(chunks)
        print(f"Uploaded {len(ids)} documents successfully!")
        return True
    except Exception as e:
        print(f"Error during upload: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Get the path to the AAOIFI PDF in the parent directory
    pdf_path = Path(__file__).parent.parent / "AAOIFI - Shariaa Standards-ENG.pdf"
    
    print(f"Looking for PDF at: {pdf_path}")
    
    if not pdf_path.exists():
        print(f"Error: PDF not found at {pdf_path}")
        print("Please make sure the PDF file exists in the project root directory.")
        exit(1)
    
    success = upload_pdf(str(pdf_path))
    if success:
        print("\n✅ PDF uploaded successfully!")
    else:
        print("\n❌ PDF upload failed!")
        exit(1)
