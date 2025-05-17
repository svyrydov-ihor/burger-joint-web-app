from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .logging import configure_logging, LogLevels
from src.endpoints.customer import router as customer_router
from src.endpoints.burger import router as burger_router
from src.endpoints.order import router as order_router
from src.endpoints.ingredient import router as ingredient_router
from src.endpoints.web_pages import router as web_pages_router

configure_logging(LogLevels.info)

app = FastAPI()

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

app.include_router(web_pages_router)
app.include_router(customer_router)
app.include_router(burger_router)
app.include_router(order_router)
app.include_router(ingredient_router)