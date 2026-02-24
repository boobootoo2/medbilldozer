# Release Notes

## v0.3.1 - Security Notice Enhancement

**Release Date:** [Current Date]

### New Features
- **Security Warning Banner**: Added a prominent warning banner displayed globally across all routes
  - Alerts users to NOT upload personal medical files or any real personally identifiable information
  - Sticky positioning ensures banner remains visible while scrolling
  - Clear visual design with warning icon for maximum visibility

### Security Improvements
- Enhanced user awareness about data privacy and the demonstration nature of the application
- Banner appears on all protected and public routes to ensure all users see the warning

### Technical Details
- New `SecurityBanner` component added to the component library
- Integrated at the top-level App component for global display
- Styled with high z-index for visibility above other UI elements

### User Impact
- Users will immediately see the security notice upon accessing any page
- Reduces risk of accidental PII uploads
- Reinforces that this is a demonstration tool meant for sample data only

---

## Previous Releases

[Additional release notes would go here]
