from fastapi import FastAPI, HTTPException

from src.api.schemas import AskRequest, AskResponse
from src.rag.rag_pipeline import ask_rag

app = FastAPI(
    title="Puls-Events RAG API",
    description="API REST pour interroger le système RAG Puls-Events",
    version="0.4.0"
)


@app.get("/")
def root():
    return {"message": "API Puls-Events RAG opérationnelle"}


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="La question est vide")

    try:
        result = ask_rag(question)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))