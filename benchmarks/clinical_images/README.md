# Clinical Error Detection Benchmarks

Multi-modal image analysis benchmarks for detecting clinical errors where medical procedures or treatments do not match diagnostic results.

## Overview

This benchmark suite evaluates AI models' ability to detect discrepancies between medical imaging findings and prescribed treatments. The benchmark includes:

- **10 Error Scenarios (False Positives)**: Cases where diagnostic evidence does NOT support the clinical action - potential malpractice
- **10 Correct Treatment Scenarios (True Positives)**: Cases where diagnostic evidence DOES support the clinical action - appropriate medical care

This balanced dataset tests the model's ability to both detect errors AND recognize appropriate medical decisions.

## 🆕 Real Medical Images from Kaggle

### Quick Start: Download Real Images

Get **12 real medical images** (6 positive, 6 negative) covering all 6 modalities with proper attribution:

```bash
# 1. Setup Kaggle (one-time, 5 minutes)
pip install kaggle
# Get API key from https://www.kaggle.com/settings → Create New Token
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json

# 2. Download all datasets (~6.5 GB, 30-60 min)
python3 scripts/download_kaggle_medical_images.py --download-all

# 3. Select 12 images (1 pos + 1 neg per modality)
python3 scripts/download_kaggle_medical_images.py --select-images
```

**Result:** `kaggle_datasets/selected/` with 12 images + `manifest.json` with full attribution!

**See:** [KAGGLE_QUICKSTART.md](KAGGLE_QUICKSTART.md) for detailed instructions.

### Available Datasets

| Modality | Dataset | Size | License |
|----------|---------|------|---------|
| X-ray | COVID-19 Radiography | 1.2 GB | CC BY 4.0 |
| Histopathology | LC25000 Lung/Colon | 1.5 GB | CC BY-NC-SA 4.0 |
| MRI | Brain Tumor MRI | 150 MB | Unknown |
| CT | SIIM Medical Images | 3 GB | CC0 Public |
| Echo | China Echocardiogram | 500 MB | Unknown |
| Ultrasound | Breast Ultrasound | 50 MB | CC BY-NC-SA 4.0 |

## Benchmark Categories

### Error Scenarios (10 cases)

#### 1. Diagnostic Mismatch
Imaging shows normal results, but treatment is prescribed for a condition that doesn't exist.

**Examples:**
- X-ray shows healthy bone, but cast is prescribed
- Chest X-ray shows clear lungs, but IV antibiotics for "pneumonia"

#### 2. Overtreatment
Excessive or unnecessary procedures recommended despite benign findings.

**Examples:**
- Normal MRI, but surgery recommended
- Benign histology, but chemotherapy prescribed
- Normal echocardiogram, but open-heart surgery planned

#### 3. Unnecessary Follow-up
Ordering additional tests or procedures that aren't medically justified.

**Examples:**
- Normal NT scan, but amniocentesis ordered
- Normal mammogram, but biopsy recommended

### Correct Treatment Scenarios (10 cases)

#### 4. Appropriate Interventions
Imaging shows clear abnormalities that warrant the prescribed treatment.

**Examples:**
- Displaced fracture appropriately treated with cast
- Confirmed cancer appropriately treated with chemotherapy/surgery
- Severe valve disease appropriately treated with surgery
- Acute appendicitis appropriately treated with emergency surgery
- Suspicious mass appropriately biopsied

## Imaging Modalities

- **X-Ray**: Bone and chest imaging
- **MRI**: Brain, spine, and soft tissue
- **CT Scan**: Abdominal and thoracic imaging
- **Ultrasound**: Prenatal and thyroid imaging
- **Echocardiogram**: Cardiac function
- **Mammography**: Breast screening
- **Microscopy**: Histological analysis

## Severity Scoring

Each scenario is assigned a severity score from 1-10:

- **1-3**: Low severity (unnecessary tests, minor overtreatment)
- **4-6**: Medium severity (unnecessary procedures, moderate risk)
- **7-10**: High severity (unnecessary surgery, high malpractice risk)

## Directory Structure

```
clinical_images/
├── README.md                    # This file
├── scenarios.json               # Benchmark scenario definitions
├── synthetic_images/            # Synthetic medical images
│   ├── xray_healthy_forearm.png
│   ├── mri_normal_brain.png
│   ├── echo_normal_heart.png
│   └── ...
└── results/                     # Benchmark results
    ├── model_comparison.json
    └── detailed_results.json
```

## Running Benchmarks

### 1. Generate Synthetic Images

