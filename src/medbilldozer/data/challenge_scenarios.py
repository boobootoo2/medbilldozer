"""
Challenge Scenario Data Structures
Defines the schema for MedBillDozer challenge scenarios with clinical validation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path


@dataclass
class ClinicalImage:
    """Medical image for clinical validation"""
    file_path: str  # Relative to clinical_images directory
    modality: str  # xray, mri, ct, ultrasound, histopathology
    finding: str  # Expected clinical finding
    is_abnormal: bool  # True if pathology present
    base64_data: Optional[str] = None  # Lazy-loaded for display

    def to_dict(self) -> Dict:
        return {
            "file_path": self.file_path,
            "modality": self.modality,
            "finding": self.finding,
            "is_abnormal": self.is_abnormal
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ClinicalImage':
        return cls(
            file_path=data["file_path"],
            modality=data["modality"],
            finding=data["finding"],
            is_abnormal=data["is_abnormal"]
        )


@dataclass
class MalpracticeIndicator:
    """Flags for potential malpractice"""
    is_malpractice: bool
    harm_severity: str  # none, mild, moderate, severe, critical
    outcome_description: str
    wrong_treatment: bool = False
    wrong_diagnosis: bool = False
    unnecessary_procedure: bool = False
    patient_harm: str = ""  # Description of harm

    def to_dict(self) -> Dict:
        return {
            "is_malpractice": self.is_malpractice,
            "harm_severity": self.harm_severity,
            "outcome_description": self.outcome_description,
            "wrong_treatment": self.wrong_treatment,
            "wrong_diagnosis": self.wrong_diagnosis,
            "unnecessary_procedure": self.unnecessary_procedure,
            "patient_harm": self.patient_harm
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MalpracticeIndicator':
        return cls(
            is_malpractice=data["is_malpractice"],
            harm_severity=data["harm_severity"],
            outcome_description=data["outcome_description"],
            wrong_treatment=data.get("wrong_treatment", False),
            wrong_diagnosis=data.get("wrong_diagnosis", False),
            unnecessary_procedure=data.get("unnecessary_procedure", False),
            patient_harm=data.get("patient_harm", "")
        )


@dataclass
class ChallengeScenario:
    """Complete challenge scenario with billing and clinical data"""
    scenario_id: str
    patient_name: str
    patient_avatar: str  # Emoji or icon

    # Patient profile
    patient_profile: Dict  # Demographics, medical history

    # Clinical validation (optional)
    clinical_images: List[ClinicalImage] = field(default_factory=list)

    # Billing documents
    patient_story: str = ""
    provider_bill: Dict = field(default_factory=dict)
    insurance_eob: Dict = field(default_factory=dict)

    # Expected issues
    billing_errors: List[Dict] = field(default_factory=list)
    has_billing_errors: bool = False

    # Clinical validation errors (treatment mismatch)
    clinical_errors: List[Dict] = field(default_factory=list)
    has_clinical_errors: bool = False

    # Malpractice flags
    malpractice: Optional[MalpracticeIndicator] = None

    # Difficulty and categorization
    difficulty: str = "medium"  # easy, medium, hard, expert
    category: str = "billing_only"  # billing_only, clinical_validation, combined, clean_case, malpractice
    tags: List[str] = field(default_factory=list)

    # Scoring weights
    max_score: int = 1000
    time_bonus_threshold: int = 300  # seconds

    def to_dict(self) -> Dict:
        """Convert scenario to dictionary for JSON serialization"""
        return {
            "scenario_id": self.scenario_id,
            "patient_name": self.patient_name,
            "patient_avatar": self.patient_avatar,
            "patient_profile": self.patient_profile,
            "clinical_images": [img.to_dict() for img in self.clinical_images],
            "patient_story": self.patient_story,
            "provider_bill": self.provider_bill,
            "insurance_eob": self.insurance_eob,
            "billing_errors": self.billing_errors,
            "has_billing_errors": self.has_billing_errors,
            "clinical_errors": self.clinical_errors,
            "has_clinical_errors": self.has_clinical_errors,
            "malpractice": self.malpractice.to_dict() if self.malpractice else None,
            "difficulty": self.difficulty,
            "category": self.category,
            "tags": self.tags,
            "max_score": self.max_score,
            "time_bonus_threshold": self.time_bonus_threshold
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ChallengeScenario':
        """Load scenario from dictionary"""
        clinical_images = [ClinicalImage.from_dict(img) for img in data.get("clinical_images", [])]
        malpractice = MalpracticeIndicator.from_dict(data["malpractice"]) if data.get("malpractice") else None

        return cls(
            scenario_id=data["scenario_id"],
            patient_name=data["patient_name"],
            patient_avatar=data["patient_avatar"],
            patient_profile=data["patient_profile"],
            clinical_images=clinical_images,
            patient_story=data.get("patient_story", ""),
            provider_bill=data.get("provider_bill", {}),
            insurance_eob=data.get("insurance_eob", {}),
            billing_errors=data.get("billing_errors", []),
            has_billing_errors=data.get("has_billing_errors", False),
            clinical_errors=data.get("clinical_errors", []),
            has_clinical_errors=data.get("has_clinical_errors", False),
            malpractice=malpractice,
            difficulty=data.get("difficulty", "medium"),
            category=data.get("category", "billing_only"),
            tags=data.get("tags", []),
            max_score=data.get("max_score", 1000),
            time_bonus_threshold=data.get("time_bonus_threshold", 300)
        )

    def save_to_file(self, directory: Path):
        """Save scenario to JSON file"""
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{self.scenario_id}.json"

        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

        return file_path

    @classmethod
    def load_from_file(cls, file_path: Path) -> 'ChallengeScenario':
        """Load scenario from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


def load_all_scenarios(base_dir: Path) -> List[ChallengeScenario]:
    """Load all scenarios from directory structure"""
    scenarios = []

    if not base_dir.exists():
        return scenarios

    # Walk through all subdirectories and load JSON files
    for json_file in base_dir.rglob("*.json"):
        try:
            scenario = ChallengeScenario.load_from_file(json_file)
            scenarios.append(scenario)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")

    return scenarios
