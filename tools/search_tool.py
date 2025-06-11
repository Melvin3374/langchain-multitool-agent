# tools/search_tool.py
from langchain_community.tools import DuckDuckGoSearchRun

class SearchTool:
    def __init__(self):
        self.search = DuckDuckGoSearchRun()
    
    def run(self, query):
        try:
            result = self.search.run(query)
            return result
        except Exception as e:
            return f"Erreur lors de la recherche: {e}"
