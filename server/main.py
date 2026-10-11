from fastapi import FastAPI
from auth import router as auth_router
from applications import router as applications_router

app = FastAPI(title="Job Tracker API")
app.include_router(auth_router)
app.include_router(applications_router)

@app.get("/health")
def health():
    return {"status": "ok"}