```bash
# Option 1: Local generation with PIL (fast, free, basic quality)
python3 scripts/generate_clinical_images.py --all

# Option 2: OpenAI DALL-E 3 (best quality, requires API key, ~$0.04 per image)
python3 scripts/generate_clinical_images.py --all --provider openai

# Option 3: Stability AI SDXL (good quality, requires API key, ~$0.03 per image)
python3 scripts/generate_clinical_images.py --all --provider stability

# Option 4: Replicate SDXL (good quality, requires API key, ~$0.01 per image)
python3 scripts/generate_clinical_images.py --all --provider replicate

# Generate specific modality with AI provider
python3 scripts/generate_clinical_images.py --modality mri --provider openai
```

**Image Generation Providers:**

- **PIL/Pillow** (default): Local generation using Python Imaging Library. Fast, free, no API keys needed. Creates basic schematic medical images.
  
- **OpenAI DALL-E 3**: Highest quality photorealistic medical images. Requires `OPENAI_API_KEY` in your `.env` file. Best for presentations and publications.
  
- **Stability AI**: High quality using Stable Diffusion XL. Requires `STABILITY_API_KEY`. Good balance of quality and cost.
  
- **Replicate**: Access to Stable Diffusion XL via Replicate API. Requires `REPLICATE_API_TOKEN`. Most cost-effective AI option.

**Setting up API Keys:**

Add to your `.env` file:
```bash
# For OpenAI DALL-E
OPENAI_API_KEY=sk-...

# For Stability AI
STABILITY_API_KEY=sk-...

# For Replicate
REPLICATE_API_TOKEN=r8_...
```

### 2. Run Clinical Benchmarks

```bash
# Run all models
python3 scripts/run_clinical_benchmarks.py --model all

# Run specific model
python3 scripts/run_clinical_benchmarks.py --model gpt-4o-mini

# Run with specific imaging modality
python3 scripts/run_clinical_benchmarks.py --modality mri
```

### 3. View Results

Results are automatically displayed in the Production Stability dashboard under the "Clinical Error Detection" tab.

## Benchmark Scenarios

### Error Scenarios (001-010)

### Scenario 001: X-Ray Forearm Fracture Misdiagnosis
- **Imaging**: X-ray shows healthy forearm
- **Error**: Cast prescribed for 6 weeks
- **Severity**: 6/10
- **Risk**: Unnecessary immobilization, muscle atrophy

### Scenario 002: MRI Brain Tumor False Positive
- **Imaging**: Normal brain MRI
- **Error**: Craniotomy scheduled to remove non-existent tumor
- **Severity**: 10/10
- **Risk**: Critical - brain surgery carries death/disability risk

### Scenario 003: Echocardiogram Unnecessary Intervention
- **Imaging**: Normal cardiac function
- **Error**: Open-heart valve replacement recommended
- **Severity**: 9/10
- **Risk**: Critical - high mortality and stroke risk

### Scenario 004: Histology Pathology Treatment Mismatch
- **Imaging**: Benign tissue histology
- **Error**: Aggressive chemotherapy prescribed
- **Severity**: 10/10
- **Risk**: Critical - chemo toxicity, organ failure

### Scenario 005: CT Scan Abdominal Mass False Positive
- **Imaging**: Normal abdominal CT
- **Error**: Exploratory laparotomy recommended
- **Severity**: 8/10
- **Risk**: High - surgical morbidity and complications

### Scenario 006: Nuchal Translucency Unnecessary Follow-up
- **Imaging**: Normal NT scan (1.5mm)
- **Error**: Amniocentesis and genetic testing ordered
- **Severity**: 4/10
- **Risk**: Medium - 1% miscarriage risk

### Scenario 007: Mammogram False Positive Leading to Biopsy
- **Imaging**: Normal mammogram (BI-RADS 1)
- **Error**: Core needle biopsy recommended
- **Severity**: 5/10
- **Risk**: Medium - invasive procedure, anxiety

### Scenario 008: Chest X-Ray Pneumonia Overdiagnosis
- **Imaging**: Clear lung fields
- **Error**: IV antibiotics for "severe pneumonia"
- **Severity**: 4/10
- **Risk**: Medium - antibiotic resistance, C. diff

### Scenario 009: Spine MRI Unnecessary Surgery Recommendation
- **Imaging**: Mild age-appropriate degeneration
- **Error**: Spinal fusion surgery recommended
- **Severity**: 9/10
- **Risk**: High - infection, hardware failure, chronic pain

### Scenario 010: Thyroid Ultrasound Unnecessary Thyroidectomy
- **Imaging**: Small benign thyroid nodule (8mm)
- **Error**: Total thyroidectomy recommended
- **Severity**: 7/10
- **Risk**: High - permanent hypothyroidism, nerve damage

### Correct Treatment Scenarios (011-020)

### Scenario 011: X-Ray Displaced Fracture Appropriate Cast
- **Imaging**: Displaced distal radius fracture clearly visible
- **Treatment**: Cast immobilization for 6 weeks
- **Decision**: ✓ Appropriate - standard treatment for fracture

