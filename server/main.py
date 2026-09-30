from fastapi import FastAPI
from routes.round_routes import router as round_router

app = FastAPI(title="Family Screen-Time FA Coordinator", version="0.1")
app.include_router(round_router)