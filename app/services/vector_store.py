from app.db.chroma import resume_collection

def collection_has_data() -> bool:
    try:
        count = resume_collection.count()
        return count > 0
    except Exception:
        return False