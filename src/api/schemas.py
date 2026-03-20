"""""Schemas Pydantic pour les requêtes et réponses de l'API REST du système RAG Puls-Events."""
from pydantic import BaseModel, Field
from typing import List


class AskRequest(BaseModel):
    question: str = Field(..., description="Question posée par l'utilisateur")


class SourceItem(BaseModel):
    title: str | None = Field(default=None, description="Titre de l'événement")
    city: str | None = Field(default=None, description="Ville de l'événement")
    start_datetime: str | None = Field(default=None, description="Date de début de l'événement")
    url: str | None = Field(default=None, description="URL source de l'événement")


class AskResponse(BaseModel):
    question: str = Field(..., description="Question utilisateur")
    answer: str = Field(..., description="Réponse générée par le système RAG")
    sources: List[SourceItem] = Field(default_factory=list, description="Sources utilisées pour générer la réponse")
    n_results: int = Field(..., description="Nombre de résultats récupérés dans FAISS")


class RebuildResponse(BaseModel):
    status: str = Field(..., description="Statut de la reconstruction")
    message: str = Field(..., description="Message de confirmation")