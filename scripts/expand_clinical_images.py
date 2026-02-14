#!/usr/bin/env python3
"""
Expand clinical validation image set from 2 per modality to 3 per modality.
Selects additional positive and negative images from downloaded Kaggle datasets.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
SELECTED_DIR = PROJECT_ROOT / 'benchmarks/clinical_images/kaggle_datasets/selected'
MANIFEST_PATH = SELECTED_DIR / 'manifest.json'

# Image sources to add (need 1 more of each type for each modality)
NEW_IMAGES = {
    'xray': {
        'covid_2': {
            'source': 'xray/COVID-19_Radiography_Dataset/COVID/images/COVID-2.png',
            'dest': 'xray_positive_2.png',
            'diagnosis': 'positive',
            'class': 'COVID'
        },
        'normal_2': {
            'source': 'xray/COVID-19_Radiography_Dataset/Normal/images/Normal-2.png',
            'dest': 'xray_negative_2.png',
            'diagnosis': 'negative',
            'class': 'Normal'
        },
        'covid_3': {
            'source': 'xray/COVID-19_Radiography_Dataset/COVID/images/COVID-3.png',
            'dest': 'xray_positive_3.png',
            'diagnosis': 'positive',
            'class': 'COVID'
        },
        'normal_3': {
            'source': 'xray/COVID-19_Radiography_Dataset/Normal/images/Normal-3.png',
            'dest': 'xray_negative_3.png',
            'diagnosis': 'negative',
            'class': 'Normal'
        }
    },
    'histopathology': {
        'aca_2': {
            'source': 'histopathology/lung_colon_image_set/lung_image_sets/lung_aca/lungaca2297.jpeg',
            'dest': 'histopathology_positive_2.jpeg',
            'diagnosis': 'positive',
            'class': 'lung_aca'
        },
        'normal_2': {
            'source': 'histopathology/lung_colon_image_set/lung_image_sets/lung_n/lungn2038.jpeg',
            'dest': 'histopathology_negative_2.jpeg',
            'diagnosis': 'negative',
            'class': 'lung_n'
        },
        'aca_3': {
            'source': 'histopathology/lung_colon_image_set/lung_image_sets/lung_aca/lungaca2298.jpeg',
            'dest': 'histopathology_positive_3.jpeg',
            'diagnosis': 'positive',
            'class': 'lung_aca'
        },
        'normal_3': {
            'source': 'histopathology/lung_colon_image_set/lung_image_sets/lung_n/lungn2039.jpeg',
            'dest': 'histopathology_negative_3.jpeg',
            'diagnosis': 'negative',
            'class': 'lung_n'
        }
    },
    'mri': {
        'glioma_2': {
            'source': 'mri/Testing/glioma/Te-gl_219.jpg',
            'dest': 'mri_positive_2.jpg',
            'diagnosis': 'positive',
            'class': 'glioma'
        },
        'notumor_2': {
            'source': 'mri/Testing/notumor/Te-no_201.jpg',
            'dest': 'mri_negative_2.jpg',
            'diagnosis': 'negative',
            'class': 'notumor'
        },
        'glioma_3': {
            'source': 'mri/Testing/glioma/Te-gl_220.jpg',
            'dest': 'mri_positive_3.jpg',
            'diagnosis': 'positive',
            'class': 'glioma'
        },
        'notumor_3': {
            'source': 'mri/Testing/notumor/Te-no_202.jpg',
            'dest': 'mri_negative_3.jpg',
            'diagnosis': 'negative',
            'class': 'notumor'
        }
    },
    'ultrasound': {
        'malignant_2': {
            'source': 'ultrasound/Dataset_BUSI_with_GT/malignant/malignant (186)_mask.png',
            'dest': 'ultrasound_positive_2.png',
            'diagnosis': 'positive',
            'class': 'malignant'
        },
        'benign_2': {
            'source': 'ultrasound/Dataset_BUSI_with_GT/benign/benign (247)_mask.png',
            'dest': 'ultrasound_negative_2.png',
            'diagnosis': 'negative',
            'class': 'benign'
        },
        'malignant_3': {
            'source': 'ultrasound/Dataset_BUSI_with_GT/malignant/malignant (187)_mask.png',
            'dest': 'ultrasound_positive_3.png',
            'diagnosis': 'positive',
            'class': 'malignant'
        },
        'benign_3': {
            'source': 'ultrasound/Dataset_BUSI_with_GT/benign/benign (248)_mask.png',
            'dest': 'ultrasound_negative_3.png',
            'diagnosis': 'negative',
            'class': 'benign'
        }
    }
}

# Dataset metadata
DATASET_INFO = {
    'COVID-19 Radiography Database': {
        'url': 'https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database',
        'license': 'CC BY 4.0',
        'citation': 'M.E.H. Chowdhury et al. "Can AI help in screening Viral and COVID-19 pneumonia?" IEEE Access, 2020.'
    },
    'LC25000 - Lung and Colon Cancer': {
        'url': 'https://www.kaggle.com/datasets/andrewmvd/lung-and-colon-cancer-histopathological-images',
        'license': 'CC BY-NC-SA 4.0',
        'citation': 'Borkowski AA et al. "Lung and Colon Cancer Histopathological Image Dataset (LC25000)." arXiv:1912.12142v1, 2019.'
    },
    'Brain Tumor MRI Dataset': {
        'url': 'https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset',
        'license': 'Unknown',
        'citation': 'Brain Tumor MRI Dataset (Kaggle)'
    },
    'Breast Ultrasound Images': {
        'url': 'https://www.kaggle.com/datasets/aryashah2k/breast-ultrasound-images-dataset',
        'license': 'CC BY-NC-SA 4.0',
        'citation': 'Al-Dhabyani W et al. "Dataset of breast ultrasound images." Data in Brief, 2020.'
    }
}

DATASET_MAPPING = {
    'xray': 'COVID-19 Radiography Database',
    'histopathology': 'LC25000 - Lung and Colon Cancer',
    'mri': 'Brain Tumor MRI Dataset',
    'ultrasound': 'Breast Ultrasound Images'
}


def copy_images():
    """Copy additional images to selected folder."""
    kaggle_root = PROJECT_ROOT / 'benchmarks/clinical_images/kaggle_datasets'
    
    copied = []
    skipped = []
    
    for modality, images in NEW_IMAGES.items():
        for key, info in images.items():
            source_path = kaggle_root / info['source']
            dest_path = SELECTED_DIR / info['dest']
            
            if dest_path.exists():
                print(f"⏭️  Skip: {info['dest']} (already exists)")
                skipped.append(info['dest'])
                continue
            
            if not source_path.exists():
                print(f"❌ Source not found: {source_path}")
                continue
            
            shutil.copy2(source_path, dest_path)
            print(f"✅ Copied: {info['dest']}")
            copied.append({
                'filename': info['dest'],
                'modality': modality,
                'diagnosis': info['diagnosis'],
                'class': info['class'],
                'source_file': info['source'],
                'dataset': DATASET_MAPPING[modality],
                'dataset_url': DATASET_INFO[DATASET_MAPPING[modality]]['url'],
                'license': DATASET_INFO[DATASET_MAPPING[modality]]['license'],
                'citation': DATASET_INFO[DATASET_MAPPING[modality]]['citation']
            })
    
    return copied, skipped


def update_manifest(new_images):
    """Update manifest.json with new images."""
    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)
    
    # Add new images
    manifest['images'].extend(new_images)
    manifest['total_images'] = len(manifest['images'])
    manifest['updated'] = datetime.now().isoformat()
    
    # Update dataset counts
    for img in new_images:
        dataset_name = img['dataset']
        if dataset_name in manifest['datasets_used']:
            manifest['datasets_used'][dataset_name]['images_count'] += 1
    
    # Save updated manifest
    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n📝 Updated manifest.json")
    print(f"   Total images: {manifest['total_images']}")


def main():
    print("🖼️  Expanding Clinical Validation Image Set")
    print("=" * 70)
    print("Target: 3 positive + 3 negative per modality (24 total)")
    print("=" * 70)
    
    # Copy images
    copied, skipped = copy_images()
    
    print(f"\n{'=' * 70}")
    print(f"📊 Summary:")
    print(f"   Copied: {len(copied)} images")
    print(f"   Skipped: {len(skipped)} images")
    print(f"{'=' * 70}")
    
    # Update manifest
    if copied:
        update_manifest(copied)
        print("\n✅ Image expansion complete!")
    else:
        print("\n⚠️  No new images copied")


if __name__ == '__main__':
    main()
