# Kaggle Datasets for All Medical Imaging Categories

## Quick Reference: Best Datasets by Modality

| Modality | Kaggle Dataset | Size | Images | Manual Download |
|----------|----------------|------|--------|-----------------|
| 🔬 **Histopathology** | LC25000 | 1.5 GB | 25,000 | ⭐ RECOMMENDED |
| 📷 **X-ray** | RSNA Pneumonia | 3 GB | 26,684 | ⭐ RECOMMENDED |
| 🧠 **MRI** | Brain Tumor MRI | 150 MB | 3,264 | ⭐ RECOMMENDED |
| 🫁 **CT Scan** | COVID-19 CT | 1 GB | 2,482 | ⭐ RECOMMENDED |
| 🫀 **Echo** | (Use Stanford AIMI) | 10 GB | 10,030 | Registration |
| 🦋 **Ultrasound** | Breast Ultrasound | 600 MB | 780 | ⭐ RECOMMENDED |

---

## 🔬 Histopathology

### LC25000 - Lung and Colon Cancer ⭐ BEST
**URL:** https://www.kaggle.com/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images

**Details:**
- 25,000 images (768x768 pixels)
- **Lung:** 5,000 benign + 5,000 adenocarcinoma + 5,000 squamous cell
- **Colon:** 5,000 benign + 5,000 adenocarcinoma
- H&E stained, ready to use

**Manual Download:**
```bash
# 1. Visit and click Download
open https://www.kaggle.com/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images

# 2. After download, extract to project
cd ~/Downloads
unzip lung-and-colon-cancer-histopathological-images.zip
mkdir -p ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/histopath
cp lung_colon_image_set/lung_image_sets/lung_n/*.jpeg \
   ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/histopath/
```

**Alternate:** BreakHis (Breast Cancer)
- **URL:** https://www.kaggle.com/datasets/ambarish/breakhis
- 7,909 images, 4 magnifications

---

## 📷 X-ray (Chest)

### RSNA Pneumonia Detection Challenge ⭐ BEST
**URL:** https://www.kaggle.com/competitions/rsna-pneumonia-detection-challenge/data

**Details:**
- 26,684 chest X-ray images (DICOM format)
- Labels: Normal, No Lung Opacity, Lung Opacity
- Bounding boxes for pneumonia cases

**Manual Download:**
```bash
# 1. Visit competition data page
open https://www.kaggle.com/competitions/rsna-pneumonia-detection-challenge/data

# 2. Click "Download All" 
# Files: stage_2_train_images.zip (3 GB)

# 3. Extract
cd ~/Downloads
unzip stage_2_train_images.zip -d rsna_pneumonia
mkdir -p ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/xray

# 4. Convert DICOM to PNG (first 10 for testing)
python3 << 'EOF'
import pydicom
from PIL import Image
import numpy as np
from pathlib import Path

input_dir = Path.home() / 'Downloads/rsna_pneumonia/stage_2_train_images'
output_dir = Path.home() / 'Documents/GitHub/medbilldozer/benchmarks/clinical_images/xray'
output_dir.mkdir(parents=True, exist_ok=True)

for i, dcm_file in enumerate(sorted(input_dir.glob('*.dcm'))[:10]):
    ds = pydicom.dcmread(dcm_file)
    img_array = ds.pixel_array
    img = Image.fromarray(img_array)
    img.save(output_dir / f'chest_xray_{i+1:03d}.png')
    print(f"✓ Converted: {dcm_file.name}")
EOF
```

**Alternate:** NIH Chest X-rays
- **URL:** https://www.kaggle.com/datasets/nih-chest-xrays/data
- 112,120 images, 14 disease labels

---

## 📷 X-ray (Bone/MSK)

### MURA - Musculoskeletal Radiographs ⭐ BEST
**URL:** https://www.kaggle.com/datasets/kmader/mura-bone-xrays

**Details:**
- 40,561 images
- 7 body parts: elbow, finger, forearm, hand, humerus, shoulder, wrist
- Normal vs abnormal labels

**Manual Download:**
```bash
# 1. Visit and download
open https://www.kaggle.com/datasets/kmader/mura-bone-xrays

# 2. Extract
cd ~/Downloads
unzip mura-bone-xrays.zip
mkdir -p ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/xray_msk

# 3. Copy forearm examples
cp MURA-v1.1/train/XR_FOREARM/patient*/study*/*.png \
   ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/xray_msk/ | head -10
```

---

## 🧠 MRI (Brain)

