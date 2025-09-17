import os
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# -----------------------------
# Setup vector DB (Chroma)
# -----------------------------
def setup_vector_store(pdf_path="data/AI-Partner-Playbook.pdf", persist_dir="chroma_db"):
    print("📥 Loading and indexing document...")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = Chroma.from_documents(docs, embeddings, persist_directory=persist_dir)
    db.persist()
    return db

# -----------------------------
# Researcher tool
# -----------------------------
class RAGResearcher(AssistantAgent):
    def __init__(self, name="Researcher", llm_config=None, retriever=None):
        super().__init__(
            name=name,
            system_message="You are a research assistant. Use the retriever to fetch relevant info.",
            llm_config=llm_config,
        )
        self.retriever = retriever

    def retrieve_context(self, query):
        if self.retriever:
            docs = self.retriever.get_relevant_documents(query)
            context = "\n\n".join([d.page_content for d in docs[:3]])
            return context
        return "No retriever available."

    def step(self, messages):
        query = messages[-1]["content"] if messages else "What is the context?"
        context = self.retrieve_context(query)
        # Append context to query before answering
        return f"Context retrieved:\n{context}"

# -----------------------------
# Main orchestration
# -----------------------------
def run_rag_chat(query="Summarize the Microsoft AI Partner Playbook into 3 steps."):
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm_config = {"model": "ollama/phi3", "base_url": OLLAMA_BASE_URL, "temperature": 0.2}

    # Setup retriever
    db = setup_vector_store()
    retriever = db.as_retriever()

    # Define agents
    researcher = RAGResearcher(llm_config=llm_config, retriever=retriever)
    analyst = AssistantAgent(
        name="Analyst",
        system_message="You are an analyst. Interpret research findings and extract key themes.",
        llm_config=llm_config,
    )
    reporter = AssistantAgent(
        name="Reporter",
        system_message="You are a senior communicator. Present findings as 3 executive-level actions.",
        llm_config=llm_config,
    )
    user = UserProxyAgent(name="User", code_execution_config={"work_dir": "coding", "use_docker": False})

    # Group chat with manager
    groupchat = GroupChat(
        agents=[user, researcher, analyst, reporter],
        messages=[],
        max_round=6,
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

    print(f"\n🔎 Running RAG multi-agent chat for query: {query}\n")
    user.initiate_chat(manager, message=query)

if __name__ == "__main__":
    run_rag_chat()