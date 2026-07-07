from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="星运日记", version="0.1.0")

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


@app.get("/")
def root():
    return {"app": "星运日记", "version": "0.1.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


module_load_error = None
module_load_traceback = None

try:
    from app.core.config import settings
    from app.core.database import Base, engine, auto_migrate
    from app.api import auth, users, charts, match, share, bazi, admin, fortune

    Base.metadata.create_all(bind=engine)
    auto_migrate()

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(charts.router, prefix="/api/v1")
    app.include_router(match.router, prefix="/api/v1")
    app.include_router(share.router, prefix="/api/v1")
    app.include_router(bazi.router, prefix="/api/v1")
    app.include_router(admin.router, prefix="/api/v1")
    app.include_router(fortune.router, prefix="/api/v1")

    print("All modules loaded successfully!")
except Exception as e:
    module_load_error = str(e)
    import traceback
    module_load_traceback = traceback.format_exc()
    print(f"Warning: Some modules failed to load: {e}")
    print(module_load_traceback)


@app.get("/debug/load-error")
def load_error():
    if module_load_error:
        return {"error": module_load_error, "traceback": module_load_traceback}
    return {"status": "all modules loaded successfully"}