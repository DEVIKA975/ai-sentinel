
import os
from typing import List, Dict, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

class SentinelVectorStore:
    """Manages the local FAISS vector database for AI Sentinel"""
    
    def __init__(self, index_path: str = "data/faiss_index"):
        self.index_path = index_path
        # Initialize the embedding model (all-MiniLM-L6-v2 is lightweight and effective)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_db = self._load_or_create_index()

    def _load_or_create_index(self):
        """Loads an existing FAISS index or creates a new one if it doesn't exist"""
        if os.path.exists(self.index_path):
            try:
                print(f"📁 Loading existing Vector DB from {self.index_path}")
                return FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                print(f"⚠️ Error loading Vector DB: {str(e)}. Creating new one.")
        
        # Create a tiny initial index to avoid empty index errors
        print("✨ Creating new Vector DB index")
        initial_doc = Document(page_content="AI Sentinel System Initialization", metadata={"source": "system"})
        return FAISS.from_documents([initial_doc], self.embeddings)

    def add_log_entries(self, results: List[Dict[str, Any]]):
        """Converts analysis results into documents and adds them to the vector store"""
        if not results:
            return

        documents = []
        for res in results:
            log = res.get("log_entry", {})
            # Construct a rich text representation for embedding
            content = f"""
            User: {log.get('user_id')}
            Department: {log.get('department')}
            URL: {log.get('request_url')}
            Risk: {res.get('risk_category')} (Score: {res.get('risk_score')})
            Reasoning: {res.get('reasoning')}
            Detected PII: {', '.join(res.get('detected_sensitive_data', []))}
            """
            
            # Store original result in metadata for rich retrieval
            doc = Document(
                page_content=content.strip(),
                metadata={
                    "user_id": str(log.get("user_id")),
                    "department": str(log.get("department")),
                    "risk_category": str(res.get("risk_category")),
                    "timestamp": str(log.get("timestamp", ""))
                }
            )
            documents.append(doc)

        if documents:
            self.vector_db.add_documents(documents)
            self.vector_db.save_local(self.index_path)
            print(f"✅ Indexed {len(documents)} new security records to FAISS.")

    def search_context(self, query: str, k: int = 5) -> str:
        """Searches the vector store and returns a formatted context string"""
        try:
            docs = self.vector_db.similarity_search(query, k=k)
            if not docs:
                return "No relevant historical security records found."
            
            context_parts = []
            for doc in docs:
                if doc.metadata.get("source") == "system": continue
                context_parts.append(doc.page_content)
            
            return "\n---\n".join(context_parts)
        except Exception as e:
            return f"Error retrieving security context: {str(e)}"
