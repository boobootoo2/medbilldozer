# Real Clinical Imaging Datasets Overview

## Quick Reference

This document provides a comprehensive overview of all available real clinical imaging datasets for MedBillDozer benchmarks.

---

## 🔬 Histopathology Datasets

### Brain-Mets-Lung-MRI-Path-Segs (TCIA) ⭐ NEW!

**Source:** The Cancer Imaging Archive (TCIA)  
**Access:** ✅ **NO REGISTRATION REQUIRED** - Direct download  
**Size:** 18.6 GB (histopathology) + 622 MB (MRI)

#### Contents
- 103 unique patients with brain metastases from lung cancer
- 111 whole slide histopathology images (H&E stained)
- Format: SVS (Aperio whole slide imaging)
- Magnification: 20x
- Matched MRI scans (T1CE and FLAIR sequences)
- Expert tumor segmentations

#### Clinical Data
- Histologic subtype (SCLC, adenocarcinoma, squamous cell)
- Molecular markers: EGFR, ALK, PD-L1 status
- Patient demographics (age, sex, smoking history)
- Lesion characteristics (size, location)
- Graded Prognostic Assessment (GPA) scores
- Karnofsky Performance Status

#### Use Cases
- Cancer diagnosis from histopathology
- Histologic subtype classification
- Molecular marker prediction from tissue images
- Multi-modal imaging (pathology + radiology)
- Prognostic model validation

#### Quick Start
```bash
# Download from TCIA
open https://www.cancerimagingarchive.net/collection/brain-mets-lung-mri-path-segs/

# Create preview images
python3 scripts/create_histopath_previews.py \
    --input benchmarks/clinical_images/brain_mets_histopath/histopathology \
    --output benchmarks/clinical_images/brain_mets_histopath/previews
```

#### Citation
```
Chadha, S., Sritharan, D., Dolezal, D., et al. (2025). MR Imaging and
Segmentations with Matched Brain Biopsy Pathology Slides from Patients with Brain
Metastases from Primary Lung Cancer (Brain-Mets-Lung-MRI-Path-Segs) (Version 2).
The Cancer Imaging Archive. https://doi.org/10.7937/k0sm-y874
```

**📖 Detailed Guide:** [HISTOPATHOLOGY_GUIDE.md](HISTOPATHOLOGY_GUIDE.md)

---

## 🫀 Echocardiogram Datasets

### EchoNet-Dynamic (Stanford AIMI)

**Source:** Stanford AIMI  
**Access:** Registration required (1-day turnaround)  
**Size:** 10,030 labeled videos

#### Contents
- Echocardiogram videos (apical 4-chamber view)
- Expert measurements and calculations
- Cardiac chamber dimensions
- Ejection fraction values
- Ventricular volumes

#### Use Cases
- Normal echocardiogram (Scenario 003)
- Aortic stenosis (Scenario 013)
- Cardiac function assessment
- Ejection fraction estimation

#### Quick Start
```bash
python3 scripts/download_aimi_samples.py --dataset echonet-dynamic --prepare
```

---

## 🦋 Ultrasound Datasets

### Thyroid Ultrasound Cine-clip (Stanford AIMI)

**Source:** Stanford AIMI  
**Access:** Registration required (1-day turnaround)  
**Size:** 167 patients, 192 nodules

#### Contents
- Ultrasound cine-clip videos
- Radiologist-annotated segmentations
- TI-RADS descriptors (TR1-TR5)
- Biopsy-confirmed pathology
- Patient demographics
- Lesion size and location

#### Use Cases
- Thyroid nodule evaluation (Scenario 008)
- TI-RADS risk stratification
- Benign vs malignant classification
- Ultrasound feature analysis

#### Quick Start
```bash
python3 scripts/download_aimi_samples.py --dataset thyroid-ultrasound --prepare
```

**📖 Detailed Guide:** [THYROID_ULTRASOUND_GUIDE.md](THYROID_ULTRASOUND_GUIDE.md)

---

## 🫁 CT Datasets

### COCA - Coronary Calcium and Chest CTs (Stanford AIMI)

**Source:** Stanford AIMI  
**Access:** Registration required  
**Size:** Multiple chest/cardiac CTs

#### Contents
- Gated coronary CT DICOM images
- Calcium scores
- Expert segmentations
- Cardiac and chest anatomy

#### Use Cases
- CT abdomen (Scenario 005)
- CT appendicitis (Scenario 018)
- Coronary calcium scoring
- Chest CT analysis

---

### SinoCT (Stanford AIMI)

**Source:** Stanford AIMI  
**Access:** Registration required  
**Size:** 9,776 head CT scans

#### Contents
- Head CT scans
- Multiple series per patient
- DICOM format

#### Use Cases
- Brain imaging scenarios
- Head CT interpretation
- Neurological findings

---

## 📷 X-ray Datasets

### CheXpert (Stanford AIMI)

**Source:** Stanford AIMI  
**Access:** Registration required  
**Size:** 224,316 chest radiographs

#### Contents
- Chest X-rays (frontal and lateral)
- 14 pathology labels:
  - Atelectasis
  - Cardiomegaly
  - Consolidation
  - Edema
  - Effusion
  - Emphysema
  - Enlarged Cardiomediastinum
  - Fracture
  - Lung Lesion
  - Lung Opacity
  - Pneumonia
  - Pneumothorax
  - Pleural Other
  - Support Devices

#### Use Cases
- Chest X-ray pneumonia (Scenario 009)
- Pneumothorax detection
- Cardiomegaly assessment
- Multi-label pathology detection

