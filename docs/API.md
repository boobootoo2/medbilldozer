## API Reference

Public interfaces and their usage patterns.

### Provider Interface

#### `LLMProvider`

**Inherits from:** `ABC`

All analysis providers MUST implement the same interface.

Contract:
    analyze_document(raw_text: str, facts: Optional[Dict]) -> AnalysisResult

**Methods:**

- **`name(self) -> str`**
  - Return a short provider name.

- **`analyze_document(self, raw_text, facts) -> AnalysisResult`**
  - Analyze a document and return structured issues.

- **`health_check(self) -> bool`**

#### `ProviderRegistry`

**Attributes:**
- `_providers`

**Methods:**

- **`register(cls, key, provider) -> None`**

- **`get(cls, key) -> Optional[LLMProvider]`**

- **`list(cls) -> List[str]`**

#### `LocalHeuristicProvider`

**Inherits from:** `LLMProvider`

**Methods:**

- **`name(self) -> str`**

- **`analyze_document(self, raw_text, facts) -> AnalysisResult`**
