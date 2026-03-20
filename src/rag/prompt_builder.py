"""Module pour construire le prompt à envoyer au modèle de langage Mistral dans le cadre du système RAG Puls-Events.
La fonction build_prompt prend en entrée la question de l'utilisateur et le contexte (résultats de la recherche dans FAISS) et construit un prompt structuré qui guide le modèle Mistral pour générer une réponse pertinente et cohérente en se basant uniquement sur le contexte fourni.
Le prompt inclut des instructions claires pour le modèle, notamment de ne pas inventer d'informations et de répondre de manière naturelle et agréable à lire. Si l'information demandée n'est pas présente dans le contexte, le modèle doit répondre qu'il ne trouve pas cette information dans les données disponibles."""
def build_prompt(question: str, context: str) -> str:
    return f"""
Tu es un assistant qui aide à découvrir des événements culturels dans l’Hérault.

Réponds de manière claire, naturelle et agréable à lire.

RÈGLES IMPORTANTES :
- Base ta réponse uniquement sur le contexte fourni
- N'invente aucune information
- Si l'information n'est pas présente, réponds :
"Je ne trouve pas cette information dans les données disponibles."

Si plusieurs événements correspondent, présente-les de façon fluide (pas forcément en liste rigide).

Contexte :
{context}

Question :
{question}

Réponse :
""".strip()