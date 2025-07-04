import ir_datasets


class DatasetLoader:
    def __init__(self):
        self.datasets = {
            "antique/test": "antique/test",
            # "csl/trec-2023": "csl/trec-2023",
            "beir/quora/test": "beir/quora/test",
        }

    def load_dataset(self, dataset_name):
        """Load the specified dataset from ir-datasets."""
        if dataset_name not in self.datasets:
            raise ValueError(f"Dataset {dataset_name} not supported.")

        dataset = ir_datasets.load(dataset_name)
        return dataset

    def get_documents(self, dataset):
        """Retrieve all documents from the dataset."""
        sample_doc = next(dataset.docs_iter())
        # Check available attributes
        if hasattr(sample_doc, "text"):
            return [(doc.doc_id, doc.text) for doc in dataset.docs_iter()]
        elif hasattr(sample_doc, "title") and hasattr(sample_doc, "abstract"):
            return [
                (doc.doc_id, f"{doc.title} {doc.abstract}")
                for doc in dataset.docs_iter()
            ]
        else:
            raise ValueError("Unsupported document structure.")

    def get_queries(self, dataset):
        """Retrieve all queries from the dataset."""
        return [(query.query_id, query.text) for query in dataset.queries_iter()]

    def get_qrels(self, dataset):
        """Retrieve all qrels from the dataset."""
        return [
            (qrel.query_id, qrel.doc_id, qrel.relevance)
            for qrel in dataset.qrels_iter()
        ]
