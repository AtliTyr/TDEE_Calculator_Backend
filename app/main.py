from fastapi import FastAPI

app = FastAPI(title="FastAPI Backend")

@app.get("/health")
async def health():
    return {"status": "ok"}
