from pydantic import BaseModel, Field
from typing import Optional, Dict


class InstrumentVolumes(BaseModel):
    guitar: float
    drums: float
    bass: float
    vocal: float


class BalanceResponse(BaseModel):
    volumes: Optional[InstrumentVolumes] = None
    success: bool
    error_message: Optional[str] = None
