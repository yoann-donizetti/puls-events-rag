"""Client pour interagir avec le modèle de langage Mistral dans le cadre du système RAG Puls-Events.
Ce module utilise la bibliothèque mistralai pour envoyer des prompts au modèle Mistral et récupérer les réponses générées. La clé API de Mistral doit être définie dans un fichier .env à la racine du projet avec la variable MISTRAL_API_KEY.
Fonction principale :   generate_answer(prompt: str) -> str
- Envoie un prompt au modèle Mistral et retourne la réponse générée.
- Raise une erreur si la clé API n'est pas trouvée dans le fichier .env.
"""
import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL = "mistral-small-latest"
TEMPERATURE =0.2
TOP_P = 0.9
MAX_TOKENS = 300


def generate_answer(prompt: str) -> str:
    """
    Envoie le prompt au modèle Mistral et retourne la réponse générée.
    raise une erreur si la clé API n'est pas trouvée dans le fichier .env.
    """
    if not API_KEY:
        raise ValueError("MISTRAL_API_KEY introuvable dans le fichier .env")

    client = Mistral(api_key=API_KEY)

    response = client.chat.complete(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE,
        top_p=TOP_P,
        max_tokens=MAX_TOKENS
    )

    return response.choices[0].message.content