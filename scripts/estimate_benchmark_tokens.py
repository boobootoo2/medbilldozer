#!/usr/bin/env python3
"""
Estimate token usage for MedGemma benchmark runs.
Uses tiktoken to calculate input/output token requirements.
"""

import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import tiktoken
except ImportError:
    print("Installing tiktoken...")
    os.system("pip install tiktoken")
    import tiktoken


def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    """Estimate tokens using tiktoken (close approximation for most models)."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base for unknown models
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def analyze_benchmark_inputs():
    """Analyze benchmark patient profiles to estimate token needs."""
    
    # Load a sample of benchmark inputs
    benchmark_dir = Path(__file__).parent.parent / "benchmarks" / "patient_profiles"
    
    if not benchmark_dir.exists():
        print(f"❌ Benchmark directory not found: {benchmark_dir}")
        return
    
    profile_files = list(benchmark_dir.glob("*.json"))
    
    if not profile_files:
        print("❌ No benchmark profile files found")
        return
    
    print(f"📊 Analyzing {len(profile_files)} patient profiles...\n")
    
    # System and task prompts (from medgemma_hosted_provider.py)
    SYSTEM_PROMPT = """
You are a medical billing analysis system.

You MUST return valid JSON only.
Do not include prose, explanations, or markdown outside JSON.

Be conservative and factual.
Only estimate savings when the document itself clearly supports it.
Never guess insurance outcomes.
Never exceed patient responsibility amounts shown on the document.
"""

    TASK_PROMPT = """
Analyze the following medical billing documents.

Identify administrative or billing issues.

For each issue, determine whether a MAX POTENTIAL PATIENT SAVINGS
can be calculated directly from the document.

Rules for estimating max_savings:

1. Duplicate charges
   - Same CPT code
   - Same date of service
   - Identical billed/allowed/patient responsibility
   → max_savings = patient responsibility for ONE duplicate line item

2. Math or reconciliation errors
   → max_savings = difference implied by the document

3. Preventive vs diagnostic or coding issues
   → Do NOT estimate savings unless the patient responsibility amount
     could clearly be eliminated

4. If savings cannot be confidently estimated
   → max_savings = null

Return STRICT JSON using this schema:

{
  "issues": [
    {
      "type": string,
      "summary": string,
      "evidence": string,
      "max_savings": number | null
    }
  ]
}

Document:
"""
    
    prompt_overhead = estimate_tokens(SYSTEM_PROMPT + TASK_PROMPT)
    print(f"🔤 Prompt overhead: {prompt_overhead} tokens\n")
    
    # Sample profiles to analyze
    sample_size = min(10, len(profile_files))
    input_tokens = []
    
    for profile_file in profile_files[:sample_size]:
        with open(profile_file) as f:
            profile = json.load(f)
        
        # Construct the full input as the orchestrator does
        docs = profile.get("documents", [])
        doc_texts = []
        for i, doc in enumerate(docs, 1):
            content = doc.get("content", "")
            doc_texts.append(f"Document {i}:\n{content}")
        
        full_input = "\n\n".join(doc_texts)
        
        # Add patient context (demographics + medical history)
        patient_info = f"Patient: {profile.get('name', 'Unknown')}\n"
        patient_info += f"Age: {profile.get('demographics', {}).get('age', 'Unknown')}, "
        patient_info += f"Sex: {profile.get('demographics', {}).get('sex', 'Unknown')}\n"
        
        med_history = profile.get('medical_history', {})
        conditions = med_history.get('conditions', [])
        if conditions:
            patient_info += f"Medical History: {', '.join(conditions)}\n"
        
        full_input = patient_info + "\n" + full_input
        
        input_size = estimate_tokens(full_input)
        input_tokens.append(input_size)
        
        print(f"  Profile {profile_file.stem}: {input_size} tokens")
    
    # Calculate statistics
    avg_input = sum(input_tokens) / len(input_tokens)
    max_input = max(input_tokens)
    min_input = min(input_tokens)
    
    print(f"\n📈 Input Token Statistics:")
    print(f"  Min:     {min_input} tokens")
    print(f"  Average: {avg_input:.0f} tokens")
    print(f"  Max:     {max_input} tokens")
    print(f"  Total:   {prompt_overhead + max_input} tokens (worst case)\n")
    
    # Estimate output tokens needed
    # Based on observed outputs: typically 2-5 issues per patient
    # Each issue has ~100-200 tokens
    typical_output_tokens = 5 * 200  # 5 issues × 200 tokens each
    max_output_tokens = 8 * 250  # Allow for verbose cases
    
    print(f"📤 Estimated Output Tokens:")
    print(f"  Typical: {typical_output_tokens} tokens (5 issues × 200 tokens)")
    print(f"  Maximum: {max_output_tokens} tokens (8 issues × 250 tokens)\n")
    
    # Recommendations
    print(f"💡 Recommendations:")
    print(f"  Current max_tokens: 600 ❌ TOO LOW")
    print(f"  Recommended max_tokens: {max_output_tokens} ✅")
    print(f"  Conservative max_tokens: {max_output_tokens + 500} (with buffer)\n")
    
    # Total context window check
    total_tokens = prompt_overhead + max_input + max_output_tokens
    print(f"📊 Total Token Usage (worst case):")
    print(f"  Input:  {prompt_overhead + max_input} tokens")
    print(f"  Output: {max_output_tokens} tokens")
    print(f"  Total:  {total_tokens} tokens")
    print(f"  Model context window: 131,072 tokens (MedGemma-4B-IT)")
    print(f"  Utilization: {total_tokens / 131072 * 100:.1f}%")


if __name__ == "__main__":
    analyze_benchmark_inputs()
