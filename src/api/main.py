from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from src.api.schemas import AskRequest, AskResponse,RebuildResponse
from src.rag.rag_pipeline import ask_rag
from src.pipelines.vector_pipeline import main as rebuild_vectorstore


app = FastAPI(
    title="Puls-Events RAG API",
    description="API REST pour interroger le système RAG Puls-Events",
    version="0.4.0"
)


@app.get("/",include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


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
    
@app.post("/rebuild", response_model=RebuildResponse)
def rebuild_vectorstore_endpoint():
    try:
        rebuild_vectorstore()
        return RebuildResponse(status="success", message="Index FAISS reconstruit avec succès")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la reconstruction de l'index FAISS: {str(e)}")