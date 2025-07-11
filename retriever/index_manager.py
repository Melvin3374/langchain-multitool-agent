import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS

from dotenv import load_dotenv

load_dotenv()

INDEX_PATH = "faiss_index"

def create_faiss_index(pdf_path: str):
    """
    Charge un PDF, crée un index FAISS vectoriel, et le sauvegarde sur disque.
    """
    print(f"Chargement du PDF : {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    print(f"Nombre de pages chargées : {len(documents)}")

    # On découpe le texte en chunks gérables
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs_split = text_splitter.split_documents(documents)

    print(f"Nombre de chunks : {len(docs_split)}")

    # Embeddings HuggingFace
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Crée ou recharge un index FAISS
    if os.path.exists(INDEX_PATH):
        print("Chargement de l'index FAISS existant...")
        index = FAISS.load_local(INDEX_PATH, embeddings)
    else:
        print("Création d'un nouvel index FAISS...")
        index = FAISS.from_documents(docs_split, embeddings)

    # Sauvegarde l'index sur disque
    index.save_local(INDEX_PATH)
    print(f"Index sauvegardé dans {INDEX_PATH}")

    return index

def load_faiss_index():
    """
    Charge un index FAISS depuis le disque
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if os.path.exists(INDEX_PATH):
        index = FAISS.load_local(INDEX_PATH, embeddings)
        print("Index FAISS chargé.")
        return index
    else:
        print("Pas d'index FAISS trouvé, crée-le d'abord avec create_faiss_index(pdf_path).")
        return None

def query_index(index, query: str, k=3):
    """
    Recherche k documents pertinents à partir d'une query
    """
    if not index:
        return "Aucun index disponible. Merci de créer un index avec un PDF d'abord."

    docs = index.similarity_search(query, k=k)
    combined = "\n---\n".join([doc.page_content for doc in docs])
    return combined
