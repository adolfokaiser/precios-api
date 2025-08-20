from fastapi import FastAPI
from .auth import router as auth_router
from .profile import router as profile_router
from .prices import router as prices_router
from .upload import router as upload_router

app = FastAPI(title="Precios API", debug=True)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(prices_router) 
app.include_router(upload_router)
