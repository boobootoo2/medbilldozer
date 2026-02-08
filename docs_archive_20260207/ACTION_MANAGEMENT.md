# Action Management Feature

## Overview

The Production Workflow now includes comprehensive action management capabilities, allowing users to track the status of document reviews and share actioned items with team members or for record-keeping.

## Features

### 1. Action Types

Each document can be assigned one of three actions:

| Action | Icon | Purpose | Use Case |
|--------|------|---------|----------|
| **Ignore** | ⊘ | Mark document as not requiring further action | False positives, already handled outside system |
| **Follow-up** | 🔔 | Document requires additional investigation | Need more information, pending provider response |
| **Resolved** | ✅ | Issue has been addressed and closed | Billing corrected, dispute settled, payment made |

### 2. Action Management Interface

Located within each document card in the Production Workflow:

#### Action Dropdown
- Select from: — No Action, ⊘ Ignore, 🔔 Follow-up Required, ✅ Resolved
- Current action is highlighted if already set
- Changes are not saved until "Save Action" button is clicked

#### Action Notes
- Text area appears when an action is selected
- Add context, next steps, or resolution details
- Notes persist with the document
- Save button updates notes independently
- Maximum display length: 50 characters in table (full text in card)

#### Action Date
- Automatically recorded when action is saved
- Format: YYYY-MM-DD HH:MM
- Displayed in actioned items table

#### Clear Action
- Button to remove action and reset to "No Action"
- Clears action, notes, and date
- Confirmation not required (can be re-applied)

### 3. Actioned Items Dashboard

Appears at the top of the document list when any actions have been taken:

#### Metrics Row
- **Total Actions**: Count of all actioned documents
- **Ignored**: Count of documents marked as ignored
- **Follow-up**: Count of documents requiring follow-up
- **Resolved**: Count of resolved documents

#### Actioned Items Table

| Column | Description |
|--------|-------------|
| Doc ID | Document identifier (e.g., DOC-PH-001) |
| Provider | Healthcare provider name |
| Amount | Dollar amount with $ formatting |
| Action | Icon + action type (⊘ Ignore, 🔔 Follow-up, ✅ Resolved) |
| Date | When action was taken |
| Notes | Truncated preview (50 chars) with ellipsis |

#### Export Options

**Download CSV**
- Button: "📥 Download CSV"
- Filename format: `actioned_items_{PROFILE_ID}_{YYYYMMDD}.csv`
- Includes all columns with full notes text
- Opens browser download dialog

**Copy Table**
- Button: "📋 Copy Table"
- Simulates copying table data to clipboard
- In production: Would use clipboard API
- Currently shows info message

## User Workflows

### Workflow 1: Mark Document as Ignored

1. Open document card
2. Select "⊘ Ignore" from Action dropdown
3. Click "💾 Save Action"
4. Optionally add notes explaining why (e.g., "Duplicate of DOC-PH-003")
5. Click "💾 Save Notes"
6. Document appears in Actioned Items table

### Workflow 2: Create Follow-up Task

1. Open flagged document
2. Select "🔔 Follow-up Required"
3. Click "💾 Save Action"
4. Add notes: "Called provider on 1/30. Waiting for itemized bill."
5. Click "💾 Save Notes"
6. Document tracked in Follow-up metric
7. Review actioned items table to see pending follow-ups

### Workflow 3: Resolve Issue

1. Open document with previous action (e.g., Follow-up)
2. Change action to "✅ Resolved"
3. Click "💾 Save Action"
4. Update notes: "Provider issued credit of $250. Confirmed on 2/1."
5. Click "💾 Save Notes"
6. Document moves from Follow-up to Resolved count

### Workflow 4: Export for Reporting

1. Review actioned items dashboard
2. Click "📥 Download CSV"
3. Save file locally
4. Open in Excel/Google Sheets
5. Share with insurance, provider, or team members
6. Use for dispute documentation or audit trails

### Workflow 5: Clear Incorrect Action

1. Open document with wrong action
2. Click "🗑️ Clear Action" button
3. Action, notes, and date are removed
4. Document removed from actioned items table
5. Re-apply correct action if needed

## Data Structure

### ProfileDocument Type
```python
{
    'doc_id': 'DOC-PH-001',
    'profile_id': 'PH-001',
    'profile_name': 'John Sample',
    'doc_type': 'medical_bill',
    'provider': 'Valley Medical Center',
    'service_date': '2026-01-12',
    'amount': 1200.00,
    'flagged': True,
    'status': 'completed',
    'action': 'followup',  # None, 'ignored', 'followup', 'resolved'
    'action_notes': 'Waiting for corrected bill from provider',
    'action_date': '2026-01-30 14:35',
    'content': '...'
}
```

### CSV Export Format
```csv
Document ID,Profile,Provider,Service Date,Amount,Action,Action Date,Notes,Flagged
DOC-PH-001,John Sample,Valley Medical Center,2026-01-12,$1200.00,Followup,2026-01-30 14:35,Waiting for corrected bill,Yes
```

## Helper Functions

### `get_actioned_documents(profile_id)`
Returns list of documents with actions set.

```python
actioned = get_actioned_documents('PH-001')
# Returns only documents where action is not None
```

### `export_actioned_items_csv(docs)`
Generates CSV string from actioned documents.