### Brain Tumor MRI Dataset ⭐ BEST
**URL:** https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset

**Details:**
- 3,264 brain MRI images
- 4 classes: glioma, meningioma, pituitary tumor, no tumor
- Pre-processed, ready to use

**Manual Download:**
```bash
# 1. Visit and download
open https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset

# 2. Extract
cd ~/Downloads
unzip brain-tumor-mri-dataset.zip
mkdir -p ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/mri

# 3. Copy examples from each category
cp Training/notumor/*.jpg ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/mri/ | head -3
cp Training/glioma/*.jpg ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/mri/ | head -3
```

**Alternate:** Brain MRI with Alzheimer's
- **URL:** https://www.kaggle.com/datasets/tourist55/alzheimers-dataset-4-class-of-images
- 6,400 images, 4 dementia stages

---

## 🫁 CT Scan

### COVID-19 CT Scan Dataset ⭐ BEST
**URL:** https://www.kaggle.com/datasets/plameneduardo/sarscov2-ctscan-dataset

**Details:**
- 2,482 CT scan images
- COVID-19 positive vs negative
- Lung window images

**Manual Download:**
```bash
# 1. Visit and download
open https://www.kaggle.com/datasets/plameneduardo/sarscov2-ctscan-dataset

# 2. Extract
cd ~/Downloads
unzip sarscov2-ctscan-dataset.zip
mkdir -p ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/ct

# 3. Copy examples
cp COVID/*.png ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/ct/ | head -5
cp non-COVID/*.png ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/ct/ | head -5
```

**Alternate:** CT Medical Images
- **URL:** https://www.kaggle.com/datasets/kmader/siim-medical-images
- 10,000+ CT and X-ray images

---

## 🦋 Ultrasound

### Breast Ultrasound Images ⭐ BEST
**URL:** https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset

**Details:**
- 780 ultrasound images
- 3 classes: normal, benign, malignant
- Ground truth masks included

**Manual Download:**
```bash
# 1. Visit and download
open https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset

# 2. Extract
cd ~/Downloads
unzip breast-ultrasound-images-dataset.zip
mkdir -p ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/ultrasound

# 3. Copy examples
cp Dataset_BUSI_with_GT/normal/*.png ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/ultrasound/ | head -3
cp Dataset_BUSI_with_GT/benign/*.png ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/ultrasound/ | head -3
cp Dataset_BUSI_with_GT/malignant/*.png ~/Documents/GitHub/medbilldozer/benchmarks/clinical_images/ultrasound/ | head -3
```

**Alternate:** For Thyroid - Use Stanford AIMI (see other guide)

---

## 🫀 Echocardiogram

### No Good Kaggle Dataset
**Recommendation:** Use **Stanford AIMI EchoNet-Dynamic** (best quality)
- 10,030 labeled echocardiogram videos
- Requires registration but free
- See: `download_aimi_samples.py --dataset echonet-dynamic`

**Alternate (Lower Quality):**
- **URL:** https://www.kaggle.com/datasets/waseemhussain/ultrasound-heart-images
- Small dataset, less comprehensive

---

## 📊 Complete Setup Script

Save this script and run after manual downloads:

