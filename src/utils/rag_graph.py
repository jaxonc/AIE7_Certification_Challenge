from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.documents import Document
import os

def build_rag_graph():
    """
    Build and return a compiled RAG graph for product information retrieval.
    
    Returns:
        Compiled LangGraph that can be invoked with {"question": str} and returns
        {"response": str, "context": List[Document]}
    """
    
    # Get the absolute path to the data directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    data_path = os.path.join(project_root, "data")
    loader = DirectoryLoader(data_path, glob="*.txt", loader_cls=TextLoader)
    docs = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 750,
        chunk_overlap = 100,
    )

    document_chunks = text_splitter.split_documents(docs)

    # Initialize embeddings
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

    # Setup Qdrant vector store
    client = QdrantClient(":memory:")

    client.create_collection(
        collection_name="Product_Data",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name="Product_Data",  # Fixed: now matches the created collection name
        embedding=embedding_model,
    )

    # Add documents to vector store
    _ = vector_store.add_documents(documents=document_chunks)

    # Create retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    # Define retrieval function
    def retrieve(state):
        retrieved_docs = retriever.invoke(state["question"])
        return {"context" : retrieved_docs}

    # Define RAG prompt
    RAG_PROMPT = """\
You are a helpful assistant who answers questions based on provided context. You must only use the provided context, and cannot use your own knowledge.

### Question
{question}

### Context
{context}
"""

    rag_prompt = ChatPromptTemplate.from_template(RAG_PROMPT)

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4.1-nano")

    # Define generation function
    def generate(state):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = rag_prompt.format_messages(question=state["question"], context=docs_content)
        response = llm.invoke(messages)
        return {"response" : response.content}

    # Define state schema
    class State(TypedDict):
        question: str
        context: List[Document]
        response: str

    # Build and compile graph
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    
    return graph

rag_graph = build_rag_graph()