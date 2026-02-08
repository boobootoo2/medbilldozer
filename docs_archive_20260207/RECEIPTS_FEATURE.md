# 🧾 Stored Receipts Feature

## Overview

The **Stored Receipts** feature allows patient profiles to maintain a history of previous medical bills and payments. These receipts are used as contextual data during analysis to:

1. **Detect Patterns**: Identify recurring overcharges from specific providers
2. **Provider Reputation**: Flag providers with a history of billing errors
3. **Comparative Analysis**: Compare new bills against historical data
4. **Savings Tracking**: Calculate potential savings across all receipts

## Receipt Data Structure

Each receipt contains:

```python
{
    "id": "RCP-001",                    # Unique receipt identifier
    "date": "01/12/2026",               # Service date
    "provider": "Valley Medical Center", # Provider name
    "service": "Screening Colonoscopy",  # Service description
    "cpt_code": "45378",                # CPT/CDT/NDC code
    "billed_amount": 1450.00,           # Amount billed by provider
    "insurance_paid": 1100.00,          # Amount paid by insurance
    "patient_paid": 100.00,             # Amount paid by patient
    "status": "Paid",                   # Payment status
    "notes": "Billed $250 over..."      # Analysis notes
}
```

## Sample Receipts

### Policy Holder (John Sample) - 10 Receipts

1. **RCP-001**: Colonoscopy - Overcharged $250
2. **RCP-002**: Annual Physical - Correctly billed
3. **RCP-003**: Metformin (Pharmacy) - Out-of-network
4. **RCP-004**: Metabolic Panel - Overcharged $20
5. **RCP-005**: Diabetes Follow-up - Overcharged $35
6. **RCP-006**: Chest X-Ray - Overcharged $60
7. **RCP-007**: Urgent Care - Out-of-network balance billing
8. **RCP-008**: Blood Count - Overcharged $20
9. **RCP-009**: Hypertension Check - Correctly billed
10. **RCP-010**: EKG - Overcharged $50

**Total Overcharges Detected**: ~$435

### Dependent (Jane Sample) - 10 Receipts

1. **RCP-D001**: Dental Crown - 35% coverage
2. **RCP-D002**: Albuterol Inhaler - Out-of-network
3. **RCP-D003**: Dental Cleaning - 100% covered
4. **RCP-D004**: Allergy Panel - 80% coverage
5. **RCP-D005**: Gynecological Exam - 100% covered
6. **RCP-D006**: Asthma Visit - Overcharged $25
7. **RCP-D007**: Urgent Care - Out-of-network balance billing
8. **RCP-D008**: Cetirizine (Pharmacy) - Out-of-network
9. **RCP-D009**: Pulmonary Function Test - Overcharged $55
10. **RCP-D010**: Follow-up Visit - Correctly billed

**Total Overcharges Detected**: ~$175

## UI Display

Receipts are displayed in an expandable section under the profile details:

```
🧾 Stored Receipts
├── Summary Metrics (Total Billed, Insurance Paid, Patient Paid)
├── Individual Receipts
│   ├── Receipt ID & Service Name
│   ├── Date, Provider, Code
│   ├── Billing Breakdown
│   └── Analysis Notes (color-coded)
└── Pattern Detection Notes
```

### Color Coding

- 🟢 **Green (Success)**: Correctly billed, 100% covered
- 🟡 **Yellow (Warning)**: Potential overcharge detected
- 🔵 **Blue (Info)**: Out-of-network, reimbursement notes

## Integration with Analysis

When a profile is selected, receipts are included in the analysis context:

### Context Structure

```
========================================
BILLING HISTORY (STORED RECEIPTS)
========================================
Total Receipts: 10

⚠️ OVERCHARGE PATTERNS DETECTED (6 receipts):
  - 01/12/2026: Valley Medical Center | Colonoscopy
    Billed: $1,450.00 | Patient: $100.00
    Note: Billed $250 over in-network accepted fee
  ...

🟡 OUT-OF-NETWORK USAGE (3 receipts):
  - 12/15/2025: GreenLeaf Pharmacy | Metformin
    Patient paid: $17.00 | Note: 80% reimbursement
  ...

TOTALS ACROSS ALL STORED RECEIPTS:
  Total Billed: $4,850.00
  Insurance Paid: $3,750.00
  Patient Paid: $1,100.00
  Potential Savings: $435.00
```

### Enhanced Validation Instructions

The LLM receives additional instructions when receipts are present:

8. **PATTERN DETECTION**: Compare new bills against stored receipt history to identify recurring overcharges from same providers
9. **PROVIDER REPUTATION**: Flag providers with history of overcharging based on stored receipts

