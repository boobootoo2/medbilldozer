# Orchestration Workflow

The `OrchestratorAgent` coordinates the entire document analysis pipeline, managing extraction, analysis, and result aggregation.

## Core Responsibilities

1. **Document Classification**: Determine document type via regex patterns
2. **Extractor Selection**: Route to appropriate fact extractor (OpenAI/Gemini/local)
3. **Fact Extraction**: Extract structured data from unstructured text
4. **Line-Item Parsing**: Document-specific parsing (CPT codes, receipts, FSA claims)
5. **Provider Routing**: Select appropriate LLM analyzer
6. **Issue Detection**: Hybrid deterministic + LLM analysis
7. **Result Normalization**: Enforce schema invariants

## Orchestration Flow

```python
class OrchestratorAgent:
    def __init__(self, analyzer_override=None, extractor_override=None):
        """Initialize orchestrator with optional provider overrides."""
        self.analyzer_override = analyzer_override
        self.extractor_override = extractor_override
    
    def run(self, raw_text: str, progress_callback=None) -> Dict:
        """Execute 5-stage DAG pipeline."""
        
        # Stage 1: Pre-extraction
        classification = classify_document(raw_text)
        pre_facts = extract_pre_facts(raw_text)
        
        # Stage 2: Fact extraction
        extractor = self._select_extractor(classification)
        facts = self._extract_facts(raw_text, extractor)
        facts = normalize_facts(facts)
        
        # Stage 3: Line-item parsing (document-type specific)
        if classification["document_type"] in ["medical_bill", "dental_bill"]:
            line_items = extract_line_items_openai(raw_text, facts)
            facts["line_items"] = line_items
        elif classification["document_type"] == "fsa_receipt":
            fsa_items = extract_fsa_claims(raw_text)
            facts["fsa_claim_items"] = fsa_items
        
        # Stage 4: Analysis
        provider = ProviderRegistry.get(self.analyzer_override or "gpt-4o-mini")
        analysis = provider.analyze_document(raw_text, facts=facts)
        
        # Add deterministic issues
        deterministic_issues = deterministic_issues_from_facts(facts)
        analysis.issues = (analysis.issues or []) + deterministic_issues
        analysis.issues = normalize_issues(analysis.issues)
        
        # Stage 5: Complete
        return {
            "facts": facts,
            "analysis": analysis,
            "_orchestration": {...},
            "_workflow_log": {...}
        }
```

## Document Classification

Classification uses regex patterns to identify document types:

```python
def classify_document(text: str) -> Dict:
    """Classify document type via pattern matching."""
    
    patterns = {
        "medical_bill": r"\b(CPT|Current Procedural Terminology)\b",
        "dental_bill": r"\b(CDT|D\d{4})\b",
        "pharmacy_receipt": r"\b(Rx|NDC|Prescription)\b",
        "insurance_eob": r"\b(EOB|Explanation of Benefits|Claim)\b",
        "fsa_receipt": r"\b(FSA|HSA|Flex Spending)\b",
    }
    
    scores = {}
    for doc_type, pattern in patterns.items():
        matches = len(re.findall(pattern, text, re.IGNORECASE))
        scores[doc_type] = matches
    
    # Return highest scoring type
    best_type = max(scores, key=scores.get) if any(scores.values()) else "generic"
    
    return {
        "document_type": best_type,
        "confidence": scores.get(best_type, 0),
        "scores": scores
    }
```

## Extractor Selection

The orchestrator routes to the appropriate extractor:

```python
DOCUMENT_EXTRACTOR_MAP = {
    "medical_bill": "openai",
    "dental_bill": "openai",
    "pharmacy_receipt": "openai",
    "insurance_eob": "openai",
    "fsa_receipt": "openai",
    "generic": "openai",
}

def _select_extractor(self, classification: Dict) -> str:
    """Select extractor based on document type."""
    if self.extractor_override:
        return self.extractor_override
    
    return DOCUMENT_EXTRACTOR_MAP.get(
        classification["document_type"],
        "openai"  # fallback
    )
```

