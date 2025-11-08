"""Vector database service using ChromaDB with Ollama nomic-embed-text embeddings."""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import logging
import requests
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB vector store with Ollama embeddings."""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        ollama_url: str = "http://localhost:11434"
    ):
        """
        Initialize vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            ollama_url: Ollama API URL
        """
        self.ollama_url = ollama_url
        self.embedding_model = "nomic-embed-text"
        
        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        logger.info(f"📦 Initialized ChromaDB at {persist_directory}")
        logger.info(f"🧠 Using Ollama embeddings: {self.embedding_model}")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector from Ollama.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            embedding = data.get('embedding', [])
            
            if not embedding:
                raise ValueError("Empty embedding returned")
            
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Embedding failed: {e}")
            raise RuntimeError(f"Failed to get embedding: {e}")
    
    def create_collection(
        self,
        name: str,
        metadata: Optional[Dict] = None
    ) -> chromadb.Collection:
        """
        Create or get a collection.
        
        Args:
            name: Collection name
            metadata: Optional collection metadata
            
        Returns:
            ChromaDB collection
        """
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection(name)
                logger.info(f"🗑️  Deleted existing collection: {name}")
            except:
                pass
            
            # Ensure metadata is not None or empty
            collection_metadata = metadata if metadata else {"created": "true"}
            
            collection = self.client.create_collection(
                name=name,
                metadata=collection_metadata
            )
            
            logger.info(f"✅ Created collection: {name}")
            return collection
            
        except Exception as e:
            logger.error(f"❌ Collection creation failed: {e}")
            raise
    
    def add_documents(
        self,
        collection_name: str,
        chunks: List[Dict],
        document_metadata: Optional[Dict] = None
    ):
        """
        Add document chunks to collection with embeddings.
        
        Args:
            collection_name: Name of collection
            chunks: List of chunk dicts with 'chunk_id', 'text'
            document_metadata: Optional metadata for all chunks
        """
        try:
            collection = self.client.get_collection(collection_name)
        except:
            collection = self.create_collection(collection_name)
        
        logger.info(f"📥 Adding {len(chunks)} chunks to collection '{collection_name}'")
        
        # Prepare data for batch insertion
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            logger.debug(f"  Embedding chunk {i+1}/{len(chunks)}...")
            embedding = self.get_embedding(chunk['text'])
            
            # Prepare metadata
            metadata = {
                'chunk_id': chunk['chunk_id'],
                'length': chunk['length'],
                'start': chunk['start'],
                'end': chunk['end']
            }
            if document_metadata:
                metadata.update(document_metadata)
            
            ids.append(f"chunk_{chunk['chunk_id']}")
            embeddings.append(embedding)
            documents.append(chunk['text'])
            metadatas.append(metadata)
        
        # Add to collection in batches
        batch_size = 10
        for i in range(0, len(ids), batch_size):
            batch_end = min(i + batch_size, len(ids))
            
            collection.add(
                ids=ids[i:batch_end],
                embeddings=embeddings[i:batch_end],
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )
            
            logger.debug(f"  ✓ Added batch {i//batch_size + 1}/{(len(ids)-1)//batch_size + 1}")
        
        logger.info(f"✅ Added {len(chunks)} chunks to '{collection_name}'")
    
    def search_similar(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5
    ) -> Dict:
        """
        Search for similar chunks using semantic search.
        
        Args:
            collection_name: Name of collection to search
            query: Search query
            n_results: Number of results to return
            
        Returns:
            Dict with 'chunks', 'distances', 'metadatas'
        """
        try:
            collection = self.client.get_collection(collection_name)
        except:
            logger.error(f"❌ Collection '{collection_name}' not found")
            return {'chunks': [], 'distances': [], 'metadatas': []}
        
        logger.info(f"🔍 Searching for: '{query[:50]}...'")
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        chunks = results['documents'][0] if results['documents'] else []
        distances = results['distances'][0] if results['distances'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        
        logger.info(f"✅ Found {len(chunks)} results")
        
        return {
            'chunks': chunks,
            'distances': distances,
            'metadatas': metadatas
        }
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """
        Get statistics about a collection.
        
        Args:
            collection_name: Collection name
            
        Returns:
            Dict with collection statistics
        """
        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()
            
            return {
                'name': collection_name,
                'count': count,
                'exists': True
            }
        except:
            return {
                'name': collection_name,
                'count': 0,
                'exists': False
            }
    
    def list_collections(self) -> List[str]:
        """
        List all collection names.
        
        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        names = [col.name for col in collections]
        logger.info(f"📚 Found {len(names)} collections")
        return names
    
    def delete_collection(self, collection_name: str):
        """Delete a collection."""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"🗑️  Deleted collection: {collection_name}")
        except Exception as e:
            logger.error(f"❌ Failed to delete collection: {e}")
            raise


# Global vector store instances keyed by persist_directory
_vector_stores: Dict[str, VectorStore] = {}


def get_vector_store(
    persist_directory: str = "./chroma_db",
    ollama_url: str = "http://localhost:11434"
) -> VectorStore:
    """
    Get or create vector store instance for the given persist directory.
    
    Args:
        persist_directory: ChromaDB persist directory
        ollama_url: Ollama API URL
        
    Returns:
        VectorStore instance
    """
    global _vector_stores
    
    # Normalize path
    persist_dir_key = str(Path(persist_directory).resolve())
    
    if persist_dir_key not in _vector_stores:
        _vector_stores[persist_dir_key] = VectorStore(persist_directory, ollama_url)
        logger.info(f"📦 Created new VectorStore instance for {persist_dir_key}")
    
    return _vector_stores[persist_dir_key]
