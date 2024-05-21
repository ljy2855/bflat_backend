from pydantic import BaseModel, Field
from typing import Optional, Dict


class InstrumentVolumes(BaseModel):
    other: float
    drums: float
    bass: float
    vocals: float


class BalanceResponse(BaseModel):
    volumes: Optional[InstrumentVolumes] = None
    success: bool
    error_message: Optional[str] = None


class InstrumentFileUrls(BaseModel):
    other: str
    drums: str
    bass: str
    vocals: str


class AnalysisResponse(BaseModel):
    files: Optional[InstrumentFileUrls] = None
    success: bool
    error_message: Optional[str] = None

class BPMMeter:
    def __init__(self, bpm, meter):
        self.bpm = bpm
        self.meter = meter