## Benefits

### 1. Pattern Recognition
- Identify providers who consistently overcharge
- Detect systematic billing errors
- Track out-of-network usage patterns

### 2. Improved Accuracy
- Compare new bills against known accepted fees
- Validate insurance reimbursement rates
- Cross-reference procedure codes with history

### 3. Cost Savings
- Calculate cumulative overcharges
- Project potential savings
- Inform future provider selection

### 4. Contextual Analysis
- Understand patient's billing history
- Reference previous similar procedures
- Identify changes in pricing over time

## API Usage

### Get Profile with Receipts

```python
from _modules.ui.health_profile import get_profile_data

profile = get_profile_data('policyholder')
receipts = profile.get('stored_receipts', [])

print(f"Found {len(receipts)} receipts")
for receipt in receipts:
    print(f"{receipt['id']}: {receipt['service']} - ${receipt['billed_amount']}")
```

### Get Analysis Context

```python
from _modules.ui.health_profile import get_profile_context_for_analysis

context = get_profile_context_for_analysis('policyholder')
# Context string includes receipts section with pattern analysis
```

### Render Profile UI

```python
from _modules.ui.health_profile import (
    render_profile_selector,
    render_profile_details
)

# In your Streamlit app
selected_profile = render_profile_selector()
if selected_profile:
    render_profile_details(selected_profile)  # Includes receipts expander
```

## Future Enhancements

### Planned Features
- [ ] Receipt upload functionality (PDF, image OCR)
- [ ] Receipt editing and annotation
- [ ] Export receipts to CSV/Excel
- [ ] Receipt categorization and tagging
- [ ] Visual analytics (charts, trends)
- [ ] Receipt search and filtering
- [ ] Duplicate detection
- [ ] Receipt verification status

### Advanced Analytics
- [ ] Provider overcharge rate scoring
- [ ] Time-series analysis of costs
- [ ] Predictive billing error detection
- [ ] Savings opportunity dashboard
- [ ] Comparative provider analysis

## Implementation Notes

### Data Location
- Receipts are stored in `_modules/ui/health_profile.py`
- Part of `SAMPLE_PROFILES` dictionary
- Nested under each profile's `stored_receipts` key

### Display Logic
- Rendered in `render_profile_details()` function
- Uses Streamlit expanders for organization
- Automatically color-codes based on notes content
- Calculates summary metrics on-the-fly

### Analysis Integration
- Receipts included in `get_profile_context_for_analysis()`
- Formatted as structured text for LLM consumption
- Highlights overcharge and out-of-network patterns
- Provides statistical summaries

## Testing

To test the receipts feature:

1. **Select a Profile**:
   ```python
   # In medBillDozer.py (already enabled)
   selected_profile = render_profile_selector()
   ```

2. **View Receipts**:
   - Expand the "🧾 Stored Receipts" section
   - Review 10 sample receipts per profile
   - Check color-coded notes

3. **Run Analysis**:
   - Upload a document for analysis
   - Profile context (including receipts) is automatically included
   - LLM will reference receipt history in analysis

4. **Verify Context**:
   - Enable debug mode
   - Check session state for profile_context
   - Confirm receipts section is present

## Example Usage

```python
# medBillDozer.py (main application)
from _modules.ui.health_profile import (
    render_profile_selector,
    render_profile_details,
    get_profile_context_for_analysis,
)

# Render profile selector
selected_profile = render_profile_selector()

if selected_profile:
    # Display profile details (includes receipts)
    render_profile_details(selected_profile)
    
    # Get context for analysis (includes receipt patterns)
    profile_context = get_profile_context_for_analysis(selected_profile)
    
    # Pass context to orchestrator
    agent = OrchestratorAgent(
        extractor_override=extractor_override,
        analyzer_override=analyzer_override,
        profile_context=profile_context,  # Includes receipts!
    )
```

## POC Demonstration

The current implementation includes:

✅ **20 Total Sample Receipts** (10 per profile)
✅ **Realistic Billing Scenarios** (overcharges, out-of-network, correct billing)
✅ **Pattern Detection** (recurring provider issues)
✅ **Visual UI** (expandable, color-coded, summary metrics)
✅ **Analysis Integration** (automatic context inclusion)
✅ **Multiple Code Types** (CPT, CDT, NDC)
✅ **Diverse Services** (medical, dental, pharmacy)

This POC demonstrates how stored receipts provide valuable historical context for analyzing new medical bills and detecting patterns of overcharging or billing errors.
