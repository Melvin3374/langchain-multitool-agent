import os
from langchain.tools import BaseTool
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocReaderTool(BaseTool):
    name: str = "LectureDoc"
    description: str = (
        "Lit un PDF et répond aux questions dessus. "
        "Utilisez 'load:<chemin_vers_pdf>' pour charger un document, puis posez vos questions."
    )
    index: object = None
    qa_chain: object = None
    embeddings: object = None
    llm: object = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "index", None)
        object.__setattr__(self, "qa_chain", None)
        object.__setattr__(self, "embeddings", HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
        object.__setattr__(self, "llm", ChatMistralAI(model="mistral-small", temperature=0))

    def load_pdf(self, filepath):
        if not os.path.exists(filepath):
            return f"Fichier {filepath} introuvable"
        loader = PyPDFLoader(filepath)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)
        object.__setattr__(self, "index", FAISS.from_documents(splits, self.embeddings))
        object.__setattr__(self, "qa_chain", RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.index.as_retriever()
        ))
        return f"Document {os.path.basename(filepath)} chargé avec succès"

    def _run(self, query: str) -> str:
        # On accepte 'load:<chemin>' ou 'load <chemin>'
        if query.lower().startswith("load:") or query.lower().startswith("load "):
            # Supporte les deux syntaxes
            filepath = query.split(":", 1)[-1].strip() if ":" in query else query.split(" ", 1)[-1].strip()
            return self.load_pdf(filepath)
        if not self.qa_chain:
            return "Veuillez d'abord charger un PDF avec 'load:<chemin_vers_pdf>'"
        try:
            return self.qa_chain.run(query)
        except Exception as e:
            return f"Erreur lors de la recherche: {str(e)}"