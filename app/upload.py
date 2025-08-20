from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from io import BytesIO
import re

# Dependencia de auth
from .auth import get_current_user, UserPublic

# Intentamos importar; si faltan, levantamos error claro
try:
    import openpyxl
except Exception:  # pragma: no cover
    openpyxl = None

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover
    PdfReader = None

router = APIRouter(prefix="/upload", tags=["upload"])

# Patrones de ejemplo (elige uno que aparezca en tus archivos):
RFC_PATTERN = re.compile(r"\b([A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3})\b")
STATION_PATTERN = re.compile(r"\b[A-Z]{4}\d{4}\b")  # p.ej. ACAP1234

class UploadResult(BaseModel):
    filename: str
    kind: str                       # pdf|excel
    extracted: Optional[str] = None # primer match
    candidates: List[str] = []      # todos los matches encontrados

def _find_matches(text: str) -> List[str]:
    if not text:
        return []
    c = set()
    c.update(RFC_PATTERN.findall(text))
    c.update(STATION_PATTERN.findall(text))
    return list(c)

def _error_500(msg: str) -> HTTPException:
    return HTTPException(status_code=500, detail=msg)

@router.post("", response_model=UploadResult)
async def upload_file(
    file: UploadFile = File(...),
    _: UserPublic = Depends(get_current_user),
):
    ct = (file.content_type or "").lower()
    data = await file.read()

    # ---- Excel (.xlsx)
    if ct in ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel") \
       or file.filename.lower().endswith(".xlsx"):
        if openpyxl is None:
            raise _error_500("openpyxl no está instalado")
        try:
            wb = openpyxl.load_workbook(BytesIO(data), read_only=True, data_only=True)
            ws = wb.active
            candidates = set()
            for row in ws.iter_rows(values_only=True):
                for cell in row:
                    if isinstance(cell, str):
                        for m in _find_matches(cell):
                            candidates.add(m)
            cand_list = sorted(candidates)
            return UploadResult(
                filename=file.filename,
                kind="excel",
                extracted=cand_list[0] if cand_list else None,
                candidates=cand_list,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Excel inválido: {e}")

    # ---- PDF
    if ct in ("application/pdf",) or file.filename.lower().endswith(".pdf"):
        if PdfReader is None:
            raise _error_500("pypdf no está instalado")
        try:
            reader = PdfReader(BytesIO(data))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            cand_list = _find_matches(text)
            return UploadResult(
                filename=file.filename,
                kind="pdf",
                extracted=cand_list[0] if cand_list else None,
                candidates=cand_list,
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF inválido: {e}")

    # ---- Tipo no permitido
    raise HTTPException(
        status_code=415,
        detail="Tipo de archivo no soportado. Sube .pdf o .xlsx",
    )
