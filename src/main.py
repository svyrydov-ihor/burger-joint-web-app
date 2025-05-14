from fastapi import FastAPI
from .logging import configure_logging, LogLevels

configure_logging(LogLevels.info)

app = FastAPI()