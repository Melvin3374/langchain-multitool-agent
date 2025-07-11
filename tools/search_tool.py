from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun

class SearchTool(BaseTool):
    name: str = "RechercheWeb"
    description: str = "Recherche une information sur le web avec DuckDuckGo."
    search: DuckDuckGoSearchRun = None  # <--- Ajoute cette ligne

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "search", DuckDuckGoSearchRun())

    def _run(self, query: str) -> str:
        try:
            return self.search.run(query)
        except Exception as e:
            return f"Erreur lors de la recherche: {e}"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("Pas de support async pour le moment")