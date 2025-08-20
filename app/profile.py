from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

from .auth import get_current_user, UserPublic, fake_users_db

router = APIRouter(tags=["profile"])

# ---- GET /profile
@router.get("/profile", response_model=UserPublic)
def read_profile(current: UserPublic = Depends(get_current_user)):
    return current

# ---- PUT /profile (actualiza nombre y/o email)
class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

@router.put("/profile", response_model=UserPublic)
def update_profile(
    payload: ProfileUpdate,
    current: UserPublic = Depends(get_current_user),
):
    if payload.name is None and payload.email is None:
        raise HTTPException(status_code=400, detail="Nada que actualizar")

    # registro actual
    rec = fake_users_db.get(current.email)
    if not rec:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # actualizar nombre
    if payload.name is not None:
        rec["name"] = payload.name

    # actualizar email (mover la clave del "DB" en memoria)
    new_email = current.email
    if payload.email is not None:
        new_email = payload.email.lower()
        if new_email != current.email and new_email in fake_users_db:
            raise HTTPException(status_code=400, detail="Email ya registrado")
        # mover registro si cambia
        if new_email != current.email:
            rec["email"] = new_email
            fake_users_db[new_email] = rec
            del fake_users_db[current.email]

    return UserPublic(email=new_email, name=rec["name"])
