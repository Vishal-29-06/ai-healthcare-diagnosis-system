from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import auth, doctors, appointments, records

# This creates the actual FastAPI application object.
# The title/description/version show up automatically in the
# auto-generated docs at /docs — nice touch for a portfolio project.
app = FastAPI(
    title="AI Healthcare Diagnosis & Hospital Management System",
    description="Predicts disease risk from patient data while managing hospital operations.",
    version="0.1.0",
)

# Tells FastAPI: "any file inside app/static should be served directly"
# e.g. app/static/css/style.css becomes available at /static/css/style.css
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Tells FastAPI where to find our HTML template files
templates = Jinja2Templates(directory="app/templates")

# Registers every route defined in app/routers/auth.py onto our app.
# Because that router had prefix="/auth", these become:
# POST /auth/signup, POST /auth/login, GET /auth/me
app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(records.router)


@app.get("/")
def home(request: Request):
    """
    This is a 'path operation' — @app.get('/') means:
    'when someone visits the root URL with a GET request, run this function.'
    We return a rendered HTML page instead of raw JSON here, since it's
    a page a human will actually look at.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    """
    A simple endpoint to confirm the API itself is alive.
    Visit /docs and you'll see this listed automatically.
    """
    return {"status": "ok", "message": "API is running"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    """
    This route proves the MySQL connection actually works.
    Depends(get_db) is FastAPI's dependency injection in action:
    it runs get_db(), hands us a working `db` session, and closes
    it automatically when this function finishes.
    """
    result = db.execute(text("SELECT 1")).scalar()
    return {"database_connected": result == 1}