## Fact Extraction

Facts are extracted using LLM-based structured extraction:

```python
def _extract_facts(self, text: str, extractor: str) -> Dict:
    """Extract structured facts from raw text."""
    
    if extractor == "openai":
        return extract_facts_openai(text)
    elif extractor == "gemini":
        return extract_facts_gemini(text)
    elif extractor == "local":
        return extract_facts_local(text)  # Heuristic-based
    else:
        raise ValueError(f"Unknown extractor: {extractor}")
```

### Extracted Fact Schema

```python
{
  "provider_name": str,              # "Dr. Smith"
  "service_date": str,               # "2024-01-15"
  "total_charge": float,             # 1250.00
  "patient_name": str,               # "John Doe"
  "insurance_carrier": str,          # "Blue Cross"
  "cpt_codes": List[str],           # ["99213", "80053"]
  "line_items": List[Dict],         # Parsed line items
  "fsa_claim_items": List[Dict],    # FSA-specific
  "diagnosis_codes": List[str],     # ["Z00.00"]
  # ... additional fields
}
```

## Deterministic Issue Detection

Rule-based issues are generated from extracted facts:

```python
def deterministic_issues_from_facts(facts: Dict) -> List[Issue]:
    """Generate issues from deterministic rules."""
    
    issues = []
    
    # Rule: Missing diagnosis code
    if not facts.get("diagnosis_codes"):
        issues.append(Issue(
            category="missing_information",
            severity="medium",
            title="Missing Diagnosis Code",
            explanation="Bill lacks required diagnosis code...",
            max_savings=0.0,
            source="deterministic"
        ))
    
    # Rule: Unusually high charge
    line_items = facts.get("line_items", [])
    for item in line_items:
        if item.get("charge", 0) > 10000:
            issues.append(Issue(
                category="overcharge",
                severity="high",
                title="Unusually High Charge",
                explanation=f"Charge of ${item['charge']} exceeds typical range...",
                max_savings=item['charge'] * 0.3,
                source="deterministic"
            ))
    
    return issues
```

## Hybrid Analysis

The orchestrator combines deterministic and LLM-based issues:

```python
# LLM-detected issues
analysis = provider.analyze_document(raw_text, facts=facts)

# Deterministic issues
deterministic = deterministic_issues_from_facts(facts)

# Merge (deterministic issues appear first)
analysis.issues = (analysis.issues or []) + deterministic
```

## Savings Calculation

```python
def compute_deterministic_savings(facts: Dict) -> float:
    """Calculate savings from deterministic issues."""
    
    deterministic_issues = deterministic_issues_from_facts(facts)
    return sum(issue.max_savings or 0 for issue in deterministic_issues)

# In orchestrator
analysis.meta["deterministic_savings"] = compute_deterministic_savings(facts)
analysis.meta["llm_max_savings"] = sum(
    issue.max_savings or 0 
    for issue in analysis.issues 
    if issue.source != "deterministic"
)
analysis.meta["total_max_savings"] = sum(
    issue.max_savings or 0 
    for issue in analysis.issues
)
```

## Error Recovery

The orchestrator gracefully handles errors:

```python
try:
    facts = extract_facts_openai(text)
    workflow_log["extraction"]["extractor"] = "openai"
except Exception as e:
    # Log error but continue with empty facts
    workflow_log["extraction"]["extraction_error"] = str(e)
    facts = {}
```

## Configuration

Orchestrator behavior is configurable via overrides:

```python
# Use specific analyzer (e.g., for benchmarking)
agent = OrchestratorAgent(analyzer_override="gemini-2.0-flash")

# Use specific extractor (e.g., for offline mode)
agent = OrchestratorAgent(extractor_override="local")

# Both
agent = OrchestratorAgent(
    analyzer_override="gpt-4o",
    extractor_override="openai"
)
```

## Next Steps

- [DAG Pipeline Model](dag_pipeline.md)
- [Provider Abstraction](provider_abstraction.md)
- [Benchmark Engine](benchmark_engine.md)
