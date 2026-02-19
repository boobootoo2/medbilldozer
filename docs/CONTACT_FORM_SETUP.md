# Contact Form Setup Guide

This guide explains how to configure the "Want to Know More" contact form with email delivery and reCAPTCHA protection.

## Overview

The contact form at [pages/want_to_know_more.py](../pages/want_to_know_more.py) sends emails to `john.g.shultz@gmail.com` and includes Google reCAPTCHA v3 for spam protection.

## Configuration Steps

### 1. Set Up Gmail App Password (for Email Sending)

To send emails through Gmail:

1. Go to your Google Account: https://myaccount.google.com
2. Navigate to **Security** > **2-Step Verification** (enable if not already)
3. Scroll down to **App passwords**: https://myaccount.google.com/apppasswords
4. Create a new app password:
   - App: Select "Mail"
   - Device: Select "Other" and name it "MedBillDozer"
5. Copy the 16-character password (you'll use this in secrets.toml)

### 2. Set Up Google reCAPTCHA v3

1. Go to Google reCAPTCHA admin: https://www.google.com/recaptcha/admin/create
2. Fill in the form:
   - **Label**: MedBillDozer Contact Form
   - **reCAPTCHA type**: Select **reCAPTCHA v3**
   - **Domains**: Add your domains:
     - `localhost` (for local development)
     - `127.0.0.1` (for local development)
     - Your production domain (e.g., `medbilldozer.vercel.app`)
3. Accept the Terms of Service
4. Click **Submit**
5. Copy both:
   - **Site Key** (public key, used in frontend)
   - **Secret Key** (private key, used in backend verification)

### 3. Configure Streamlit Secrets

Edit `.streamlit/secrets.toml` and add your credentials:

```toml
# SMTP Configuration for Email Sending
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "john.g.shultz@gmail.com"
SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"  # Your 16-character Gmail app password

# Google reCAPTCHA v3 Configuration
RECAPTCHA_SITE_KEY = "6Lc..."  # Your site key from reCAPTCHA admin
RECAPTCHA_SECRET_KEY = "6Lc..."  # Your secret key from reCAPTCHA admin
```

**Important**: Never commit `secrets.toml` to version control! It's already in `.gitignore`.

### 4. Alternative: Environment Variables

Instead of `secrets.toml`, you can set environment variables:

```bash
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USERNAME="john.g.shultz@gmail.com"
export SMTP_PASSWORD="your-app-password"
export RECAPTCHA_SITE_KEY="your-site-key"
export RECAPTCHA_SECRET_KEY="your-secret-key"
```

## Testing the Contact Form

### Local Testing

1. Start Streamlit:
   ```bash
   streamlit run medbilldozer_poc.py
   ```

2. Navigate to "Want to Know More" page in the sidebar

3. Fill out and submit the form

4. Check john.g.shultz@gmail.com for the email

### Development Mode

If credentials are not configured, the form will:
- Show a warning about missing SMTP configuration
- Skip reCAPTCHA verification (development mode)
- Still display the form for testing UI/UX

## Email Format

Emails are sent with:
- **From**: Your SMTP username (john.g.shultz@gmail.com)
- **To**: john.g.shultz@gmail.com
- **Reply-To**: The email address entered by the user
- **Subject**: "MedBillDozer Contact Form: [Name]"
- **Body**: HTML formatted with all form fields

## reCAPTCHA v3 Behavior

reCAPTCHA v3:
- Is **invisible** to users (no checkbox or challenge)
- Runs automatically in the background
- Gives a score from 0.0 (bot) to 1.0 (human)
- We accept scores ≥ 0.5
- Does not interrupt user experience

## Troubleshooting

### Email Not Sending

**Error: "Authentication failed"**
- Make sure you're using a Gmail App Password, not your regular password
- Verify 2-Step Verification is enabled on your Google account

**Error: "SMTP connection failed"**
- Check your internet connection
- Verify SMTP_SERVER and SMTP_PORT are correct
- Try port 465 with SSL instead of 587 with TLS

**Error: "Email not configured"**
- Make sure secrets.toml exists in `.streamlit/` directory
- Check that all SMTP variables are set
- Restart Streamlit after changing secrets.toml

### reCAPTCHA Issues

**reCAPTCHA verification failed**
- Verify your site key and secret key are correct
- Check that your domain is registered in reCAPTCHA admin
- Make sure you're using reCAPTCHA v3, not v2

**Score too low (< 0.5)**
- This indicates the submission looks like a bot
- In production, you might want to:
  - Lower the threshold
  - Add additional verification (email confirmation)
  - Manual review queue for low-scoring submissions

## Security Considerations

1. **Never commit secrets**: Keep secrets.toml out of version control
2. **Use App Passwords**: Don't use your main Gmail password
3. **Rate limiting**: Consider adding rate limiting to prevent abuse
4. **Input validation**: The form validates email format and required fields
5. **XSS protection**: Email content is escaped in HTML formatting

## Production Deployment

For production (e.g., Streamlit Cloud, Cloud Run):

1. **Streamlit Cloud**:
   - Add secrets in app settings: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management

2. **Cloud Run / Docker**:
   - Use environment variables
   - Or mount secrets from Google Secret Manager

3. **Vercel** (if using Next.js frontend):
   - Add environment variables in project settings
   - Use API routes to handle form submission server-side

## Quick Start Checklist

- [ ] Enable 2-Step Verification on Google account
- [ ] Create Gmail App Password at https://myaccount.google.com/apppasswords
- [ ] Create reCAPTCHA v3 keys at https://www.google.com/recaptcha/admin/create
- [ ] Add domains to reCAPTCHA: localhost, 127.0.0.1, your production domain
- [ ] Edit `.streamlit/secrets.toml` with your credentials
- [ ] Restart Streamlit
- [ ] Test the contact form
- [ ] Check email at john.g.shultz@gmail.com

## Contact

For questions about this setup, contact john.g.shultz@gmail.com
