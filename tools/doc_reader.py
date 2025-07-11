import os
from langchain.tools import BaseTool
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI # AJOUTE cette ligne
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv # AJOUTE cette ligne pour que le tool puisse charger sa propre clé si nécessaire

load_dotenv() # AJOUTE cette ligne ici pour s'assurer que les variables sont chargées pour ce fichier

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
        
        # MODIFIE cette ligne pour utiliser Gemini
        # Assurez-vous que GEMINI_API_KEY est disponible dans les variables d'environnement
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY n'est pas définie pour DocReaderTool")
        object.__setattr__(self, "llm", ChatGoogleGenerativeAI(
            model="models/gemini-1.5-flash-latest", # Ou le modèle Gemini que vous préférez
            temperature=0,
            google_api_key=gemini_api_key # Passez la clé API ici
        ))

    def load_pdf(self, filepath):
        if not os.path.exists(filepath):
            return f"Fichier {filepath} introuvable"
        
        try: # AJOUTE un bloc try-except ici pour capturer les erreurs de lecture PDF
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            if not docs: # Vérifie si le PDF est vide après chargement
                return f"Le fichier PDF '{os.path.basename(filepath)}' ne contient aucune page ou est corrompu."
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(docs)
            
            if not splits: # Vérifie si le splitter a produit des chunks
                 return f"Impossible d'extraire du texte du fichier PDF '{os.path.basename(filepath)}'. Il est peut-être vide ou non textuel."

            object.__setattr__(self, "index", FAISS.from_documents(splits, self.embeddings))
            object.__setattr__(self, "qa_chain", RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.index.as_retriever()
            ))
            return f"Document {os.path.basename(filepath)} chargé avec succès"
        except Exception as e:
            return f"Erreur lors du chargement ou du traitement du PDF '{os.path.basename(filepath)}': {str(e)}"

    def _run(self, query: str) -> str:
        # On accepte 'load:<chemin>' ou 'load <chemin>'
        if query.lower().startswith("load:") or query.lower().startswith("load "):
            filepath = query.split(":", 1)[-1].strip() if ":" in query else query.split(" ", 1)[-1].strip()
            return self.load_pdf(filepath)
        
        if not self.qa_chain:
            return "Veuillez d'abord charger un PDF avec 'load:<chemin_vers_pdf>'"
        
        try:
            return self.qa_chain.run(query)
        except Exception as e:
            return f"Erreur lors de la recherche: {str(e)}"