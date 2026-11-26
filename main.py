from fastapi import FastAPI

app = FastAPI(title="Platform API")

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}