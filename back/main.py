from fastapi import FastAPI
from pydantic import BaseModel
from routers import symptom, location_router, distance_router, recommend_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(symptom.router, prefix="/symptom")
app.include_router(location_router.router, prefix="/location")
app.include_router(distance_router.router, prefix="/distance")
app.include_router(recommend_router.router, prefix="/recommend")

class MedRequest(BaseModel):
    medicine: str

@app.post("/medicine-info")
def get_medicine_info(req: MedRequest):
    return {"result": f"{req.medicine}은(는) 복용 시 충분한 수분 섭취와 휴식이 권장됩니다. 필요시 병원 방문을 고려하세요."}