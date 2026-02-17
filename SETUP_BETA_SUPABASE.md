# 🚀 Using Beta Supabase Configuration

Your beta Supabase credentials are already configured in `.zprofile`. Here's how to use them with the FastAPI backend.

---

## ✅ What's Already Set Up

Your `.zprofile` has:
```bash
export SUPABASE_BETA_URL="https://zrhlpitzonhftigmdvgz.supabase.co"
export SUPABASE_BETA_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpyaGxwaXR6b25oZnRpZ21kdmd6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTAxMjc1MywiZXhwIjoyMDg2NTg4NzUzfQ.QzuezQ-nFgdxc9p1p5S4TYrCvo09KHBGFu6JiQ6o8DE"
```

The backend is now configured to automatically use these beta credentials!

---

## 🔧 How It Works

The backend configuration (`backend/app/config.py`) now checks for environment variables in this order:

1. **First priority:** `SUPABASE_BETA_URL` and `SUPABASE_BETA_KEY` (from `.zprofile`)
2. **Fallback:** `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` (from `.env`)

This means:
- ✅ Your beta credentials are automatically used when available
- ✅ No need to edit `.env` files
- ✅ Works seamlessly with your existing shell configuration

---

## 🧪 Quick Start

```bash
# 1. Load your environment
source ~/.zprofile

# 2. Test connection
cd backend
python test_supabase_connection.py

# 3. Start backend
uvicorn app.main:app --reload --port 8080
```

That's it! Your backend now uses beta Supabase automatically.

---

## 📋 Full Setup Guide

### Step 1: Verify Environment Variables

```bash
source ~/.zprofile
echo $SUPABASE_BETA_URL
# Should show: https://zrhlpitzonhftigmdvgz.supabase.co
```

### Step 2: Check if Schema Exists

```bash
cd backend
python test_supabase_connection.py
```

If tables don't exist, create them:

1. Go to: https://supabase.com/dashboard/project/zrhlpitzonhftigmdvgz
2. Click "SQL Editor" → "New query"
3. Copy contents of `sql/schema_production_api.sql`
4. Paste and click "Run"

### Step 3: Run Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

Test: `curl http://localhost:8080/health`

---

## ✅ You're Done!

Your backend now automatically uses beta Supabase credentials from `.zprofile`. No `.env` editing needed!