```python
csv_data = export_actioned_items_csv(actioned_docs)
# Returns CSV formatted string for download
```

## UI Components

### Action Selector
```python
st.selectbox(
    "Action",
    options=['none', 'ignored', 'followup', 'resolved'],
    format_func=lambda x: {
        'none': '— No Action',
        'ignored': '⊘ Ignore',
        'followup': '🔔 Follow-up Required',
        'resolved': '✅ Resolved'
    }[x]
)
```

### Metrics Display
```python
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Actions", len(actioned_docs))
with col2:
    st.metric("Ignored", ignored_count)
with col3:
    st.metric("Follow-up", followup_count)
with col4:
    st.metric("Resolved", resolved_count)
```

### Download Button
```python
st.download_button(
    label="📥 Download CSV",
    data=csv_data,
    file_name=f"actioned_items_{profile_id}_{date}.csv",
    mime="text/csv"
)
```

## Best Practices

### When to Use Each Action

**Ignore (⊘)**
- False flags (document is actually correct)
- Duplicate documents
- Already resolved outside the system
- Non-issues flagged by automatic detection

**Follow-up (🔔)**
- Need more information from provider
- Waiting for response to dispute
- Pending investigation
- Requires consultation with insurance

**Resolved (✅)**
- Issue corrected by provider
- Refund received
- Dispute settled in your favor
- No further action needed

### Note-Taking Tips

**Good Notes:**
- "Called provider 1/30. Rep confirmed $250 credit will be issued."
- "Insurance confirmed coverage. Waiting for corrected EOB."
- "Duplicate charge removed. New bill shows $850 (correct amount)."

**Poor Notes:**
- "Fixed"
- "OK"
- "Done"

### Documentation Strategy

1. **Initial Action**: Record what you're doing and why
2. **Progress Updates**: Add notes as situation evolves
3. **Resolution**: Document final outcome and confirmation
4. **Reference**: Include case numbers, rep names, dates

## Integration Points

### With Profile Management
- Actions are profile-specific
- Switching profiles shows different actioned items
- Each family member has independent action tracking

### With Document Status
- Actions are independent of analysis status
- Can act on pending, analyzing, or completed documents
- Status and action tracked separately

### With Flagging System
- Flagged documents often need actions
- Unflagged documents can also be actioned
- Action doesn't remove flag (flag indicates issue detected)

## Future Enhancements

### Planned Features
- [ ] Action history timeline (track changes over time)
- [ ] Reminders for follow-up items
- [ ] Bulk action assignment
- [ ] Action templates (common notes)
- [ ] Email sharing of actioned items
- [ ] PDF export with document attachments
- [ ] Integration with calendar for follow-up dates
- [ ] Action assignment to team members
- [ ] Custom action types
- [ ] Action workflows (e.g., Ignored → Reopened)

### Technical Improvements
- [ ] Persist actions to database
- [ ] Real-time sync across sessions
- [ ] Undo/redo for actions
- [ ] Audit log of action changes
- [ ] Version control for notes
- [ ] Search and filter actioned items
- [ ] Analytics dashboard (time to resolution, etc.)
- [ ] API endpoints for action management

## Troubleshooting

### Action Not Saving
- **Issue**: Click "Save Action" but action doesn't persist
- **Solution**: Ensure action is different from current state
- **Workaround**: Clear action first, then set new action

### Notes Not Updating
- **Issue**: Notes text changes but doesn't save
- **Solution**: Click "💾 Save Notes" button after editing
- **Note**: Notes auto-save not implemented (by design)

### CSV Download Not Working
- **Issue**: Download button doesn't trigger download
- **Solution**: Check browser popup blocker settings
- **Alternative**: Use "Copy Table" and paste into spreadsheet

### Actioned Items Table Not Showing
- **Issue**: No actioned items dashboard appears
- **Solution**: At least one document must have an action set
- **Note**: Table only appears when actions exist

## Examples

### Example 1: Overcharge Follow-up
```
Document: DOC-PH-001 - Colonoscopy ($1,200)
Action: 🔔 Follow-up Required
Notes: "Billed amount exceeds insurance allowed rate by $300. 
       Called provider 1/30 at 2pm. Spoke with billing dept (ext 4523).
       They are reviewing and will call back within 48 hours."
Date: 2026-01-30 14:15
```

### Example 2: Resolved Dispute
```
Document: DOC-PH-002 - Pharmacy ($125)
Action: ✅ Resolved
Notes: "Resubmitted to insurance as in-network (CVS in network, 
       not GreenLeaf). Insurance paid $110. Patient responsibility 
       reduced to $15. Confirmation email received 2/1."
Date: 2026-02-01 09:30
```

### Example 3: Ignored False Flag
```
Document: DOC-DEP-001 - Dental Crown ($850)
Action: ⊘ Ignore
Notes: "Lab fee is standard for porcelain crowns. Verified with 
       insurance - covered under major services. No issue."
Date: 2026-01-30 16:45
```

## Related Documentation

- [Two-Tab Workflow](TWO_TAB_WORKFLOW.md) - Overall workflow structure
- [Production Workflow](TWO_TAB_QUICKSTART.md) - Quick start guide
- [Profile Editor](PROFILE_EDITOR_QUICKSTART.md) - Profile management

---

**Last Updated**: January 30, 2026
