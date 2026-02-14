# Histopathology Dataset Guide: Brain-Mets-Lung-MRI-Path-Segs

## Overview

The **Brain-Mets-Lung-MRI-Path-Segs** dataset from The Cancer Imaging Archive (TCIA) provides 103 patients with brain metastases from primary lung cancer, including **111 whole slide histopathology images** matched with MRI scans.

This is an excellent resource for:
- Training AI models on real histopathology images
- Benchmarking cancer diagnosis scenarios
- Multi-modal imaging research (histopathology + radiology)
- Cancer pathology classification

## Dataset Details

### Basic Statistics
- **Patients:** 103 unique patients (8 with recurrences)
- **Cases:** 111 total cases (including recurrences)
- **Histopathology Images:** 111 whole slide images (SVS format)
- **MRI Scans:** 111 pre-operative MRI studies with segmentations
- **Size:** 18.6 GB (histopathology) + 622 MB (MRI)

### Histopathology Image Specifications
- **Format:** SVS (Aperio/Leica whole slide image format)
- **Staining:** Hematoxylin and Eosin (H&E)
- **Magnification:** 20x
- **Scanner:** MoticEasyScan Infinity whole slide imaging system
- **Resolution:** High-resolution digital pathology (gigapixel images)
- **Tissue:** FFPE (formalin-fixed paraffin-embedded) sections at 5 μm thickness

### Histologic Subtypes
The dataset includes diverse lung cancer subtypes:
- **Small Cell Lung Cancer (SCLC):** 12 cases (11%)
- **Non-Small Cell Lung Cancer (NSCLC):** 99 cases (89%)
  - Adenocarcinoma: 79 cases (71%)
  - Non-adenocarcinoma: 20 cases (18%)

### Clinical Data Included
Each case includes comprehensive metadata:
- Patient demographics (age, sex, race)
- Smoking history (pack-years)
- Lesion characteristics (size, location)
- Histologic subtype
- Molecular markers:
  - EGFR mutation status
  - ALK translocation status
  - PD-L1 expression level
- Graded Prognostic Assessment (GPA) score
- Karnofsky Performance Status (KPS)
- Number of brain metastases
- Presence of extracranial metastasis (ECM)

### Matched Radiology Data
Each histopathology slide is matched with:
- **T1CE MRI:** T1-weighted contrast-enhanced sequences
- **FLAIR MRI:** Fluid-attenuated inversion recovery sequences
- **Core Tumor Segmentation:** Expert neuroradiologist annotations (107/111 cases)
- **Whole Tumor Segmentation:** Including peritumoral edema (104/111 cases)
- **Radiomic Features:** 107 PyRadiomics features per case

## Download Instructions

### Step 1: Visit TCIA Collection Page
Navigate to: https://www.cancerimagingarchive.net/collection/brain-mets-lung-mri-path-segs/

### Step 2: Download Options
The dataset offers three download packages:

1. **Histopathology Images** (18.6 GB)
   - 111 whole slide images in SVS format
   - Recommended: Use IBM Aspera Connect for faster downloads

2. **Radiology Images and Segmentations** (622 MB)
   - MRI scans in NIfTI format (BraTS 2023 Challenge format)
   - Brain-extracted for privacy

3. **Clinical Data and Radiomics** (367 KB)
   - Excel spreadsheet with clinical metadata
   - Scanner acquisition parameters
   - Extracted radiomic features

### Step 3: Install Download Tool (Optional)
For large files, install IBM Aspera Connect:
```bash
# Visit: https://www.ibm.com/aspera/connect/
# Or download directly from TCIA download page
```

### Step 4: Download Files
Click the "DOWNLOAD" buttons for each package you need.

### Step 5: Extract and Organize
```bash
# Create directory structure
mkdir -p benchmarks/clinical_images/brain_mets_histopath
cd benchmarks/clinical_images/brain_mets_histopath

# Extract downloaded files
unzip Brain-Mets-Lung-MRI-Path-Segs_histopathology.zip
unzip Brain-Mets-Lung-MRI-Path-Segs_radiology.zip

# Expected structure:
# brain_mets_histopath/
# ├── histopathology/
# │   ├── case_001.svs
# │   ├── case_002.svs
# │   └── ...
# ├── radiology/
# │   ├── case_001_t1ce_img.nii.gz
# │   ├── case_001_flair_img.nii.gz
# │   ├── case_001_core_seg.nii.gz
# │   ├── case_001_whole_seg.nii.gz
# │   └── ...
# └── clinical_data.xlsx
```