```bash
#!/bin/bash
# organize_kaggle_datasets.sh

BASE_DIR=~/Documents/GitHub/medbilldozer/benchmarks/clinical_images
DOWNLOADS=~/Downloads

echo "Organizing Kaggle datasets..."

# 1. Histopathology (LC25000)
if [ -d "$DOWNLOADS/lung_colon_image_set" ]; then
    echo "📦 Processing LC25000..."
    mkdir -p $BASE_DIR/histopath
    cp $DOWNLOADS/lung_colon_image_set/lung_image_sets/lung_n/lungn{1,2}.jpeg $BASE_DIR/histopath/
    cp $DOWNLOADS/lung_colon_image_set/lung_image_sets/lung_aca/lungaca1.jpeg $BASE_DIR/histopath/
    cp $DOWNLOADS/lung_colon_image_set/lung_image_sets/lung_scc/lungscc1.jpeg $BASE_DIR/histopath/
    echo "  ✓ Copied 4 histopathology images"
fi

# 2. Chest X-ray (RSNA)
if [ -d "$DOWNLOADS/rsna_pneumonia" ]; then
    echo "📦 Processing RSNA Pneumonia..."
    mkdir -p $BASE_DIR/xray_chest
    # Convert first 10 DICOM files (requires pydicom)
    python3 - << 'EOF'
import pydicom
from PIL import Image
from pathlib import Path
import sys

input_dir = Path.home() / 'Downloads/rsna_pneumonia/stage_2_train_images'
output_dir = Path.home() / 'Documents/GitHub/medbilldozer/benchmarks/clinical_images/xray_chest'
output_dir.mkdir(parents=True, exist_ok=True)

for i, dcm in enumerate(sorted(input_dir.glob('*.dcm'))[:10]):
    try:
        ds = pydicom.dcmread(dcm)
        img = Image.fromarray(ds.pixel_array)
        img.save(output_dir / f'chest_xray_{i+1:03d}.png')
    except: pass
print("  ✓ Converted 10 chest X-rays")
EOF
fi

# 3. Brain MRI
if [ -d "$DOWNLOADS/Training" ]; then
    echo "📦 Processing Brain MRI..."
    mkdir -p $BASE_DIR/mri_brain
    find $DOWNLOADS/Training/notumor -name "*.jpg" | head -3 | xargs -I {} cp {} $BASE_DIR/mri_brain/
    find $DOWNLOADS/Training/glioma -name "*.jpg" | head -3 | xargs -I {} cp {} $BASE_DIR/mri_brain/
    echo "  ✓ Copied 6 brain MRI images"
fi

# 4. CT Scan
if [ -d "$DOWNLOADS/COVID" ]; then
    echo "📦 Processing COVID CT..."
    mkdir -p $BASE_DIR/ct_chest
    find $DOWNLOADS/COVID -name "*.png" | head -5 | xargs -I {} cp {} $BASE_DIR/ct_chest/
    find $DOWNLOADS/non-COVID -name "*.png" | head -5 | xargs -I {} cp {} $BASE_DIR/ct_chest/
    echo "  ✓ Copied 10 CT images"
fi

# 5. Ultrasound
if [ -d "$DOWNLOADS/Dataset_BUSI_with_GT" ]; then
    echo "📦 Processing Breast Ultrasound..."
    mkdir -p $BASE_DIR/ultrasound
    find $DOWNLOADS/Dataset_BUSI_with_GT/normal -name "*.png" ! -name "*mask*" | head -2 | xargs -I {} cp {} $BASE_DIR/ultrasound/
    find $DOWNLOADS/Dataset_BUSI_with_GT/benign -name "*.png" ! -name "*mask*" | head -2 | xargs -I {} cp {} $BASE_DIR/ultrasound/
    find $DOWNLOADS/Dataset_BUSI_with_GT/malignant -name "*.png" ! -name "*mask*" | head -2 | xargs -I {} cp {} $BASE_DIR/ultrasound/
    echo "  ✓ Copied 6 ultrasound images"
fi

# 6. MSK X-ray
if [ -d "$DOWNLOADS/MURA-v1.1" ]; then
    echo "📦 Processing MURA MSK X-rays..."
    mkdir -p $BASE_DIR/xray_msk
    find $DOWNLOADS/MURA-v1.1/train/XR_FOREARM -name "*.png" | head -10 | xargs -I {} cp {} $BASE_DIR/xray_msk/
    echo "  ✓ Copied 10 forearm X-rays"
fi

echo ""
echo "✅ Done! Check your images in:"
echo "   $BASE_DIR/"
```

Save as `scripts/organize_kaggle_datasets.sh` and run:
```bash
chmod +x scripts/organize_kaggle_datasets.sh
./scripts/organize_kaggle_datasets.sh
```

---

## Summary: What to Download

### Priority Downloads (Recommended Order)

1. **🔬 Histopathology** - LC25000 (1.5 GB) ⭐ Start here!
2. **📷 X-ray Chest** - RSNA Pneumonia (3 GB)
3. **🧠 MRI** - Brain Tumor (150 MB)
4. **🫁 CT** - COVID-19 CT (1 GB)
5. **🦋 Ultrasound** - Breast US (600 MB)
6. **📷 X-ray MSK** - MURA (5 GB - optional)

### Total Download: ~6.5 GB for core datasets

---

## Quick Start

```bash
# 1. Download datasets manually from Kaggle (click Download buttons)
# Visit each URL and download:
open https://www.kaggle.com/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images
open https://www.kaggle.com/competitions/rsna-pneumonia-detection-challenge/data
open https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset
open https://www.kaggle.com/datasets/plameneduardo/sarscov2-ctscan-dataset
open https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset

# 2. After downloads complete, run organizer
./scripts/organize_kaggle_datasets.sh

# 3. Check results
ls -R benchmarks/clinical_images/
```

---

**Last Updated:** February 14, 2026
