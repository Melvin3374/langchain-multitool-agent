from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from agent import GeminiAgent
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import requests # Ajouté pour les appels HTTP

import firebase_admin
from firebase_admin import credentials, auth

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(title="LangChain Gemini Agent API", version="1.0.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # À restreindre en production !
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INITIALISATION FIREBASE ADMIN ---
FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json")

try:
    cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin SDK initialisé avec succès")
except Exception as e:
    print(f"❌ Erreur lors de l'initialisation de Firebase Admin SDK: {e}")
    # Gérer l'erreur, par exemple en arrêtant l'application ou en logant gravement.

# --- Modèles Pydantic pour l'authentification ---
class UserCredentials(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    status: str
    message: str
    id_token: Optional[str] = None # Le jeton ID Firebase après authentification réussie

# --- Modèles Pydantic pour le Chat ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

# Initialisation de l'agent Gemini
try:
    agent = GeminiAgent()
    print("Agent Gemini initialisé avec succès")
except Exception as e:
    print(f"Erreur lors de l'initialisation de l'agent: {e}")
    agent = None

# --- DEPENDENCY POUR L'AUTHENTIFICATION FIREBASE ---
async def get_current_user(request: Request):
    id_token = request.headers.get("Authorization")
    if not id_token:
        raise HTTPException(status_code=401, detail="Jeton d'authentification manquant (Authorization header)")
    
    if id_token.startswith("Bearer "):
        id_token = id_token.split(" ")[1]
    else:
        raise HTTPException(status_code=401, detail="Format de jeton invalide (doit être 'Bearer <token>')")

    try:
        # Firebase vérifie la signature et l'expiration du token.
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        return uid
    except Exception as e:
        print(f"Erreur de vérification du jeton Firebase: {e}")
        raise HTTPException(status_code=401, detail=f"Jeton d'authentification invalide ou expiré: {e}")

# --- INSCRIPTION ET CONNEXION SÉCURISÉE ---
@app.post("/signup", response_model=AuthResponse)
async def signup(credentials: UserCredentials):
    try:
        # Création de l'utilisateur via Firebase Admin SDK
        user = auth.create_user(email=credentials.email, password=credentials.password)
        # Après création, on peut générer un jeton personnalisé que le client pourra échanger
        custom_token = auth.create_custom_token(user.uid).decode('utf-8')
        
        return AuthResponse(
            status="success", 
            message="Utilisateur créé avec succès. Veuillez vous connecter.",
            id_token=custom_token # On renvoie le jeton personnalisé
        )
    except Exception as e:
        # Gérer les erreurs spécifiques de création d'utilisateur (email déjà utilisé, mot de passe faible)
        error_message = str(e)
        if "EMAIL_ALREADY_EXISTS" in error_message:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")
        if "WEAK_PASSWORD" in error_message:
            raise HTTPException(status_code=400, detail="Mot de passe trop faible (min. 6 caractères).")
        raise HTTPException(status_code=400, detail=f"Échec de l'inscription: {error_message}")

@app.post("/login", response_model=AuthResponse)
async def login(credentials: UserCredentials):
    try:
        # Pour la connexion, on doit utiliser l'API REST de Firebase Authentication,
        # car Firebase Admin SDK ne permet pas de "login" un utilisateur avec email/mot de passe.
        # Le processus sécurisé est: client -> Firebase Auth REST API -> idToken.
        # Mais comme Streamlit ne fait pas de JS, notre FastAPI va PROXY cet appel.

        FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_API_KEY") # Clé API publique du client 

        if not FIREBASE_WEB_API_KEY:
            raise HTTPException(status_code=500, detail="FIREBASE_API_KEY n'est pas configurée dans .env pour l'API web Firebase.")

        rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
        payload = {
            "email": credentials.email,
            "password": credentials.password,
            "returnSecureToken": True
        }
        
        # Appel sécurisé à l'API REST de Firebase Auth
        rest_response = requests.post(rest_api_url, json=payload)
        rest_response.raise_for_status() # Lève une exception pour les codes d'erreur HTTP (400, 401, etc.)

        response_data = rest_response.json()
        id_token = response_data.get("idToken")
        
        if id_token:
            return AuthResponse(
                status="success",
                message="Connecté avec succès!",
                id_token=id_token # On renvoie l'ID Token obtenu de Firebase
            )
        else:
            raise HTTPException(status_code=500, detail="Erreur: Impossible d'obtenir le jeton d'authentification.")

    except requests.exceptions.HTTPError as http_err:
        error_msg = http_err.response.json().get("error", {}).get("message", "Erreur inconnue")
        # Gérer les erreurs spécifiques de connexion (mauvais mot de passe, utilisateur non trouvé)
        if "EMAIL_NOT_FOUND" in error_msg or "INVALID_LOGIN_CREDENTIALS" in error_msg:
             raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")
        raise HTTPException(status_code=http_err.response.status_code, detail=f"Échec de la connexion Firebase: {error_msg}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne lors de la connexion: {str(e)}")

# --- FIN LOGIQUE D'AUTHENTIFICATION SÉCURISÉE ---


@app.get("/")
async def root():
    return {"message": "LangChain Gemini Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent_loaded": agent is not None}

# La route /chat est protégée par l'authentification
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: str = Depends(get_current_user)):
    print(f"Requête chat de l'utilisateur: {current_user}")
    
    if not agent:
        raise HTTPException(status_code=500, detail="Agent non initialisé")
    
    try:
        response = agent.run(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)