## Working with Histopathology Images

### Opening SVS Files
SVS (Aperio/Leica) files are large pyramidal whole slide images. You can use:

#### Python with OpenSlide
```python
from openslide import OpenSlide
import numpy as np
from PIL import Image

# Open whole slide image
slide = OpenSlide('case_001.svs')

# Get slide properties
print(f"Dimensions: {slide.dimensions}")  # Full resolution (e.g., 100,000 x 80,000)
print(f"Level count: {slide.level_count}")  # Pyramid levels (e.g., 4 levels)
print(f"Downsample factors: {slide.level_downsamples}")

# Read a region at full resolution (careful: can be huge!)
region = slide.read_region((0, 0), 0, (2048, 2048))  # x, y, level, (width, height)
region = region.convert('RGB')

# Or read a thumbnail for preview
thumbnail = slide.get_thumbnail((1024, 1024))
thumbnail.save('preview.png')

# Read at lower resolution level
level_2_dims = slide.level_dimensions[2]
lower_res = slide.read_region((0, 0), 2, level_2_dims)

slide.close()
```

#### QuPath (Free GUI Tool)
```bash
# Download QuPath: https://qupath.github.io/
# Open .svs files directly
# Annotate regions of interest
# Export as PNG or TIFF
```

#### ImageJ/Fiji with Bio-Formats
```bash
# Download Fiji: https://fiji.sc/
# Install Bio-Formats plugin
# Open .svs files
# Export regions as standard image formats
```

### Extracting Patches for Deep Learning

```python
from openslide import OpenSlide
import numpy as np
from pathlib import Path

def extract_patches(svs_path, patch_size=256, stride=256, level=0, output_dir='patches'):
    """Extract fixed-size patches from whole slide image."""
    slide = OpenSlide(svs_path)
    width, height = slide.level_dimensions[level]
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    patch_count = 0
    for y in range(0, height - patch_size, stride):
        for x in range(0, width - patch_size, stride):
            # Read patch
            patch = slide.read_region((x, y), level, (patch_size, patch_size))
            patch = patch.convert('RGB')
            
            # Skip mostly white/background patches
            patch_array = np.array(patch)
            if patch_array.mean() < 220:  # Not mostly white
                patch.save(output_path / f'patch_{patch_count:05d}_x{x}_y{y}.png')
                patch_count += 1
    
    slide.close()
    print(f"Extracted {patch_count} patches from {svs_path}")
    return patch_count

# Example usage
extract_patches('case_001.svs', patch_size=512, stride=512, level=1)
```

### Creating Preview Images

```python
def create_preview_image(svs_path, max_size=2048):
    """Create a preview image from whole slide."""
    slide = OpenSlide(svs_path)
    
    # Get thumbnail that fits in max_size
    thumbnail = slide.get_thumbnail((max_size, max_size))
    
    # Save as PNG
    output_name = Path(svs_path).stem + '_preview.png'
    thumbnail.save(output_name)
    
    print(f"Created preview: {output_name}")
    print(f"Size: {thumbnail.size}")
    
    slide.close()
    return output_name

# Create previews for all slides
from pathlib import Path
for svs_file in Path('histopathology').glob('*.svs'):
    create_preview_image(svs_file)
```

## Integration with MedBillDozer Benchmarks

### Step 1: Create Preview Images

```bash
# Install OpenSlide Python library
pip install openslide-python pillow

# Create preview script
python3 scripts/create_histopath_previews.py
```

### Step 2: Update scenarios.json

