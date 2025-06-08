from fastapi import FastAPI
from pydantic import BaseModel
from routers import symptom, location_router, distance_router, recommend_router, medicine_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(symptom.router)
app.include_router(location_router.router)
app.include_router(distance_router.router)
app.include_router(recommend_router.router)
app.include_router(medicine_router.router)

class MedRequest(BaseModel):
    medicine: str
