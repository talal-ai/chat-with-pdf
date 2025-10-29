"""Vector store service for Pinecone integration."""
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from pinecone import Pinecone, ServerlessSpec
from langchain.schema import Document
from typing import List, Optional
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class VectorStoreService:
    """Service for managing vector store operations with lazy initialization."""
    
    def __init__(self):
        self._embeddings: Optional[HuggingFaceEmbeddings] = None
        self._pinecone_client: Optional[Pinecone] = None
        self._index = None
        self._vectorstore: Optional[PineconeVectorStore] = None
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
            logger.info("Initializing HuggingFace embeddings")
            self._embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
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
        index_name = settings.pinecone_index_name
        if index_name not in self._pinecone_client.list_indexes().names():
            logger.info("Creating new Pinecone index", index_name=index_name)
            # HuggingFace model dimension is 384
            self._pinecone_client.create_index(
                name=index_name,
                dimension=384,  # sentence-transformers/all-MiniLM-L6-v2 dimension
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=settings.pinecone_environment)
            )
        else:
            logger.info("Using existing Pinecone index", index_name=index_name)
        
        self._index = self._pinecone_client.Index(index_name)
        self._vectorstore = PineconeVectorStore(
            index=self._index,
            embedding=self._embeddings,
            text_key="text"
        )
    
    @property
    def vectorstore(self) -> PineconeVectorStore:
        """Get the vector store instance, initializing if needed."""
        self._ensure_initialized()
        return self._vectorstore
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to the vector store."""
        self._ensure_initialized()
        return self._vectorstore.add_documents(documents)
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """Search for similar documents."""
        self._ensure_initialized()
        k = k or min(settings.top_k_retrieval, 8)  # Cap at 8 for faster retrieval
        return self._vectorstore.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, query: str, k: int = None) -> List[tuple]:
        """Search for similar documents with relevance scores."""
        self._ensure_initialized()
        k = k or min(settings.top_k_retrieval, 8)  # Cap at 8 for faster retrieval
        return self._vectorstore.similarity_search_with_score(query, k=k)
    
    def as_retriever(self, **kwargs):
        """Get a retriever instance."""
        self._ensure_initialized()
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