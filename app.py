from agent import create_agent
import logging

logging.basicConfig(
    filename='agent.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Démarrage de l'agent")
 
    agent = create_agent()
    print("=== Agent Personnel Multitâche ===")
    print("Commandes spéciales:")
    print("- 'exit' pour quitter")
    print("- 'clear' pour effacer la mémoire")
    print("- 'tools' pour lister les outils disponibles\n")

    while True:
        try:
            user_input = input("Vous: ")
            if user_input.lower() == "exit":
                break
            if user_input.lower() == "clear":
                agent.memory.clear()
                print("Mémoire effacée")
                continue
            if user_input.lower() == "tools":
                print("\nOutils disponibles:")
                for tool in agent.tools:
                    print(f"- {tool.name}: {tool.description}")
                print()
                continue

            response = agent.run(input=user_input)
            print(f"\nAgent: {response}\n")

        except Exception as e:
            print(f"\nErreur: {str(e)}\n")