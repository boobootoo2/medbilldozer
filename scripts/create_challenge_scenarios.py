"""
Challenge Scenario Generator
Creates 10-15 initial scenarios for the MedBillDozer challenge
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.medbilldozer.data.challenge_scenarios import (
    ChallengeScenario,
    ClinicalImage,
    MalpracticeIndicator
)


def create_sarah_scenario() -> ChallengeScenario:
    """Convert Sarah's scenario to new format"""
    return ChallengeScenario(
        scenario_id="scenario_001_sarah_billing",
        patient_name="Sarah",
        patient_avatar="👩‍⚕️",
        patient_profile={
            "age": 35,
            "gender": "Female",
            "insurance": "Blue Cross Gold Plan",
            "deductible": 1500,
            "deductible_met": 800
        },
        patient_story="""**Patient Story: Sarah's 2026 Medical Journey**

In March 2026, I visited Dr. Jennifer Wu at Metro Medical Center for persistent headaches.
After a thorough examination, Dr. Wu ordered an MRI scan which was performed on March 15, 2026.
The MRI cost was $1,200 and was deemed medically necessary.

I have Blue Cross Gold Plan insurance with a $1,500 deductible (already met $800 from earlier visits)
and 80/20 coinsurance after deductible. My out-of-pocket maximum is $5,000.

The diagnosis was tension headaches, and I was prescribed physical therapy (10 sessions at $150 each).
I completed 8 sessions between April and May 2026.""",
        provider_bill={
            "date": "2026-03-20",
            "provider": "Metro Medical Center",
            "items": [
                {"service": "Office Visit - Level 4", "code": "99214", "charge": 250.00, "error": None},
                {"service": "MRI Brain without contrast", "code": "70551", "charge": 1200.00, "error": None},
                {"service": "MRI Brain with contrast", "code": "70553", "charge": 800.00, "error": "Not performed - duplicate billing"},
                {"service": "Physical Therapy - 8 sessions", "code": "97110", "charge": 1200.00, "error": None},
                {"service": "Physical Therapy - 5 sessions", "code": "97110", "charge": 750.00, "error": "Only 8 sessions total, not 13"},
            ],
            "total": 4200.00
        },
        insurance_eob={
            "date": "2026-04-10",
            "plan": "Blue Cross Gold Plan",
            "items": [
                {"service": "Office Visit - Level 4", "billed": 250.00, "allowed": 200.00, "paid": 120.00, "patient_responsibility": 80.00},
                {"service": "MRI Brain without contrast", "billed": 1200.00, "allowed": 800.00, "paid": 100.00, "patient_responsibility": 700.00},
                {"service": "MRI Brain with contrast", "billed": 800.00, "allowed": 600.00, "paid": 480.00, "patient_responsibility": 120.00},
                {"service": "Physical Therapy - 13 sessions", "billed": 1950.00, "allowed": 1200.00, "paid": 960.00, "patient_responsibility": 240.00},
            ],
            "total_paid": 1660.00,
            "patient_owes": 1140.00
        },
        billing_errors=[
            {
                "id": "B1",
                "severity": "High",
                "category": "Duplicate Billing",
                "description": "MRI with contrast ($800) was not performed according to patient story, but was billed and partially paid by insurance.",
                "provider_charge": 800.00,
                "insurance_paid": 480.00,
                "potential_savings": 800.00
            },
            {
                "id": "B2",
                "severity": "High",
                "category": "Quantity Mismatch",
                "description": "Physical therapy billed for 13 sessions (5+8) but patient only received 8 sessions according to medical records.",
                "provider_charge": 750.00,
                "insurance_paid": 960.00,
                "potential_savings": 750.00
            }
        ],
        has_billing_errors=True,
        has_clinical_errors=False,
        difficulty="medium",
        category="billing_only",
        tags=["duplicate_billing", "quantity_mismatch", "headaches"],
        max_score=1000
    )


