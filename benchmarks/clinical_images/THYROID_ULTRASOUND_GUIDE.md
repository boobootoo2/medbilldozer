# Using Real Thyroid Ultrasound Images from Stanford AIMI

## Quick Start

Instead of generating synthetic ultrasound images, you can use real clinical thyroid ultrasound images from Stanford's AIMI dataset.

---

## Dataset: Thyroid Ultrasound Cine-clip

**Official Page:** https://aimi.stanford.edu/datasets/thyroid-ultrasound-cine-clip  
**Download:** https://stanfordaimi.azurewebsites.net/datasets/a72f2b02-7b53-4c5d-963c-d7253220bfd5  
**DOI:** https://doi.org/10.71718/7m5n-rh16

### Dataset Contents

- **167 patients** with biopsy-confirmed thyroid nodules
- **192 thyroid nodules** total
- **Ultrasound cine-clip images** (video sequences)
- **Radiologist-annotated segmentations** of nodules
- **Patient demographics**
- **Lesion characteristics:** size, location
- **TI-RADS descriptors** (standardized classification)
- **Histopathological diagnoses** (benign vs malignant)

---

## Why Use This Dataset?

### ✅ Advantages Over Synthetic Images

1. **Real clinical data** - Actual images from Stanford University Medical Center
2. **Expert annotations** - Radiologist segmentations and classifications
3. **Ground truth pathology** - Biopsy-confirmed diagnoses
4. **TI-RADS scores** - Standardized risk stratification
5. **Diverse cases** - Range of benign and malignant nodules
6. **Research-grade** - Published, peer-reviewed dataset

### 🎯 Perfect For Your Benchmarks

Your scenario_006 and scenario_008 both involve thyroid ultrasounds:

**Scenario 006:** Normal NT scan (nuchal translucency)  
**Scenario 008:** Thyroid nodule evaluation

This dataset provides real ultrasound images with known pathology that you can use to test AI models' ability to correctly interpret findings.

---

## How to Download

### Step 1: Visit the Download Page

```bash
# Open in browser
https://stanfordaimi.azurewebsites.net/datasets/a72f2b02-7b53-4c5d-963c-d7253220bfd5
```

### Step 2: Request Access

1. Click "Download" or "Request Access"
2. Complete the registration form
3. Accept the Data Use Agreement
4. Wait for email with download link (usually within 24 hours)

### Step 3: Download and Extract

```bash
# Create directory
mkdir -p benchmarks/clinical_images/real_images/thyroid-ultrasound

# Download (link provided in email)
# Extract to the directory above
```

### Step 4: Organize Files

Expected structure:
```
benchmarks/clinical_images/real_images/thyroid-ultrasound/
├── images/
│   ├── patient001_clip.mp4
│   ├── patient002_clip.mp4
│   └── ...
├── segmentations/
│   ├── patient001_seg.nii.gz
│   └── ...
├── metadata.csv
└── README.txt
```

---

## Integration with Your Benchmarks

### Option 1: Extract Still Frames from Cine-clips

```python
import cv2
from pathlib import Path

def extract_frames(video_path, output_dir, num_frames=5):
    """Extract representative frames from ultrasound cine-clip."""
    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Extract evenly spaced frames
    frame_indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
    
    for idx, frame_num in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if ret:
            output_path = output_dir / f"{video_path.stem}_frame{idx:02d}.png"
            cv2.imwrite(str(output_path), frame)
    
    cap.release()

# Usage
video_dir = Path("benchmarks/clinical_images/real_images/thyroid-ultrasound/images")
output_dir = Path("benchmarks/clinical_images/synthetic_images")

for video in video_dir.glob("*.mp4"):
    extract_frames(video, output_dir)
```

### Option 2: Update scenarios.json

```json
{
    "id": "scenario_008",
    "title": "Thyroid Nodule Benign vs Malignant",
    "imaging_modality": "Ultrasound",
    "error_category": "Diagnostic Mismatch",
    "ground_truth": "Benign thyroid nodule with TI-RADS 2 characteristics",
    "image_file": "real_images/thyroid-ultrasound/images/patient042_frame03.png",
    "metadata": {
        "source": "Stanford AIMI Thyroid Ultrasound Dataset",
        "patient_id": "patient042",
        "ti_rads_score": 2,
        "biopsy_result": "benign",
        "nodule_size_mm": 8
    }
}
```

### Option 3: Match Cases to Scenarios

Use the metadata.csv to find cases that match your scenarios:

```python
import pandas as pd

# Load metadata
df = pd.read_csv('benchmarks/clinical_images/real_images/thyroid-ultrasound/metadata.csv')

# Find benign nodules (for error scenarios)
benign_cases = df[df['histopathology'] == 'benign']

# Find nodules with low TI-RADS (should NOT have aggressive treatment)
low_risk = df[df['ti_rads'] <= 2]

# Select specific cases
for idx, case in low_risk.head(5).iterrows():
    print(f"Patient: {case['patient_id']}")
    print(f"TI-RADS: {case['ti_rads']}")
    print(f"Diagnosis: {case['histopathology']}")
    print(f"Image: {case['image_filename']}")
    print()
```

