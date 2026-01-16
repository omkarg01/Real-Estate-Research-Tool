from uuid import uuid4
from dotenv import load_dotenv
from pathlib import Path
from langchain.chains import RetrievalQAWithSourcesChain

from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings


load_dotenv()

# Constants
CHUNK_SIZE = 1000
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR = Path(__file__).parent / "resources/vectorstore"
COLLECTION_NAME = "real_estate"


llm = None
vector_store = None


def initialize_compnents():
    global llm, vector_store
    
    if not llm:
        llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.9, max_tokens=1000)


    if not vector_store:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"trust_remote_code": True, "device": "cpu"})

        vector_store = Chroma(persist_directory=str(VECTORSTORE_DIR), embedding_function=embeddings, collection_name=COLLECTION_NAME)

    

def process_urls(urls):
    print("Processing URLs...")

    yield "Initializing components... can take a few minutes ⏳"
    # print("Initializing components...")
    initialize_compnents()

    yield "Resetting vector store... ⏳"
    # print("Resetting vector store...✅")
    vector_store.reset_collection()

    yield "Loading data from URLs... ⏳"
    # print("Loading data from URLs...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    loader = UnstructuredURLLoader(urls=urls, headers=headers)
    data = loader.load()

    yield "Splitting data into chunks... ⏳"
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", ".", " ", ""], chunk_size=CHUNK_SIZE, chunk_overlap=200)
    docs = text_splitter.split_documents(data)

    yield "Creating vector store... ⏳"
    # print("Creating vector store...")
    ids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(docs, ids=ids)
 

    yield "Done adding documents to vector store...✅"
    print("Done adding documents to vector store...✅")


def generate_answer(query):

    if not vector_store:
        raise RuntimeError("Vector store not initialized")

    retriever = vector_store.as_retriever()
    chain = RetrievalQAWithSourcesChain.from_chain_type(llm=llm, retriever=retriever)

    result = chain.invoke({"question": query}, return_only_outputs=True)
    sources = result.get("sources", "")


    return result["answer"], sources

if __name__ == "__main__":
    urls = [
        "https://www.cnbc.com/2024/12/21/how-the-federal-reserves-rate-policy-affects-mortgages.html",
        "https://www.cnbc.com/2024/12/20/why-mortgage-rates-jumped-despite-fed-interest-rate-cut.html"
    ]

    process_urls(urls)
    answer, sources = generate_answer("Tell me what was the 30 year fixed mortagate rate along with the date?")
    print(f"Answer: {answer}")
    print(f"Sources: {sources}")