def create_marcus_scenario() -> ChallengeScenario:
    """Convert Marcus's scenario to new format"""
    return ChallengeScenario(
        scenario_id="scenario_002_marcus_billing",
        patient_name="Marcus",
        patient_avatar="👨‍⚕️",
        patient_profile={
            "age": 42,
            "gender": "Male",
            "insurance": "Aetna Silver Plan",
            "deductible": 2000,
            "deductible_met": 300
        },
        patient_story="""**Patient Story: Marcus's 2026 Medical Journey**

In February 2026, I had an emergency room visit at City Hospital for severe abdominal pain.
The ER physician, Dr. Michael Torres, ordered a CT scan and bloodwork on February 20, 2026.
The total ER visit cost was $3,500, including a $200 CT scan and $150 lab work.

I have Aetna Silver Plan with a $2,000 deductible (only $300 met previously) and 70/30 coinsurance.
My out-of-pocket maximum is $6,500 annually.

The diagnosis was gastritis, and I was prescribed medication (Omeprazole) for 3 months.
I also had a follow-up visit with a gastroenterologist in March ($250 specialist visit).""",
        provider_bill={
            "date": "2026-02-25",
            "provider": "City Hospital Emergency Department",
            "items": [
                {"service": "ER Visit - Level 5", "code": "99285", "charge": 2500.00, "error": None},
                {"service": "CT Abdomen without contrast", "code": "74150", "charge": 1200.00, "error": "Should be $200"},
                {"service": "CT Abdomen with contrast", "code": "74160", "charge": 950.00, "error": "Not performed"},
                {"service": "Blood Work - Comprehensive", "code": "80053", "charge": 150.00, "error": None},
                {"service": "IV Administration", "code": "96374", "charge": 300.00, "error": None},
                {"service": "Gastroenterology Consult", "code": "99253", "charge": 450.00, "error": "This was a separate follow-up, not ER"},
            ],
            "total": 5550.00
        },
        insurance_eob={
            "date": "2026-03-15",
            "plan": "Aetna Silver Plan",
            "items": [
                {"service": "ER Visit - Level 5", "billed": 2500.00, "allowed": 2000.00, "paid": 200.00, "patient_responsibility": 1800.00},
                {"service": "CT Abdomen without contrast", "billed": 1200.00, "allowed": 200.00, "paid": 0.00, "patient_responsibility": 200.00},
                {"service": "CT Abdomen with contrast", "billed": 950.00, "allowed": 800.00, "paid": 130.00, "patient_responsibility": 670.00},
                {"service": "Blood Work", "billed": 150.00, "allowed": 120.00, "paid": 0.00, "patient_responsibility": 120.00},
                {"service": "IV Administration", "billed": 300.00, "allowed": 250.00, "paid": 0.00, "patient_responsibility": 250.00},
                {"service": "Gastroenterology Consult", "billed": 450.00, "allowed": 250.00, "paid": 0.00, "patient_responsibility": 250.00},
            ],
            "total_paid": 330.00,
            "patient_owes": 3290.00
        },
        billing_errors=[
            {
                "id": "BY1",
                "severity": "High",
                "category": "Service Not Rendered",
                "description": "CT scan with contrast ($950) was not performed - only CT without contrast was done per medical records.",
                "provider_charge": 950.00,
                "insurance_paid": 130.00,
                "potential_savings": 950.00
            },
            {
                "id": "BY2",
                "severity": "High",
                "category": "Price Inflation",
                "description": "CT Abdomen without contrast billed at $1,200 but patient story indicates actual cost was $200. 600% markup.",
                "provider_charge": 1200.00,
                "insurance_paid": 0.00,
                "potential_savings": 1000.00
            },
            {
                "id": "BY3",
                "severity": "High",
                "category": "Unbundling/Separate Visit",
                "description": "Gastroenterology consult ($450) was a separate follow-up appointment in March, not part of February ER visit.",
                "provider_charge": 450.00,
                "insurance_paid": 0.00,
                "potential_savings": 250.00
            }
        ],
        has_billing_errors=True,
        has_clinical_errors=False,
        difficulty="medium",
        category="billing_only",
        tags=["price_inflation", "unbundling", "gastritis"],
        max_score=1200
    )


