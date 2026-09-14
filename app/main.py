from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(title="CodeLens AI")


@app.get("/")
def root():
    return {"message": "CodeLens AI is running"}
