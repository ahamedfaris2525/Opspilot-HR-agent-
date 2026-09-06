import chromadb

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    Settings,
)

from llama_index.core.node_parser import TokenTextSplitter
from llama_index.readers.file import PDFReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.rag.llm_adapter import OpsPilotLLM


# --------------------------------------------------
# 1. Configure models
# --------------------------------------------------

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

Settings.llm = OpsPilotLLM()


# --------------------------------------------------
# 2. Load documents
# --------------------------------------------------

documents = SimpleDirectoryReader(
    input_files=["docs/mock_company_employee_handbook.pdf"],
    file_extractor={".pdf": PDFReader()},
).load_data()


# --------------------------------------------------
# 3. Create chunks
# --------------------------------------------------

splitter = TokenTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

nodes = splitter.get_nodes_from_documents(documents)


print("DOCUMENTS:", len(documents))
print("NODES:", len(nodes))


# --------------------------------------------------
# 4. Connect to Chroma
# --------------------------------------------------

chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_or_create_collection("opspilot_framework")

vector_store = ChromaVectorStore(chroma_collection=collection)

storage_context = StorageContext.from_defaults(vector_store=vector_store)


# --------------------------------------------------
# 5. Clear existing collection
# --------------------------------------------------

print("OLD CHROMA COUNT:", collection.count())

if collection.count() > 0:
    chroma_client.delete_collection("opspilot_framework")

    collection = chroma_client.get_or_create_collection("opspilot_framework")

    vector_store = ChromaVectorStore(chroma_collection=collection)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)


# --------------------------------------------------
# 6. Create index
# --------------------------------------------------

VectorStoreIndex(
    nodes,
    storage_context=storage_context,
)


print("NEW CHROMA COUNT:", collection.count())
print("\nINGESTION COMPLETE")