def create_clinical_xray_scenario() -> ChallengeScenario:
    """Clinical validation scenario with X-ray"""
    return ChallengeScenario(
        scenario_id="scenario_003_xray_overtreatment",
        patient_name="Jennifer",
        patient_avatar="👩",
        patient_profile={
            "age": 45,
            "gender": "Female",
            "insurance": "UnitedHealthcare PPO",
            "deductible": 1000,
            "deductible_met": 600
        },
        clinical_images=[
            ClinicalImage(
                file_path="xray_negative.png",
                modality="xray",
                finding="Clear lung fields, no infiltrates, no effusion",
                is_abnormal=False
            )
        ],
        patient_story="""**Patient Story: Jennifer's Routine Checkup**

In January 2026, I visited my primary care physician for a routine annual checkup.
I mentioned having a mild cough for a couple of days, but no fever or other symptoms.

The doctor ordered a chest X-ray as a precaution, which came back completely normal.
However, the doctor prescribed IV antibiotics for pneumonia and recommended hospitalization.""",
        provider_bill={
            "date": "2026-01-15",
            "provider": "Community Health Center",
            "items": [
                {"service": "Office Visit - Level 3", "code": "99213", "charge": 200.00, "error": None},
                {"service": "Chest X-ray", "code": "71046", "charge": 150.00, "error": None},
                {"service": "IV Antibiotic Administration", "code": "96365", "charge": 500.00, "error": "Not medically necessary"},
                {"service": "Hospital Admission", "code": "99221", "charge": 800.00, "error": "Not medically necessary"},
            ],
            "total": 1650.00
        },
        insurance_eob={
            "date": "2026-02-01",
            "plan": "UnitedHealthcare PPO",
            "items": [
                {"service": "Office Visit", "billed": 200.00, "allowed": 180.00, "paid": 144.00, "patient_responsibility": 36.00},
                {"service": "Chest X-ray", "billed": 150.00, "allowed": 130.00, "paid": 104.00, "patient_responsibility": 26.00},
                {"service": "IV Antibiotics", "billed": 500.00, "allowed": 450.00, "paid": 360.00, "patient_responsibility": 90.00},
                {"service": "Hospital Admission", "billed": 800.00, "allowed": 700.00, "paid": 560.00, "patient_responsibility": 140.00},
            ],
            "total_paid": 1168.00,
            "patient_owes": 292.00
        },
        billing_errors=[],
        clinical_errors=[
            {
                "id": "C1",
                "severity": "Critical",
                "category": "Overtreatment",
                "description": "X-ray shows clear lungs, but IV antibiotics and hospitalization were prescribed for pneumonia that doesn't exist.",
                "provider_charge": 1300.00,
                "insurance_paid": 920.00,
                "potential_savings": 1300.00,
                "image_finding": "Normal chest X-ray",
                "prescribed_treatment": "IV antibiotics + hospitalization"
            }
        ],
        has_billing_errors=False,
        has_clinical_errors=True,
        malpractice=MalpracticeIndicator(
            is_malpractice=True,
            harm_severity="moderate",
            outcome_description="Patient received unnecessary IV antibiotics which could lead to antibiotic resistance and allergic reactions.",
            wrong_treatment=True,
            wrong_diagnosis=True,
            unnecessary_procedure=True,
            patient_harm="Potential adverse drug reactions, unnecessary hospitalization"
        ),
        difficulty="hard",
        category="clinical_validation",
        tags=["overtreatment", "xray", "respiratory"],
        max_score=1500
    )


