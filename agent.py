import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Import de tes classes de tools personnalisés
from tools.todo_tool import TodoTool
from tools.search_tool import SearchTool
from tools.doc_reader import DocReaderTool
from tools.calculator_tool import CalculatorTool

class GeminiAgent:
    def __init__(self):
        """
        Initialise l'agent Gemini avec tous les outils
        """
        # Vérification de la clé API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY n'est pas définie dans les variables d'environnement")
        
        # Configuration de Gemini
        genai.configure(api_key=api_key)
        
        # Initialisation du LLM Gemini pour LangChain
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-1.5-flash-latest",
            temperature=0.5,
            google_api_key=api_key
        )
        
        # Initialisation des outils avec gestion d'erreurs
        self.tools = []
        self._init_tools()
        
        # Création de l'agent LangChain
        self.agent = self._create_langchain_agent()
    
    def _init_tools(self):
        """Initialise tous les outils avec gestion d'erreurs"""
        tool_classes = [
            (TodoTool, "TodoTool"),
            (SearchTool, "SearchTool"),
            (DocReaderTool, "DocReaderTool"),
            (CalculatorTool, "CalculatorTool")
        ]
        
        for tool_class, tool_name in tool_classes:
            try:
                tool_instance = tool_class()
                self.tools.append(tool_instance)
                print(f"✅ {tool_name} initialisé")
            except Exception as e:
                print(f"❌ Erreur {tool_name}: {e}")
        
        if not self.tools:
            raise ValueError("Aucun outil n'a pu être initialisé")
    
    def _create_langchain_agent(self):
        """Crée l'agent LangChain avec les outils"""
        # Convertir en outils LangChain
        langchain_tools = []
        for tool in self.tools:
            langchain_tools.append(
                Tool(
                    name=tool.name,
                    func=tool._run,
                    description=tool.description
                )
            )
        
        # Mémoire pour la conversation
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        
        # Configuration de l'agent
        agent = initialize_agent(
            tools=langchain_tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="generate"
        )
        
        print(f"🤖 Agent initialisé avec {len(langchain_tools)} outils")
        return agent
    
    def run(self, input_text: str) -> str:
        """
        Exécute une requête avec l'agent
        """
        try:
            response = self.agent.run(input=input_text)
            return response
        except Exception as e:
            return f"Erreur lors de l'exécution: {str(e)}"
    
    def chat(self, message: str) -> str:
        """
        Méthode de chat compatible avec l'ancienne interface
        """
        return self.run(message)

# Fonction de compatibilité avec l'ancien code
def create_agent():
    """
    Fonction de compatibilité pour créer un agent Gemini
    """
    return GeminiAgent()

# Test de l'agent (optionnel, pour debug)
if __name__ == "__main__":
    try:
        agent = GeminiAgent()
        print("Agent Gemini créé avec succès!")
        
        # Test rapide
        response = agent.run("Bonjour, comment ça va ?")
        print(f"Réponse: {response}")
    except Exception as e:
        print(f"Erreur lors de la création de l'agent: {e}")