```json
{
  "scenarios": [
    {
      "id": "scenario_015",
      "category": "histopathology",
      "title": "Brain Metastasis - Adenocarcinoma",
      "clinical_context": "64-year-old with lung adenocarcinoma, new brain lesion on MRI",
      "question": "What is your diagnosis based on this brain biopsy?",
      "image_file": "benchmarks/clinical_images/brain_mets_histopath/case_042_preview.png",
      "image_metadata": {
        "modality": "histopathology",
        "stain": "H&E",
        "magnification": "20x",
        "histologic_subtype": "adenocarcinoma",
        "primary_site": "lung",
        "metastatic_site": "brain",
        "molecular_markers": {
          "EGFR": "mutant",
          "ALK": "negative",
          "PD-L1": "50%"
        }
      },
      "ground_truth": {
        "diagnosis": "Metastatic adenocarcinoma from lung primary",
        "key_findings": [
          "Atypical glandular structures",
          "High nuclear-to-cytoplasmic ratio",
          "Prominent nucleoli",
          "TTF-1 positive (lung origin)"
        ],
        "molecular_profile": "EGFR-mutant, ALK-negative, PD-L1 50%"
      }
    }
  ]
}
```

### Step 3: Link Clinical Data

```python
import pandas as pd

# Load clinical data
clinical_df = pd.read_excel('clinical_data.xlsx', sheet_name='Clinical Data')

# Filter by histologic subtype
adenocarcinoma_cases = clinical_df[
    clinical_df['Histologic Subtype'] == 'Adenocarcinoma'
]

# Select cases with EGFR mutations
egfr_mutant = adenocarcinoma_cases[
    adenocarcinoma_cases['EGFR Status'] == 'Mutant'
]

print(f"Found {len(egfr_mutant)} EGFR-mutant adenocarcinoma cases")

# Get case IDs for benchmark scenarios
for idx, row in egfr_mutant.head(5).iterrows():
    case_id = row['Accession Number']
    print(f"Case {case_id}: Age {row['Age']}, PD-L1 {row['PD-L1 Expression']}")
```

## Use Cases for MedBillDozer

### 1. Cancer Diagnosis Scenarios
Use histopathology images for:
- Metastatic cancer identification
- Histologic subtype classification (SCLC vs adenocarcinoma)
- Tumor cellularity assessment

### 2. Molecular Marker Prediction
Test AI models on:
- EGFR mutation status prediction from histology
- ALK translocation detection
- PD-L1 expression level estimation

### 3. Multi-Modal AI Testing
Combine histopathology with radiology:
- Correlate pathology findings with MRI features
- Test radiomics-pathomics integration
- Validate imaging biomarkers with ground truth pathology

### 4. Prognostic Assessment
Use GPA scores and survival data:
- Test prognostic model predictions
- Validate risk stratification
- Compare AI predictions to clinical outcomes

## Example Benchmark Scenarios

### Scenario: Lung Adenocarcinoma Brain Met with EGFR Mutation

```json
{
  "id": "histopath_001",
  "category": "histopathology",
  "title": "Brain Metastasis - EGFR-Mutant Adenocarcinoma",
  "patient_context": {
    "age": 62,
    "sex": "Female",
    "smoking_history": "15 pack-years",
    "primary_diagnosis": "Lung adenocarcinoma",
    "presentation": "New neurologic symptoms, brain MRI shows enhancing lesion"
  },
  "question": "Review this brain biopsy and determine: 1) Histologic diagnosis, 2) Likely primary site, 3) Molecular profile implications for treatment",
  "image_file": "brain_mets_histopath/case_042_preview.png",
  "ground_truth": {
    "diagnosis": "Metastatic adenocarcinoma, lung primary",
    "histologic_features": [
      "Atypical glandular architecture",
      "High mitotic rate",
      "Necrosis present",
      "TTF-1 positive (IHC)"
    ],
    "molecular_profile": {
      "EGFR": "Exon 19 deletion",
      "ALK": "Negative",
      "PD-L1": "60% TPS"
    },
    "treatment_implications": "EGFR TKI eligible (osimertinib)"
  }
}
```

### Scenario: Small Cell Lung Cancer Brain Met

```json
{
  "id": "histopath_002",
  "category": "histopathology",
  "title": "Brain Metastasis - Small Cell Carcinoma",
  "patient_context": {
    "age": 68,
    "sex": "Male",
    "smoking_history": "40 pack-years",
    "primary_diagnosis": "Small cell lung cancer (limited stage)",
    "presentation": "Confusion, multiple brain lesions on imaging"
  },
  "question": "What is the histologic diagnosis and what are the key distinguishing features?",
  "image_file": "brain_mets_histopath/case_015_preview.png",
  "ground_truth": {
    "diagnosis": "Metastatic small cell carcinoma, lung primary",
    "histologic_features": [
      "Small round blue cells",
      "Scant cytoplasm",
      "Salt-and-pepper chromatin",
      "High nuclear-to-cytoplasmic ratio",
      "Extensive necrosis",
      "Crush artifact"
    ],
    "immunohistochemistry": [
      "Synaptophysin positive",
      "Chromogranin positive",
      "TTF-1 positive",
      "Ki-67 >80%"
    ],
    "treatment_implications": "Platinum-based chemotherapy, PCI candidate"
  }
}
```