def create_clean_case_scenario() -> ChallengeScenario:
    """Clean case with no errors"""
    return ChallengeScenario(
        scenario_id="scenario_004_clean_case",
        patient_name="David",
        patient_avatar="👨",
        patient_profile={
            "age": 55,
            "gender": "Male",
            "insurance": "Kaiser Permanente HMO",
            "deductible": 500,
            "deductible_met": 500
        },
        patient_story="""**Patient Story: David's Routine Care**

In March 2026, I had my annual physical exam with Dr. Sarah Chen at Kaiser Permanente.
Everything went smoothly - routine blood work, blood pressure check, and cholesterol screening.

All my tests came back normal, and my doctor said to continue my current medication regimen.
The billing was straightforward and matched exactly what was performed.""",
        provider_bill={
            "date": "2026-03-10",
            "provider": "Kaiser Permanente Medical Center",
            "items": [
                {"service": "Annual Physical Exam", "code": "99395", "charge": 250.00, "error": None},
                {"service": "Lipid Panel", "code": "80061", "charge": 75.00, "error": None},
                {"service": "Complete Blood Count", "code": "85025", "charge": 50.00, "error": None},
            ],
            "total": 375.00
        },
        insurance_eob={
            "date": "2026-03-20",
            "plan": "Kaiser Permanente HMO",
            "items": [
                {"service": "Annual Physical", "billed": 250.00, "allowed": 250.00, "paid": 250.00, "patient_responsibility": 0.00},
                {"service": "Lipid Panel", "billed": 75.00, "allowed": 75.00, "paid": 75.00, "patient_responsibility": 0.00},
                {"service": "CBC", "billed": 50.00, "allowed": 50.00, "paid": 50.00, "patient_responsibility": 0.00},
            ],
            "total_paid": 375.00,
            "patient_owes": 0.00
        },
        billing_errors=[],
        clinical_errors=[],
        has_billing_errors=False,
        has_clinical_errors=False,
        difficulty="easy",
        category="clean_case",
        tags=["preventive_care", "clean"],
        max_score=500
    )


def create_clinical_mri_scenario() -> ChallengeScenario:
    """Clinical validation scenario with MRI"""
    return ChallengeScenario(
        scenario_id="scenario_005_mri_brain_tumor",
        patient_name="Robert",
        patient_avatar="👨‍🦳",
        patient_profile={
            "age": 58,
            "gender": "Male",
            "insurance": "Medicare",
            "deductible": 500,
            "deductible_met": 500
        },
        clinical_images=[
            ClinicalImage(
                file_path="mri_positive.jpg",
                modality="mri",
                finding="Mass lesion in right frontal lobe consistent with glioma",
                is_abnormal=True
            )
        ],
        patient_story="""**Patient Story: Robert's Headache Investigation**

In February 2026, I began experiencing severe headaches and occasional dizziness.
My neurologist, Dr. Sarah Mitchell, ordered an MRI which revealed a concerning mass in my brain.

The MRI showed a glioma (brain tumor) that requires immediate attention.
Dr. Mitchell recommended surgical consultation and radiation therapy planning.""",
        provider_bill={
            "date": "2026-02-20",
            "provider": "Neurology Associates",
            "items": [
                {"service": "Neurology Consultation", "code": "99244", "charge": 350.00, "error": None},
                {"service": "MRI Brain with contrast", "code": "70553", "charge": 2500.00, "error": None},
                {"service": "Neurosurgery Consultation", "code": "99244", "charge": 400.00, "error": None},
                {"service": "Radiation Therapy Planning", "code": "77295", "charge": 1800.00, "error": None},
            ],
            "total": 5050.00
        },
        insurance_eob={
            "date": "2026-03-10",
            "plan": "Medicare Part B",
            "items": [
                {"service": "Neurology Consult", "billed": 350.00, "allowed": 300.00, "paid": 240.00, "patient_responsibility": 60.00},
                {"service": "MRI Brain", "billed": 2500.00, "allowed": 2000.00, "paid": 1600.00, "patient_responsibility": 400.00},
                {"service": "Neurosurgery Consult", "billed": 400.00, "allowed": 350.00, "paid": 280.00, "patient_responsibility": 70.00},
                {"service": "Radiation Planning", "billed": 1800.00, "allowed": 1500.00, "paid": 1200.00, "patient_responsibility": 300.00},
            ],
            "total_paid": 3320.00,
            "patient_owes": 830.00
        },
        billing_errors=[],
        clinical_errors=[],
        has_billing_errors=False,
        has_clinical_errors=False,
        difficulty="medium",
        category="clinical_validation",
        tags=["mri", "brain", "oncology"],
        max_score=1000
    )


