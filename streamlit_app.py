import streamlit as st # type: ignore
import requests # type: ignore
import json
import os
from dotenv import load_dotenv # type: ignore

# Charger les variables d'environnement
load_dotenv()

# Configurez l'URL de votre API FastAPI
FASTAPI_API_URL = os.getenv("FASTAPI_API_URL", "http://localhost:8000")

# --- Configuration de la page Streamlit ---
st.set_page_config(
    page_title="Langchain Multitool Agent",
    page_icon="🤖",
    layout="wide"
)

# --- Initialisation du Session State ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.id_token = None
    st.session_state.email = None
    st.session_state.messages = []


# ======================================================================================
# --- SECTION POUR LES UTILISATEURS NON AUTHENTIFIÉS (LANDING PAGE) ---
# ======================================================================================
if not st.session_state.authenticated:

    # --- Header de la Landing Page ---
    st.title("Langchain Multitool Agent IA 🚀")
    st.subheader("Bienvenue sur votre assistant intelligent, propulsé par l'IA 🧠")
    st.markdown("---")
    st.header("🔐 Accédez à votre espace")
    login_container, signup_container = st.columns(2)

    with login_container:
        with st.form("login_form"):
            st.subheader("J'ai déjà un compte")
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Mot de passe", type="password", key="login_password")
            login_button = st.form_submit_button("Se connecter", use_container_width=True)

            if login_button:
                if not login_email or not login_password:
                    st.error("Veuillez entrer un email et un mot de passe.")
                else:
                    try:
                        auth_response = requests.post(
                            f"{FASTAPI_API_URL}/login",
                            json={"email": login_email, "password": login_password}
                        )
                        auth_response.raise_for_status()
                        auth_data = auth_response.json()

                        if auth_data.get("status") == "success" and "id_token" in auth_data:
                            st.session_state.authenticated = True
                            st.session_state.id_token = auth_data["id_token"]
                            st.session_state.email = login_email
                            st.rerun()
                        else:
                            st.error(auth_data.get("message", "Erreur de connexion."))

                    except requests.exceptions.HTTPError as http_err:
                        error_detail = http_err.response.json().get("detail", str(http_err))
                        st.error(f"Erreur d'authentification : {error_detail}")
                    except Exception as e:
                        st.error(f"Erreur de connexion au service : {e}")

    with signup_container:
        with st.form("signup_form"):
            st.subheader("Je crée mon compte")
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Mot de passe", type="password", key="signup_password")
            signup_button = st.form_submit_button("S'inscrire", use_container_width=True)

            if signup_button:
                if not signup_email or not signup_password:
                    st.error("Veuillez entrer un email et un mot de passe.")
                else:
                    try:
                        auth_response = requests.post(
                            f"{FASTAPI_API_URL}/signup",
                            json={"email": signup_email, "password": signup_password}
                        )
                        auth_response.raise_for_status()
                        auth_data = auth_response.json()

                        if auth_data.get("status") == "success":
                            st.success(auth_data["message"])
                            st.info("Vous pouvez maintenant vous connecter avec vos identifiants.")
                        else:
                            st.error(auth_data.get("message", "Erreur lors de l'inscription."))

                    except requests.exceptions.HTTPError as http_err:
                        error_detail = http_err.response.json().get("detail", str(http_err))
                        st.error(f"Erreur d'inscription : {error_detail}")
                    except Exception as e:
                        st.error(f"Erreur de connexion au service : {e}")


# ======================================================================================
# --- SECTION POUR LES UTILISATEURS AUTHENTIFIÉS (CHATBOT) ---
# ======================================================================================
if st.session_state.authenticated:

    # --- Barre latérale ---
    st.sidebar.header(f"👋 Bienvenue,")
    st.sidebar.success(f"**{st.session_state.email}**")
    if st.sidebar.button("Déconnexion", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.id_token = None
        st.session_state.email = None
        st.session_state.messages = [] # Optionnel: vider l'historique à la déconnexion
        st.rerun()
    st.sidebar.markdown("---")
    st.sidebar.info("Posez vos questions dans la zone de texte ci-dessous et validez pour obtenir une réponse de l'agent")


    # --- Interface principale du Chat ---
    st.title("🤖 Agent Conversationnel")
    st.write("Je suis prêt à discuter avec vous. Que souhaitez-vous faire ?")
    
    # Conteneur pour l'historique du chat
    chat_container = st.container()

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Champ de saisie utilisateur en bas de la page
    if prompt := st.chat_input("Votre message..."):
        # Ajouter le message utilisateur à l'historique et l'afficher
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Obtenir et afficher la réponse de l'assistant
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("..."):
                    try:
                        headers = {
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {st.session_state.id_token}"
                        }
                        response = requests.post(
                            f"{FASTAPI_API_URL}/chat",
                            headers=headers,
                            json={"message": prompt}
                        )
                        response.raise_for_status()
                        assistant_response = response.json()["response"]
                        st.markdown(assistant_response)
                        # Ajouter la réponse de l'assistant à l'historique
                        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

                    except requests.exceptions.HTTPError as http_err:
                        error_message = f"Erreur HTTP : {http_err.response.status_code}. Détail : {http_err.response.text}"
                        st.error(error_message)
                        st.session_state.messages.append({"role": "assistant", "content": error_message})
                    except requests.exceptions.RequestException as e:
                        error_message = f"Erreur de connexion à l'API : {e}"
                        st.error(error_message)
                        st.session_state.messages.append({"role": "assistant", "content": error_message})
                    except Exception as e:
                        error_message = f"Une erreur inattendue est survenue: {e}"
                        st.error(error_message)
                        st.session_state.messages.append({"role": "assistant", "content": error_message})