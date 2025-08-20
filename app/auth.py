from datetime import datetime, timedelta, timezone
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "dev-secret-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# "DB" en memoria por ahora
fake_users_db: Dict[str, Dict] = {}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserPublic(BaseModel):
    email: EmailStr
    name: str

def get_password_hash(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pwd_context.verify(p, hashed)

def create_access_token(sub: str):
    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic, status_code=201)
def register(user: UserCreate):
    email = user.email.lower()
    if email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    fake_users_db[email] = {
        "email": email,
        "name": user.name,
        "hashed_password": get_password_hash(user.password),
    }
    return {"email": email, "name": user.name}

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    email = form.username.lower()
    user = fake_users_db.get(email)
    if not user or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")
    return {
        "access_token": create_access_token(email),
        "token_type": "bearer"   # <- importante
    }

def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = fake_users_db.get(email)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return UserPublic(email=email, name=user["name"])

