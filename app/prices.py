from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from .auth import get_current_user, UserPublic

router = APIRouter(prefix="/prices", tags=["prices"])

# Modelos
class FuelEnum(str, Enum):
    Regular = "Regular"
    Premium = "Premium"
    Diesel = "Diesel"

class PriceIn(BaseModel):
    station_id: str = Field(min_length=3, max_length=20)
    date: date
    product: FuelEnum
    price: float = Field(gt=0)
    currency: str = "MXN"
    notes: Optional[str] = None

class PriceOut(PriceIn):
    id: int
    created_by: str
    created_at: datetime

class PriceList(BaseModel):
    items: List[PriceOut]
    page: int
    limit: int
    total: int

# Almacenamiento en memoria (solo para pruebas)
_prices_db: Dict[int, PriceOut] = {}
_id = 0

def _next_id() -> int:
    """Genera un ID incremental (no concurrente)."""
    global _id
    _id += 1
    return _id

# Compatibilidad Pydantic v1/v2
def to_dict(model):
    """Devuelve el dict del modelo para Pydantic v1 o v2."""
    return model.model_dump() if hasattr(model, "model_dump") else model.dict()

@router.post("", response_model=PriceOut, status_code=201)
def create_price(payload: PriceIn, user: UserPublic = Depends(get_current_user)):
    """Crear un precio nuevo."""
    item = PriceOut(
        id=_next_id(),
        created_by=user.email,
        created_at=datetime.utcnow(),  # UTC naive
        **to_dict(payload),
    )
    _prices_db[item.id] = item
    return item

@router.get("", response_model=PriceList)
def list_prices(
    station_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    q: Optional[str] = None,  # búsqueda por station_id/notes
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    _: UserPublic = Depends(get_current_user),
):
    """Listar precios con filtros y paginación."""
    items = list(_prices_db.values())

    if station_id:
        items = [x for x in items if x.station_id == station_id]
    if date_from:
        items = [x for x in items if x.date >= date_from]
    if date_to:
        items = [x for x in items if x.date <= date_to]
    if q:
        ql = q.lower()
        items = [x for x in items if ql in x.station_id.lower() or ql in (x.notes or "").lower()]

    total = len(items)
    start = (page - 1) * limit
    end = start + limit
    return PriceList(items=items[start:end], page=page, limit=limit, total=total)

@router.get("/{price_id}", response_model=PriceOut)
def get_price(price_id: int, _: UserPublic = Depends(get_current_user)):
    """Obtener un precio por ID."""
    item = _prices_db.get(price_id)
    if not item:
        raise HTTPException(status_code=404, detail="No encontrado")
    return item

@router.put("/{price_id}", response_model=PriceOut)
def update_price(price_id: int, payload: PriceIn, user: UserPublic = Depends(get_current_user)):
    """Reemplazar un precio existente."""
    if price_id not in _prices_db:
        raise HTTPException(status_code=404, detail="No encontrado")

    updated = PriceOut(
        id=price_id,
        created_by=user.email,
        created_at=datetime.utcnow(),
        **to_dict(payload),
    )
    _prices_db[price_id] = updated
    return updated

@router.delete("/{price_id}", status_code=204)
def delete_price(price_id: int, _: UserPublic = Depends(get_current_user)):
    """Eliminar un precio por ID."""
    if price_id not in _prices_db:
        raise HTTPException(status_code=404, detail="No encontrado")
    del _prices_db[price_id]