## Data Citation Requirements

### Required Citation

When publishing research using this dataset, cite:

```
Chadha, S., Sritharan, D., Dolezal, D., Chande, S., Hager, T., Bousabarah, K.,
Aboian, M., chiang, v., Lin, M., Nguyen, D., Aneja, S. (2025). MR Imaging and
Segmentations with Matched Brain Biopsy Pathology Slides from Patients with Brain
Metastases from Primary Lung Cancer (Brain-Mets-Lung-MRI-Path-Segs) (Version 2)
[dataset]. The Cancer Imaging Archive. https://doi.org/10.7937/k0sm-y874
```

### Related Publication

```
Chadha, S., Sritharan, D. V., Dolezal, D., Chande, S., Hager, T., Bousabarah, K.,
Aboian, M. S., Chiang, V., Lin, M., Nguyen, D. X., & Aneja, S. (2026). Matched MRI,
Segmentations, and Histopathologic Images of Brain Metastases from Primary Lung
Cancer. Scientific Data, 13(1). https://doi.org/10.1038/s41597-025-06353-2
```

## Data Use Policy

This dataset is provided under **Creative Commons Attribution 4.0 (CC BY 4.0)**.

You may:
- ✅ Use for commercial and non-commercial purposes
- ✅ Share and redistribute
- ✅ Adapt and build upon

You must:
- ✅ Give appropriate credit
- ✅ Cite the dataset (see above)
- ✅ Indicate if changes were made
- ✅ Comply with TCIA data usage policies

No registration required! Direct download available.

## External Resources

- **GitHub Repository:** https://github.com/Aneja-Lab-Yale/BM-Pathology-Dataset
  - Code for radiomic feature extraction
  - Brain extraction scripts
  - Analysis pipelines

- **BraTS 2023 Challenge:** Segmentation data formatted for BraTS challenge

## Tips and Best Practices

### Memory Management
Whole slide images are HUGE (gigapixels):
```python
# Don't do this - will crash!
# full_image = slide.read_region((0, 0), 0, slide.dimensions)

# Do this instead - read regions or use lower resolution levels
thumbnail = slide.get_thumbnail((2048, 2048))  # Safe
region = slide.read_region((1000, 1000), 0, (512, 512))  # Safe
low_res = slide.read_region((0, 0), 2, slide.level_dimensions[2])  # Safe
```

### Tissue Detection
Skip background/white areas:
```python
def is_tissue(patch, threshold=220):
    """Check if patch contains tissue (not background)."""
    gray = np.array(patch.convert('L'))
    return gray.mean() < threshold  # Lower values = more tissue
```

### Normalization
H&E staining varies between slides:
```python
# Consider using stain normalization
# pip install histomicstk
from histomicstk.preprocessing.color_normalization import reinhard

normalized = reinhard(patch_array, target_means, target_stds)
```

### Performance
Use multiprocessing for batch processing:
```python
from multiprocessing import Pool

def process_slide(svs_path):
    # Your processing function
    pass

with Pool(processes=4) as pool:
    pool.map(process_slide, svs_files)
```

## Quick Start Checklist

- [ ] Download histopathology images (18.6 GB)
- [ ] Download clinical data spreadsheet (367 KB)
- [ ] Install OpenSlide: `pip install openslide-python`
- [ ] Test opening one SVS file
- [ ] Create preview images for all slides
- [ ] Load clinical data with pandas
- [ ] Select cases for benchmark scenarios
- [ ] Update scenarios.json with image paths and metadata
- [ ] Test benchmark runs with real histopathology images

## Support

- **TCIA Help Desk:** https://www.cancerimagingarchive.net/support/
- **OpenSlide Documentation:** https://openslide.org/api/python/
- **QuPath Forum:** https://forum.image.sc/tag/qupath

---

**Last Updated:** February 14, 2026
