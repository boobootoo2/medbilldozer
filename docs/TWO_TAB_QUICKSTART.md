# Two-Tab Workflow - Quick Start Guide

## What Changed?

The MedBillDozer home page now has **two tabs** at the top:

### 🧪 Demo POC
The original workflow - paste documents, select engine, analyze

### 🏭 Demo Prod Workflow  
NEW! Profile-based workflow with preloaded documents and status tracking

---

## Demo Prod Workflow Features

### 📊 What You'll See

1. **Profile Selector**
   - Choose between Policy Holder (John Sample) or Dependent (Emma Sample)
   - See insurance details for selected profile

2. **Metrics Dashboard**
   - Total Documents
   - Flagged Documents 🚩
   - Pending Analysis
   - Total Flagged Amount

3. **Document Table**
   - Doc ID and Status (⏳ Pending, 🔄 Analyzing, ✅ Completed)
   - Flagged badge 🚩 for documents needing review
   - Expandable cards to view full document content

4. **Analyze Button**
   - Click to analyze all pending documents
   - Watch parallel processing with spinners
   - Progress bar shows completion status

---

## Sample Documents Included

### Policy Holder (John Sample)
- **DOC-PH-001**: Colonoscopy - $1,200 🚩 (exceeds allowed amount)
- **DOC-PH-002**: Pharmacy - $125 🚩 (out-of-network)
- **DOC-PH-003**: Insurance EOB - $0 ✓ (properly processed)

### Dependent (Emma Sample)
- **DOC-DEP-001**: Dental Crown - $850 🚩 (lab fee not itemized)
- **DOC-DEP-002**: Pharmacy - $15 ✓ (properly processed)
- **DOC-DEP-003**: Office Visit - $45 ✓ (standard copay)

---

## How to Use

### Step 1: Select a Profile
Click on either:
- 👨 **John Sample (Policy Holder)** - 3 documents
- 👧 **Emma Sample (Dependent)** - 3 documents

### Step 2: Review Documents
- Expand any document card to see full content
- Look for 🚩 flagged documents
- Check status: ⏳ Pending, ✅ Completed

### Step 3: Analyze Pending Documents
1. Click **"🔍 Analyze X Pending Document(s)"**
2. Watch the progress bar
3. Each document shows a spinner (🔄) while analyzing
4. Status changes to ✅ Completed when done

### Step 4: Review Results
- All documents now show ✅ Completed status
- Flagged documents still show 🚩 badge
- Click 🔄 Refresh to reset (demo only)

---

## Key Differences from POC Tab

| Feature | Demo POC | Demo Prod Workflow |
|---------|----------|-------------------|
| Documents | Demo samples + paste | Preloaded by profile |
| Analysis | Single/multiple pasted | All pending docs |
| Status Tracking | No | Yes (pending/analyzing/completed) |
| Flagging | No | Yes (automatic) |
| Profiles | Optional selector | Required selector |
| Progress | Spinner | Progress bar + individual spinners |
| Parallel Processing | No | Yes (simulated) |

---

## File Structure

```
app.py                           # Main app with tab routing
_modules/ui/
  ├── bootstrap.py               # POC workflow initialization
  └── prod_workflow.py           # NEW: Production workflow
docs/
  ├── TWO_TAB_WORKFLOW.md        # Full documentation
  └── TWO_TAB_QUICKSTART.md      # This file
```

---

## Technical Notes

### Data Structure
```python
ProfileDocument = {
    'doc_id': 'DOC-PH-001',
    'profile_id': 'PH-001',
    'doc_type': 'medical_bill',
    'provider': 'Valley Medical Center',
    'amount': 1200.00,
    'flagged': True,
    'status': 'pending',  # pending | analyzing | completed | error
    'content': '...'
}
```

### Status Flow
```
pending → analyzing → completed
   ⏳        🔄           ✅
```

### Analysis Simulation
For demo purposes:
- Each document takes ~1.5 seconds
- Progress updates in real-time
- No actual AI analysis (can be integrated)

---

## Next Steps

1. **Try the Prod Workflow** - Select a profile and analyze documents
2. **Compare with POC** - Switch between tabs to see differences
3. **Review Flagged Docs** - See what issues were detected
4. **Read Full Docs** - See [TWO_TAB_WORKFLOW.md](TWO_TAB_WORKFLOW.md)

---

## Common Questions

**Q: Will this break the original POC workflow?**  
A: No! Tab 1 (Demo POC) works exactly as before.

**Q: Is the analysis real?**  
A: Currently simulated for demo. Can be integrated with OrchestratorAgent.

**Q: Can I add my own documents?**  
A: Not yet in Prod Workflow. Use Demo POC tab for custom documents.

**Q: What happens when I click Analyze?**  
A: All pending documents are processed in parallel (simulated). Each shows a spinner, then completes.

**Q: Why are some documents flagged?**  
A: Flagged (🚩) means potential issues detected: overcharges, out-of-network, missing info, etc.

**Q: Can I switch profiles during analysis?**  
A: Yes, but analysis is per-profile. Each profile has its own documents.

---

## Future Enhancements

- [ ] Real AI analysis integration
- [ ] Document upload to profiles
- [ ] Export analysis reports
- [ ] Historical tracking
- [ ] Multi-family member support
- [ ] Batch document operations
- [ ] Database persistence
- [ ] WebSocket real-time updates

---

## Support

For questions or issues:
1. Check [TWO_TAB_WORKFLOW.md](TWO_TAB_WORKFLOW.md) for details
2. Review [MODULES.md](MODULES.md) for API reference
3. See [QUICKSTART.md](QUICKSTART.md) for general setup

---

**Last Updated**: January 30, 2026
