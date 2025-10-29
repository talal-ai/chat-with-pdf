"""Reset Pinecone index and re-upload PDF with HuggingFace embeddings."""
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from pinecone import Pinecone
from app.core.config import settings
from app.services.document_processor import document_processor
from app.services.vector_store import vector_store

def reset_pinecone_index():
    """Delete and recreate Pinecone index with new dimensions."""
    print("=" * 80)
    print("RESETTING PINECONE INDEX FOR HUGGINGFACE EMBEDDINGS")
    print("=" * 80)
    
    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key=settings.pinecone_api_key)
        index_name = settings.pinecone_index_name
        
        # Delete existing index if it exists
        existing_indexes = pc.list_indexes().names()
        if index_name in existing_indexes:
            print(f"\n🗑️  Deleting existing index: {index_name}")
            pc.delete_index(index_name)
            print("✅ Index deleted successfully")
        else:
            print(f"\n ℹ️  No existing index found: {index_name}")
        
        print(f"\n🔨 Creating new index with HuggingFace embeddings (384 dimensions)...")
        from pinecone import ServerlessSpec
        pc.create_index(
            name=index_name,
            dimension=384,  # HuggingFace sentence-transformers/all-MiniLM-L6-v2
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region=settings.pinecone_environment
            )
        )
        print("✅ New index created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting index: {e}")
        import traceback
        traceback.print_exc()
        return False

def upload_pdf():
    """Upload PDF to Pinecone with new embeddings."""
    pdf_path = Path(__file__).parent.parent / "AAOIFI - Shariaa Standards-ENG.pdf"
    
    print(f"\n📄 Looking for PDF at: {pdf_path}")
    
    if not pdf_path.exists():
        print(f"❌ Error: PDF not found at {pdf_path}")
        return False
    
    try:
        print("\n📝 Processing PDF...")
        chunks = document_processor.process_pdf(str(pdf_path))
        print(f"✅ Created {len(chunks)} chunks")
        
        print("\n⬆️  Uploading to Pinecone with HuggingFace embeddings...")
        print("   (This may take a few minutes...)")
        ids = vector_store.add_documents(chunks)
        print(f"✅ Uploaded {len(ids)} documents successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will DELETE your existing Pinecone index and recreate it!")
    print("   All existing embeddings will be lost.")
    
    response = input("\nDo you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n❌ Operation cancelled.")
        sys.exit(0)
    
    # Reset index
    if not reset_pinecone_index():
        print("\n❌ Failed to reset index. Exiting.")
        sys.exit(1)
    
    # Wait a moment for index to be ready
    print("\n⏳ Waiting for index to be ready...")
    import time
    time.sleep(10)
    
    # Upload PDF
    if not upload_pdf():
        print("\n❌ Failed to upload PDF. Exiting.")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS! Your chatbot is now using FREE HuggingFace embeddings!")
    print("=" * 80)
    print("\n🚀 You can now:")
    print("   1. Restart your backend server (it will auto-reload)")
    print("   2. Test your chatbot at http://localhost:3000")
    print("\n💡 Benefits:")
    print("   - 100% FREE - no OpenAI API key needed for embeddings")
    print("   - Still using Groq for LLM (text generation)")
    print("   - Good quality embeddings from sentence-transformers")
