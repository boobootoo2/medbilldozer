# Profile Editor Quick Start Guide

The Profile Editor has been integrated into medBillDozer! This guide will help you get started.

## 🚀 Quick Start (3 steps)

### Step 1: Enable the Feature

Create a `.env` file in your project root (or edit existing one):

```bash
# Enable Profile Editor
PROFILE_EDITOR_ENABLED=TRUE

# Enable Import Wizard (optional, but recommended)
IMPORTER_ENABLED=TRUE
```

### Step 2: Start the App

```bash
streamlit run app.py
```

### Step 3: Access Profile Editor

Look for the **📋 Profile** button in the sidebar (next to 🏠 Home).

## 📋 What You Can Do

### 1. Manage Your Identity
- Full name, date of birth
- Primary address (street, city, state, zip)
- Quick validation and saving

### 2. Manage Insurance Plans
- Add multiple insurance plans (primary, secondary)
- Track carrier, plan name, member ID, group number
- Set deductibles (individual/family)
- Set out-of-pocket maximums
- Mark plans as active/inactive
- Track network status (in-network/out-of-network)

### 3. Manage Provider Directory
- Add doctors, hospitals, specialists
- Track NPI numbers
- Record specialty and practice information
- Mark network status for each provider
- Add notes about each provider

### 4. Import Data (Plaid-like Wizard)
- **4-step wizard experience**
  1. Choose source (Insurance EOB, Claim History, Bill/Receipt)
  2. Provide data (PDF upload, CSV paste, or text input)
  3. Review & edit extracted data inline
  4. Complete import with success confirmation

## 💾 Where Data is Stored

All profile data is saved as JSON files in the `./data/` directory:

```
data/
  ├── user_profile.json          # Your identity
  ├── insurance_plans.json       # All insurance plans
  ├── providers.json             # Provider directory
  ├── import_jobs.json           # Import history/metadata
  └── normalized_line_items.json # Imported transactions
```

**Note:** This directory is gitignored by default for privacy.

## 🎯 Navigation

The navigation buttons are in the sidebar at the top:

- **🏠 Home** - Main analysis page (default)
- **📋 Profile** - Profile Editor (only visible when enabled)

The active page is highlighted with a primary button style.

## 🔍 Using Profile Data in Analysis

Your profile data is automatically available during document analysis:

- Insurance plans help detect billing errors
- Provider directory validates network status
- Personal info ensures claim matching

The integration is seamless - just load your profile and analyze documents as normal!

## 🎨 Features

### ✅ Atomic Saves
All data writes use atomic operations (temp file + rename) to prevent corruption.

### ✅ Type Safety
All data models use TypedDict for full type checking and IDE autocomplete.

### ✅ Accessibility
- Clear labels and headings
- Keyboard navigation support
- No color-only indicators
- Screen reader friendly

### ✅ Smart Validation
- Required field checks
- Date format validation
- State code validation
- Duplicate detection

## 🛠️ Troubleshooting

### Profile button not showing up?

Check your `.env` file:
```bash
PROFILE_EDITOR_ENABLED=TRUE
```

Then restart the Streamlit app.

### Import wizard not available?

Enable it in `.env`:
```bash
IMPORTER_ENABLED=TRUE
```

### Data not persisting?

Check that the `./data/` directory exists and is writable:
```bash
mkdir -p data
ls -la data/
```

### Want to reset everything?

Simply delete the JSON files in `./data/`:
```bash
rm data/*.json
```

## 📚 Advanced Usage

For detailed integration patterns, customization options, and API reference, see:

- **[PROFILE_EDITOR_INTEGRATION.md](./PROFILE_EDITOR_INTEGRATION.md)** - Complete integration guide
- **[data/schema_examples.json](./data/schema_examples.json)** - JSON schema reference
- **[profile_integration_example.py](./profile_integration_example.py)** - Code examples

## 🤝 Support

If you encounter issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section above
2. Review the [Integration Guide](./PROFILE_EDITOR_INTEGRATION.md)
3. Check the [JSON Schema Examples](./data/schema_examples.json)
4. Look at [Code Examples](./profile_integration_example.py)

## 🎉 That's It!

You're ready to use the Profile Editor. Start by:

1. Setting `PROFILE_EDITOR_ENABLED=TRUE` in `.env`
2. Running `streamlit run app.py`
3. Clicking **📋 Profile** in the sidebar
4. Adding your information

Happy profiling!

