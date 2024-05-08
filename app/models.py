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


class InstrumentFileUrls(BaseModel):
    guitar: str
    drums: str
    bass: str
    vocal: str


class AnalysisResponse(BaseModel):
    files: Optional[InstrumentFileUrls] = None
    success: bool
    error_message: Optional[str] = None
