import sys
import os
import json
import csv

from dataset_loader.datasetsLoader import DatasetLoader
from db_module import mongodb_handler
from db_module.mongodb_handler import MongoDBHandler
from preprocessing_module.data_preprocessor import DataPreprocessor

# Force UTF-8 encoding for output
sys.stdout.reconfigure(encoding="utf-8")


def print_first_10(documents):
    print("\n=== First 10 Processed Documents ===")
    for i, doc in enumerate(documents[:10], 1):
        if len(doc) == 3:
            doc_id, original, processed = doc
        elif len(doc) == 2:
            doc_id, processed = doc
            original = "[Original text not provided]"

        print(f"\n#{i} Doc ID: {doc_id}")
        print(f"--- Original Text ---\n{original[:200]}...\n")
        print(f"--- Processed Text ---\n{processed[:200]}...")
        print("-" * 70)


def save_local_formats(processed_docs, dataset_name, version_name):
    base_dir = os.path.join("data", version_name)
    os.makedirs(base_dir, exist_ok=True)

    base_name = dataset_name.replace("/", "_") + "_" + version_name
    json_path = os.path.join(base_dir, f"{base_name}.msi.json")
    tsv_path = os.path.join(base_dir, f"{base_name}.tsv")
    msi_path = os.path.join(base_dir, f"{base_name}.msi")

    # Remove original before saving
    json_data = [{"doc_id": doc[0], "text": doc[-1]} for doc in processed_docs]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    with open(tsv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["doc_id", "text"])
        for doc in processed_docs:
            writer.writerow([doc[0], doc[-1]])

    with open(msi_path, "wb") as f:
        f.write(json.dumps(json_data, ensure_ascii=False).encode("utf-8"))

    print(f"\n✅ Saved local files in version directory '{base_dir}':")
    print(f"- {json_path}\n- {tsv_path}\n- {msi_path}")


def main():
    loader = DatasetLoader()
    preprocessor = DataPreprocessor()
    mongo_handler = MongoDBHandler()

    while True:
        print("\n=== Information Retrieval System Menu ===")
        print("1. Process and save a dataset")
        print("2. Display stored versions")
        print("3. Delete a specific stored version")
        print("4. Delete all stored versions")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            print("\nAvailable datasets:")
            dataset_list = list(loader.datasets.keys())
            for i, dataset in enumerate(dataset_list, 1):
                print(f"{i}. {dataset}")
            dataset_choice = input("Enter dataset number (e.g., 1) or name (e.g., beir/quora/test): ")

            try:
                if dataset_choice.isdigit():
                    dataset_index = int(dataset_choice) - 1
                    if 0 <= dataset_index < len(dataset_list):
                        dataset_choice = dataset_list[dataset_index]
                    else:
                        raise ValueError("Invalid dataset number.")

                dataset = loader.load_dataset(dataset_choice)
                documents = loader.get_documents(dataset)
                processed_docs = preprocessor.preprocess_documents(documents)

                if not processed_docs:
                    print("No documents were processed successfully.")
                    continue

                # ✅ فقط الطباعة تتضمن النص الأصلي
                print_first_10(processed_docs)

                version_name = input("Enter a version name for saving (e.g., v1): ").strip()
                if not version_name:
                    print("No version name provided. Cancelling save.")
                    continue

                # ❌ لا نحفظ original في التخزين
                mongo_safe_docs = [(doc[0], doc[-1]) for doc in processed_docs]
                collection_name = mongo_handler.save_processed_data(
                    dataset_choice, mongo_safe_docs, version_name=version_name
                )
                print(f"\n✅ Processed data saved to MongoDB collection: {collection_name}")

                save_local_formats(processed_docs, dataset_choice, version_name)

            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "2":
            versions = mongo_handler.get_stored_versions()
            if not versions:
                print("No stored versions found.")
                continue

            print("\nStored versions:")
            for i, ver in enumerate(versions, 1):
                print(f"{i}. {ver}")

            version_choice = input("Enter version name to display (or number): ").strip()
            if version_choice.isdigit():
                idx = int(version_choice) - 1
                if 0 <= idx < len(versions):
                    version_choice = versions[idx]
                else:
                    print("Invalid version number.")
                    continue

            try:
                stats = mongo_handler.display_version(version_choice)
                print(f"\nVersion: {stats['name']}")
                print(f"Documents: {stats['documents']}")
                print(f"Queries: {stats['queries']}")
                print(f"Qrels: {stats['qrels']}")
                print("\nSample documents:")
                for doc in stats["samples"]:
                    print(f"Doc ID: {doc.get('doc_id', '')}")
                    print(f"Text: {doc.get('text', '')[:200]}...")
                    print("-" * 50)
            except Exception as e:
                print(f"Error displaying version: {e}")

        elif choice == "3":
            versions = mongo_handler.get_stored_versions()
            if not versions:
                print("No stored versions to delete.")
                continue

            print("\nStored versions:")
            for i, ver in enumerate(versions, 1):
                print(f"{i}. {ver}")

            version_choice = input("Enter version name to delete (or number): ").strip()
            if version_choice.isdigit():
                idx = int(version_choice) - 1
                if 0 <= idx < len(versions):
                    version_choice = versions[idx]
                else:
                    print("Invalid version number.")
                    continue

            result = mongo_handler.delete_version(version_choice)
            print(result)

        elif choice == "4":
            confirm = input("Are you sure you want to delete ALL versions? (yes/no): ").strip().lower()
            if confirm == "yes":
                result = mongo_handler.delete_all_versions()
                print(result)
            else:
                print("Deletion cancelled.")

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()