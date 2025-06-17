# use this in terminal for antique : $env:PYTHONUTF8 = "1"
import ir_datasets

ds = ir_datasets.load("antique/test")
docs = list(ds.docs_iter())
queries = list(ds.queries_iter())
qrels = list(ds.qrels_iter())

print("🔹 docs:", len(docs))
print("🔹 queries:", len(queries))
print("🔹 qrels:", len(qrels))