def create_clinical_ultrasound_scenario() -> ChallengeScenario:
    """Clinical validation scenario with ultrasound"""
    return ChallengeScenario(
        scenario_id="scenario_006_ultrasound_unnecessary_biopsy",
        patient_name="Emily",
        patient_avatar="👩‍🦰",
        patient_profile={
            "age": 42,
            "gender": "Female",
            "insurance": "Cigna PPO",
            "deductible": 1500,
            "deductible_met": 800
        },
        clinical_images=[
            ClinicalImage(
                file_path="ultrasound_negative.png",
                modality="ultrasound",
                finding="Simple cyst, benign appearance, BI-RADS 2",
                is_abnormal=False
            )
        ],
        patient_story="""**Patient Story: Emily's Breast Screening**

During my annual mammogram in March 2026, a small lump was detected.
The radiologist ordered a follow-up breast ultrasound to evaluate the finding.

The ultrasound showed a simple, benign-appearing cyst (BI-RADS 2 - benign).
Despite the benign findings, the doctor recommended an immediate surgical biopsy.""",
        provider_bill={
            "date": "2026-03-15",
            "provider": "Women's Imaging Center",
            "items": [
                {"service": "Breast Ultrasound", "code": "76642", "charge": 450.00, "error": None},
                {"service": "Surgical Breast Biopsy", "code": "19101", "charge": 2800.00, "error": "Not indicated for BI-RADS 2"},
                {"service": "Pathology Analysis", "code": "88305", "charge": 650.00, "error": "Not indicated for BI-RADS 2"},
            ],
            "total": 3900.00
        },
        insurance_eob={
            "date": "2026-04-01",
            "plan": "Cigna PPO",
            "items": [
                {"service": "Ultrasound", "billed": 450.00, "allowed": 400.00, "paid": 320.00, "patient_responsibility": 80.00},
                {"service": "Surgical Biopsy", "billed": 2800.00, "allowed": 2400.00, "paid": 1920.00, "patient_responsibility": 480.00},
                {"service": "Pathology", "billed": 650.00, "allowed": 550.00, "paid": 440.00, "patient_responsibility": 110.00},
            ],
            "total_paid": 2680.00,
            "patient_owes": 670.00
        },
        billing_errors=[],
        clinical_errors=[
            {
                "id": "C1",
                "severity": "High",
                "category": "Unnecessary Procedure",
                "description": "Ultrasound shows simple benign cyst (BI-RADS 2). Surgical biopsy is not indicated and represents overtreatment.",
                "provider_charge": 3450.00,
                "insurance_paid": 2360.00,
                "potential_savings": 3450.00,
                "image_finding": "Benign simple cyst",
                "prescribed_treatment": "Surgical biopsy + pathology"
            }
        ],
        has_billing_errors=False,
        has_clinical_errors=True,
        malpractice=MalpracticeIndicator(
            is_malpractice=True,
            harm_severity="moderate",
            outcome_description="Patient underwent unnecessary surgical procedure with risks of infection, bleeding, and scarring.",
            wrong_treatment=True,
            wrong_diagnosis=False,
            unnecessary_procedure=True,
            patient_harm="Surgical risks, anxiety, and unnecessary costs for benign finding"
        ),
        difficulty="hard",
        category="clinical_validation",
        tags=["ultrasound", "unnecessary_procedure", "breast"],
        max_score=1500
    )


