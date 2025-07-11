# 🚀 LangChain Multitool Gemini Agent
Assistant IA multimodal avec Gemini Pro via LangChain, exposé en FastAPI et Streamlit, conteneurisé avec Docker, prêt à être déployé sur AWS EC2 capable de :

- Gérer une TODO-list
- Faire des recherches web (DuckDuckGo)
- Lire et interroger des documents PDF
- Effectuer des calculs mathématiques

## 📌 Objectifs

- Déployer un assistant IA accessible publiquement sur EC2.
- API FastAPI exposant un endpoint de chat.
- Front Streamlit pour interagir de manière simple.
- Conteneurisation avec Docker et Docker Compose.
- Prêt pour montée en production.

### 1️⃣ Prérequis

- Python 3.10+
- Docker & Docker Compose
- Une clé `GEMINI_API_KEY` valide.
- [Git] (pour cloner le repo)

## Installation

1. Clone le repo :
   ```sh
   git clone https://github.com/Melvin3374/langchain-multitool-agent.git
   cd langchain-multitool-agent
   ```

2. Crée un environnement virtuel et active-le :
   ```sh
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. Installe les dépendances :
   ```sh
   pip install -r requirements.txt
   ```

4. Ajoute ta clé API MistralAI dans une variable d’environnement :
   ```sh
   set GEMINI_API_KEY=XXX
   ```
   (ou crée un fichier `.env` avec `GEMINI_API_KEY=XXX...`)

## Utilisation

Lance l’agent :
```sh
python app.py
```

### Commandes spéciales

- `exit` : quitte l’agent
- `clear` : efface la mémoire de l’agent
- `tools` : liste les outils disponibles

### Exemples d’utilisation

- **TODO** :
  - Ajouter une tâche : `add:acheter du lait`
  - Lister les tâches : `list`
  - Supprimer une tâche : `remove:1`
- **Recherche web** :  
  Pose une question générale, ex :  
  `Quelles sont les dernières actualités sur le football ?`
- **Lecture de PDF** :
  - Charger un PDF : `load:chemin/vers/monfichier.pdf`
  - Poser une question sur le PDF chargé :  
    `Quels sont les points clés du document ?`
- **Calculatrice** :  
  `2+2`, `sin(45)`, etc.

## Structure du projet

```
.
├── app.py
├── agent.py
├── tools/
│   ├── todo_tool.py
│   ├── search_tool.py
│   ├── doc_reader.py
│   └── calculator_tool.py
├── requirements.txt
└── README.md
```

## Notes

- Les fichiers PDF doivent être accessibles depuis le chemin fourni.
- `.venv/` et les fichiers volumineux sont ignorés grâce au `.gitignore`.
- Les logs sont enregistrés dans `agent.log`.

---
