import os
from langchain_mistralai.chat_models import ChatMistralAI
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory

# Import de tes classes de tools personnalisés
from tools.todo_tool import TodoTool
from tools.search_tool import SearchTool
from tools.doc_reader import DocReaderTool
from tools.calculator_tool import CalculatorTool

def create_agent():
    llm = ChatMistralAI(
        api_key=os.getenv("MISTRAL_API_KEY"),
        model="mistral-small",
        temperature=0.3,  # Un peu plus de créativité
    )

    # Initialisation des outils
    tools = [
        TodoTool(),
        SearchTool(),
        DocReaderTool(),
        CalculatorTool()
    ]

    # Convertir en outils LangChain
    langchain_tools = []
    for tool in tools:
        langchain_tools.append(
            Tool(
                name=tool.name,
                func=tool._run,
                description=tool.description
            )
        )

    # Mémoire avec summary pour une meilleure persistance
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )

    # Agent avec meilleure configuration
    agent = initialize_agent(
        tools=langchain_tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,  # Meilleur pour les conversations
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5,  # Éviter les boucles infinies
        early_stopping_method="generate"
    )

    return agent
