#!/usr/bin/env python3
"""
Test Fine-Tuned MedGemma LoRA Model

Quick evaluation script to test the fine-tuned model on validation examples.
"""

import json
import sys
import torch
from pathlib import Path
from typing import Dict, List
import argparse

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("\nInstall with:")
    print("  pip install transformers peft torch")
    sys.exit(1)


class FineTunedMedGemma:
    """Wrapper for inference with fine-tuned model."""
    
    def __init__(self, base_model: str, lora_weights: Path, device: str = "auto"):
        # Setup device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        else:
            self.device = device
        
        print(f"🖥️  Using device: {self.device}")
        
        # Load tokenizer
        print(f"📦 Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load base model
        print(f"🧠 Loading base model...")
        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map='auto' if self.device == "cuda" else None
        )
        
        # Load LoRA weights
        print(f"🔧 Loading LoRA weights from {lora_weights}...")
        self.model = PeftModel.from_pretrained(self.base_model, str(lora_weights))
        self.model.eval()
        
        print("✅ Model loaded successfully!")
    
    def generate(self, prompt: str, max_length: int = 512) -> str:
        """Generate response for a clinical prompt."""
        inputs = self.tokenizer(prompt, return_tensors='pt', truncation=True, max_length=max_length)
        
        if self.device != "cpu":
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the answer (after the prompt)
        if prompt in response:
            response = response[len(prompt):].strip()
        
        return response


def run_validation_test(model: FineTunedMedGemma, val_data_path: Path):
    """Test on validation examples."""
    print("\n" + "=" * 80)
    print("Running Validation Test")
    print("=" * 80)
    
    # Load validation data
    val_examples = []
    with open(val_data_path) as f:
        for line in f:
            val_examples.append(json.loads(line))
    
    print(f"\nTesting on {len(val_examples)} validation examples...\n")
    
    correct = 0
    total = len(val_examples)
    results = []
    
    for i, example in enumerate(val_examples, 1):
        # Build prompt
        prompt = f"{example['instruction']}\n\n{example['input']}\n"
        
        # Generate
        response = model.generate(prompt)
        
        # Check correctness
        expected = example['output']
        is_correct = False
        
        # Semantic matching (ERROR vs CORRECT)
        if 'ERROR' in expected.upper() and 'ERROR' in response.upper():
            is_correct = True
        elif 'CORRECT' in expected.upper() and 'CORRECT' in response.upper():
            is_correct = True
        
        if is_correct:
            correct += 1
            status = "✅"
        else:
            status = "❌"
        
        # Store result
        results.append({
            'id': example['id'],
            'modality': example['metadata']['modality'],
            'expected': expected,
            'predicted': response,
            'correct': is_correct
        })
        
        print(f"{status} [{i}/{total}] {example['id']}")
        print(f"   Expected: {expected[:60]}...")
        print(f"   Predicted: {response[:60]}...")
        print()
    
    # Summary
    accuracy = (correct / total) * 100
    
    print("=" * 80)
    print("Test Results")
    print("=" * 80)
    print(f"Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    
    # By modality
    by_modality = {}
    for result in results:
        modality = result['modality']
        if modality not in by_modality:
            by_modality[modality] = {'correct': 0, 'total': 0}
        by_modality[modality]['total'] += 1
        if result['correct']:
            by_modality[modality]['correct'] += 1
    
    print(f"\nBy Modality:")
    for modality, stats in by_modality.items():
        acc = (stats['correct'] / stats['total']) * 100
        print(f"  {modality}: {stats['correct']}/{stats['total']} ({acc:.1f}%)")
    
    return accuracy, results


def main():
    parser = argparse.ArgumentParser(description="Test fine-tuned MedGemma")
    parser.add_argument('--base-model', default='google/medgemma-2b', help='Base model name')
    parser.add_argument('--lora-weights', default='models/medgemma-lora', help='LoRA weights directory')
    parser.add_argument('--val-data', default='data/lora_training/val.jsonl', help='Validation data')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("Testing Fine-Tuned MedGemma")
    print("=" * 80)
    
    # Setup paths
    lora_weights = PROJECT_ROOT / args.lora_weights
    val_data_path = PROJECT_ROOT / args.val_data
    
    if not lora_weights.exists():
        print(f"❌ LoRA weights not found: {lora_weights}")
        print("\nTrain first:")
        print("  python3 scripts/finetune_medgemma_lora.py")
        return 1
    
    if not val_data_path.exists():
        print(f"❌ Validation data not found: {val_data_path}")
        print("\nPrepare dataset first:")
        print("  python3 scripts/prepare_lora_dataset.py")
        return 1
    
    # Load model
    model = FineTunedMedGemma(
        base_model=args.base_model,
        lora_weights=lora_weights
    )
    
    # Run validation
    accuracy, results = run_validation_test(model, val_data_path)
    
    # Save results
    results_path = PROJECT_ROOT / 'benchmarks/lora_validation_results.json'
    with open(results_path, 'w') as f:
        json.dump({
            'accuracy': accuracy,
            'results': results,
            'base_model': args.base_model,
            'lora_weights': str(lora_weights)
        }, f, indent=2)
    
    print(f"\n📊 Results saved to: {results_path}")
    
    if accuracy >= 90:
        print("\n🎉 Target accuracy achieved! (≥90%)")
    elif accuracy >= 85:
        print("\n✅ Good progress! (≥85%)")
    else:
        print(f"\n⚠️  Below target. Current: {accuracy:.1f}%, Target: 90%")
        print("Consider:")
        print("  - More training epochs")
        print("  - Larger LoRA rank")
        print("  - Data augmentation")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
