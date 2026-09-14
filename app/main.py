from fastapi import FastAPI

app = FastAPI(title="CodeLens AI")


@app.get("/")
def root():
    return {"message": "CodeLens AI is running"}
