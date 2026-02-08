# Provider Abstraction Layer

medBillDozer uses a pluggable provider architecture that enables swapping LLM backends without changing core logic.

## Design Goals

1. **Vendor Independence**: No lock-in to specific LLM provider
2. **Fact-Aware Analysis**: Providers receive both raw text and extracted facts
3. **Graceful Degradation**: System continues if provider unavailable
4. **Benchmark Comparison**: Test multiple providers against same dataset

## Provider Interface

All providers implement the `LLMAnalysisProvider` interface:

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict

class LLMAnalysisProvider(ABC):
    """Abstract base class for LLM analysis providers."""
    
    @abstractmethod
    def analyze_document(
        self, 
        raw_text: str, 
        facts: Optional[Dict] = None
    ) -> AnalysisResult:
        """Analyze document and return structured issues.
        
        Args:
            raw_text: Raw document text
            facts: Optional extracted facts (provider may use or ignore)
            
        Returns:
            AnalysisResult with issues list and metadata
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Return human-readable model identifier."""
        pass
```

## AnalysisResult Schema

```python
@dataclass
class AnalysisResult:
    """Structured analysis result."""
    
    issues: List[Issue]              # Detected billing issues
    meta: Dict[str, Any]             # Metadata (model, latency, etc.)
    raw_response: Optional[str]      # Original LLM response


@dataclass
class Issue:
    """Individual billing issue."""
    
    category: str                    # "overcharge" | "duplicate" | "missing_info"
    severity: str                    # "high" | "medium" | "low"
    title: str                       # Brief summary
    explanation: str                 # Plain-language explanation
    max_savings: Optional[float]     # Potential dollar savings
    source: str = "llm"             # "llm" | "deterministic"
    confidence: Optional[float] = None
    affected_line_items: List[str] = field(default_factory=list)
```

## Provider Registry

The `ProviderRegistry` manages provider instances:

```python
class ProviderRegistry:
    """Central registry for LLM providers."""
    
    _providers: Dict[str, LLMAnalysisProvider] = {}
    
    @classmethod
    def register(cls, key: str, provider: LLMAnalysisProvider):
        """Register a provider with a unique key."""
        cls._providers[key] = provider
    
    @classmethod
    def get(cls, key: str) -> Optional[LLMAnalysisProvider]:
        """Retrieve provider by key."""
        return cls._providers.get(key)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        """List all registered provider keys."""
        return list(cls._providers.keys())
