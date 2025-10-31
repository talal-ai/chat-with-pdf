"""Vector store service for Pinecone integration."""

from __future__ import annotations
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain.schema import Document
from typing import List, Optional, TYPE_CHECKING
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class VectorStoreService:
    """Service for managing vector store operations with lazy initialization."""

    def __init__(self):
        self._embeddings: Optional["HuggingFaceEmbeddings"] = None
        self._pinecone_client: Optional["Pinecone"] = None
        self._index = None
        self._vectorstore: Optional["PineconeVectorStore"] = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization of Pinecone client and vector store."""
        if self._initialized:
            return

        try:
            logger.info("Initializing vector store service")

            # Validate required settings
            if not settings.pinecone_api_key:
                raise ValueError("PINECONE_API_KEY is not set. Please configure it in .env")

            # Initialize HuggingFace embeddings (free, no API key needed)
            logger.info(
                "Initializing HuggingFace embeddings",
                model="sentence-transformers/all-MiniLM-L6-v2",
            )
            self._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
                cache_folder=".cache/huggingface",  # Cache model locally for faster subsequent loads
            )
            logger.info("✓ HuggingFace embeddings loaded")

            # Initialize Pinecone client
            self._pinecone_client = Pinecone(api_key=settings.pinecone_api_key)

            # Initialize index
            self._initialize_index()

            self._initialized = True
            logger.info("Vector store service initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize vector store service", error=str(e))
            raise RuntimeError(
                f"Vector store initialization failed: {str(e)}. "
                "Please check your Pinecone API key and network connection."
            ) from e

    def _initialize_index(self):
        """Initialize or connect to Pinecone index."""
        if self._pinecone_client is None:
            raise RuntimeError("Pinecone client not initialized")

        index_name = settings.pinecone_index_name

        # List existing indexes (handle different return shapes across SDK versions)
        existing_indexes_raw = self._pinecone_client.list_indexes()
        existing_names = []
        try:
            if isinstance(existing_indexes_raw, list):
                existing_names = existing_indexes_raw
            elif hasattr(existing_indexes_raw, "names"):
                existing_names = existing_indexes_raw.names()
            else:
                # Attempt to coerce iterable to list of names
                existing_names = list(existing_indexes_raw)
        except Exception:
            logger.warning(
                "Could not parse existing indexes response from Pinecone client; assuming none exist"
            )
            existing_names = []

        if index_name not in existing_names:
            logger.info("Creating new Pinecone index", index_name=index_name)
            # Use configured embedding dimension (kept in sync with embedding model)
            dimension = int(getattr(settings, "embedding_dimension", 384))

            # Parse region from environment (e.g., "us-west1-gcp" -> cloud="gcp", region="us-west1")
            env = settings.pinecone_environment
            if "gcp" in env.lower():
                cloud = "gcp"
                region = env.lower().replace("-gcp", "")
            elif "aws" in env.lower():
                cloud = "aws"
                region = env.lower().replace("-aws", "")
            elif "azure" in env.lower():
                cloud = "azure"
                region = env.lower().replace("-azure", "")
            else:
                # Default to AWS if format unclear
                cloud = "aws"
                region = "us-east-1"
                logger.warning(
                    f"Could not parse cloud provider from '{env}', defaulting to AWS us-east-1"
                )

            if self._pinecone_client is None:
                raise RuntimeError("Pinecone client not initialized")

            try:
                self._pinecone_client.create_index(
                    name=index_name,
                    dimension=dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud=cloud, region=region),
                )
            except Exception as e:
                logger.warning(
                    "Failed to create index with ServerlessSpec, trying simpler create_index signature",
                    error=str(e),
                )
                # Fallback attempt without ServerlessSpec (some SDK versions differ)
                # Note: Some Pinecone SDK versions require spec parameter
                try:
                    self._pinecone_client.create_index(
                        name=index_name,
                        dimension=dimension,
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                    )
                except Exception as e2:
                    logger.error("Failed to create Pinecone index", error=str(e2))
                    raise
        else:
            logger.info("Using existing Pinecone index", index_name=index_name)

        if self._pinecone_client is None:
            raise RuntimeError("Pinecone client not initialized")
        self._index = self._pinecone_client.Index(index_name)
        self._vectorstore = PineconeVectorStore(
            index=self._index, embedding=self._embeddings, text_key="text"
        )

    @property
    def vectorstore(self) -> PineconeVectorStore:
        """Get the vector store instance, initializing if needed."""
        self._ensure_initialized()
        if self._vectorstore is None:
            raise RuntimeError("Vector store failed to initialize")
        return self._vectorstore

    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        self._ensure_initialized()
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized")
        return self._vectorstore.add_documents(documents)

    def add_texts(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> List[str]:
        """Add texts directly to the vector store.

        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dicts for each text

        Returns:
            List of document IDs
        """
        self._ensure_initialized()
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized")
        # Some versions of PineconeVectorStore implement `add_texts`, others may not.
        try:
            add_texts_fn = getattr(self._vectorstore, "add_texts", None)
            if callable(add_texts_fn):
                result = add_texts_fn(texts, metadatas=metadatas)
                return result if isinstance(result, list) else []
        except Exception:
            logger.warning(
                "vectorstore.add_texts failed; falling back to constructing Documents and using add_documents"
            )

        # Fallback: convert texts + metadatas to Document objects and use add_documents
        docs: List[Document] = []
        for i, t in enumerate(texts):
            meta = metadatas[i] if metadatas and i < len(metadatas) else {}
            docs.append(Document(page_content=t, metadata=meta))

        return self.add_documents(docs)

    def similarity_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """Search for similar documents."""
        self._ensure_initialized()
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized")
        k_val = k if k is not None else min(settings.top_k_retrieval, 8)
        return self._vectorstore.similarity_search(query, k=k_val)

    def similarity_search_with_score(self, query: str, k: Optional[int] = None) -> List[tuple]:
        """Search for similar documents with relevance scores."""
        self._ensure_initialized()
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized")
        k_val = k if k is not None else min(settings.top_k_retrieval, 8)
        return self._vectorstore.similarity_search_with_score(query, k=k_val)

    def as_retriever(self, **kwargs):
        """Get a retriever instance."""
        self._ensure_initialized()
        if self._vectorstore is None:
            raise RuntimeError("Vector store not initialized")
        return self._vectorstore.as_retriever(**kwargs)

    def is_initialized(self) -> bool:
        """Check if the service is initialized."""
        return self._initialized

    def is_available(self) -> bool:
        """Check if vector store is available without raising exceptions."""
        try:
            self._ensure_initialized()
            return True
        except Exception:
            return False


vector_store = VectorStoreService()
