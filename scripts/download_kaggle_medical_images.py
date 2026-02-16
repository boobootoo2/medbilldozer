#!/usr/bin/env python3
"""
Download medical images from Kaggle datasets covering all modalities.

This script downloads curated datasets from Kaggle for:
- X-ray (chest, bone)
- Histopathology (cancer tissue)
- MRI (brain)
- CT (chest, abdomen)
- Echocardiogram (cardiac ultrasound)
- Sonogram/Ultrasound (general)

Each dataset is tracked in manifest.json with full attribution.

Usage:
    python3 scripts/download_kaggle_medical_images.py --setup
    python3 scripts/download_kaggle_medical_images.py --download-all
    python3 scripts/download_kaggle_medical_images.py --select-images
"""

import argparse
import json
import shutil
import subprocess  # nosec B404 - subprocess needed for Kaggle CLI interaction with controlled inputs
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Kaggle datasets for each modality
KAGGLE_DATASETS = {
    'xray': {
        'name': 'COVID-19 Radiography Database',
        'kaggle_id': 'tawsifurrahman/covid19-radiography-database',
        'url': 'https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database',
        'size': '~1.2 GB',
        'description': 'Chest X-rays with COVID-19, normal, viral pneumonia, and lung opacity',
        'classes': ['Normal', 'COVID', 'Lung_Opacity', 'Viral Pneumonia'],
        'image_format': 'PNG',
        'license': 'CC BY 4.0',
        'citation': 'M.E.H. Chowdhury et al. "Can AI help in screening Viral and COVID-19 pneumonia?" IEEE Access, 2020.',
        'positive_class': 'COVID',
        'negative_class': 'Normal'
    },
    'histopathology': {
        'name': 'LC25000 - Lung and Colon Cancer',
        'kaggle_id': 'andrewmvd/lung-and-colon-cancer-histopathological-images',
        'url': 'https://www.kaggle.com/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images',
        'size': '~1.5 GB',
        'description': '25,000 histopathological images of lung and colon tissues',
        'classes': ['lung_n (benign)', 'lung_aca (adenocarcinoma)', 'lung_scc (squamous cell)', 'colon_n', 'colon_aca'],
        'image_format': 'JPEG (768x768)',
        'license': 'CC BY-NC-SA 4.0',
        'citation': 'Borkowski AA et al. "Lung and Colon Cancer Histopathological Image Dataset (LC25000)." arXiv:1912.12142v1, 2019.',
        'positive_class': 'lung_aca',
        'negative_class': 'lung_n'
    },
    'mri': {
        'name': 'Brain Tumor MRI Dataset',
        'kaggle_id': 'masoudnickparvar/brain-tumor-mri-dataset',
        'url': 'https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset',
        'size': '~150 MB',
        'description': 'Brain MRI images with glioma, meningioma, pituitary tumors, and normal',
        'classes': ['glioma', 'meningioma', 'notumor', 'pituitary'],
        'image_format': 'JPG',
        'license': 'Unknown',
        'citation': 'Brain Tumor MRI Dataset (Kaggle)',
        'positive_class': 'glioma',
        'negative_class': 'notumor'
    },
    'ct': {
        'name': 'CT Medical Images',
        'kaggle_id': 'kmader/siim-medical-images',
        'url': 'https://www.kaggle.com/datasets/kmader/siim-medical-images',
        'size': '~3 GB',
        'description': 'DICOM medical images including CT scans from SIIM',
        'classes': ['Various CT scans'],
        'image_format': 'DICOM',
        'license': 'CC0 Public Domain',
        'citation': 'SIIM (Society for Imaging Informatics in Medicine)',
        'positive_class': 'abnormal',
        'negative_class': 'normal'
    },
    'mammogram': {
        'name': 'MIAS Mammography',
        'kaggle_id': 'kmader/mias-mammography',
        'url': 'https://www.kaggle.com/datasets/kmader/mias-mammography',
        'size': '~170 MB',
        'description': 'Mammographic Image Analysis Society (MIAS) database - 322 mammograms',
        'classes': ['Normal', 'Benign', 'Malignant'],
        'image_format': 'PGM',
        'license': 'Unknown',
        'citation': 'Suckling et al. "The Mammographic Image Analysis Society Digital Mammogram Database." Exerpta Medica International Congress Series, 1994.',
        'positive_class': 'malignant',
        'negative_class': 'normal'
    },
    'ultrasound': {
        'name': 'Breast Ultrasound Images',
        'kaggle_id': 'aryashah2k/breast-ultrasound-images-dataset',
        'url': 'https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset',
        'size': '~50 MB',
        'description': 'Breast ultrasound images: normal, benign, and malignant',
        'classes': ['normal', 'benign', 'malignant'],
        'image_format': 'PNG',
        'license': 'CC BY-NC-SA 4.0',
        'citation': 'Al-Dhabyani W et al. "Dataset of breast ultrasound images." Data in Brief, 2020.',
        'positive_class': 'malignant',
        'negative_class': 'normal'
    }
}


