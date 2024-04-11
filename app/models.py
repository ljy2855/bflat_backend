from pydantic import BaseModel, Field
from typing import Optional, Dict


class InstrumentVolumes(BaseModel):
    guitar: float
    drums: float
    bass: float
    vocal: float


class BalanceResponse(BaseModel):
    volumes: InstrumentVolumes
    success: bool
    error_message: Optional[str] = None
