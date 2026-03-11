from fastapi import FastAPI

app = FastAPI(
    title="Puls-Events RAG API",
    description="API REST locale pour interroger le système RAG Puls-Events",
    version="0.4.0"
)


@app.get("/")
def root():
    return {"message": "API Puls-Events RAG opérationnelle"}