def check_kaggle_setup() -> bool:
    """Check if Kaggle is properly configured."""
    kaggle_json = Path.home() / '.kaggle' / 'kaggle.json'
    
    if not kaggle_json.exists():
        print("\n❌ Kaggle credentials not found!")
        print("\nSetup instructions:")
        print("1. Visit: https://www.kaggle.com/settings")
        print("2. Scroll to 'API' section")
        print("3. Click 'Create New Token'")
        print("4. Save kaggle.json to ~/.kaggle/")
        print("5. Run: chmod 600 ~/.kaggle/kaggle.json")
        return False
    
    try:
        result = subprocess.run(  # nosec B603, B607 - Safe: list form, trusted kaggle CLI, no user input
            ['kaggle', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Kaggle CLI configured: {result.stdout.strip()}")
            return True
    except Exception as e:
        print(f"❌ Kaggle CLI error: {e}")
        print("\nInstall kaggle CLI:")
        print("  pip install kaggle")
        return False
    
    return False


def download_dataset(modality: str, dataset_info: Dict, base_dir: Path) -> bool:
    """Download a dataset from Kaggle."""
    output_dir = base_dir / modality
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"Downloading: {dataset_info['name']}")
    print(f"Modality: {modality.upper()}")
    print(f"Size: {dataset_info['size']}")
    print(f"{'='*70}")
    
    # Check if already downloaded
    if list(output_dir.glob('**/*')):
        response = input(f"\n{output_dir} already has files. Re-download? (y/n): ").strip().lower()
        if response != 'y':
            print("Skipping download.")
            return True
    
    try:
        print("\nDownloading from Kaggle...")
        result = subprocess.run(  # nosec B603, B607 - Safe: list form, dataset_id from trusted config
            [
                'kaggle', 'datasets', 'download', '-d',
                dataset_info['kaggle_id'],
                '-p', str(output_dir),
                '--unzip'
            ],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes
        )
        
        if result.returncode != 0:
            print(f"❌ Download failed: {result.stderr}")
            return False
        
        print(f"✅ Downloaded to: {output_dir}")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Download timed out (30 min limit)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def find_and_select_images(modality: str, dataset_info: Dict, base_dir: Path, manifest: Dict) -> List[Dict]:
    """Find and select 1 positive and 1 negative image from dataset."""
    modality_dir = base_dir / modality
    
    if not modality_dir.exists():
        print(f"⚠️  Directory not found: {modality_dir}")
        return []
    
    print(f"\n{'='*70}")
    print(f"Selecting images for: {modality.upper()}")
    print(f"{'='*70}")
    
    # Find image files
    image_extensions = ['.png', '.jpg', '.jpeg', '.dcm']
    all_images = []
    for ext in image_extensions:
        all_images.extend(modality_dir.glob(f'**/*{ext}'))
    
    if not all_images:
        print(f"⚠️  No images found in {modality_dir}")
        return []
    
    print(f"Found {len(all_images)} images")
    
    # Try to find positive and negative based on directory structure
    positive_keywords = [dataset_info['positive_class'].lower(), 'abnormal', 'malignant', 'positive']
    negative_keywords = [dataset_info['negative_class'].lower(), 'normal', 'benign', 'negative']
    
    positive_imgs = []
    negative_imgs = []
    
    for img_path in all_images:
        path_str = str(img_path).lower()
        if any(kw in path_str for kw in positive_keywords):
            positive_imgs.append(img_path)
        elif any(kw in path_str for kw in negative_keywords):
            negative_imgs.append(img_path)
    
    print(f"  Positive candidates: {len(positive_imgs)}")
    print(f"  Negative candidates: {len(negative_imgs)}")
    
    selected = []
    
    # Select 1 positive
    if positive_imgs:
        pos_img = positive_imgs[0]
        dest_name = f"{modality}_positive.{pos_img.suffix.lstrip('.')}"
        dest_path = base_dir / 'selected' / dest_name
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pos_img, dest_path)
        
        selected.append({
            'filename': dest_name,
            'modality': modality,
            'diagnosis': 'positive',
            'class': dataset_info['positive_class'],
            'source_file': str(pos_img.relative_to(base_dir)),
            'dataset': dataset_info['name'],
            'dataset_url': dataset_info['url'],
            'license': dataset_info['license'],
            'citation': dataset_info['citation']
        })
        print(f"  ✓ Selected positive: {dest_name}")
    
    # Select 1 negative
    if negative_imgs:
        neg_img = negative_imgs[0]
        dest_name = f"{modality}_negative.{neg_img.suffix.lstrip('.')}"
        dest_path = base_dir / 'selected' / dest_name
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(neg_img, dest_path)
        
        selected.append({
            'filename': dest_name,
            'modality': modality,
            'diagnosis': 'negative',
            'class': dataset_info['negative_class'],
            'source_file': str(neg_img.relative_to(base_dir)),
            'dataset': dataset_info['name'],
            'dataset_url': dataset_info['url'],
            'license': dataset_info['license'],
            'citation': dataset_info['citation']
        })
        print(f"  ✓ Selected negative: {dest_name}")
    
    return selected


