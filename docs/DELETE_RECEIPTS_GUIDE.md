# How to Delete Receipts

## Quick Answer

**To delete receipts:**
1. Go to **Profile Editor** tab
2. Scroll down to the **Receipts** section
3. Find the receipt you want to delete
4. Click the **🗑️ Delete** button next to it
5. Receipt is immediately removed from storage

## Detailed Guide

### Step-by-Step: Deleting a Receipt

#### 1. Navigate to Profile Editor

```
App Navigation:
├─ Demo POC (tab 1)
├─ Demo Prod Workflow (tab 2)
└─ Profile Editor (tab 3) ← Go here
```

#### 2. Find the Receipts Section

Scroll down in the Profile Editor to the **"Receipts"** section. You'll see a list of all uploaded receipts with their status indicators:

- 🟡 Yellow = Pending Review / Review
- ✅ Green = Reconciled

#### 3. Locate the Receipt to Delete

Each receipt shows:
- Status emoji (🟡 or ✅)
- File name (e.g., "Pasted_20260131_055530.txt")
- Status text (e.g., "Pending Review")

#### 4. Click the Delete Button

On each receipt card, you'll see buttons on the right side:
- **💾 Save Notes** (if notes were edited)
- **🗑️ Delete** ← Click this

#### 5. Confirm Deletion

After clicking delete:
- Receipt is removed from the list
- Success message: "Receipt deleted!"
- Page refreshes automatically
- Receipt is permanently removed from `data/receipts.json`

### Effect on Production Workflow

#### Current Session (Same App Instance)

**If you delete a receipt while the app is running:**

1. **In Profile Editor**: Receipt disappears immediately
2. **In Production Workflow**: Receipt document stays in session until you reload
3. **To sync**: Click **"📥 Reload Receipts"** in Production Workflow → Won't re-add deleted receipt

#### After Restart

**If you delete a receipt and restart the app:**
- Receipt won't appear in Profile Editor (deleted)
- Receipt won't load into Production Workflow (doesn't exist)
- Session state starts fresh without that receipt

### Bulk Deletion

To delete multiple receipts:

1. Go to Profile Editor
2. Click 🗑️ Delete on first receipt
3. Wait for page refresh
4. Click 🗑️ Delete on next receipt
5. Repeat for each receipt

**Note**: There's currently no "Delete All" button - each receipt must be deleted individually.

### What Gets Deleted

When you delete a receipt:

✅ **Permanently Removed:**
- Receipt entry from `data/receipts.json`
- File reference (if uploaded)
- All metadata (provider, amount, date, notes, status)

❌ **NOT Removed:**
- The receipt document in Production Workflow session (until reload/restart)
- Any actions/notes you added in Production Workflow
- Analysis results from Production Workflow

### Recovery

**Can I recover a deleted receipt?**

❌ No - Deletion is permanent. The receipt data is removed from `receipts.json`.

**However:**
- If you still have the original file, you can re-upload it
- If it was pasted text, you'd need to paste it again

### Best Practices

#### Before Deleting

1. **Check if reconciled**: Make sure you don't need the receipt anymore
2. **Review notes**: Check if you added important notes
3. **Verify provider/amount**: Ensure it's the right receipt

#### Safe Deletion Workflow

```
1. Review receipt in Profile Editor
   └─ Check provider, amount, date, notes

2. If needed in Production Workflow:
   └─ Export follow-up tasks CSV first
   └─ Save any analysis results

3. Delete from Profile Editor
   └─ Click 🗑️ Delete

4. In Production Workflow (optional):
   └─ Click "🔄 Reset All" to clear session
   └─ Receipts will reload without deleted one
```

### Common Scenarios

#### Scenario 1: Duplicate Receipts

**Problem**: Same receipt uploaded twice

**Solution**:
1. Compare receipt details (amount, date, provider)
2. Keep the one with better data/notes
3. Delete the duplicate with 🗑️ Delete

#### Scenario 2: Wrong Receipt Uploaded

**Problem**: Uploaded wrong file or pasted wrong text

**Solution**:
1. Delete the wrong receipt immediately
2. Upload/paste the correct receipt
3. In Production Workflow: Click "Reload Receipts"

#### Scenario 3: Testing/Demo Cleanup

**Problem**: Added sample receipts for testing, want to clean up

**Solution**:
1. Go to Profile Editor
2. Delete each test receipt individually
3. In Production Workflow: Click "Reset All"
4. Session resets with only real receipts

#### Scenario 4: Already Reconciled

**Problem**: Receipt is reconciled and no longer needed

**Solution**:
1. Verify status = "Reconciled" ✅
2. Check notes for any important info
3. Export data if needed
4. Delete with 🗑️ Delete

### Alternative: Status Instead of Delete

Instead of deleting, you can change the receipt status:

| Status | When to Use | Effect in Prod Workflow |
|--------|-------------|------------------------|
| **Review** | Needs attention | Flagged for review |
| **Pending Review** | Not yet processed | Flagged for review |
| **Reconciled** | Fully processed | Not flagged, marked complete |

**To change status:**
1. In receipt card, find "Status" dropdown
2. Select new status
3. Click 💾 Save (or it saves automatically)

This way you keep the receipt but mark it as handled.

### Troubleshooting

#### Receipt Won't Delete

**Symptoms**: Clicked delete but receipt still appears

**Solutions**:
1. Refresh the page (F5 or Cmd+R)
2. Check if error message appeared
3. Check file permissions on `data/receipts.json`

#### Deleted Receipt Still in Production Workflow

**Symptoms**: Deleted from Profile Editor but still shows in Prod Workflow

**Explanation**: Session state hasn't updated yet

**Solutions**:
1. Click "📥 Reload Receipts" (won't re-add deleted receipt)
2. Click "🔄 Reset All" (clears everything and reloads)
3. Restart the app

#### Can't Find Delete Button

**Symptoms**: Don't see 🗑️ Delete button

**Check**:
1. Are you in Profile Editor tab (not Prod Workflow)?
2. Is the receipt card expanded?
3. Scroll to the right side of the receipt card
4. Button is next to notes/status controls

### Data File Location

Receipts are stored in:
```
/Users/jgs/Documents/GitHub/medbilldozer/data/receipts.json
```

**Advanced**: You can manually edit this file, but be careful with the JSON format.

### Future Enhancements

Potential features for easier deletion:

1. **Bulk Delete**
   - Select multiple receipts
   - Delete all selected at once

2. **Delete Confirmation**
   - "Are you sure?" dialog
   - Prevent accidental deletion

3. **Soft Delete**
   - Mark as deleted but keep in archive
   - Ability to restore

4. **Delete from Production Workflow**
   - Delete button on receipt documents
   - Syncs back to Profile Editor

## Summary

**Quick Steps:**
1. Profile Editor → Receipts section
2. Find receipt → Click 🗑️ Delete
3. Confirm deletion
4. Done!

**Remember:**
- Deletion is permanent
- Delete from Profile Editor (not Prod Workflow)
- Session state updates on next reload
- Consider changing status instead of deleting

---

**Last Updated**: January 31, 2026  
**Version**: 1.0
