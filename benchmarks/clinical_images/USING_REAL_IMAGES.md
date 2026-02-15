# Using Real Clinical Images Instead of Synthetic

## Why Real Images Are Better

✅ **Authentic clinical appearance** - Real PACS/DICOM quality  
✅ **Expert annotations** - Radiologist interpretations included  
✅ **Ground truth pathology** - Biopsy-confirmed diagnoses  
✅ **Research validity** - Published, peer-reviewed datasets  
✅ **Diverse cases** - Real patient variability  

---

## Available Stanford AIMI Datasets

### 1. EchoNet-Dynamic 🫀
- **10,030 echocardiogram videos**
- Expert measurements and calculations
- Cardiac chamber sizes, ejection fraction
- **Perfect for:** Scenario 003 (normal echo), Scenario 013 (aortic stenosis)

### 2. Thyroid Ultrasound Cine-clip 🦋
- **192 thyroid nodules** from 167 patients
- TI-RADS scores and segmentations
- Biopsy-confirmed pathology
- **Perfect for:** Scenario 008 (thyroid nodule evaluation)

### 3. COCA - Coronary CT 🫁
- **Gated coronary CT scans**
- Calcium scores and segmentations
- **Perfect for:** Scenario 005 (CT abdomen), Scenario 018 (CT appendicitis)

### 4. CheXpert 📷
- **224,316 chest X-rays**
- 14 pathology labels
- **Perfect for:** Scenario 001 (forearm X-ray), Scenario 009 (chest X-ray pneumonia)

### 5. Brain-Mets-Lung Histopathology 🔬 (NEW!)
- **111 whole slide histopathology images** (H&E stained, 20x magnification)
- 103 patients with brain metastases from lung cancer
- Matched MRI scans with expert segmentations
- Molecular markers (EGFR, ALK, PD-L1) and clinical data
- **Source:** TCIA (Cancer Imaging Archive) - NO REGISTRATION REQUIRED!
- **Perfect for:** Cancer diagnosis, histopathology scenarios

---

## Quick Start: Get Thyroid Ultrasounds

This is the easiest dataset to start with:

```bash
# 1. Run helper script
python3 scripts/download_aimi_samples.py --dataset thyroid-ultrasound --prepare

# 2. Visit registration page (opens in browser)
# https://stanfordaimi.azurewebsites.net/datasets/a72f2b02-7b53-4c5d-963c-d7253220bfd5

# 3. Complete registration form (5 minutes)
# - Name, email, institution
# - Research purpose
# - Accept Data Use Agreement

# 4. Receive download link via email (usually within 1 hour)

# 5. Download and extract
mkdir -p benchmarks/clinical_images/real_images/thyroid-ultrasound
# Extract downloaded files here

# 6. Use in scenarios
# Update scenarios.json to point to real images
```

---

## Integration Example

### Before (Synthetic):
```json
{
    "id": "scenario_008",
    "image_file": "synthetic_images/ultrasound_normal_nt.png",
    "ground_truth": "Normal nuchal translucency - 1.5mm at 12 weeks"
}
```

### After (Real AIMI):
```json
{
    "id": "scenario_008",
    "image_file": "real_images/thyroid-ultrasound/patient042_frame03.png",
    "ground_truth": "Benign thyroid nodule, TI-RADS 2, biopsy confirmed",
    "metadata": {
        "source": "Stanford AIMI Thyroid Ultrasound Dataset",
        "doi": "10.71718/7m5n-rh16",
        "patient_id": "patient042",
        "ti_rads": 2,
        "pathology": "benign"
    }
}
```

---

## All Available Datasets