def create_combined_scenario() -> ChallengeScenario:
    """Combined billing + clinical errors scenario"""
    return ChallengeScenario(
        scenario_id="scenario_007_combined_ct_billing",
        patient_name="Michael",
        patient_avatar="👨",
        patient_profile={
            "age": 65,
            "gender": "Male",
            "insurance": "Medicare Advantage",
            "deductible": 2000,
            "deductible_met": 1500
        },
        clinical_images=[],  # No images for this one
        patient_story="""**Patient Story: Michael's Abdominal Pain**

In January 2026, I went to the ER with severe abdominal pain.
The ER doctor ordered a CT scan which showed diverticulitis (inflammation).

I was treated with antibiotics and pain medication, then discharged.
However, the bill included several unexpected charges.""",
        provider_bill={
            "date": "2026-01-25",
            "provider": "City General Hospital ER",
            "items": [
                {"service": "ER Visit - Level 4", "code": "99284", "charge": 1800.00, "error": None},
                {"service": "CT Abdomen with contrast", "code": "74160", "charge": 2200.00, "error": None},
                {"service": "CT Abdomen without contrast", "code": "74150", "charge": 1900.00, "error": "Duplicate - only one CT performed"},
                {"service": "IV Antibiotics", "code": "96365", "charge": 450.00, "error": None},
                {"service": "Surgical Consultation", "code": "99253", "charge": 600.00, "error": "Not performed"},
            ],
            "total": 6950.00
        },
        insurance_eob={
            "date": "2026-02-15",
            "plan": "Medicare Advantage",
            "items": [
                {"service": "ER Visit", "billed": 1800.00, "allowed": 1500.00, "paid": 1200.00, "patient_responsibility": 300.00},
                {"service": "CT with contrast", "billed": 2200.00, "allowed": 1800.00, "paid": 1440.00, "patient_responsibility": 360.00},
                {"service": "CT without contrast", "billed": 1900.00, "allowed": 1600.00, "paid": 1280.00, "patient_responsibility": 320.00},
                {"service": "IV Antibiotics", "billed": 450.00, "allowed": 400.00, "paid": 320.00, "patient_responsibility": 80.00},
                {"service": "Surgical Consult", "billed": 600.00, "allowed": 500.00, "paid": 400.00, "patient_responsibility": 100.00},
            ],
            "total_paid": 4640.00,
            "patient_owes": 1160.00
        },
        billing_errors=[
            {
                "id": "B1",
                "severity": "High",
                "category": "Duplicate Billing",
                "description": "Billed for both CT with and without contrast, but medical records show only one CT scan was performed.",
                "provider_charge": 1900.00,
                "insurance_paid": 1280.00,
                "potential_savings": 1900.00
            },
            {
                "id": "B2",
                "severity": "High",
                "category": "Service Not Rendered",
                "description": "Billed for surgical consultation that was never performed. Patient was seen only by ER physician.",
                "provider_charge": 600.00,
                "insurance_paid": 400.00,
                "potential_savings": 600.00
            }
        ],
        has_billing_errors=True,
        has_clinical_errors=False,
        difficulty="medium",
        category="combined",
        tags=["duplicate_billing", "emergency", "ct_scan"],
        max_score=1200
    )


def main():
    """Generate all scenarios"""
    # Create output directory
    output_dir = project_root / "benchmarks" / "challenge_scenarios"

    # Category directories
    billing_dir = output_dir / "billing_only"
    clinical_dir = output_dir / "clinical_validation"
    clean_dir = output_dir / "clean_cases"
    combined_dir = output_dir / "combined"

    # Create scenarios
    scenarios = [
        create_sarah_scenario(),
        create_marcus_scenario(),
        create_clinical_xray_scenario(),
        create_clean_case_scenario(),
        create_clinical_mri_scenario(),
        create_clinical_ultrasound_scenario(),
        create_combined_scenario()
    ]

    # Save scenarios
    for scenario in scenarios:
        if scenario.category == "billing_only":
            path = scenario.save_to_file(billing_dir)
        elif scenario.category == "clinical_validation":
            path = scenario.save_to_file(clinical_dir)
        elif scenario.category == "clean_case":
            path = scenario.save_to_file(clean_dir)
        elif scenario.category == "combined":
            path = scenario.save_to_file(combined_dir)
        else:
            path = scenario.save_to_file(output_dir)

        print(f"✓ Created {scenario.scenario_id} at {path}")

    print(f"\n✅ Generated {len(scenarios)} scenarios")
    print(f"📁 Saved to {output_dir}")


if __name__ == "__main__":
    main()
