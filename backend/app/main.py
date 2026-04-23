from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers.auth_routes import router as auth_router
from .routers.form import router as form_router
from .routers.coupon import router as coupon_router
from .routers.query import router as query_router

app = FastAPI(title="DevOps Lesson API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(form_router)
app.include_router(coupon_router)
app.include_router(query_router)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "DevOps Lesson API", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "healthy"}