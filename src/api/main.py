from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from src.api.schemas import AskRequest, AskResponse, RebuildResponse
from src.rag.rag_pipeline import ask_rag
from src.pipelines.vector_pipeline import main as rebuild_vectorstore

app = FastAPI(
    title="Puls-Events RAG API",
    description="API REST pour interroger le système RAG Puls-Events",
    version="0.4.0"
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="La question est vide."
        )

    try:
        result = ask_rag(question)
        return result

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Une erreur est survenue lors de la génération de la réponse."
        )


@app.post("/rebuild", response_model=RebuildResponse)
def rebuild_index():
    try:
        rebuild_vectorstore()
        return {
            "status": "success",
            "message": "Index FAISS reconstruit avec succès."
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Une erreur est survenue lors de la reconstruction de l'index."
        )