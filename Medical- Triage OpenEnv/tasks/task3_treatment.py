from environment import MedicalTriageEnv
from models.actions import AgentAction, TreatmentAction
from models.patient import Diagnosis

def grade_treatment_planning(env: MedicalTriageEnv, action: AgentAction) -> float:
    """Clinical guideline compliance score"""
    if not action.treatment:
        return 0.0
    
    patient = list(env.patients.values())[0]
    true_diagnosis = env._get_true_diagnosis(patient)
    
    # Diagnosis accuracy (70% weight)
    dx_score = 1.0 if action.treatment.diagnosis == true_diagnosis else 0.0
    
    # Treatment appropriateness (30% weight)
    treatment_score = 1.0 if _is_appropriate_treatment(action.treatment, patient) else 0.3
    
    return 0.7 * dx_score + 0.3 * treatment_score

def _is_appropriate_treatment(treatment: TreatmentAction, patient: PatientState) -> bool:
    # Simplified clinical logic
    if treatment.diagnosis == Diagnosis.SEPSIS:
        return "antibiotics" in treatment.treatment.medication.lower()
    return True

def run_treatment_baseline(env: MedicalTriageEnv) -> float:
    """Random baseline for Task 3"""
    action = AgentAction(
        task_type="treatment_planning",
        treatment=TreatmentAction(
            diagnosis=Diagnosis.NONE,
            treatment=None  # Simplified
        )
    )
    _, reward, _, _ = env.step(action)
    return reward