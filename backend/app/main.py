from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import Base, engine, auto_migrate
from app.api import auth, users, charts, match, share, bazi, admin, fortune
from app.models.models import User, Chart

Base.metadata.create_all(bind=engine)
auto_migrate()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "type": type(exc).__name__}
    )

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(charts.router, prefix="/api/v1")
app.include_router(match.router, prefix="/api/v1")
app.include_router(share.router, prefix="/api/v1")
app.include_router(bazi.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(fortune.router, prefix="/api/v1")


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
