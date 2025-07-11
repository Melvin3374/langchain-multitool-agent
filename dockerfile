# Utilise une image Python légère
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt en premier pour profiter de la mise en cache de Docker
# Si requirements.txt ne change pas, cette étape ne sera pas reconstruite
COPY requirements.txt .

# Installer les dépendances
# build-essential est nécessaire pour certaines dépendances Python qui compilent du code C
# Le && \ et les && suivants permettent d'enchaîner les commandes en cas de succès et de nettoyer
RUN apt-get update && \
    apt-get install -y build-essential && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* # Nettoyer les fichiers temporaires pour réduire la taille de l'image

# Copier le reste de l'application
# Cette étape ne sera reconstruite que si d'autres fichiers que requirements.txt changent
COPY . /app

# Exposer le port sur lequel l'application FastAPI va écouter
EXPOSE 8000

# Commande pour démarrer l'application FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]