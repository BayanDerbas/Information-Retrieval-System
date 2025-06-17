# # Information-Retrieval-System
# from ir_datasets import load
#
# class DatasetLoader:
#     def __init__(self, dataset_path):
#         self.dataset_path = dataset_path
#         self.dataset = load(dataset_path)
#         self.load_data()
#         self.show_statistics()
#
#     def load_data(self):
#         try:
#             self.documents = list(self.dataset.docs_iter())
#             self.queries = list(self.dataset.queries_iter())
#             self.qrels = list(self.dataset.qrels_iter())
#         except Exception as e:
#             print(f"❌ Error loading dataset '{self.dataset_path}': {e}")
#             self.documents = []
#             self.queries = []
#             self.qrels = []
#
#     def show_statistics(self):
#         print(f"📂 Dataset: {self.dataset_path}")
#         print(f"📄 Number of documents: {len(self.documents)}")
#         print(f"🔍 Number of queries: {len(self.queries)}")
#         print(f"✅ Number of qrels: {len(self.qrels)}\n")
#
# # DatasetLoader('antique/train')
# DatasetLoader('beir/quora/test')
