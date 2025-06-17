from pymongo import MongoClient
from datetime import datetime


class MongoDBHandler:
    def __init__(self, db_name="ir_system", collection_prefix="processed_"):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client[db_name]
        self.collection_prefix = collection_prefix

    def get_stored_versions(self):
        """Get all stored collection names with the processing prefix."""
        collections = self.db.list_collection_names()
        versions = [
            col for col in collections if col.startswith(self.collection_prefix)
        ]
        return versions

    def save_processed_data(
        self,
        dataset_name,
        processed_docs,
        version_name=None,
        processed_queries=None,
        processed_qrels=None,
    ):
        """Save processed documents (and optionally queries, qrels) to a new collection."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_dataset = dataset_name.replace("/", "_")

        # Use user version name directly if given, otherwise fallback to timestamp
        collection_name = (
            f"{self.collection_prefix}{safe_dataset}_{version_name or timestamp}"
        )
        collection = self.db[collection_name]

        for doc in processed_docs:
            if isinstance(doc, tuple):
                if len(doc) == 2:
                    doc_id, text = doc
                    collection.insert_one(
                        {"type": "document", "doc_id": doc_id, "text": text}
                    )
                elif len(doc) == 3:
                    doc_id, original_text, processed_text = doc
                    collection.insert_one(
                        {
                            "type": "document",
                            "doc_id": doc_id,
                            "original_text": original_text,
                            "text": processed_text,
                        }
                    )

        if processed_queries:
            for query in processed_queries:
                if isinstance(query, tuple) and len(query) == 3:
                    qid, original_text, processed_text = query
                    collection.insert_one(
                        {
                            "type": "query",
                            "query_id": qid,
                            "original_text": original_text,
                            "text": processed_text,
                        }
                    )

        if processed_qrels:
            for qid, docid, rel in processed_qrels:
                collection.insert_one(
                    {"type": "qrel", "query_id": qid, "doc_id": docid, "relevance": rel}
                )

        return collection_name

    def display_version(self, version_name, limit=10):
        """Return statistics and first documents from a given collection."""
        if version_name not in self.db.list_collection_names():
            raise ValueError(f"Version '{version_name}' not found in the database.")

        collection = self.db[version_name]

        stats = {
            "name": version_name,
            "documents": collection.count_documents({"type": "document"}),
            "queries": collection.count_documents({"type": "query"}),
            "qrels": collection.count_documents({"type": "qrel"}),
            "samples": list(collection.find({"type": "document"}).limit(limit)),
        }
        return stats

    def delete_version(self, version_name):
        """Delete a specific version (collection) by name."""
        if version_name in self.db.list_collection_names():
            self.db.drop_collection(version_name)
            return f"Version '{version_name}' deleted successfully."
        return f"Version '{version_name}' not found."

    def delete_all_versions(self):
        """Delete all collections with the processing prefix."""
        collections = self.get_stored_versions()
        for col in collections:
            self.db.drop_collection(col)
        return f"Deleted {len(collections)} versions."