# MedBillDozer Documentation

*Auto-generated from codebase analysis*

## Project Overview

**Total Modules:** 1

### Application (1 modules)

- **app**: MedBillDozer - Medical billing error detection application.


## Module: `app`

**Source:** `app.py`

### Description

MedBillDozer - Medical billing error detection application.

Main Streamlit application that orchestrates document analysis, provider registration,
and UI rendering for detecting billing, pharmacy, dental, and insurance claim issues.

### Functions

#### `main()`

Main application entry point.

Orchestrates the complete workflow:
1. Bootstrap UI and register providers
2. Initialize guided tour state
3. Render privacy dialog
4. Collect document inputs
5. Analyze documents with selected provider
6. Display results and savings summary
7. Render coverage matrix and debug info

