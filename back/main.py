from fastapi import FastAPI
from routers import symptom

app = FastAPI()

app.include_router(symptom.router, prefix="/symptom")
