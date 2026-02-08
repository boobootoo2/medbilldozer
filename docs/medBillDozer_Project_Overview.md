# medBillDozer: AI-Powered Medical Bill Error Detection

## Project Name

**medBillDozer**\
Empowering patients to bulldoze through medical billing errors with
healthcare-aligned AI.

------------------------------------------------------------------------

## Team medBillDozer

### John Shultz

**Founder \| Application Architect \| Healthcare AI Systems Engineer**

John Shultz brings together experience in life sciences, enterprise
financial systems, and AI architecture to address one of the most
financially destructive problems in American healthcare: medical billing
errors.

With a background spanning regulated environments at JPMorgan Chase and
Bank of America, John has worked inside large-scale financial systems
where risk management, auditability, security, and compliance are
non-negotiable. That experience directly informs the architecture of
medBillDozer.

Healthcare billing is fundamentally a fragmented financial risk system.
medBillDozer applies financial-grade detection principles to healthcare
AI through disciplined, privacy-first engineering.

------------------------------------------------------------------------

# Problem Statement

## The Medical Billing Crisis

-   49--80% of medical bills contain at least one error\
-   \$1,300 average error on hospital bills over \$10,000\
-   \$68B lost annually due to billing mistakes\
-   \~550,000 bankruptcies per year tied to medical issues\
-   66.5% of bankruptcy filers cite medical issues

These numbers represent families choosing between treatment and
financial survival.

------------------------------------------------------------------------

## The Gap

Current solutions fail patients because:

1.  Manual audit tools require expert knowledge\
2.  Generic AI lacks medical domain reasoning\
3.  Centralized platforms create privacy risks

**The need:** A privacy-focused AI assistant that understands medical
billing language and plain English.

------------------------------------------------------------------------

# Overall Solution: Effective Use of HAI-DEF Models

## Why MedGemma Is Critical

MedGemma (google/medgemma-4b-it) provides:

-   Medical-domain expertise\
-   CPT/CDT/NDC code understanding\
-   Clinical reasoning (age/gender inconsistencies)\
-   Conservative, evidence-based outputs\
-   Edge deployment capability

------------------------------------------------------------------------

# Ensemble Architecture

``` python
class MedGemmaEnsembleProvider(LLMProvider):
    """Calls MedGemma, then applies canonicalization and heuristics."""

    def __init__(self):
        self.medgemma = MedGemmaHostedProvider()
        self.enable_openai = os.getenv("ENABLE_ENSEMBLE_OPENAI", "false")

    def analyze_document(self, raw_text: str, facts: Dict) -> AnalysisResult:
        result = self.medgemma.analyze_document(raw_text, facts)

        canonical_issues = self._canonicalize_type(result.issues)

        if self.enable_openai:
            canonical_issues = self._call_openai_canonicalizer(canonical_issues)

        heuristic_issues = self._run_deterministic_heuristics(raw_text)

        return AnalysisResult(
            issues=canonical_issues + heuristic_issues
        )
```

### Why This Works

-   MedGemma captures subtle clinical reasoning errors\
-   Deterministic rules provide high-confidence safeguards\
-   Canonicalization ensures taxonomy consistency\
-   Ensemble logic improves recall while preserving precision

------------------------------------------------------------------------

# Performance Snapshot

  Model                    Precision   Recall   F1       Savings Capture
  ------------------------ ----------- -------- -------- -----------------
  medgemma-ensemble-v1.0   43.06%      62.16%   45.84%   59.21%
  OpenAI GPT-4             46.04%      42.40%   42.43%   51.27%
  MedGemma-4B-IT           47.54%      31.01%   36.01%   41.22%

High recall is critical --- missed billing errors cost real money.

------------------------------------------------------------------------

# Deployment Strategy

## Current

-   Streamlit cloud deployment\
-   Session-only storage\
-   Aggregated monitoring

## Future

-   Quantized MedGemma GGUF\
-   On-device inference (MLX / llama.cpp)\
-   100% offline processing\
-   HIPAA-aligned architecture

------------------------------------------------------------------------

# Competitive Advantage

-   Healthcare-aligned foundation model\
-   Ensemble precision + recall balance\
-   Privacy-first design\
-   Open-source extensibility

------------------------------------------------------------------------

# Call to Action

For Patients: Take control of your medical bills.\
For Developers: Contribute and expand the ecosystem.\
For Healthcare Systems: Improve billing accuracy and trust.

**Let's bulldoze medical billing errors --- one family at a time.**
