from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import init_db
from routers.auth_router import router as auth_router
from routers.chat_router import router as chat_router
from routers.message_router import router as message_router
from routers.websocket_router import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database
    await init_db()
    yield
    # Shutdown: cleanup
    pass


app = FastAPI(title="ChatAPP API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(message_router, prefix="/api")
app.include_router(ws_router)
