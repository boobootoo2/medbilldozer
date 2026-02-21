/**
 * Main entry point
 */
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { initRecaptchaFixes } from './utils/recaptchaFix'

// Initialize reCAPTCHA autocomplete fixes
initRecaptchaFixes();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
