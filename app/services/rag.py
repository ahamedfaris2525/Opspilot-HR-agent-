import chromadb

from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.rag.llm_adapter import OpsPilotLLM


class RAGService:
    def __init__(self):

        Settings.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        Settings.llm = OpsPilotLLM()

        chroma_client = chromadb.PersistentClient(path="./chroma_db")

        collection = chroma_client.get_collection("opspilot_framework")

        vector_store = ChromaVectorStore(chroma_collection=collection)

        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex.from_vector_store(
            vector_store,
            storage_context=storage_context,
        )

        self.query_engine = index.as_query_engine(similarity_top_k=3)

    def query(self, question: str) -> str:

        response = self.query_engine.query(question)

        return str(response)