def create_manifest(images: List[Dict], manifest_path: Path):
    """Create manifest.json with all image metadata and attributions."""
    manifest = {
        'created': datetime.now().isoformat(),
        'description': 'Medical imaging dataset with attributions',
        'total_images': len(images),
        'modalities': list(set(img['modality'] for img in images)),
        'images': images,
        'datasets_used': {}
    }
    
    # Group by dataset for easy attribution
    for img in images:
        dataset_name = img['dataset']
        if dataset_name not in manifest['datasets_used']:
            manifest['datasets_used'][dataset_name] = {
                'url': img['dataset_url'],
                'license': img['license'],
                'citation': img['citation'],
                'images_count': 0
            }
        manifest['datasets_used'][dataset_name]['images_count'] += 1
    
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Created manifest: {manifest_path}")


def print_attribution_guide(manifest_path: Path):
    """Print attribution guide for use in papers/presentations."""
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    print("\n" + "="*70)
    print("ATTRIBUTION GUIDE")
    print("="*70)
    print("\nFor publications, include these citations:\n")
    
    for dataset_name, info in manifest['datasets_used'].items():
        print(f"• {dataset_name}")
        print(f"  {info['citation']}")
        print(f"  {info['url']}")
        print(f"  License: {info['license']}")
        print(f"  Images used: {info['images_count']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Download medical images from Kaggle with attribution tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--setup', action='store_true', help='Check Kaggle setup')
    parser.add_argument('--list-datasets', action='store_true', help='List available datasets')
    parser.add_argument('--download-all', action='store_true', help='Download all datasets')
    parser.add_argument('--download', type=str, help='Download specific modality')
    parser.add_argument('--select-images', action='store_true', help='Select 1 pos + 1 neg from each')
    parser.add_argument('--output', type=Path, default=Path('benchmarks/clinical_images/kaggle_datasets'))
    
    args = parser.parse_args()
    
    base_dir = args.output
    base_dir.mkdir(parents=True, exist_ok=True)
    
    if args.setup or args.list_datasets:
        print("\n" + "="*70)
        print("KAGGLE MEDICAL IMAGING DATASETS")
        print("="*70)
        
        for modality, info in KAGGLE_DATASETS.items():
            print(f"\n📊 {modality.upper()}: {info['name']}")
            print(f"   Dataset: {info['kaggle_id']}")
            print(f"   Size: {info['size']}")
            print(f"   Classes: {', '.join(info['classes'])}")
            print(f"   License: {info['license']}")
            print(f"   URL: {info['url']}")
        
        if args.setup:
            print("\n" + "="*70)
            check_kaggle_setup()
        
        return
    
    if not check_kaggle_setup():
        sys.exit(1)
    
    if args.download_all:
        print("\n" + "="*70)
        print("DOWNLOADING ALL DATASETS")
        print("="*70)
        print("\nThis will download ~6.5 GB of data. Continue? (y/n): ", end='')
        
        if input().strip().lower() != 'y':
            print("Cancelled.")
            return
        
        for modality, dataset_info in KAGGLE_DATASETS.items():
            download_dataset(modality, dataset_info, base_dir)
    
    elif args.download:
        modality = args.download.lower()
        if modality not in KAGGLE_DATASETS:
            print(f"❌ Unknown modality: {modality}")
            print(f"Available: {', '.join(KAGGLE_DATASETS.keys())}")
            sys.exit(1)
        
        download_dataset(modality, KAGGLE_DATASETS[modality], base_dir)
    
    if args.select_images:
        print("\n" + "="*70)
        print("SELECTING IMAGES (1 positive + 1 negative per modality)")
        print("="*70)
        
        all_selected = []
        for modality, dataset_info in KAGGLE_DATASETS.items():
            selected = find_and_select_images(modality, dataset_info, base_dir, {})
            all_selected.extend(selected)
        
        if all_selected:
            manifest_path = base_dir / 'selected' / 'manifest.json'
            create_manifest(all_selected, manifest_path)
            print_attribution_guide(manifest_path)
            
            print("\n" + "="*70)
            print("✅ SUCCESS!")
            print("="*70)
            print(f"\nSelected images: {base_dir / 'selected'}/")
            print(f"Manifest: {manifest_path}")
            print(f"\nTotal images: {len(all_selected)}")


if __name__ == '__main__':
    main()
