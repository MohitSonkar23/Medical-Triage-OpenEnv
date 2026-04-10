from typing import Dict, Any, Optional, Tuple, List
import random
from pydantic import Field, BaseModel
from enum import Enum

# Inline models to avoid import issues
class UrgencyLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"

class Diagnosis(str, Enum):
    SEPSIS = "sepsis"
    HEART_ATTACK = "myocardial_infarction"
    PNEUMONIA = "pneumonia"
    FRACTURE = "fracture"
    STROKE = "stroke"
    NONE = "none"

class VitalSign(BaseModel):
    heart_rate: int = Field(..., ge=40, le=200)
    blood_pressure: str = Field(...)  
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

class MedicalTriageEnv:
    def __init__(self, task_type: str = "triage_priority"):
        self.task_type = task_type
        self.max_steps = 20
        self.current_step = 0
        self.patients: Dict[str, PatientState] = {}
        self.reset()
    
    def reset(self) -> Dict[str, Any]:
        self.current_step = 0
        if self.task_type == "triage_priority":
            self.patients = {"p1": self._generate_patient()}
        elif self.task_type == "er_queue_management":
            self.patients = {f"p{i}": self._generate_patient(deterioration_rate=random.uniform(0.05, 0.2)) 
                           for i in range(1, 6)}
        else:  # treatment_planning
            self.patients = {"p1": self._generate_complex_patient()}
        
        obs = self._get_observation()
        return {"observation": obs, "state": self.get_state()}
    
    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        self.current_step += 1
        
        for patient in self.patients.values():
            self._deteriorate_patient(patient)
        
        reward = self._compute_reward(action)
        done = self.current_step >= self.max_steps
        obs = self._get_observation()
        
        return {
            "observation": obs,
            "reward": reward,
            "done": done,
            "info": {"step": self.current_step}
        }, reward, done, {}
    
    def _generate_patient(self, deterioration_rate: float = 0.1) -> PatientState:
        return PatientState(
            patient_id="p1",
            name="John Doe",
            age=random.randint(25, 85),
            symptoms=[Symptom(name="chest_pain", severity=random.randint(3, 10))],
            vitals=VitalSign(
                heart_rate=random.randint(60, 140),
                blood_pressure=f"{random.randint(90, 180)}/{random.randint(60, 110)}",
                respiratory_rate=random.randint(12, 35),
                oxygen_saturation=round(random.uniform(88, 99), 1),
                temperature=round(random.uniform(36.5, 39.5), 1)
            ),
            deterioration_rate=deterioration_rate
        )
    
    def _generate_complex_patient(self) -> PatientState:
        return PatientState(
            patient_id="p1",
            name="Jane Smith",
            age=65,
            symptoms=[
                Symptom(name="fever", severity=8),
                Symptom(name="shortness_of_breath", severity=7),
                Symptom(name="confusion", severity=6)
            ],
            vitals=VitalSign(
                heart_rate=115,
                blood_pressure="90/60",
                respiratory_rate=28,
                oxygen_saturation=89.5,
                temperature=39.2
            ),
            history=["diabetes", "recent_surgery"],
            allergies=["penicillin"],
            deterioration_rate=0.15
        )
    
    def _deteriorate_patient(self, patient: PatientState):
        patient.time_step += 1
        if patient.deterioration_rate > 0:
            patient.vitals.heart_rate = min(200, patient.vitals.heart_rate + int(random.gauss(2, 1)))
            patient.vitals.respiratory_rate = min(60, patient.vitals.respiratory_rate + int(random.gauss(1, 0.5)))
            patient.vitals.oxygen_saturation = max(70, patient.vitals.oxygen_saturation - random.uniform(0.5, 2))
    
    def _get_observation(self) -> Dict[str, Any]:
        if self.task_type == "triage_priority":
            p = list(self.patients.values())[0]
            return {
                "patient": {
                    "id": p.patient_id,
                    "name": p.name,
                    "age": p.age,
                    "symptoms": [s.dict() for s in p.symptoms],
                    "vitals": p.vitals.dict()
                }
            }
        return {"patients": [p.dict() for p in self.patients.values()]}
    
    def _compute_reward(self, action: Dict[str, Any]) -> float:
        if self.task_type == "triage_priority":
            predicted = action.get("triage", {}).get("urgency", "GREEN")
            patient = list(self.patients.values())[0]
            return 1.0 if predicted == patient.true_urgency else 0.0
        return 0.5  # Default reward
    
    def get_state(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type,
            "step": self.current_step,
            "patients": {pid: p.dict() for pid, p in self.patients.items()}
        }

if __name__ == "__main__":
    env = MedicalTriageEnv()
    print("✅ Environment Working!")
    obs = env.reset()
    print("Sample observation:", obs["observation"])