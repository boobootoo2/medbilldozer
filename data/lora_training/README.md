# MedGemma LoRA Fine-Tuning Dataset

This directory contains the prepared dataset for Phase 2 of the MedGemma enhancement roadmap.

## Dataset Overview

**Created:** 2026-02-14  
**Total Examples:** 24 (16 train, 8 val)  
**Format:** Instruction-following with clinical context  
**Purpose:** Fine-tune MedGemma for improved clinical error detection

## Files

```
lora_training/
├── README.md                # This file
├── train.jsonl              # Training data (16 examples)
├── train.json               # Training data (human-readable)
├── val.jsonl                # Validation data (8 examples)
├── val.json                 # Validation data (human-readable)
└── dataset_stats.json       # Dataset statistics
```

## Dataset Structure

Each example contains:
- **instruction**: System prompt for clinical error detection
- **input**: Patient info + clinical finding + prescribed treatment
- **output**: Expected determination (ERROR or CORRECT)
- **image_file**: Associated medical image filename
- **image_path**: Full path to image
- **metadata**: Scenario details (modality, error type, severity, etc.)

### Example

```json
{
  "id": "xray_004_covid_appropriate_treatment",
  "instruction": "You are a medical AI assistant trained to detect clinical errors...",
  "input": "**Patient Information:**\n- Age: 62\n- Gender: Male\n...",
  "output": "CORRECT - Treatment matches imaging findings",
  "image_file": "xray_positive.png",
  "metadata": {
    "modality": "xray",
    "error_type": "none",
    "severity": "none"
  }
}
```

## Dataset Statistics

### Coverage
- **X-ray**: 6 scenarios (3 ERROR, 3 CORRECT)
- **Histopathology**: 6 scenarios (3 ERROR, 3 CORRECT)
- **MRI**: 6 scenarios (3 ERROR, 3 CORRECT)
- **Ultrasound**: 6 scenarios (3 ERROR, 3 CORRECT)

### Error Types
- **No Error (CORRECT)**: 12 cases
- **Overtreatment (ERROR)**: 7 cases
- **Unnecessary Procedure (ERROR)**: 5 cases

### Severity Distribution
- **None**: 12 (correct treatments)
- **Moderate**: 3 (unnecessary but not harmful)
- **High**: 3 (potentially harmful)
- **Critical**: 6 (dangerous clinical errors)

## Training Strategy

### LoRA Configuration
- **Rank**: 16 (low-rank adaptation)
- **Alpha**: 32 (scaling factor)
- **Dropout**: 0.1 (regularization)
- **Target Modules**: q_proj, v_proj, o_proj (attention layers)

### Training Hyperparameters
- **Epochs**: 3-5
- **Batch Size**: 4 (with gradient accumulation)
- **Learning Rate**: 2e-4
- **Optimizer**: AdamW with warmup
- **Loss**: Causal Language Modeling

### Expected Performance
- **Baseline**: 79% accuracy (text heuristics only)
- **After Phase 1** (BioMedCLIP): 85% accuracy
- **After Phase 2** (LoRA): **90% accuracy** ← Target

## Usage

### 1. Prepare Dataset (Already Done!)
```bash
python3 scripts/prepare_lora_dataset.py
# Output: train.jsonl, val.jsonl, dataset_stats.json
```

### 2. Fine-Tune with LoRA
```bash
# Install dependencies
pip install transformers peft datasets pillow torch

# Train (3-5 epochs, 2-4 hours on M2 Max)
python3 scripts/finetune_medgemma_lora.py \
  --epochs 3 \
  --batch-size 4 \
  --lr 2e-4 \
  --lora-rank 16

# Output: models/medgemma-lora/
```

### 3. Test Fine-Tuned Model
```bash
# Run validation test
python3 scripts/test_finetuned_medgemma.py

# Expected: 90%+ accuracy (16/16 train, 7-8/8 val)
```

### 4. Integrate into Production
```bash
# Run full benchmark suite
python3 scripts/run_clinical_validation_benchmarks.py --model medgemma-lora

# Generate updated heatmaps
python3 scripts/generate_clinical_validation_heatmaps.py

# Should see green across all modalities!
```

## Data Augmentation (Future)

Current dataset is small (24 examples). Consider augmenting with:

### Paraphrasing
- Vary clinical finding descriptions
- Rephrase treatment prescriptions
- Add uncertainty language ("possible", "suggests", "concerning for")

### External Datasets
- **MIMIC-CXR**: 227k chest X-rays with radiology reports
- **PubMed Clinical Cases**: Extracted from case reports
- **Synthetic Cases**: GPT-4 generated with medical validation

### Target Size
- **Phase 2**: 100-500 examples (sufficient for LoRA)
- **Phase 3**: 1,000-5,000 examples (for robust RL training)

## Monitoring

Track these metrics during training:

### Loss Metrics
- **Train Loss**: Should decrease steadily
- **Validation Loss**: Should track train loss (no overfitting)
- **Perplexity**: Lower is better

### Performance Metrics
- **Accuracy**: Overall correctness (target: 90%)
- **True Positive Rate**: Detecting valid treatments (target: 95%)
- **True Negative Rate**: Detecting errors (target: 95%)
- **False Positive Rate**: Incorrect error flags (target: <5%)

### Modality Balance
- Ensure similar performance across all 4 modalities
- No modality should be <85% accuracy

## Troubleshooting

### Overfitting
**Symptoms**: Train accuracy >>90%, val accuracy <<80%  
**Solutions**:
- Increase dropout (0.1 → 0.2)
- Reduce epochs (5 → 3)
- Add more validation examples
- Implement data augmentation

### Underfitting
**Symptoms**: Train accuracy <80%, val accuracy <80%  
**Solutions**:
- Increase LoRA rank (16 → 32)
- More epochs (3 → 5)
- Higher learning rate (2e-4 → 5e-4)
- Check vision features are being used

### Catastrophic Forgetting
**Symptoms**: Model loses general medical knowledge  
**Solutions**:
- Lower learning rate (2e-4 → 1e-4)
- Use LoRA (already using)
- Add general medical QA examples to dataset

## Related Documentation

- **Enhancement Roadmap**: `docs/MEDGEMMA_VISION_ENHANCEMENT.md`
- **Phase 1 (BioMedCLIP)**: `scripts/integrate_biomedclip_vision.py`
- **Phase 3 (RL)**: `docs/MEDGEMMA_VISION_ENHANCEMENT.md#phase-3`

## Contact

Questions about the dataset or training process?
- Check: `docs/MEDGEMMA_VISION_ENHANCEMENT.md`
- Review: Dataset statistics in `dataset_stats.json`
- Test: Dry run with `--dry-run` flag
