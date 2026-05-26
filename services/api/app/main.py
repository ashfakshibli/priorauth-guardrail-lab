from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import cases, runs, queue
from app.seed import seed

Base.metadata.create_all(bind=engine)
seed()

app = FastAPI(
    title="PriorAuth Guardrail Lab API",
    description=(
        "Synthetic prior authorization decision engine with guardrails and eval tracing. "
        "DEMO DATA ONLY — no real patient data."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(runs.router)
app.include_router(queue.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "priorauth-guardrail-lab-api"}