---

## Data Use Agreement Requirements

### ✅ You Must:

1. **Use for non-commercial research only**
2. **Acknowledge Stanford AIMI** in all publications:

> "This research used data provided by the Stanford Center for Artificial Intelligence 
> in Medicine and Imaging (AIMI). AIMI curated a publicly available imaging data 
> repository containing clinical imaging and data from Stanford Health Care."

3. **Cite the dataset DOI:** https://doi.org/10.71718/7m5n-rh16
4. **Follow HIPAA and patient privacy guidelines**
5. **Not redistribute the original data**

### ❌ You Cannot:

- Use for commercial purposes without separate agreement
- Share/redistribute raw data files
- Attempt to re-identify patients
- Violate patient privacy protections

---

## Technical Details

### Image Specifications

- **Format:** Video cine-clips (MP4) + Still frames
- **Modality:** B-mode ultrasound
- **Transducer:** High-frequency linear array (7-12 MHz typical)
- **Views:** Transverse and sagittal
- **Resolution:** Variable (typical: 640x480 to 1024x768)
- **Color:** Grayscale (ultrasound) + some with Doppler color overlay

### Metadata Fields

```csv
patient_id, age, sex, nodule_id, nodule_size_mm, location, 
ti_rads_score, composition, echogenicity, shape, margin, 
echogenic_foci, histopathology, image_filename, segmentation_filename
```

### TI-RADS Categories

| Score | Risk | Management |
|-------|------|------------|
| TR1 | Benign | No follow-up |
| TR2 | Not suspicious | No biopsy |
| TR3 | Mildly suspicious | Follow-up / FNA if ≥2.5cm |
| TR4 | Moderately suspicious | FNA if ≥1.5cm |
| TR5 | Highly suspicious | FNA if ≥1.0cm |

---

## Example Use Cases

### Scenario A: Benign Nodule - Unnecessary Biopsy (Error)

**Find:** TR1 or TR2 nodule (low risk)  
**Error:** Doctor recommends biopsy anyway  
**Test:** Does AI flag this as overtreatment?

```python
# Select case
case = df[(df['ti_rads'] == 2) & (df['histopathology'] == 'benign')].iloc[0]
image_path = f"real_images/thyroid-ultrasound/{case['image_filename']}"
```

### Scenario B: Malignant Nodule - Appropriate Biopsy (Correct)

**Find:** TR4 or TR5 nodule (high risk)  
**Correct:** Doctor recommends biopsy  
**Test:** Does AI confirm this is appropriate?

```python
# Select case
case = df[(df['ti_rads'] >= 4) & (df['histopathology'] == 'malignant')].iloc[0]
image_path = f"real_images/thyroid-ultrasound/{case['image_filename']}"
```

---

## Helper Script

I've created a helper script to make this easier:

```bash
# Prepare download
python3 scripts/download_aimi_samples.py --dataset thyroid-ultrasound --prepare

# This creates:
# - Download instructions
# - Helper script
# - README with usage examples
```

---

## Benefits Summary

| Feature | Synthetic Images | Real AIMI Images |
|---------|-----------------|------------------|
| Realism | ⭐⭐ Cartoon-like | ⭐⭐⭐⭐⭐ Clinical grade |
| Annotations | ❌ None | ✅ Expert segmentations |
| Ground Truth | ❌ Hypothetical | ✅ Biopsy-confirmed |
| TI-RADS Scores | ❌ Made up | ✅ Actual scores |
| Research Validity | ⚠️ Limited | ✅ High |
| Cost | Free (generated) | Free (registration) |
| Setup Time | Instant | ~24hr registration |

---

## Next Steps

1. **Register:** Visit the download page and request access
2. **Wait:** Receive email with download link (usually same day)
3. **Download:** Get the dataset files (~2-5 GB)
4. **Extract:** Organize into your benchmark directory
5. **Process:** Extract frames from cine-clips
6. **Update:** Modify scenarios.json to use real images
7. **Test:** Run benchmarks with real clinical data!

---

## Contact & Support

**Stanford AIMI Center**  
Email: aimicenter@stanford.edu  
Web: https://aimi.stanford.edu

**Dataset Issues**  
Report technical issues or questions about the dataset directly to AIMI.

**Integration Help**  
For help integrating this into your benchmarks, see the helper scripts in `scripts/`.

---

## Additional Resources

- [AIMI Shared Datasets](https://aimi.stanford.edu/shared-datasets)
- [TI-RADS Classification](https://www.acr.org/Clinical-Resources/Reporting-and-Data-Systems/TI-RADS)
- [Thyroid Imaging Guidelines](https://www.thyroid.org/thyroid-nodules/)

---

**Last Updated:** February 14, 2026
