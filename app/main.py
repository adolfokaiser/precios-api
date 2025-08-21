from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .auth import router as auth_router
from .profile import router as profile_router
from .prices import router as prices_router
from .upload import router as upload_router

# Inicializa la aplicación FastAPI
app = FastAPI(title="Precios API", debug=True)

# Ruta raíz: redirige a la documentación interactiva
@app.get("/")
def root():
    return RedirectResponse(url="/docs")

# Endpoint de prueba para verificar que el servicio esté en línea
@app.get("/health")
def health():
    return {"status": "ok"}

# Registro de los distintos módulos (rutas) en la API
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(prices_router)
app.include_router(upload_router)
