from fastapi import FastAPI
from routers import entities, cases

app = FastAPI(title="FinShield Core API")

app.include_router(entities.router)
app.include_router(cases.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}