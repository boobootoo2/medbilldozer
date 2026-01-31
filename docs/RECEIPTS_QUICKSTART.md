# 🧾 Receipts Feature - Quick Start

## What's New

Added **Stored Receipts** functionality to health profiles! Each profile now includes 10 sample receipts that provide historical billing context for improved analysis.

## Key Features

🎯 **10 Sample Receipts per Profile** (20 total)
- Policy Holder: John Sample (10 receipts)
- Dependent: Jane Sample (10 receipts)

📊 **Pattern Detection**
- Identifies providers with overcharge history
- Tracks out-of-network usage
- Calculates potential savings

🎨 **Visual Display**
- Color-coded notes (green = good, yellow = warning, blue = info)
- Summary metrics (total billed, insurance paid, patient paid)
- Expandable receipt details

🔍 **Analysis Integration**
- Receipts automatically included in analysis context
- LLM references receipt history for pattern detection
- Enhanced validation against historical data

## How to Use

### 1. Select a Profile

```python
# Profile selector appears on home page
selected_profile = render_profile_selector()
```

Choose from:
- **Policy Holder** (John Sample) - 51M with diabetes, hypertension
- **Dependent** (Jane Sample) - 39F with asthma, allergies

### 2. View Receipts

Expand the **🧾 Stored Receipts** section to see:
- 10 historical receipts
- Summary metrics
- Pattern analysis
- Individual receipt details with notes

### 3. Run Analysis

Upload a document for analysis. The system automatically:
- Includes receipt history in context
- Compares new bills against stored receipts
- Flags providers with overcharge history
- Detects billing patterns

## Receipt Examples

### Policy Holder Receipts

| Receipt | Service | Provider | Issue |
|---------|---------|----------|-------|
| RCP-001 | Colonoscopy | Valley Medical | Overcharged $250 |
| RCP-005 | Diabetes Follow-up | Dr. Reynolds | Overcharged $35 |
| RCP-006 | Chest X-Ray | HealthFirst | Overcharged $60 |
| RCP-007 | Urgent Care | QuickCare | Out-of-network + balance billing |

**Total Overcharges**: ~$435 across 10 receipts

### Dependent Receipts

| Receipt | Service | Provider | Issue |
|---------|---------|----------|-------|
| RCP-D001 | Dental Crown | BrightSmile | 35% coverage (dental) |
| RCP-D006 | Asthma Visit | HealthFirst | Overcharged $25 |
| RCP-D007 | Urgent Care | QuickCare | Out-of-network + balance billing |
| RCP-D009 | Pulmonary Test | Valley Medical | Overcharged $55 |

**Total Overcharges**: ~$175 across 10 receipts

## Analysis Context

When a profile is selected, receipts are included in the LLM prompt:

```
========================================
BILLING HISTORY (STORED RECEIPTS)
========================================
Total Receipts: 10

⚠️ OVERCHARGE PATTERNS DETECTED (6 receipts):
  - Valley Medical Center: 3 instances
  - HealthFirst Medical Group: 2 instances
  - QuickCare Urgent Care: 1 instance

🟡 OUT-OF-NETWORK USAGE (3 receipts):
  - GreenLeaf Pharmacy: recurring pharmacy charges
  - QuickCare Urgent Care: balance billing issues

TOTALS:
  Potential Savings if overcharges corrected: ~$435
```

## UI Components

### Receipt Card

```
┌─────────────────────────────────────────┐
│ RCP-001 - Screening Colonoscopy    ✅ Paid│
├─────────────────────────────────────────┤
│ 📅 Date: 01/12/2026                     │
│ 🏥 Provider: Valley Medical Center      │
│ 🔢 CPT Code: 45378                      │
│                                          │
│ 💵 Billed: $1,450.00                    │
│ 🏦 Insurance: $1,100.00                 │
│ 💳 Patient: $100.00                     │
│                                          │
│ ⚠️ Billed $250 over in-network fee      │
└─────────────────────────────────────────┘
```

### Summary Metrics

```
┌─────────────┬──────────────┬─────────────┐
│ Total Billed│Insurance Paid│Patient Paid │
│  $4,850.00  │  $3,750.00   │  $1,100.00  │
└─────────────┴──────────────┴─────────────┘
```

## Code Integration

### Enable in app.py

```python
# Import (already added)
from _modules.ui.health_profile import (
    render_profile_selector,
    render_profile_details,
    get_profile_context_for_analysis,
)

# Render UI (already enabled)
selected_profile = render_profile_selector()
if selected_profile:
    render_profile_details(selected_profile)

# Get context for analysis (already enabled)
profile_context = None
if selected_profile:
    profile_context = get_profile_context_for_analysis(selected_profile)

# Pass to orchestrator (already wired)
agent = OrchestratorAgent(
    profile_context=profile_context,  # Includes receipts!
)
```

## Benefits

### For Users
- ✅ See billing history at a glance
- ✅ Identify problematic providers
- ✅ Track out-of-network spending
- ✅ Calculate potential savings

### For Analysis
- ✅ Pattern-based validation
- ✅ Provider reputation scoring
- ✅ Historical fee comparison
- ✅ Improved accuracy

## Testing

1. **Start the app**: `streamlit run app.py`
2. **Select profile**: Choose "Policy Holder" or "Dependent"
3. **Expand receipts**: Click "🧾 Stored Receipts"
4. **Review data**: Check 10 sample receipts
5. **Run analysis**: Upload a bill and see receipt context in action

## Data Files

- **Module**: `_modules/ui/health_profile.py`
- **Profiles**: `SAMPLE_PROFILES` dictionary
- **Receipts**: `stored_receipts` key under each profile

## Next Steps

- [ ] Upload real receipts (future enhancement)
- [ ] Edit/annotate receipts
- [ ] Export receipt data
- [ ] Visual analytics dashboard
- [ ] Receipt verification workflow

## Documentation

- Full documentation: `docs/RECEIPTS_FEATURE.md`
- Profile architecture: `docs/PROFILE_EDITOR_ARCHITECTURE.md`
- Module reference: `docs/MODULE_REFERENCE.md`

---

**🚀 Ready to test!** The receipts feature is now live and integrated with the analysis workflow.
