from app.db.chroma import resume_collection, documents_collection
from app.services.embedding import get_embedding

def retrieve_context(query: str, collection_type: str = "documents", k=4) -> str:
    """
    Search ChromaDB for relevant chunks.
    collection_type: 'resume' or 'documents'
    """
    collection = documents_collection if collection_type == "documents" else resume_collection
    
    embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=k
    )

    if not results or not results["documents"] or not results["documents"][0]:
        return ""

    return "\n".join(results["documents"][0])

def retrieve_resume_context(query: str, k=4) -> str:
    # Legacy wrapper for existing code if needed
    return retrieve_context(query, collection_type="resume", k=k)