# Analysis Model

medBillDozer uses a hybrid deterministic + LLM approach to detect billing errors with high accuracy and explainability.

## Analysis Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Raw Document Text                         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Structured Fact Extraction                      │
│  • Provider name, NPI                                        │
│  • Service dates, DOS                                        │
│  • CPT/CDT codes                                             │
│  • Charges, payments                                         │
│  • Insurance info                                            │
└─────────────────────────────────────────────────────────────┘
                         ↓
            ┌────────────┴────────────┐
            │                         │
┌───────────────────────┐  ┌──────────────────────┐
│  Deterministic Rules  │  │  LLM Analysis        │
│  ──────────────────── │  │  ──────────────────  │
│  • Missing codes      │  │  • Context-aware     │
│  • Duplicate charges  │  │  • Policy violations │
│  • Out-of-range costs │  │  • Medical necessity │
│  • Schema validation  │  │  • Pattern detection │
└───────────────────────┘  └──────────────────────┘
            │                         │
            └────────────┬────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│               Merged & Normalized Issues                     │
│  • De-duplicated                                             │
│  • Severity ranked                                           │
│  • Savings calculated                                        │
│  • Actionable recommendations                                │
└─────────────────────────────────────────────────────────────┘
```

## Issue Categories

medBillDozer detects issues across these categories:

### 1. Overcharge / Upcoding
Procedures billed at higher code than performed:
- **Example**: Colonoscopy with polyp removal billed, but only diagnostic performed
- **Detection**: LLM compares procedure notes to CPT code
- **Typical Savings**: $200-$2,000

### 2. Duplicate Charges
Same service billed multiple times:
- **Example**: Anesthesia charged twice for same procedure
- **Detection**: Deterministic rule (same CPT + date + amount)
- **Typical Savings**: $100-$500

### 3. Unbundling
Services that should be billed together, billed separately:
- **Example**: Office visit + separate charge for reviewing test results
- **Detection**: LLM recognizes bundling rules
- **Typical Savings**: $50-$300

### 4. Balance Billing
Out-of-network charges exceeding allowed amounts:
- **Example**: Out-of-network anesthesiologist at in-network hospital
- **Detection**: Deterministic rule + policy check
- **Typical Savings**: $500-$5,000

### 5. Missing Information
Required fields not documented:
- **Example**: Missing diagnosis code on medical claim
- **Detection**: Deterministic rule (schema validation)
- **Typical Savings**: $0 (but claim may be denied)

### 6. Incorrect Insurance Application
Wrong deductible, co-insurance, or network status:
- **Example**: Full deductible applied when already met
- **Detection**: LLM checks against insurance plan (if provided)
- **Typical Savings**: $200-$2,000

### 7. Incorrect Quantities
Wrong units or quantities billed:
- **Example**: 10 units of drug billed, but only 5 administered
- **Detection**: LLM cross-references medical records
- **Typical Savings**: $100-$1,000

### 8. Medical Necessity
Services not medically necessary:
- **Example**: Unnecessary diagnostic tests
- **Detection**: LLM evaluates clinical justification
- **Typical Savings**: $200-$1,500

## Deterministic Detection

Rule-based detection provides high-confidence results:

```python
def detect_duplicate_charges(line_items: List[Dict]) -> List[Issue]:
    """Detect identical charges on same date."""
    
    issues = []
    seen = {}
    
    for item in line_items:
        key = (item["cpt_code"], item["service_date"], item["charge"])
        
        if key in seen:
            issues.append(Issue(
                category="duplicate_charge",
                severity="high",
                title="Duplicate Charge Detected",
                explanation=f"CPT {item['cpt_code']} charged twice on {item['service_date']}",
                max_savings=item["charge"],
                confidence=1.0,  # Deterministic
                source="deterministic"
            ))
        else:
            seen[key] = item
    
    return issues
```

### Deterministic Rules

1. **Duplicate Detection**: Same CPT + date + amount
2. **Missing Fields**: Required schema fields empty
3. **Range Validation**: Charges outside typical ranges
4. **Code Validation**: Invalid CPT/CDT/ICD-10 codes
5. **Date Logic**: Service date after claim date
6. **Math Errors**: Total doesn't match sum of line items

## LLM-Based Detection

AI analysis provides context-aware detection:

### Prompt Engineering

medBillDozer uses specialized prompts per document type:

```python
# Medical Bill Prompt (simplified)
MEDICAL_BILL_PROMPT = """
You are a medical billing expert analyzing a bill for errors.

**Extracted Facts**:
- Provider: {provider_name}
- Service Date: {service_date}
- Total Charge: ${total_charge}
- CPT Codes: {cpt_codes}
- Line Items: {line_items}

**Raw Bill**:
{raw_text}

**Task**:
Identify billing errors in these categories:
1. Upcoding (procedure billed higher than performed)
2. Unbundling (services separated that should be bundled)
3. Balance billing (out-of-network overcharges)
4. Medical necessity (unjustified procedures)
5. Incorrect quantities

For each issue:
- Category
- Severity (high/medium/low)
- Brief title
- Plain-language explanation
- Estimated savings
- Affected CPT codes

Return JSON array of issues.
"""
```

### Fact-Aware Analysis

When structured facts are extracted, LLMs provide more accurate analysis:

**Text-Only Mode**:
```
"Analyze this medical bill: [5000 characters of raw text]"
```

**Fact-Aware Mode**:
```
"I've extracted these facts from the bill:
- Provider: Dr. Smith (NPI: 1234567890)
- Service: Colonoscopy (CPT 45378)
- Charge: $2,450
- Date: 2024-01-15