---

### MURA (Stanford AIMI)

**Source:** Stanford AIMI  
**Access:** Registration required  
**Size:** 40,561 musculoskeletal radiographs

#### Contents
- X-rays of multiple body parts:
  - Elbow
  - Finger
  - Forearm
  - Hand
  - Humerus
  - Shoulder
  - Wrist
- Normal vs abnormal labels

#### Use Cases
- Forearm X-ray (Scenario 001)
- Fracture detection
- Musculoskeletal abnormalities

---

## Dataset Comparison

| Dataset | Modality | Cases | Registration | Download Size | Best For |
|---------|----------|-------|--------------|---------------|----------|
| **Brain-Mets-Lung** | Histopath | 111 | ❌ **No** | 18.6 GB | Cancer diagnosis, molecular markers |
| **Thyroid US** | Ultrasound | 192 | ✅ Yes | ~5 GB | Thyroid nodules, TI-RADS |
| **EchoNet-Dynamic** | Echo | 10,030 | ✅ Yes | ~10 GB | Cardiac function, stenosis |
| **CheXpert** | X-ray | 224K+ | ✅ Yes | ~440 GB | Chest pathology, pneumonia |
| **MURA** | X-ray | 40K+ | ✅ Yes | ~40 GB | MSK, fractures |
| **COCA** | CT | Multiple | ✅ Yes | ~100 GB | Cardiac/chest CT |
| **SinoCT** | CT | 9,776 | ✅ Yes | ~50 GB | Head CT |

---

## Registration Instructions

### Stanford AIMI Datasets (Most datasets)

1. **Visit:** <https://aimi.stanford.edu/shared-datasets>
2. **Select dataset** and click "Request Access"
3. **Complete form:**
   - Name, email, institution
   - Research purpose
   - Accept Data Use Agreement
4. **Wait for approval** (usually 1-24 hours)
5. **Receive download link** via email
6. **Download** using provided link or Aspera Connect

### TCIA Datasets (Brain-Mets-Lung)

1. **Visit:** <https://www.cancerimagingarchive.net/collection/brain-mets-lung-mri-path-segs/>
2. **Click "DOWNLOAD"** for each package you need
3. **No registration required!** - Direct download
4. **Optional:** Install IBM Aspera Connect for faster downloads

---

## Citation Requirements

### Stanford AIMI Datasets

All publications must include:

> "This research used data provided by the Stanford Center for Artificial Intelligence in Medicine and Imaging (AIMI). AIMI curated a publicly available imaging data repository containing clinical imaging and data from Stanford Health Care, the Stanford Children's Hospital, the University Healthcare Alliance and Packard Children's Health Alliance clinics provisioned for research use by the Stanford Medicine Research Data Repository (STARR)."

### TCIA Datasets

Cite the specific dataset DOI (see individual dataset sections above).

---

## Scenario Mapping

Recommended datasets for each MedBillDozer scenario:

| Scenario ID | Title | Best Dataset |
|-------------|-------|--------------|
| 001 | Forearm X-ray fracture | **MURA** |
| 002 | Brain MRI | **Brain-Mets-Lung** (MRI) |
| 003 | Normal echocardiogram | **EchoNet-Dynamic** |
| 005 | CT abdomen | **COCA** |
| 008 | Thyroid ultrasound | **Thyroid Ultrasound** ⭐ |
| 009 | Chest X-ray pneumonia | **CheXpert** |
| 013 | Aortic stenosis echo | **EchoNet-Dynamic** |
| 018 | CT appendicitis | **COCA** |
| Cancer Dx | Histopathology diagnosis | **Brain-Mets-Lung** ⭐ NEW! |

---

## File Format Guide

### Working with Different Formats

#### SVS Files (Whole Slide Images)
```python
# Install: pip install openslide-python
from openslide import OpenSlide

slide = OpenSlide('case_001.svs')
thumbnail = slide.get_thumbnail((2048, 2048))
thumbnail.save('preview.png')
```

#### DICOM Files (CT/MRI)
```python
# Install: pip install pydicom pillow
import pydicom
from PIL import Image

ds = pydicom.dcmread('scan_001.dcm')
image_array = ds.pixel_array
image = Image.fromarray(image_array)
```

#### Video Files (Echo/Ultrasound)
```python
# Install: pip install opencv-python
import cv2

cap = cv2.VideoCapture('echo_001.avi')
ret, frame = cap.read()
cv2.imwrite('frame.png', frame)
```

#### NIfTI Files (Brain MRI)
```python
# Install: pip install nibabel
import nibabel as nib

img = nib.load('brain_mri.nii.gz')
data = img.get_fdata()
# Extract slice: data[:, :, slice_idx]
```

---

## Next Steps

1. **Choose datasets** based on your scenarios
2. **Download** using helper scripts:
   ```bash
   python3 scripts/download_aimi_samples.py --list
   python3 scripts/download_aimi_samples.py --info <dataset-name>
   python3 scripts/download_aimi_samples.py --dataset <dataset-name> --prepare
   ```
3. **Process images** to create benchmark-ready formats
4. **Update scenarios.json** with real image paths
5. **Run benchmarks** with real clinical data

---

## Support Resources

- **Download Helper:** `python3 scripts/download_aimi_samples.py --help`
- **Histopath Previews:** `python3 scripts/create_histopath_previews.py --help`
- **Stanford AIMI Contact:** aimicenter@stanford.edu
- **TCIA Help Desk:** <https://www.cancerimagingarchive.net/support/>

---

**Last Updated:** February 14, 2026
