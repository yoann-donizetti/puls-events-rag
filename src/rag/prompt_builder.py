def build_prompt(question: str, context: str) -> str:
    """
    Construit le prompt envoyé au LLM à partir de la question
    utilisateur et du contexte récupéré depuis FAISS.
    """

    return f"""
Tu es un assistant spécialisé dans les événements culturels.

Réponds uniquement à partir du contexte fourni.
Si l'information n'est pas présente dans le contexte, dis-le clairement.
Ne fais pas d'hypothèse.
Réponds de manière claire, concise et utile.

Contexte :
{context}

Question :
{question}

Réponse :
""".strip()