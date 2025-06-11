from langchain.tools import BaseTool
from pydantic import Field

todo_list = []

class TodoTool(BaseTool):
    name = "TODO"
    description = """Utilisez cet outil pour gérer votre liste de tâches.
    Format d'entrée:
    - "add:<tâche>" pour ajouter
    - "list" pour lister
    - "remove:<numéro>" pour supprimer"""

    def _run(self, query: str) -> str:
        try:
            if query.startswith("add:"):
                task = query.split("add:")[1].strip()
                todo_list.append(task)
                return f"Tâche ajoutée: {task}"
            
            elif query == "list":
                if not todo_list:
                    return "Aucune tâche enregistrée"
                return "\n".join(f"{i+1}. {t}" for i, t in enumerate(todo_list))
            
            elif query.startswith("remove:"):
                num = int(query.split("remove:")[1].strip()) - 1
                if 0 <= num < len(todo_list):
                    removed = todo_list.pop(num)
                    return f"Tâche supprimée: {removed}"
                return "Numéro de tâche invalide"
            
            return "Commande non reconnue. Utilisez add:, list ou remove:"
        
        except Exception as e:
            return f"Erreur: {str(e)}"