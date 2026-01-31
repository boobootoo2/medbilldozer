# Two-Tab Workflow Documentation

## Overview

The MedBillDozer application now features a dual-workflow interface with two distinct tabs on the home page:

1. **🧪 Demo POC** - Original proof-of-concept workflow with demo documents and paste functionality
2. **🏭 Demo Prod Workflow** - Production-style workflow with profile-based preloaded documents

## Tab 1: Demo POC

### Description
The original workflow that demonstrates the core analysis capabilities of MedBillDozer.

### Features
- **Demo Documents**: 5 sample medical documents (colonoscopy bill, pharmacy receipt, dental bill, FSA claim, insurance claim)
- **Paste Functionality**: Users can paste their own medical documents
- **Document Upload**: Support for multiple document types
- **Guided Tour**: Interactive onboarding with audio narration
- **Analysis Engine**: Selectable analysis providers (Smart/OpenAI/Gemini)
- **Coverage Matrix**: Visual representation of document coverage

### User Flow
1. Select or paste documents
2. Choose analysis engine
3. Click "Analyze with medBillDozer"
4. Review results with savings summary
5. Clear history and start new analysis

## Tab 2: Demo Prod Workflow

### Description
A production-ready interface that simulates a real-world healthcare billing management system where documents are automatically loaded based on the user's health profile.

### Features

#### Profile Selection
- **Policy Holder**: John Sample (age 51, Horizon PPO Plus)
- **Dependent**: Emma Sample (age 16, same insurance)

Each profile includes:
- Full demographic information
- Insurance details (member ID, group number, deductible, OOP max)
- Provider network information

#### Preloaded Documents

**Policy Holder Documents:**
1. **DOC-PH-001**: Colonoscopy bill ($1,200) - 🚩 FLAGGED
   - Issue: Amount exceeds insurance allowed amount
   - Provider: Valley Medical Center
   
2. **DOC-PH-002**: Pharmacy receipt ($125) - 🚩 FLAGGED
   - Issue: Out-of-network pharmacy, insurance not billed
   - Provider: GreenLeaf Pharmacy
   
3. **DOC-PH-003**: Insurance EOB ($0) - ✓ Clear
   - Annual physical exam properly processed
   - Provider: Horizon PPO Plus

**Dependent Documents:**
1. **DOC-DEP-001**: Dental crown bill ($850) - 🚩 FLAGGED
   - Issue: Lab fee not itemized in insurance estimate
   - Provider: BrightSmile Dental
   
2. **DOC-DEP-002**: Pharmacy receipt ($15) - ✓ Clear
   - Properly processed prescription
   - Provider: CVS Pharmacy
   
3. **DOC-DEP-003**: Medical office visit ($45) - ✓ Clear
   - Standard copay and coinsurance applied
   - Provider: HealthFirst Medical Group

#### Document Status Tracking

Each document has a status:
- **⏳ Pending**: Not yet analyzed
- **🔄 Analyzing**: Currently being processed (shows spinner)
- **✅ Completed**: Analysis finished
- **❌ Error**: Analysis failed

#### Flagging System

Documents are automatically flagged (🚩) when they contain potential issues:
- Amounts exceeding insurance allowed rates
- Out-of-network charges
- Missing itemization
- Billing discrepancies
- Duplicate charges

#### Key Metrics Dashboard

Displays at the top of the page:
- **Total Documents**: Count of all documents for selected profile
- **Flagged**: Number of documents requiring review
- **Pending Analysis**: Documents not yet processed
- **Flagged Amount**: Total dollar amount of flagged documents

#### Parallel Analysis

When clicking **Analyze**, all pending documents are processed in parallel:
- Progress bar shows overall completion
- Individual documents display spinner while analyzing
- Status updates in real-time
- Success message upon completion

### User Flow

1. Select a health profile (Policy Holder or Dependent)
2. Review profile summary (name, DOB, insurance info)
3. View metrics dashboard (total docs, flagged, pending)
4. Browse preloaded documents in expandable cards
5. Click "Analyze X Pending Document(s)"
6. Watch parallel analysis with progress tracking
7. Review completed analysis results

### Document Card Details

Each document card shows:
- **Header**: Icon, status, document ID, provider, flag badge
- **Left Column**: Doc ID, type, provider, service date
- **Right Column**: Status, flagged indicator, amount
- **Spinner**: Displayed while analyzing (status = 'analyzing')
- **Content Viewer**: Expandable section to view full document text

## Implementation Details

### File Structure

```
_modules/ui/
├── bootstrap.py          # Home page initialization (unchanged)
├── prod_workflow.py      # NEW: Production workflow logic
└── ...

app.py                    # Main application with tab routing
```

