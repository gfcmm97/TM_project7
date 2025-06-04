from fastapi import FastAPI
from routers import symptom
from medicine.routers import recommend_router  # ✅ 추가

app = FastAPI()

# 기존 라우터 유지
app.include_router(symptom.router, prefix="/symptom")

# 추천 시스템 라우터 추가
app.include_router(recommend_router.router, prefix="/api")
