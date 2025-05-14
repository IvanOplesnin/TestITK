from fastapi import FastAPI
from backend.api import wallet_router

app = FastAPI()

app.include_router(wallet_router)
