# 🚀 LangChain Multitool Gemini Agent
Assistant IA multimodal avancé propulsé par Google Gemini Pro via LangChain. 
- Déployer un assistant IA accessible publiquement sur EC2.
- API FastAPI pour la logique backend
- Front Streamlit pour une interface utilisateur intuitive
- Conteneurisation avec Docker et Docker Compose.
- Prêt pour montée en production.

## ✨ Fonctionnalités

Cet agent est capable de :
- Gérer une TODO-list : Créez, listez et supprimez vos tâches quotidiennes.
- Recherches web : Effectuez des recherches d'informations en temps réel via DuckDuckGo.
- Lecture et interrogation de documents PDF : Chargez des fichiers PDF locaux et posez des questions sur leur contenu.
- Effectuer des calculs mathématiques : Résolvez des opérations et expressions mathématiques complexes.

## 🎯  Objectifs

Assistant IA complet : Fournir un agent conversationnel puissant et polyvalent.
Architecture modulaire : Séparer la logique métier (agent), l'API (FastAPI) et l'interface utilisateur (Streamlit).
Déploiement simplifié : Utiliser Docker pour une conteneurisation facile et un déploiement rapide.
Préparation à la production : Mettre en place les bases pour une montée en charge sur des infrastructures cloud comme AWS EC2.

### 1️⃣ Prérequis

- Python 3.10+
- Docker & Docker Compose
- Une clé GEMINI_API_KEY valide (obtenue depuis Google AI Studio ou Google Cloud Console).
- [Git] (pour cloner le repo)

## Installation

1. Clone le repo :
   ```sh
   git clone https://github.com/Melvin3374/langchain-multitool-agent.git
   cd langchain-multitool-agent
   ```
   
2. Configurez votre clé API Gemini :
   ```sh
Créez un fichier nommé .env à la racine du projet (au même niveau que docker-compose.yml) et ajoutez-y votre clé API :
GEMINI_API_KEY=votre_clé_api_gemini_ici
FASTAPI_API_URL=http://localhost:8000 # URL de votre API FastAPI (pour Streamlit)
   ```

3. Lancez les services avec Docker Compose :
   ```sh
docker-compose up --build
Cette commande va construire les images Docker nécessaires, puis démarrer l'API FastAPI et l'application Streamlit.
   ```

3. Accédez à l'application Streamlit :
   ```sh
Ouvrez votre navigateur web et naviguez vers :
http://localhost:8501

L'API FastAPI sera accessible sur http://localhost:8000, mais vous n'aurez pas besoin d'interagir directement avec elle via votre navigateur.
   ```
```
### 💬 Utilisation de l'Agent
Une fois l'application Streamlit lancée et après vous être connecté (ou inscrit), vous pourrez interagir avec l'agent Gemini via l'interface de chat.
Commandes spéciales de l'agent (en fonction de l'implémentation)

L'agent est conçu pour comprendre des requêtes en langage naturel, mais certains outils peuvent réagir à des formats spécifiques :
- **Généralités** : Posez simplement votre question ou votre instruction.
- **TODO** :
  - Ajouter une tâche : `add:acheter du lait`
  - Lister les tâches : `list`
  - Supprimer une tâche : `remove:1`
- **Recherche web** :  
  Pose une question générale, ex :  
  `Quelles sont les dernières actualités sur le football ?`
- **Lecture de PDF** :
  - Charger un PDF : `load:chemin/vers/monfichier.pdf` (le chemin doit être accessible depuis l'environnement Docker de l'API, ce qui peut nécessiter de monter des volumes dans Docker Compose si les fichiers sont hors du contexte du projet Docker).
  - Poser une question sur le PDF chargé :  
    `Quels sont les points clés du document ?`
- **Calculatrice** :  
  `2+2`, `sin(45)`, etc.

## Structure du projet

```
.
├── app.py                      # Point d'entrée de l'API FastAPI (sûrement renommée en main.py ou similaire pour un déploiement standard)
├── agent.py                    # Logique de l'agent LangChain
├── streamlit_app.py            # Application front-end Streamlit
├── tools/
│   ├── todo_tool.py            # Outil de gestion de TODO
│   ├── search_tool.py          # Outil de recherche web (DuckDuckGo)
│   ├── doc_reader.py           # Outil de lecture et d'interrogation de PDF
│   └── calculator_tool.py      # Outil de calcul mathématique
├── requirements.txt            # Dépendances Python
├── Dockerfile.fastapi          # Dockerfile pour l'API FastAPI
├── Dockerfile.streamlit        # Dockerfile pour l'application Streamlit
├── docker-compose.yml          # Fichier pour orchestrer les conteneurs Docker
├── .env.example                # Exemple de fichier .env
└── README.md
```

## Notes

- **Sécurité des API Keys** : Ne jamais exposer directement votre GEMINI_API_KEY dans le code public ou dans des dépôts Git. Utilisez les variables d'environnement (.env localement, puis des méthodes sécurisées comme les Secrets Managers d'AWS ou les variables d'environnement EC2/ECS/EKS en production).

- **Accès aux fichiers PDF** : Pour que DocReaderTool puisse lire les PDF sur EC2, assurez-vous que les fichiers PDF sont présents sur l'instance et que le chemin spécifié dans la commande load: est correct et accessible depuis le conteneur Docker de l'API. Il est souvent nécessaire de monter un volume Docker pour cela.

- **Gestion des quotas API** : L'API Gemini a des quotas d'utilisation (requêtes par minute/jour). Déployer l'agent publiquement sans gestion d'accès stricte peut rapidement épuiser votre quota ou entraîner des coûts si vous dépassez les limites gratuites. Surveillez votre utilisation via la console Google Cloud.

- **Sécurité du déploiement sur EC2** :

    Par défaut, si vous ne configurez pas les Groupes de Sécurité (Security Groups) de votre instance EC2, votre application sera accessible publiquement par n'importe qui sur Internet.

    **Fortement recommandé** : Restreignez l'accès aux ports de votre application (par exemple, port 8501 pour Streamlit et port 8000 pour FastAPI) dans votre groupe de sécurité EC2. N'autorisez le trafic entrant que depuis des adresses IP spécifiques (votre IP personnelle, une plage d'IP de bureau, etc.) au lieu de 0.0.0.0/0.

    Pour un déploiement en production, envisagez des solutions d'authentification plus robustes (ex: Amazon Cognito) et une architecture réseau plus sécurisée.

---
