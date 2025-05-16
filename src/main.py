from fastapi import FastAPI

from .logging import configure_logging, LogLevels
from src.endpoints.customer import router as customer_router
from src.endpoints.burger import router as burger_router
from src.endpoints.order import router as order_router
from src.endpoints.ingredient import router as ingredient_router

configure_logging(LogLevels.info)

app = FastAPI()
app.include_router(customer_router)
app.include_router(burger_router)
app.include_router(order_router)
app.include_router(ingredient_router)