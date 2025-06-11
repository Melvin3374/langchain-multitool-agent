from langchain.tools import BaseTool
import re
import math

class CalculatorTool(BaseTool):
    name: str = "Calculator"
    description: str = "Effectue des calculs mathématiques. Entrez une expression comme '2+2' ou 'sin(45)'"

    def _run(self, query: str) -> str:
        try:
            # Sécurité : vérifier que la requête ne contient que des caractères mathématiques
            if not re.match(r'^[\d+\-*/().^% sincoetanlg! ]+$', query):
                return "Expression mathématique invalide"
            
            result = eval(query, {'__builtins__': None}, math.__dict__)
            return f"Résultat: {result}"
        except Exception as e:
            return f"Erreur de calcul: {str(e)}"