### Scenario 012: MRI Glioblastoma Appropriate Surgery
- **Imaging**: 4cm ring-enhancing brain mass with mass effect
- **Treatment**: Craniotomy for tumor resection
- **Decision**: ✓ Appropriate - life-threatening tumor requires surgery

### Scenario 013: Echo Severe Aortic Stenosis Valve Replacement
- **Imaging**: Severe aortic stenosis (valve area 0.6 cm²)
- **Treatment**: Aortic valve replacement surgery
- **Decision**: ✓ Appropriate - guideline-directed, life-saving intervention

### Scenario 014: Histology Invasive Carcinoma Appropriate Chemotherapy
- **Imaging**: Triple-negative invasive breast cancer, Grade 3
- **Treatment**: Aggressive chemotherapy protocol
- **Decision**: ✓ Appropriate - standard of care for aggressive cancer

### Scenario 015: CT Scan Appendicitis Appropriate Surgery
- **Imaging**: Acute appendicitis with signs of early perforation
- **Treatment**: Emergency appendectomy
- **Decision**: ✓ Appropriate - surgical emergency requires prompt intervention

### Scenario 016: NT Scan Increased Thickness Appropriate Amniocentesis
- **Imaging**: Markedly increased NT (5.2mm, normal <2.5mm)
- **Treatment**: Genetic counseling and amniocentesis offered
- **Decision**: ✓ Appropriate - high-risk screening warrants testing

### Scenario 017: Mammogram Suspicious Mass Appropriate Biopsy
- **Imaging**: Spiculated mass with microcalcifications (BI-RADS 5)
- **Treatment**: Core needle biopsy
- **Decision**: ✓ Appropriate - suspicious findings require tissue diagnosis

### Scenario 018: Chest X-Ray Lobar Pneumonia Appropriate Antibiotics
- **Imaging**: Dense lobar consolidation with air bronchograms
- **Treatment**: Antibiotics for community-acquired pneumonia
- **Decision**: ✓ Appropriate - clear bacterial pneumonia requires treatment

### Scenario 019: Spine MRI Herniated Disc Appropriate Surgery
- **Imaging**: Cauda equina syndrome from large disc herniation
- **Treatment**: Emergency decompression surgery
- **Decision**: ✓ Appropriate - surgical emergency to prevent paralysis

### Scenario 020: Thyroid Ultrasound Suspicious Nodule Appropriate Surgery
- **Imaging**: Biopsy-proven papillary thyroid carcinoma, 3.5cm
- **Treatment**: Total thyroidectomy
- **Decision**: ✓ Appropriate - confirmed cancer requires surgical resection

## Model Evaluation Metrics

Models are evaluated on:

1. **Error Detection Rate**: % of error scenarios (001-010) correctly identified as errors
2. **Correct Treatment Recognition**: % of appropriate scenarios (011-020) correctly identified as appropriate
3. **Overall Accuracy**: (True Positives + True Negatives) / Total Cases
4. **Precision**: True Positives / (True Positives + False Positives)
5. **Recall**: True Positives / (True Positives + False Negatives)
6. **F1 Score**: Harmonic mean of precision and recall
7. **Confidence Calibration**: Model's confidence scores vs actual accuracy
8. **Modality Performance**: Detection rates by imaging type

## Expected Outputs

Each model should:

1. Analyze the medical image
2. Review the prescribed treatment/action
3. Identify if there's a mismatch (for error scenarios) OR confirm appropriateness (for correct scenarios)
4. Provide confidence score
5. Suggest appropriate action
6. Assess malpractice risk level (for error scenarios)

**For Error Scenarios (001-010):**
- Expected: `clinical_error_detected = true`
- Model should identify the discrepancy between imaging and treatment

**For Correct Treatment Scenarios (011-020):**
- Expected: `clinical_error_detected = false`
- Model should recognize the treatment is appropriate and justified

## Integration with Billing Error Detection

Clinical error detection complements billing error detection by:

- Identifying medically unnecessary procedures that generate fraudulent bills
- Detecting malpractice scenarios that may involve insurance fraud
- Cross-validating billing claims against medical necessity
- Flagging patterns of systematic overtreatment by providers

## Contributing

To add new benchmark scenarios:

1. Add scenario definition to `scenarios.json`
2. Generate or obtain synthetic medical image
3. Update README with scenario description
4. Run benchmarks to validate

## Privacy & Ethics

All medical images used in these benchmarks are **synthetic** and do not represent real patients. This ensures:

- HIPAA compliance
- No patient privacy violations
- Ethical AI development
- Reproducible benchmarks

## License

Same as parent project (see LICENSE in root directory)

## Contact

For questions or contributions, see main project documentation.
