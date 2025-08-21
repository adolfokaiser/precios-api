
Precios API – FastAPI + JWT + Upload (PDF/XLSX)

API REST para gestión de precios por estación/fecha/producto con autenticación JWT, CRUD del recurso principal y análisis de archivos (PDF/XLSX) para extraer un dato (RFC o código de estación). Documentación interactiva en Swagger.

Live: https://precios-api-zhs8.onrender.com

Docs: https://precios-api-zhs8.onrender.com/docs

1) Stack breve

FastAPI, Uvicorn

Pydantic (validaciones)

JWT con python-jose + passlib[bcrypt]

openpyxl (Excel), pypdf (PDF)

pytest (tests), python-dotenv (.env)

Persistencia en memoria (propósito demo)

2) Variables de entorno

Crea un archivo .env en la raíz:

SECRET_KEY=super-secret-dev
ACCESS_TOKEN_EXPIRE_MINUTES=60


Cambia SECRET_KEY en ambientes reales.

3) Cómo correr (local)

Requisitos: Python 3.10+ (o 3.8+ compatible)

python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload


Abre: http://127.0.0.1:8000/docs

4) Docker (local / despliegue)
# build
docker build -t precios-api .

# run (leyendo variables desde .env)
docker run -d -p 8000:8000 --env-file .env --name precios-api-cnt precios-api

5) Endpoints clave
Autenticación y perfil

POST /auth/register – registro (email, name, password)

POST /auth/login – OAuth2 Password → access_token (JWT)

GET /profile – datos del usuario autenticado

PUT /profile – actualizar name y/o email

Recurso principal (precios)

POST /prices – crear precio

GET /prices – filtros station_id, date_from, date_to · búsqueda q · paginación page, limit

GET /prices/{price_id} – obtener por id

PUT /prices/{price_id} – actualizar

DELETE /prices/{price_id} – eliminar

Análisis de archivos

POST /upload – subir PDF o .xlsx
→ valida tipo; extrae un dato (RFC/código estación) y devuelve { filename, kind, extracted, candidates }

Salud

GET /health – {"status":"ok"}

6) Cómo probar rápido en /docs

Register → POST /auth/register

{ "email": "test@mail.com", "name": "Test", "password": "123456" }


Authorize (candado) → username=test@mail.com, password=123456.

Crear precio → POST /prices

{
  "station_id": "ACAP1234",
  "date": "2025-08-19",
  "product": "Regular",
  "price": 23.19,
  "currency": "MXN",
  "notes": "Carga inicial"
}


Listar → GET /prices?station_id=ACAP1234&date_from=2025-08-19&date_to=2025-08-21&q=carga&page=1&limit=10.

7) Manejo de errores (ejemplos)

401 sin token o token inválido (rutas protegidas)

415 en POST /upload si el tipo de archivo no es PDF/XLSX

400 en POST /upload por errores de parsing con mensaje claro

422 validaciones (p. ej., price > 0, product ∈ {Regular,Premium,Diesel})

8) Pruebas
pip install pytest
pytest -q


Incluye pruebas de integración básicas para auth y upload.

9) Mapeo contra los requisitos
Requisitos funcionales (mínimos)

Auth & autorización

Registro/login  (/auth/register, /auth/login)

JWT access token  (refresh opcional; no requerido)

Middleware / dependencia para rutas protegidas 

Perfil de usuario

GET /profile 

PUT /profile 

CRUD recurso principal

Precios: modelo + POST/GET/GET by id/PUT/DELETE 

GET /prices con filtros (1–2+), búsqueda global y paginación 

Análisis de archivos

POST /upload PDF/Excel 

Validación de tipo y manejo de errores 

Extraer y devolver un dato específico (RFC/código) 

Despliegue

Dockerfile 

README con pasos local/nube 

Live (Render)  https://precios-api-zhs8.onrender.com

Requisitos no funcionales

Código modular, organizado, legible  (app/auth.py, profile.py, prices.py, upload.py, main.py)

Documentación Swagger/OpenAPI  (/docs)

Manejo consistente de errores 

Pruebas mínimas (auth y upload) 

Variables .env 

Lenguaje: Python (se prefiere tipado, pero no obligatorio) 

10) Credenciales de prueba

Usuario: test@mail.com

Password: 123456

Puedes crearlo en POST /auth/register o usar tus propios datos.

11) Estructura mínima del proyecto
app/
  auth.py       # registro/login + JWT
  profile.py    # GET/PUT perfil
  prices.py     # CRUD + filtros/búsqueda/paginación
  upload.py     # análisis PDF/XLSX
  main.py       # FastAPI app + routers
tests/
  test_auth.py
  test_upload.py
Dockerfile
requirements.txt
.env.example
README.md

