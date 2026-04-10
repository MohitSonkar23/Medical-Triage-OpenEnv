from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import random

class UrgencyLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"

class VitalSign(BaseModel):
    heart_rate: int = Field(..., ge=40, le=200)
    blood_pressure: str = Field(...)  # "120/80"
    respiratory_rate: int = Field(..., ge=5, le=60)
    oxygen_saturation: float = Field(..., ge=70, le=100)
    temperature: float = Field(..., ge=30, le=42)

class Symptom(BaseModel):
    name: str
    severity: int = Field(..., ge=1, le=10)

class PatientState(BaseModel):
    patient_id: str
    name: str
    age: int = Field(..., ge=0, le=120)
    symptoms: List[Symptom] = []
    vitals: VitalSign
    history: List[str] = []
    allergies: List[str] = []
    time_step: int = 0
    deterioration_rate: float = Field(0.0, ge=0.0, le=1.0)
    
    @property
    def true_urgency(self) -> UrgencyLevel:
        """Gold standard urgency calculation"""
        hr = self.vitals.heart_rate
        rr = self.vitals.respiratory_rate
        o2 = self.vitals.oxygen_saturation
        temp = self.vitals.temperature
        severity_score = sum(s.severity for s in self.symptoms)
        
        score = 0
        if hr > 120 or hr < 60: score += 3
        if rr > 30 or rr < 12: score += 3
        if o2 < 92: score += 4
        if temp > 40 or temp < 35: score += 2
        score += min(severity_score, 10)
        
        if score >= 12: return UrgencyLevel.RED
        if score >= 7: return UrgencyLevel.YELLOW
        return UrgencyLevel.GREEN

class Diagnosis(str, Enum):
    SEPSIS = "sepsis"
    HEART_ATTACK = "myocardial_infarction"
    PNEUMONIA = "pneumonia"
    FRACTURE = "fracture"
    STROKE = "stroke"
    NONE = "none"

class Treatment(BaseModel):
    diagnosis: Diagnosis
    medication: str
    dosage: str
    instructions: str