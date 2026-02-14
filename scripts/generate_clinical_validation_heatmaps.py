#!/usr/bin/env python3
"""
Generate heatmaps for clinical validation benchmark results.

Creates two heatmaps:
1. True Positive Detection Rate (correctly identifying valid treatments)
2. True Negative Detection Rate (correctly identifying inappropriate treatments)

Organized by model (rows) and modality (columns).
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_ROOT / 'benchmarks/clinical_validation_results'
OUTPUT_DIR = PROJECT_ROOT / 'benchmarks/clinical_validation_heatmaps'

# Models to analyze
MODELS = ['gpt-4o-mini', 'gpt-4o', 'medgemma', 'medgemma-ensemble']
MODALITIES = ['xray', 'histopathology', 'mri', 'ultrasound']


def load_latest_results():
    """Load the most recent results for each model."""
    results = {}
    
    for model in MODELS:
        # Find latest result file for this model
        model_files = sorted(RESULTS_DIR.glob(f'{model}_*.json'), reverse=True)
        if model_files:
            with open(model_files[0], 'r') as f:
                results[model] = json.load(f)
                print(f"✅ Loaded: {model_files[0].name}")
        else:
            print(f"⚠️  No results found for {model}")
    
    return results


def calculate_detection_rates(results):
    """
    Calculate true positive and true negative detection rates per model per modality.
    
    True Positive (TP): Expected CORRECT, Model said CORRECT
    True Negative (TN): Expected ERROR, Model said ERROR
    False Positive (FP): Expected ERROR, Model said CORRECT
    False Negative (FN): Expected CORRECT, Model said ERROR
    """
    tp_rates = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0}))
    tn_rates = defaultdict(lambda: defaultdict(lambda: {'correct': 0, 'total': 0}))
    
    for model, data in results.items():
        for scenario in data.get('scenario_results', []):
            modality = scenario['modality']
            expected = scenario['expected'].upper()
            is_correct = scenario.get('correct', False)
            
            # Determine if this is a positive or negative case
            is_positive_case = 'CORRECT' in expected  # Expected valid treatment
            is_negative_case = 'ERROR' in expected    # Expected inappropriate treatment
            
            if is_positive_case:
                # True Positive case - should say CORRECT
                tp_rates[model][modality]['total'] += 1
                if is_correct:
                    tp_rates[model][modality]['correct'] += 1
            
            elif is_negative_case:
                # True Negative case - should say ERROR
                tn_rates[model][modality]['total'] += 1
                if is_correct:
                    tn_rates[model][modality]['correct'] += 1
    
    return tp_rates, tn_rates


def rates_to_matrix(rates, models, modalities):
    """Convert rates dictionary to matrix for heatmap."""
    matrix = np.zeros((len(models), len(modalities)))
    
    for i, model in enumerate(models):
        for j, modality in enumerate(modalities):
            stats = rates[model][modality]
            if stats['total'] > 0:
                matrix[i, j] = (stats['correct'] / stats['total']) * 100
            else:
                matrix[i, j] = np.nan  # No data
    
    return matrix


def create_heatmap(matrix, models, modalities, title, filename):
    """Create and save a heatmap."""
    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create heatmap
    sns.heatmap(
        matrix,
        annot=True,
        fmt='.1f',
        cmap='RdYlGn',
        vmin=0,
        vmax=100,
        center=50,
        cbar_kws={'label': 'Detection Rate (%)'},
        xticklabels=[m.upper() for m in modalities],
        yticklabels=[m.upper() for m in models],
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )
    
    # Styling
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Modality', fontsize=12, fontweight='bold')
    ax.set_ylabel('Model', fontsize=12, fontweight='bold')
    
    # Rotate x-axis labels
    plt.xticks(rotation=0, ha='center')
    plt.yticks(rotation=0)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    output_path = OUTPUT_DIR / filename
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    
    # Also save as PNG
    png_path = OUTPUT_DIR / filename.replace('.pdf', '.png')
    plt.savefig(png_path, dpi=150, bbox_inches='tight')
    print(f"✅ Saved: {png_path}")
    
    plt.close()


def generate_summary_table(tp_rates, tn_rates, models):
    """Generate a text summary table."""
    summary_path = OUTPUT_DIR / 'detection_rates_summary.txt'
    
    with open(summary_path, 'w') as f:
        f.write("=" * 100 + "\n")
        f.write("CLINICAL VALIDATION DETECTION RATES SUMMARY\n")
        f.write("=" * 100 + "\n\n")
        
        for model in models:
            f.write(f"\n{'=' * 100}\n")
            f.write(f"Model: {model.upper()}\n")
            f.write(f"{'=' * 100}\n\n")
            
            # True Positive Rates
            f.write("TRUE POSITIVE DETECTION (Valid Treatment → Model says CORRECT)\n")
            f.write("-" * 100 + "\n")
            f.write(f"{'Modality':<20} {'Correct':<10} {'Total':<10} {'Rate':<10}\n")
            f.write("-" * 100 + "\n")
            
            for modality in MODALITIES:
                stats = tp_rates[model][modality]
                if stats['total'] > 0:
                    rate = (stats['correct'] / stats['total']) * 100
                    f.write(f"{modality.upper():<20} {stats['correct']:<10} {stats['total']:<10} {rate:.1f}%\n")
                else:
                    f.write(f"{modality.upper():<20} {'N/A':<10} {'N/A':<10} {'N/A':<10}\n")
            
            f.write("\n")
            
            # True Negative Rates
            f.write("TRUE NEGATIVE DETECTION (Inappropriate Treatment → Model says ERROR)\n")
            f.write("-" * 100 + "\n")
            f.write(f"{'Modality':<20} {'Correct':<10} {'Total':<10} {'Rate':<10}\n")
            f.write("-" * 100 + "\n")
            
            for modality in MODALITIES:
                stats = tn_rates[model][modality]
                if stats['total'] > 0:
                    rate = (stats['correct'] / stats['total']) * 100
                    f.write(f"{modality.upper():<20} {stats['correct']:<10} {stats['total']:<10} {rate:.1f}%\n")
                else:
                    f.write(f"{modality.upper():<20} {'N/A':<10} {'N/A':<10} {'N/A':<10}\n")
            
            f.write("\n")
    
    print(f"✅ Saved: {summary_path}")


def main():
    print("=" * 100)
    print("CLINICAL VALIDATION HEATMAP GENERATOR")
    print("=" * 100)
    print()
    
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    
    # Load results
    print("📂 Loading results...")
    results = load_latest_results()
    
    if not results:
        print("\n❌ No results found!")
        return
    
    print(f"\n✅ Loaded results for {len(results)} models\n")
    
    # Calculate detection rates
    print("📊 Calculating detection rates...")
    tp_rates, tn_rates = calculate_detection_rates(results)
    
    # Get list of models that have data
    available_models = [m for m in MODELS if m in results]
    
    # Convert to matrices
    print("🔢 Creating matrices...")
    tp_matrix = rates_to_matrix(tp_rates, available_models, MODALITIES)
    tn_matrix = rates_to_matrix(tn_rates, available_models, MODALITIES)
    
    # Create heatmaps
    print("\n🎨 Generating heatmaps...")
    create_heatmap(
        tp_matrix,
        available_models,
        MODALITIES,
        'True Positive Detection Rate\n(Correctly Identifying Valid Treatments)',
        'true_positive_detection_heatmap.pdf'
    )
    
    create_heatmap(
        tn_matrix,
        available_models,
        MODALITIES,
        'True Negative Detection Rate\n(Correctly Identifying Inappropriate Treatments)',
        'true_negative_detection_heatmap.pdf'
    )
    
    # Generate summary table
    print("\n📝 Generating summary table...")
    generate_summary_table(tp_rates, tn_rates, available_models)
    
    print("\n" + "=" * 100)
    print("✅ COMPLETE!")
    print("=" * 100)
    print(f"\nOutputs saved to: {OUTPUT_DIR}")
    print("\nFiles generated:")
    print("  - true_positive_detection_heatmap.pdf/png")
    print("  - true_negative_detection_heatmap.pdf/png")
    print("  - detection_rates_summary.txt")


if __name__ == '__main__':
    main()
