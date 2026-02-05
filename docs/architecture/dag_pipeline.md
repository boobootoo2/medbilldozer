# DAG Pipeline Execution Model

medBillDozer uses a directed acyclic graph (DAG) execution model for document analysis, ensuring deterministic, traceable, and idempotent workflows.

## Pipeline Stages

```
┌────────────────────────────────────────────────────────────┐
│  1️⃣ PRE-EXTRACTION                                         │
│  ─────────────────────────────────────────────────────────│
│  • Classify document type (regex-based)                   │
│  • Extract pre-facts (CPT presence, line count, length)   │
│  • Select extractor (OpenAI/Gemini/local)                 │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│  2️⃣ EXTRACTION                                             │
│  ─────────────────────────────────────────────────────────│
│  • Invoke chosen extractor                                 │
│  • Extract structured facts (dates, amounts, codes)       │
│  • Normalize fact schema                                  │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│  3️⃣ PHASE-2 PARSING (Document-Type Specific)              │
│  ─────────────────────────────────────────────────────────│
│  • Medical/Dental: Extract line items with CPT/CDT codes │
│  • Receipt: Parse itemized receipt lines                 │
│  • FSA: Extract claim item details                       │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│  4️⃣ ANALYSIS                                               │
│  ─────────────────────────────────────────────────────────│
│  • Invoke analyzer provider (fact-aware if supported)     │
│  • Generate LLM-detected issues                           │
│  • Add deterministic issues (rule-based)                  │
│  • Normalize issue schema                                │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│  5️⃣ COMPLETE                                               │
│  ─────────────────────────────────────────────────────────│
│  • Enhance document identity                              │
│  • Normalize transactions                                 │
│  • Build coverage matrix (if multiple docs)               │
│  • Persist workflow log                                   │
└────────────────────────────────────────────────────────────┘
```

## Workflow Log Structure

Each pipeline execution generates an immutable workflow log:

```python
{
  "workflow_id": "uuid",                    # Unique execution identifier
  "timestamp": "ISO 8601",                  # UTC timestamp
  "pre_extraction": {
    "classification": {...},                # Document type & confidence
    "facts": {...}                          # Pre-extraction metrics
  },
  "extraction": {
    "extractor": "openai|gemini|local",     # Chosen extractor
    "facts": {...},                         # Extracted structured data
    "line_item_count": int,                 # Phase-2 parsing results
    "fsa_item_count": int                   # FSA-specific count
  },
  "analysis": {
    "analyzer": "gpt-4o-mini|gemini-2.0-flash|...",
    "mode": "facts+text|text_only",         # Analysis mode
    "result": {...}                         # Issue list + metadata
  }
}
```

## Idempotency Guarantees

- **Deterministic Routing**: Document type always maps to same extractor (unless override)
- **UUID Tracking**: Each workflow execution has unique identifier
- **Immutable Logs**: Workflow logs are write-once, read-many
- **Reproducible**: Re-running same text produces same pipeline stages

## Progress Callbacks

The orchestrator supports real-time progress updates:

```python
def progress_callback(workflow_log: Dict, step_status: str):
    """Called after each pipeline stage.
    
    step_status values:
    - 'pre_extraction_active'
    - 'extraction_active'
    - 'line_items_active'
    - 'analysis_active'
    - 'complete'
    """
    # Update UI (e.g., DAG visualization)
    update_pipeline_dag(placeholder, workflow_log, step_status)
```

## Live DAG Visualization

The UI renders the pipeline as an interactive DAG:

- **Before Analysis**: Shows plan with all stages pending
- **During Analysis**: Updates in real-time as stages complete
- **After Analysis**: Shows complete execution trace

Users can expand the DAG to see:
- Document type classification confidence
- Extractor selection reasoning
- Fact extraction statistics
- Line-item parsing counts
- Analyzer choice and mode
- Issue detection summary

## Error Handling

Errors at any stage are captured in the workflow log:

```python
"extraction": {
  "extractor": "openai",
  "extraction_error": "RateLimitError: ...",  # Recorded but not thrown
  "facts": {}                                  # Empty facts on error
}
```

Pipeline continues with degraded data rather than failing completely.

## Performance Characteristics

- **Latency**: 3-8 seconds per document (varies by LLM provider)
- **Throughput**: Parallel document processing supported
- **Memory**: O(n) where n = document count (workflow logs retained in session)
- **Persistence**: Optional Supabase storage for workflow logs

## Implementation

See `src/medbilldozer/core/orchestrator_agent.py`:

```python
class OrchestratorAgent:
    def run(self, raw_text: str, progress_callback=None) -> Dict:
        # 5-stage DAG execution
        # Returns: {facts, analysis, _workflow_log, _orchestration}
```

## Document Type Classification

| Document Type | Trigger Pattern | Extractor | Analyzer |
|--------------|----------------|-----------|----------|
| `medical_bill` | CPT codes detected | OpenAI | GPT-4o-mini |
| `dental_bill` | CDT codes detected | OpenAI | GPT-4o-mini |
| `pharmacy_receipt` | Rx/NDC patterns | OpenAI | GPT-4o-mini |
| `insurance_eob` | EOB/claim keywords | OpenAI | GPT-4o-mini |
| `fsa_receipt` | FSA/HSA keywords | OpenAI | GPT-4o-mini |
| `generic` | Fallback | OpenAI | GPT-4o-mini |

## Next Steps

- [Orchestration Details](orchestration.md)
- [Provider Abstraction](provider_abstraction.md)
- [Live Visualization UI](../product/analysis_model.md)
