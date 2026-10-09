from fastapi import FastAPI, Depends 
from fastapi.middleware.cors import CORSMiddleware
from routers import entities, cases
from auth import require_api_key

app = FastAPI(title="FinShield Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(entities.router, dependencies=[Depends(require_api_key)])
app.include_router(cases.router, dependencies=[Depends(require_api_key)])

@app.get("/health")
def health_check():
    return {"status": "ok"}