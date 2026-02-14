# Kaggle Medical Images - Quick Start Guide

## Goal
Download 12 real medical images (6 positive, 6 negative) covering all 6 modalities with proper attribution.

## One-Time Setup (5 minutes)

### 1. Install Kaggle CLI
```bash
pip install kaggle
```

### 2. Get Kaggle API Credentials
1. Visit: https://www.kaggle.com/settings
2. Scroll to "API" section
3. Click **"Create New Token"**
4. This downloads `kaggle.json` to your Downloads folder

### 3. Install Credentials
```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 4. Test Setup
```bash
kaggle datasets list --page-size 5
```

If you see datasets listed, you're ready! ✅

## Download Images (3 commands)

### Step 1: List Available Datasets
```bash
python3 scripts/download_kaggle_medical_images.py --list-datasets
```

### Step 2: Download All Datasets (~6.5 GB, 30-60 minutes)
```bash
python3 scripts/download_kaggle_medical_images.py --download-all
```

This downloads 6 datasets:
- **X-ray**: COVID-19 Radiography (~1.2 GB)
- **Histopathology**: LC25000 Lung/Colon Cancer (~1.5 GB)
- **MRI**: Brain Tumor MRI (~150 MB)
- **CT**: SIIM Medical Images (~3 GB)
- **Echo**: China Echocardiogram (~500 MB)
- **Ultrasound**: Breast Ultrasound (~50 MB)

### Step 3: Select 12 Images (1 pos + 1 neg per modality)
```bash
python3 scripts/download_kaggle_medical_images.py --select-images
```

## Result

You'll have:
```
benchmarks/clinical_images/kaggle_datasets/selected/
├── xray_positive.png
├── xray_negative.png
├── histopathology_positive.jpeg
├── histopathology_negative.jpeg
├── mri_positive.jpg
├── mri_negative.jpg
├── ct_positive.dcm (or .jpg)
├── ct_negative.dcm (or .jpg)
├── echo_positive.jpg
├── echo_negative.jpg
├── ultrasound_positive.png
├── ultrasound_negative.png
└── manifest.json  ← Full attribution info!
```

## Using manifest.json for Attribution

The `manifest.json` includes everything you need:

```json
{
  "created": "2026-02-14T...",
  "total_images": 12,
  "modalities": ["xray", "histopathology", "mri", "ct", "echo", "ultrasound"],
  "images": [
    {
      "filename": "xray_positive.png",
      "modality": "xray",
      "diagnosis": "positive",
      "class": "COVID",
      "dataset": "COVID-19 Radiography Database",
      "dataset_url": "https://www.kaggle.com/...",
      "license": "CC BY 4.0",
      "citation": "M.E.H. Chowdhury et al. ..."
    }
  ],
  "datasets_used": {
    "COVID-19 Radiography Database": {
      "url": "https://www.kaggle.com/...",
      "license": "CC BY 4.0",
      "citation": "M.E.H. Chowdhury et al. ...",
      "images_count": 2
    }
  }
}
```

## Alternative: Download One Modality at a Time

If you don't want to download everything:

```bash
# Just X-rays (1.2 GB)
python3 scripts/download_kaggle_medical_images.py --download xray

# Just Histopathology (1.5 GB)
python3 scripts/download_kaggle_medical_images.py --download histopathology

# Just MRI (150 MB) - smallest!
python3 scripts/download_kaggle_medical_images.py --download mri

# Then select images
python3 scripts/download_kaggle_medical_images.py --select-images
```

## Troubleshooting

### "KeyError: 'username'"
Your `kaggle.json` is not in the right place or has wrong format.

**Fix:**
```bash
cat ~/.kaggle/kaggle.json
# Should show: {"username":"yourname","key":"abc123..."}

# If not there:
ls ~/Downloads/kaggle.json
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### "401 Unauthorized"
Your API token expired or is invalid.

**Fix:**
1. Go to https://www.kaggle.com/settings
2. Click "Create New Token" (this invalidates old ones)
3. Replace `~/.kaggle/kaggle.json` with new file

### Download is slow
Large datasets (CT = 3GB) take time. Use `--download <modality>` to download one at a time.

### Images not found during selection
Some datasets have non-standard directory structures. The script will show what it found. You can manually copy images:

```bash
# Find all images in a dataset
find benchmarks/clinical_images/kaggle_datasets/mri -name "*.jpg" | head -20

# Manually copy specific images
cp <source> benchmarks/clinical_images/kaggle_datasets/selected/mri_positive.jpg
```

## Dataset Details

| Modality | Dataset | Size | License | Images |
|----------|---------|------|---------|--------|
| X-ray | COVID-19 Radiography | 1.2 GB | CC BY 4.0 | 21,000+ |
| Histopathology | LC25000 | 1.5 GB | CC BY-NC-SA 4.0 | 25,000 |
| MRI | Brain Tumor MRI | 150 MB | Unknown | 7,000+ |
| CT | SIIM Medical Images | 3 GB | CC0 Public | 10,000+ |
| Echo | China Echocardiogram | 500 MB | Unknown | 1,000+ |
| Ultrasound | Breast Ultrasound | 50 MB | CC BY-NC-SA 4.0 | 780 |

## Using Images in Your App

Once you have the selected images and manifest:

```python
import json
from pathlib import Path

# Load manifest
manifest_path = Path('benchmarks/clinical_images/kaggle_datasets/selected/manifest.json')
with open(manifest_path) as f:
    manifest = json.load(f)

# Get all X-ray images
xray_images = [img for img in manifest['images'] if img['modality'] == 'xray']

# Get attribution for an image
image_info = manifest['images'][0]
attribution = f"{image_info['dataset']} - {image_info['license']}"
citation = image_info['citation']
```

## Quick Commands Reference

```bash
# Setup
pip install kaggle
# Download kaggle.json from https://www.kaggle.com/settings
mv ~/Downloads/kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json

# Check setup
python3 scripts/download_kaggle_medical_images.py --setup

# Download everything
python3 scripts/download_kaggle_medical_images.py --download-all

# Select 12 images
python3 scripts/download_kaggle_medical_images.py --select-images

# Done! Images in:
ls benchmarks/clinical_images/kaggle_datasets/selected/
```

---

**Total Time:** ~60 minutes (mostly download time)  
**Total Size:** ~6.5 GB  
**Result:** 12 properly attributed medical images ready to use! 🎉
