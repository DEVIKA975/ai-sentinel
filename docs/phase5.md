# AI Sentinel Phase 5: Ghost AI Vector DB Integration

Phase 5 elevates the Virtual Security Assistant from a stateless chatbot to a sophisticated intelligence engine with long-term memory.

## 🧠 The RAG Architecture
AI Sentinel now utilizes **Retrieval-Augmented Generation (RAG)** to provide context-aware responses.

### 1. Vector Embeddings
- **Algorithm**: We use `SentenceTransformers` (via LangChain) to convert structured log data into 384-dimensional vectors.
- **Data Encapsulation**: Each record includes the User ID, Department, Risk Score, and the AI Sentinel reasoning.

### 2. FAISS (Facebook AI Similarity Search)
- **Engine**: A local, CPU-optimized FAISS index.
- **Efficiency**: Allows for sub-millisecond retrieval of relevant security incidents from thousands of records.
- **Persistence**: The index is stored locally and loaded at runtime, ensuring across-session memory.

## 🔍 Search & Retrieval Flow
1. **User Query**: "Has this user ever been flagged for high-risk activity before?"
2. **Embedding**: The query is converted into a vector.
3. **Similarity Search**: FAISS retrieves the top-K most similar historical security records.
4. **Augmented Prompt**: The LLM receives the query + the retrieved records as "Memory".
5. **Informed Response**: The Assistant explains the user's history based on actual stored data.

## 🛠️ Implementation Details
- **Module**: `src/vector_db.py` handles all CRUD operations on the index.
- **Integration**: The `SecurityAdvisor` class in `src/agents.py` now triggers a retrieval step before calling the LLM.
- **Batch Processing**: Logs are automatically indexed in `app.py` after every analysis run.