### Key Components

#### 1. ProfileDocument TypedDict
```python
class ProfileDocument(TypedDict):
    doc_id: str
    profile_id: str
    profile_name: str
    doc_type: str
    provider: str
    service_date: str
    amount: float
    flagged: bool
    status: str
    content: str
```

#### 2. Preloaded Data
- `PRELOADED_DOCUMENTS`: List of 6 sample documents (3 per profile)
- Realistic document content with proper formatting
- Mix of flagged and clear documents

#### 3. Helper Functions
- `get_documents_for_profile(profile_id)`: Filter by profile
- `get_flagged_documents(profile_id)`: Get flagged docs
- `get_pending_documents(profile_id)`: Get unanalyzed docs

#### 4. Rendering
- `render_prod_workflow()`: Main interface renderer
- Profile selector with radio buttons
- Metrics dashboard with 4 key indicators
- Document list with expandable cards
- Parallel analysis with progress tracking

### Session State Management

The production workflow uses session state for:
- `prod_analyzing`: Boolean flag indicating active analysis
- Document status updates are stored in the preloaded list

### Analysis Simulation

For demo purposes, analysis is simulated:
- Each document takes ~1.5 seconds to "analyze"
- Progress bar updates in real-time
- Documents show spinner during processing
- Status changes from 'pending' → 'analyzing' → 'completed'

## Integration Points

### With Health Profile Module
- Imports `SAMPLE_PROFILES` from `_modules.ui.health_profile`
- Displays profile information from existing data structure
- Maintains consistency with profile editor

### With Existing Analysis
- Production workflow is self-contained in Tab 2
- Does not interfere with POC workflow in Tab 1
- Can be extended to use actual analysis agents in the future

## Future Enhancements

### Planned Features
1. **Real Analysis Integration**: Connect to actual OrchestratorAgent
2. **Document Upload**: Allow users to upload new documents to profiles
3. **Status Filtering**: Filter documents by status or flag
4. **Export Functionality**: Download analysis results as PDF/CSV
5. **Multi-Profile Support**: Manage multiple family members
6. **Historical Tracking**: View past analyses and trends
7. **Notifications**: Alert users to new flagged documents
8. **Batch Operations**: Select multiple documents for bulk actions

### Technical Improvements
1. **Database Persistence**: Store documents in SQLite or PostgreSQL
2. **Async Processing**: True parallel analysis with workers
3. **Caching**: Cache analysis results for faster re-rendering
4. **WebSocket Updates**: Real-time status updates without polling
5. **API Integration**: Connect to real healthcare data sources

## Usage Examples

### Selecting a Profile
```python
# User clicks on "Policy Holder" radio button
selected_profile_id = 'PH-001'
profile_docs = get_documents_for_profile(selected_profile_id)
# Returns 3 documents for John Sample
```

### Analyzing Pending Documents
```python
# User clicks "Analyze 3 Pending Document(s)"
for doc in pending_docs:
    doc['status'] = 'analyzing'  # Show spinner
    # Simulate analysis
    time.sleep(1.5)
    doc['status'] = 'completed'  # Mark done
```

### Checking Flagged Documents
```python
flagged = get_flagged_documents('PH-001')
# Returns DOC-PH-001 and DOC-PH-002 (2 flagged docs)
```

## Testing Checklist

- [ ] Tab switching works without errors
- [ ] Profile selection updates document list
- [ ] Metrics dashboard displays correct counts
- [ ] Document cards expand/collapse properly
- [ ] Flagged badges appear on correct documents
- [ ] Analyze button processes all pending docs
- [ ] Progress bar updates smoothly
- [ ] Spinners appear during analysis
- [ ] Status changes from pending → analyzing → completed
- [ ] Success message displays after analysis
- [ ] Refresh button reloads the page
- [ ] Document content viewer shows full text
- [ ] Tab 1 (POC) still works independently
- [ ] No console errors in browser

## Benefits

### For Users
- **Realistic Demo**: See how the system would work with real data
- **Profile-Based**: Understand how family members are tracked separately
- **Status Visibility**: Know which documents need attention
- **Parallel Processing**: See efficient batch analysis

### For Development
- **Separation of Concerns**: POC and Prod workflows are independent
- **Easy Testing**: Preloaded data makes testing consistent
- **Extensibility**: Production workflow can evolve without breaking POC
- **Demo-Ready**: Perfect for presentations and user testing

## Conclusion

The two-tab workflow provides both a simple proof-of-concept for new users and a sophisticated production-style interface for demonstrating enterprise capabilities. This architecture supports the dual goals of accessibility and scalability in the MedBillDozer platform.
