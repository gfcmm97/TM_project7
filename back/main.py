from fastapi import FastAPI
from routers import symptom, location_router, distance_router

app = FastAPI()

app.include_router(symptom.router, prefix="/symptom")
app.include_router(location_router.router, prefix="/location")
app.include_router(distance_router.router, prefix="/distance")