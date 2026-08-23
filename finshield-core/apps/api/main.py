from fastapi import FastAPI

app = FastAPI(title="FinShield Core API")


@app.get("/health")
def health_check():
    return {"status": "ok"}