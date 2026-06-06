"""Point d'entrée de l'application FastAPI."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.routers import auth, grades, students, transcripts
from app.seed import seed_admin

settings = get_settings()
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crée les tables et le compte admin au démarrage.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "API REST de gestion des étudiants : authentification par rôle "
        "(admin / enseignant / étudiant), CRUD des fiches étudiants, "
        "gestion des notes et export des relevés (CSV / PDF)."
    ),
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(grades.router)
app.include_router(transcripts.router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Sonde de santé utilisée par Docker et Kubernetes."""
    return {"status": "ok", "version": __version__}


if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")