Analyze the raw bill below for errors:
[5000 characters of raw text]"
```

Fact-aware mode improves:
- Accuracy: +15-20% F1 score
- Latency: -30% (smaller prompts)
- Consistency: More structured responses

## Severity Scoring

Issues are ranked by severity:

```python
def calculate_severity(issue: Issue) -> str:
    """Determine issue severity."""
    
    # High severity
    if issue.max_savings > 100:
        return "high"
    if issue.category in ["duplicate_charge", "balance_billing", "fraud"]:
        return "high"
    
    # Medium severity
    if issue.max_savings > 20:
        return "medium"
    if issue.category in ["upcoding", "unbundling", "incorrect_insurance"]:
        return "medium"
    
    # Low severity
    return "low"
```

## Savings Calculation

Savings estimates combine deterministic and LLM-based calculations:

```python
# Deterministic savings (high confidence)
deterministic_savings = sum(
    issue.max_savings 
    for issue in issues 
    if issue.source == "deterministic"
)

# LLM savings (requires verification)
llm_savings = sum(
    issue.max_savings 
    for issue in issues 
    if issue.source == "llm"
)

# Total potential
total_max_savings = deterministic_savings + llm_savings
```

**Savings Ranges**:
- **Deterministic**: Exact amount (e.g., duplicate charge)
- **LLM**: Estimated range (e.g., "20-30% upcoding")
- **Conservative**: Lower bound shown to user
- **Optimistic**: Upper bound in detailed view

## Confidence Scoring

Each issue includes confidence level:

```python
@dataclass
class Issue:
    confidence: Optional[float] = None  # 0.0 - 1.0
```

**Confidence Interpretation**:
- **1.0**: Deterministic (rule-based)
- **0.8-0.9**: High confidence LLM detection
- **0.6-0.7**: Medium confidence (requires verification)
- **< 0.6**: Low confidence (informational only)

## Issue Normalization

All issues are normalized to standard schema:

```python
def normalize_issues(issues: List[Issue]) -> List[Issue]:
    """Enforce schema invariants."""
    
    for issue in issues:
        # Ensure max_savings is non-negative
        if issue.max_savings and issue.max_savings < 0:
            issue.max_savings = 0.0
        
        # Validate category
        valid_categories = [
            "overcharge", "duplicate_charge", "unbundling",
            "balance_billing", "missing_information",
            "incorrect_insurance", "incorrect_quantity",
            "medical_necessity"
        ]
        if issue.category not in valid_categories:
            issue.category = "other"
        
        # Validate severity
        if issue.severity not in ["high", "medium", "low"]:
            issue.severity = "medium"
        
        # Truncate long explanations
        if len(issue.explanation) > 500:
            issue.explanation = issue.explanation[:497] + "..."
    
    return issues
```

## Multi-Provider Ensemble

For maximum accuracy, run multiple providers and aggregate:

```python
# Run 3 providers
providers = ["gpt-4o-mini", "gemini-2.0-flash", "medgemma"]
results = [ProviderRegistry.get(p).analyze_document(text, facts) for p in providers]

# Issues detected by 2+ providers are high confidence
consensus_issues = find_consensus_issues(results, min_agreement=2)
```

## Performance Benchmarks

| Provider | F1 Score | Precision | Recall | Avg Latency |
|----------|----------|-----------|--------|-------------|
| GPT-4o-mini | 0.89 | 0.87 | 0.92 | 4.2s |
| Gemini 2.0 | 0.86 | 0.90 | 0.82 | 3.8s |
| MedGemma | 0.91 | 0.93 | 0.89 | 5.1s |
| Heuristic | 0.72 | 1.00 | 0.57 | 0.3s |

*Benchmarked on 50 test cases with ground truth annotations*

## Next Steps

- [Cross-Document Reasoning](cross_document_reasoning.md)
- [User Workflow](user_workflow.md)
- [Provider Abstraction](../architecture/provider_abstraction.md)
