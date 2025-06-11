# tools/doc_reader.py
import os
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocReaderTool:
    def __init__(self):
        self.index = None
        self.qa_chain = None
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.llm = ChatMistralAI(model="mistral-small", temperature=0)
    
    def load_pdf(self, filepath):
        if not os.path.exists(filepath):
            return f"Fichier {filepath} introuvable"
        
        loader = PyPDFLoader(filepath)
        docs = loader.load()
        
        # Split des documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)
        
        # Création de l'index
        self.index = FAISS.from_documents(splits, self.embeddings)
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.index.as_retriever()
        )
        return f"Document {os.path.basename(filepath)} chargé avec succès"

    def run(self, input_text):
        # Format attendu : "load:<chemin_vers_pdf>" ou la question
        if input_text.startswith("load:"):
            filepath = input_text.split("load:")[1].strip()
            return self.load_pdf(filepath)
        
        if not self.qa_chain:
            return "Veuillez d'abord charger un PDF avec 'load:<chemin_vers_pdf>'"
        
        try:
            return self.qa_chain.run(input_text)
        except Exception as e:
            return f"Erreur lors de la recherche: {str(e)}"