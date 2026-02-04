# Deploying Benchmark Monitoring Dashboard to Streamlit Cloud

## Prerequisites

✅ **Supabase added to requirements.txt** (completed)  
✅ **Dashboard code ready** at `pages/benchmark_monitoring.py`  
✅ **GitHub repo pushed** with all changes

## Step 1: Push Changes to GitHub

```bash
# Add the requirements change
git add requirements.txt

# Commit
git commit -m "Add supabase to requirements for monitoring dashboard"

# Push to GitHub
git push origin develop
```

## Step 2: Deploy to Streamlit Cloud

### Option A: Deploy Dashboard as Main App

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Configure:
   - **Repository**: `boobootoo2/medbilldozer`
   - **Branch**: `develop`
   - **Main file path**: `pages/benchmark_monitoring.py`
   - **App URL**: Choose a custom URL like `medbilldozer-monitoring`

4. Click **"Advanced settings"**
5. Add **Secrets** (see Step 3 below)
6. Click **"Deploy!"**

### Option B: Deploy as Multi-Page App

1. Keep your main app as is
2. The `pages/` folder will automatically create additional pages
3. Deploy the main `app.py`
4. The monitoring dashboard will appear as a separate page in the sidebar

## Step 3: Configure Secrets

In Streamlit Cloud, add these secrets:

```toml
# .streamlit/secrets.toml format

# Supabase Configuration
SUPABASE_URL = "https://azoxzggvqhkugyysbabz.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF6b3h6Z2d2cWhrdWd5eXNiYWJ6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDE1MDAyOSwiZXhwIjoyMDg1NzI2MDI5fQ.Gheha952qfiMo_UV1DLUXaNwOJ5S_t-F_Q6c03f2-_o"

# Optional: Environment indicator
ENVIRONMENT = "production"
```

**⚠️ Important**: Use the **SERVICE_ROLE_KEY**, not the ANON key, for full database access.

### How to Add Secrets:

1. In Streamlit Cloud dashboard, click your app
2. Click **"⚙️ Settings"**
3. Click **"Secrets"** tab
4. Paste the TOML content above
5. Click **"Save"**

## Step 4: Verify Deployment

Once deployed, you'll get a URL like:
- `https://medbilldozer-monitoring.streamlit.app`

Check that:
- ✅ Dashboard loads without errors
- ✅ Data displays from Supabase
- ✅ All 5 tabs are accessible
- ✅ Snapshot history works

## Troubleshooting

### Error: "supabase module not found"

**Solution**: Make sure `requirements.txt` has `supabase==2.3.0` and redeploy.

```bash
# Check it's there
grep supabase requirements.txt

# If not, add it
echo "supabase==2.3.0" >> requirements.txt
git add requirements.txt
git commit -m "Add supabase dependency"
git push
```

### Error: "Failed to connect to database"

**Solution**: Check secrets are configured correctly in Streamlit Cloud:
1. Go to app settings
2. Click "Secrets" tab
3. Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
4. Make sure there are no extra quotes or spaces

### Error: "name 'create_client' is not defined"

**Solution**: This means the supabase package didn't install. Check:
1. `requirements.txt` has `supabase==2.3.0`
2. Restart the app in Streamlit Cloud
3. Check deployment logs for installation errors

### Dashboard Shows No Data

**Solution**: 
1. Verify Supabase credentials in secrets
2. Check Supabase is accessible (not restricted by IP)
3. Verify database has data: run `python3 scripts/check_snapshots.py` locally

## Local Testing with Cloud Secrets

To test locally with the same setup as Streamlit Cloud:

1. Create `.streamlit/secrets.toml` (this file is gitignored):

```toml
SUPABASE_URL = "https://azoxzggvqhkugyysbabz.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "your_key_here"
```

2. Access in code via `st.secrets`:

```python
url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
key = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
```

## Updating the Dashboard

When you push changes to GitHub:

1. Streamlit Cloud auto-detects the push
2. Automatically rebuilds and redeploys
3. Changes go live within 1-2 minutes

```bash
# Make changes
git add pages/benchmark_monitoring.py
git commit -m "Update dashboard UI"
git push

# Streamlit Cloud automatically redeploys!
```

## Multiple Environments

### Production Dashboard

- **Branch**: `main`
- **URL**: `medbilldozer-monitoring.streamlit.app`
- **Secrets**: Production Supabase credentials

### Staging Dashboard

- **Branch**: `develop`
- **URL**: `medbilldozer-monitoring-staging.streamlit.app`
- **Secrets**: Staging/Dev Supabase credentials

Deploy both to test changes before production!

## Monitoring Dashboard URLs

Once deployed, you can access:

- **Production**: `https://your-app.streamlit.app`
- **Direct Link**: Share with your team
- **Embed**: Use iframe to embed in other dashboards

## Security Best Practices

1. ✅ **Never commit secrets** to GitHub
2. ✅ **Use SERVICE_ROLE_KEY** for full database access
3. ✅ **Restrict Supabase RLS** if needed for production
4. ✅ **Enable Supabase auth** for production deployments
5. ✅ **Monitor usage** via Supabase dashboard

## Next Steps

After deployment:

1. **Share the URL** with your team
2. **Set up alerts** for regressions
3. **Automate benchmarks** via GitHub Actions
4. **Create baselines** for comparison
5. **Monitor costs** in Supabase dashboard

---

## Quick Deployment Checklist

- [ ] `supabase==2.3.0` in `requirements.txt`
- [ ] Changes pushed to GitHub
- [ ] Streamlit Cloud app created
- [ ] Secrets configured (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
- [ ] App deployed successfully
- [ ] Dashboard loads and shows data
- [ ] All 5 tabs working
- [ ] Snapshot history functional
- [ ] URL shared with team

---

**Dashboard Status**: ✅ Ready for Streamlit Cloud  
**Last Updated**: 2026-02-03  
**Local URL**: http://localhost:8502  
**Deployment Target**: Streamlit Cloud
