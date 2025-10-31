"""
Pre-download embeddings model for faster startup.
Run this once after installation to cache the model locally.
"""

import os
from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings


def download_embeddings_model():
    """Download and cache the embeddings model."""
    print("=" * 70)
    print(" 📥 Downloading Embeddings Model")
    print("=" * 70)
    print()
    print("This will download the sentence-transformers model (~80MB)")
    print("Future startups will be much faster!")
    print()

    # Create cache directory
    cache_dir = Path(".cache/huggingface")
    cache_dir.mkdir(parents=True, exist_ok=True)

    print("📦 Downloading model: sentence-transformers/all-MiniLM-L6-v2")
    print("This may take 1-2 minutes on first run...")
    print()

    try:
        # Initialize embeddings (this will download and cache the model)
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
            cache_folder=str(cache_dir),
        )

        # Test the embeddings
        print("🧪 Testing embeddings...")
        test_embedding = embeddings.embed_query("Test query")
        print(f"✅ Embeddings working! Dimension: {len(test_embedding)}")
        print()
        print("=" * 70)
        print(" ✨ Model cached successfully!")
        print("=" * 70)
        print(f" Cache location: {cache_dir.absolute()}")
        print(" Next startup will be much faster!")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        return False

    return True


if __name__ == "__main__":
    import sys

    try:
        success = download_embeddings_model()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Download cancelled by user")
        sys.exit(1)