| Dataset | Modality | Count | Download |
|---------|----------|-------|----------|
| EchoNet-Dynamic | Echo | 10,030 | [Link](https://stanfordaimi.azurewebsites.net/datasets/834e1cd1-92f7-4268-9daa-d359198b310a) |
| Thyroid Ultrasound | US | 192 | [Link](https://stanfordaimi.azurewebsites.net/datasets/a72f2b02-7b53-4c5d-963c-d7253220bfd5) |
| Brain-Mets-Lung | Histopath | 111 | [Link](https://www.cancerimagingarchive.net/collection/brain-mets-lung-mri-path-segs/) |
| COCA | CT | Multiple | [Link](https://stanfordaimi.azurewebsites.net/datasets/b4f0cad0-f38a-4ad6-9de9-c993c8802f8f) |
| CheXpert | X-ray | 224K+ | [Link](https://stanfordaimi.azurewebsites.net/datasets/8cbd9ed4-2eb9-4565-affc-111cf4f7ebe2) |
| MURA | X-ray | 40K+ | [Link](https://stanfordaimi.azurewebsites.net/datasets/f6a48c55-9b15-4c21-a9ad-5bb2934d4af3) |
| SinoCT | CT | 9,776 | [Link](https://stanfordaimi.azurewebsites.net/datasets/ec3f6b87-d9f6-4e7b-8d2e-e45e2319d05a) |

---

## Mapping Scenarios to Datasets

| Your Scenario | Best Dataset | Reason |
|---------------|--------------|--------|
| 001: Forearm X-ray | MURA | Musculoskeletal X-rays |
| 002: Brain MRI | Brain-Mets-Lung | Brain MRI with segmentations |
| 003: Normal Echo | EchoNet-Dynamic | 10K normal echos |
| 005: CT Abdomen | COCA | Abdominal CTs |
| 008: Thyroid US | Thyroid Ultrasound | Perfect match! |
| 009: Chest X-ray | CheXpert | Largest chest X-ray dataset |
| 013: Aortic Stenosis | EchoNet-Dynamic | Cardiac pathology cases |
| 018: CT Appendicitis | COCA | Abdominal CT with pathology |
| Cancer Diagnosis | Brain-Mets-Lung | H&E histopathology + molecular markers |

---

## Data Use Requirements

### Citation Required

Include in all publications:

> "This research used data provided by the Stanford Center for Artificial Intelligence 
> in Medicine and Imaging (AIMI)."

### DOI Citations

- **Thyroid Ultrasound:** `10.71718/7m5n-rh16`
- **EchoNet-Dynamic:** Check dataset page for DOI
- **COCA:** Check dataset page for DOI

### Restrictions

- ✅ Non-commercial research: YES
- ✅ Academic publications: YES
- ✅ AI model training: YES
- ❌ Commercial use: Requires separate agreement
- ❌ Data redistribution: NOT allowed
- ❌ Patient re-identification: PROHIBITED

---

## Helper Tools

### 1. List Available Datasets
```bash
python3 scripts/download_aimi_samples.py --list
```

### 2. Get Dataset Info
```bash
python3 scripts/download_aimi_samples.py --info thyroid-ultrasound
```

### 3. Prepare Download
```bash
python3 scripts/download_aimi_samples.py --dataset thyroid-ultrasound --prepare
```

---

## Processing Tips

### Extract Frames from Videos

Many datasets (EchoNet, Thyroid) provide video cine-clips. Extract still frames:

```python
import cv2

def extract_best_frame(video_path, output_path):
    """Extract clearest frame from ultrasound video."""
    cap = cv2.VideoCapture(video_path)
    
    # Get middle frame (usually clearest)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
    
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(output_path, frame)
    
    cap.release()
```

### Convert DICOM to PNG

For CT/MRI datasets:

```python
import pydicom
from PIL import Image
import numpy as np

def dicom_to_png(dicom_path, output_path, window_center=40, window_width=350):
    """Convert DICOM to PNG with windowing."""
    dcm = pydicom.dcmread(dicom_path)
    img = dcm.pixel_array
    
    # Apply window/level
    img_min = window_center - window_width / 2
    img_max = window_center + window_width / 2
    img = np.clip(img, img_min, img_max)
    
    # Scale to 0-255
    img = ((img - img_min) / (img_max - img_min) * 255).astype(np.uint8)
    
    Image.fromarray(img).save(output_path)
```

---

## Benefits vs Synthetic

| Aspect | Synthetic | Real AIMI |
|--------|-----------|-----------|
| Visual Quality | 6/10 | 10/10 |
| Clinical Accuracy | 5/10 | 10/10 |
| Expert Annotations | 0/10 | 10/10 |
| Ground Truth | 2/10 | 10/10 |
| Research Validity | 4/10 | 10/10 |
| Setup Time | Instant | 1-24 hours |
| Cost | Free | Free (registration) |
| Publication Ready | Maybe | Definitely ✓ |

---

## Recommended Approach

### Phase 1: Quick Prototype (Synthetic)
Use synthetic images to:
- Build the benchmark framework
- Test the dashboard UI
- Develop evaluation metrics
- **Time:** 1 hour

### Phase 2: Production Quality (Real AIMI)
Replace with real images:
- Register for datasets (1 day wait)
- Download and process images
- Update scenarios with real cases
- **Time:** 2-3 days total

### Phase 3: Publication
With real AIMI data you can:
- Submit to conferences/journals
- Claim research validity
- Compare to other studies
- Get peer review acceptance

---

## Next Steps

1. **Decide:** Which scenarios need real images most urgently?
2. **Register:** Start with Thyroid Ultrasound (smallest, easiest)
3. **Download:** Wait for email (usually same day)
4. **Process:** Extract frames, organize files
5. **Update:** Modify scenarios.json
6. **Test:** Run benchmarks with real data
7. **Publish:** Use in research with confidence

---

## Support

- **Helper script:** `scripts/download_aimi_samples.py`
- **Thyroid guide:** `THYROID_ULTRASOUND_GUIDE.md`
- **AIMI contact:** aimicenter@stanford.edu
- **AIMI website:** <https://aimi.stanford.edu>

---

**Bottom Line:** Real clinical images from Stanford AIMI will make your benchmarks publication-ready and dramatically more credible than synthetic images. The registration process is simple and most requests are approved within hours.

Start with the Thyroid Ultrasound dataset - it's perfect for your use case! 🎯
