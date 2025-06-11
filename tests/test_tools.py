import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.todo_tool import TodoTool, todo_list
from tools.search_tool import SearchTool
from tools.doc_reader import DocReaderTool

# Tests TodoTool
def test_todo_tool():
    todo = TodoTool()
    assert "ajoutée" in todo._run("add:Faire les courses")
    assert "1. Faire les courses" in todo._run("list")
    assert "supprimée" in todo._run("remove:1")

# Tests SearchTool
def test_search_tool():
    search = SearchTool()
    result = search.run("actualité IA 2024")
    assert isinstance(result, str)
    assert len(result) > 20

# Tests CalculatorTool
def test_calculator():
    calc = CalculatorTool()
    assert "4" in calc._run("2+2")
    assert "3.14" in calc._run("round(pi, 2)")

# Tests DocReaderTool
def test_doc_reader(tmp_path):
    doc = DocReaderTool()
    
    # Crée un faux PDF pour le test
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Ceci est un test PDF", ln=1)
    test_pdf = tmp_path / "test.pdf"
    pdf.output(test_pdf)
    
    assert "chargé" in doc.run(f"load:{test_pdf}")
    assert "test PDF" in doc.run("Qu'est-ce qui est écrit dans le document?")