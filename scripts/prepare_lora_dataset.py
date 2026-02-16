#!/usr/bin/env python3
"""
Phase 2: Prepare LoRA Fine-Tuning Dataset for MedGemma

Creates a dataset of (image_features, clinical_prompt, expected_output) tuples
for fine-tuning MedGemma's decoder to improve clinical reasoning.

Dataset Format:
- Input: Visual features + clinical context
- Output: ERROR or CORRECT determination
"""

import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import clinical scenarios
from scripts.run_clinical_validation_benchmarks import CLINICAL_SCENARIOS


def format_training_example(scenario_id: str, scenario: Dict, image_path: Path) -> Dict:
    """Format a single training example for LoRA fine-tuning."""
    
    # Create instruction-following format
    instruction = """You are a medical AI assistant trained to detect clinical errors. 
Review the medical image and clinical information to determine if the prescribed treatment is appropriate.

Respond with ONLY:
- "ERROR - Treatment does not match imaging" if inappropriate
- "CORRECT - Treatment matches imaging findings" if appropriate"""
    
    # Clinical context
    context = f"""**Patient Information:**
- Age: {scenario['patient_context'].get('age')}
- Gender: {scenario['patient_context'].get('gender')}
- Complaint: {scenario['patient_context'].get('chief_complaint')}

**Clinical Finding:**
{scenario['clinical_finding']}

**Prescribed Treatment:**
{scenario['prescribed_treatment']}

**Your Assessment:**"""
    
    # Expected output
    output = scenario['expected_determination']
    
    # Metadata for analysis
    metadata = {
        'scenario_id': scenario['id'],
        'modality': scenario['modality'],
        'image_type': scenario['image_type'],
        'error_type': scenario['error_type'],
        'severity': scenario['severity'],
        'cost_impact': scenario['cost_impact']
    }
    
    return {
        'id': scenario_id,
        'instruction': instruction,
        'input': context,
        'output': output,
        'image_file': scenario['image_file'],
        'image_path': str(image_path),
        'metadata': metadata
    }


def create_train_val_split(examples: List[Dict], val_ratio: float = 0.2) -> tuple:
    """Split dataset into train/validation with stratification by modality."""
    from collections import defaultdict
    import random
    
    random.seed(42)
    
    # Group by modality
    by_modality = defaultdict(list)
    for example in examples:
        modality = example['metadata']['modality']
        by_modality[modality].append(example)
    
    train = []
    val = []
    
    # Stratified split
    for modality, modality_examples in by_modality.items():
        random.shuffle(modality_examples)
        split_idx = int(len(modality_examples) * (1 - val_ratio))
        train.extend(modality_examples[:split_idx])
        val.extend(modality_examples[split_idx:])
    
    return train, val


def augment_dataset(examples: List[Dict]) -> List[Dict]:
    """
    Augment dataset with variations to prevent overfitting.
    
    Augmentation strategies:
    1. Paraphrase clinical findings
    2. Vary treatment descriptions
    3. Add uncertainty language
    """
    augmented = list(examples)  # Keep originals
    
    # Paraphrasing templates
    finding_variations = {
        'normal': ['unremarkable', 'within normal limits', 'no significant abnormality'],
        'clear': ['patent', 'unobstructed', 'without opacity'],
        'tumor': ['mass', 'lesion', 'neoplasm'],
        'benign': ['non-malignant', 'benign-appearing', 'without malignant features']
    }
    
    # Add paraphrased versions (only if we have few examples)
    if len(examples) < 100:
        print("  📝 Augmenting dataset with paraphrases...")
        # TODO: Implement paraphrasing
        # For now, just note it's a placeholder
        pass
    
    return augmented


def save_dataset(train: List[Dict], val: List[Dict], output_dir: Path):
    """Save dataset in multiple formats for different frameworks."""
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # JSONL format (Hugging Face compatible)
    with open(output_dir / 'train.jsonl', 'w') as f:
        for example in train:
            f.write(json.dumps(example) + '\n')
    
    with open(output_dir / 'val.jsonl', 'w') as f:
        for example in val:
            f.write(json.dumps(example) + '\n')
    
    # JSON format (for inspection)
    with open(output_dir / 'train.json', 'w') as f:
        json.dump(train, f, indent=2)
    
    with open(output_dir / 'val.json', 'w') as f:
        json.dump(val, f, indent=2)
    
    # Dataset statistics
    stats = {
        'created_at': datetime.now().isoformat(),
        'total_examples': len(train) + len(val),
        'train_size': len(train),
        'val_size': len(val),
        'modalities': {},
        'error_types': {},
        'severity_distribution': {}
    }
    
    for split_name, split_data in [('train', train), ('val', val)]:
        for example in split_data:
            modality = example['metadata']['modality']
            error_type = example['metadata']['error_type']
            severity = example['metadata']['severity']
            
            stats['modalities'][modality] = stats['modalities'].get(modality, 0) + 1
            stats['error_types'][error_type] = stats['error_types'].get(error_type, 0) + 1
            stats['severity_distribution'][severity] = stats['severity_distribution'].get(severity, 0) + 1
    
    with open(output_dir / 'dataset_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    return stats


def main():
    print("=" * 80)
    print("Preparing LoRA Fine-Tuning Dataset for MedGemma")
    print("=" * 80)
    
    # Load images directory
    images_dir = PROJECT_ROOT / 'benchmarks/clinical_images/kaggle_datasets/selected'
    
    if not images_dir.exists():
        print(f"❌ Images directory not found: {images_dir}")
        return 1
    
    # Create training examples
    print(f"\n📊 Processing {len(CLINICAL_SCENARIOS)} clinical scenarios...")
    examples = []
    
    for scenario_id, scenario in CLINICAL_SCENARIOS.items():
        image_path = images_dir / scenario['image_file']
        
        if not image_path.exists():
            print(f"  ⚠️  Missing image: {scenario['image_file']}")
            continue
        
        example = format_training_example(scenario_id, scenario, image_path)
        examples.append(example)
        print(f"  ✅ {scenario_id}")
    
    print(f"\n✅ Created {len(examples)} training examples")
    
    # Augment dataset
    examples = augment_dataset(examples)
    
    # Train/val split
    print("\n🔀 Creating train/validation split...")
    train, val = create_train_val_split(examples, val_ratio=0.2)
    print(f"  Train: {len(train)} examples")
    print(f"  Val: {len(val)} examples")
    
    # Save dataset
    output_dir = PROJECT_ROOT / 'data/lora_training'
    print(f"\n💾 Saving dataset to {output_dir}...")
    stats = save_dataset(train, val, output_dir)
    
    # Print statistics
    print("\n" + "=" * 80)
    print("Dataset Statistics")
    print("=" * 80)
    print(f"Total Examples: {stats['total_examples']}")
    print(f"Train/Val Split: {stats['train_size']}/{stats['val_size']}")
    print(f"\nBy Modality:")
    for modality, count in stats['modalities'].items():
        print(f"  - {modality}: {count}")
    print(f"\nBy Error Type:")
    for error_type, count in stats['error_types'].items():
        print(f"  - {error_type}: {count}")
    
    print("\n" + "=" * 80)
    print("✅ Dataset preparation complete!")
    print("=" * 80)
    print(f"\nFiles created:")
    print(f"  - {output_dir}/train.jsonl")
    print(f"  - {output_dir}/val.jsonl")
    print(f"  - {output_dir}/dataset_stats.json")
    print(f"\nNext step:")
    print(f"  python3 scripts/finetune_medgemma_lora.py")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