```

## Implemented Providers

### 1. OpenAI Provider

```python
class OpenAIAnalysisProvider(LLMAnalysisProvider):
    """OpenAI GPT-4 based analysis."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def analyze_document(self, raw_text: str, facts: Optional[Dict] = None) -> AnalysisResult:
        """Fact-aware analysis using GPT-4."""
        
        # Build prompt with facts if available
        if facts:
            prompt = build_fact_aware_prompt(raw_text, facts)
        else:
            prompt = build_text_only_prompt(raw_text)
        
        # Call OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": MEDICAL_BILLING_EXPERT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0  # Deterministic
        )
        
        # Parse structured response
        issues = parse_issues_from_response(response.choices[0].message.content)
        
        return AnalysisResult(
            issues=issues,
            meta={"model": self.model, "provider": "openai"},
            raw_response=response.choices[0].message.content
        )
    
    def get_model_name(self) -> str:
        return f"OpenAI {self.model}"
```

### 2. Gemini Provider

```python
class GeminiAnalysisProvider(LLMAnalysisProvider):
    """Google Gemini based analysis."""
    
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.client = genai.GenerativeModel(model)
    
    def analyze_document(self, raw_text: str, facts: Optional[Dict] = None) -> AnalysisResult:
        """Fact-aware analysis using Gemini."""
        
        if facts:
            prompt = build_fact_aware_prompt(raw_text, facts)
        else:
            prompt = build_text_only_prompt(raw_text)
        
        response = self.client.generate_content(
            prompt,
            generation_config={"temperature": 0.0}
        )
        
        issues = parse_issues_from_response(response.text)
        
        return AnalysisResult(
            issues=issues,
            meta={"model": self.model, "provider": "gemini"},
            raw_response=response.text
        )
    
    def get_model_name(self) -> str:
        return f"Google {self.model}"
```

### 3. MedGemma Provider

```python
class MedGemmaHostedProvider(LLMAnalysisProvider):
    """Healthcare-aligned MedGemma model (hosted)."""
    
    def __init__(self):
        self.endpoint = os.getenv("MEDGEMMA_ENDPOINT")
        self.api_key = os.getenv("MEDGEMMA_API_KEY")
    
    def analyze_document(self, raw_text: str, facts: Optional[Dict] = None) -> AnalysisResult:
        """Analysis using healthcare-aligned foundation model."""
        
        # MedGemma has domain-specific prompting
        prompt = build_medgemma_prompt(raw_text, facts)
        
        response = requests.post(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"prompt": prompt, "temperature": 0.0}
        )
        
        issues = parse_issues_from_response(response.json()["output"])
        
        return AnalysisResult(
            issues=issues,
            meta={"model": "medgemma-2b", "provider": "medgemma"},
            raw_response=response.json()["output"]
        )
    
    def get_model_name(self) -> str:
        return "MedGemma 2B (Healthcare-Aligned)"
```

### 4. Heuristic Provider (Local)

```python
class HeuristicAnalysisProvider(LLMAnalysisProvider):
    """Rule-based analysis (no LLM required)."""
    
    def analyze_document(self, raw_text: str, facts: Optional[Dict] = None) -> AnalysisResult:
        """Deterministic analysis using heuristics only."""
        
        if not facts:
            facts = extract_facts_local(raw_text)  # Regex-based
        
        issues = deterministic_issues_from_facts(facts)
        
        return AnalysisResult(
            issues=issues,
            meta={"model": "heuristic", "provider": "local"},
            raw_response=None
        )
    
    def get_model_name(self) -> str:
        return "Local Heuristic (No LLM)"
```

## Provider Registration

Providers are registered at application startup:

```python
# In src/medbilldozer/providers/__init__.py

from .openai_analysis_provider import OpenAIAnalysisProvider
from .gemini_analysis_provider import GeminiAnalysisProvider
from .medgemma_hosted_provider import MedGemmaHostedProvider
from .provider_registry import ProviderRegistry

# Register all providers
ProviderRegistry.register("gpt-4o-mini", OpenAIAnalysisProvider("gpt-4o-mini"))
ProviderRegistry.register("gpt-4o", OpenAIAnalysisProvider("gpt-4o"))
ProviderRegistry.register("gemini-2.0-flash", GeminiAnalysisProvider("gemini-2.0-flash"))
ProviderRegistry.register("gemini-1.5-pro", GeminiAnalysisProvider("gemini-1.5-pro"))
ProviderRegistry.register("medgemma", MedGemmaHostedProvider())
ProviderRegistry.register("heuristic", HeuristicAnalysisProvider())
```

## Usage in Orchestrator

```python
# Get provider from registry
analyzer_key = "gpt-4o-mini"  # or from config/user choice
provider = ProviderRegistry.get(analyzer_key)

if not provider:
    # Fallback to default
    provider = ProviderRegistry.get("gpt-4o-mini")

# Fact-aware analysis (preferred)
try:
    analysis = provider.analyze_document(raw_text, facts=facts)
    mode = "facts+text"
except TypeError:
    # Provider doesn't support facts parameter
    analysis = provider.analyze_document(raw_text)
    mode = "text_only"
```

## Fact-Aware Prompting

When facts are available, providers build richer prompts:

```python
def build_fact_aware_prompt(raw_text: str, facts: Dict) -> str:
    """Build prompt that includes extracted facts."""
    
    return f"""
You are analyzing a medical bill. I've already extracted key facts:

**Provider**: {facts.get('provider_name', 'Unknown')}
**Service Date**: {facts.get('service_date', 'Unknown')}
**Total Charge**: ${facts.get('total_charge', 0):.2f}
**CPT Codes**: {', '.join(facts.get('cpt_codes', []))}
**Line Items**: {len(facts.get('line_items', []))} items

**Raw Document**:
{raw_text}

Analyze for billing errors, overcharges, and policy violations.
Return structured JSON with issues list.
"""
```

## Benchmark Comparison

The provider abstraction enables head-to-head comparison:

```python
# Test all providers on same document
providers_to_test = ["gpt-4o-mini", "gemini-2.0-flash", "medgemma", "heuristic"]

results = {}
for provider_key in providers_to_test:
    provider = ProviderRegistry.get(provider_key)
    analysis = provider.analyze_document(raw_text, facts=facts)
    results[provider_key] = analysis

# Compare issue detection rates, savings estimates, latency
compare_provider_performance(results, ground_truth)
```

## Next Steps

- [Benchmark Engine](benchmark_engine.md)
- [Orchestration Workflow](orchestration.md)
- [Testing Guide](../development/testing.md)
