"""Persistent vector memory per user using ChromaDB."""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from datetime import datetime
import structlog
from config.settings import settings


logger = structlog.get_logger()


class UserMemoryManager:
    """
    Manages persistent vector memory per user.
    
    Stores conversation history, intents, and outcomes for context-aware decisions.
    """
    
    def __init__(self):
        self.client: Optional[chromadb.ClientAPI] = None
        self.collections: Dict[str, chromadb.Collection] = {}
    
    def connect(self):
        """Initialize ChromaDB client."""
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        logger.info("Connected to ChromaDB for memory management")
    
    def get_collection(self, user_id: str) -> chromadb.Collection:
        """Get or create a collection for a user."""
        if user_id not in self.collections:
            collection_name = f"user_memory_{user_id}"
            try:
                self.collections[user_id] = self.client.get_collection(collection_name)
            except:
                self.collections[user_id] = self.client.create_collection(
                    name=collection_name,
                    metadata={"user_id": user_id, "created_at": datetime.utcnow().isoformat()}
                )
                logger.info(f"Created memory collection for user {user_id}")
        
        return self.collections[user_id]
    
    def add_interaction(self, user_id: str, message: str, intent: str, outcome: str, metadata: Optional[Dict] = None):
        """
        Store an interaction in user's memory.
        
        Args:
            user_id: User identifier
            message: Original user message
            intent: Extracted intent
            outcome: Result of the action
            metadata: Additional metadata (e.g., execution_id, timestamp)
        """
        collection = self.get_collection(user_id)
        
        doc_text = f"Message: {message}\nIntent: {intent}\nOutcome: {outcome}"
        if metadata:
            doc_text += f"\nMetadata: {metadata}"
        
        collection.add(
            documents=[doc_text],
            ids=[f"interaction_{datetime.utcnow().timestamp()}"],
            metadatas=[{
                "type": "interaction",
                "timestamp": datetime.utcnow().isoformat(),
                "intent": intent,
                **(metadata or {})
            }]
        )
    
    def search_relevant_memory(self, user_id: str, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for relevant past interactions.
        
        Returns:
            List of relevant interactions with similarity scores
        """
        collection = self.get_collection(user_id)
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        interactions = []
        if results["documents"] and len(results["documents"][0]) > 0:
            for i, doc in enumerate(results["documents"][0]):
                interactions.append({
                    "document": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None
                })
        
        return interactions
    
    def get_recent_interactions(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get most recent interactions for a user."""
        collection = self.get_collection(user_id)
        
        # Get all documents (ChromaDB doesn't have native ordering, so we'll use metadata)
        # In production, you'd want to maintain a separate ordered index
        all_results = collection.get()
        
        # Sort by timestamp if available
        interactions = []
        for i, doc in enumerate(all_results["documents"]):
            metadata = all_results["metadatas"][i] if all_results["metadatas"] else {}
            interactions.append({
                "document": doc,
                "metadata": metadata,
                "id": all_results["ids"][i]
            })
        
        # Sort by timestamp descending
        interactions.sort(
            key=lambda x: x["metadata"].get("timestamp", ""),
            reverse=True
        )
        
        return interactions[:limit]


# Global memory manager instance
memory_manager = UserMemoryManager()

