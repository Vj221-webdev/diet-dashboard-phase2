# Quick Start Guide - Diet Dashboard Phase 2

## Prerequisites Check
- [ ] Azure account with active subscription
- [ ] Azure CLI installed (`az --version`)
- [ ] Git installed
- [ ] All_Diets.csv file available

## 5-Step Deployment

### Step 1: Prepare Your Files
```bash
# Clone or download the project
cd diet-dashboard-phase2

# Ensure All_Diets.csv is in the project root
ls All_Diets.csv
```

### Step 2: Deploy Azure Resources
```bash
cd deployment
chmod +x deploy.sh
./deploy.sh
```

**This script will:**
- Create Resource Group
- Create Storage Account
- Upload your CSV file
- Create and deploy Azure Function
- Output your Function URL

### Step 3: Update Dashboard Configuration
```bash
cd ../dashboard

# Open app.js and update line 2:
# API_BASE_URL = 'https://YOUR-FUNCTION-APP.azurewebsites.net/api'
```

Replace with your actual Function App URL from Step 2.

### Step 4: Test Your Function
```bash
# Replace with your Function URL
FUNCTION_URL="https://your-function-app.azurewebsites.net/api"

# Test endpoints
curl $FUNCTION_URL/health
curl $FUNCTION_URL/nutritional-insights
curl $FUNCTION_URL/pie-chart-data
```

### Step 5: Deploy Dashboard

**Option A - GitHub Pages (Easiest)**
```bash
# 1. Create GitHub repo
# 2. Push code
git init
git add .
git commit -m "Phase 2 deployment"
git remote add origin YOUR_REPO_URL
git push -u origin main

# 3. Enable GitHub Pages
# Go to repo Settings → Pages → Source: main branch → /dashboard folder
```

**Option B - Azure Static Web Apps**
```bash
# Install SWA CLI
npm install -g @azure/static-web-apps-cli

# Deploy
cd dashboard
swa deploy
```

**Option C - Local Testing**
```bash
cd dashboard
python -m http.server 8000
# Open http://localhost:8000
```

## Testing Checklist

Visit your deployed dashboard and verify:
- [ ] All 4 charts load correctly
- [ ] Diet type filter works
- [ ] API buttons return data
- [ ] Pagination functions
- [ ] No console errors (F12)

## Common Issues & Solutions

**Issue**: "Failed to load data"
- **Fix**: Check if API_BASE_URL is correct in app.js
- **Fix**: Verify Function App is running in Azure Portal

**Issue**: CORS error
- **Fix**: Run: `az functionapp cors add --name YOUR-APP --allowed-origins "*"`

**Issue**: Charts not rendering
- **Fix**: Clear browser cache (Ctrl+Shift+Del)
- **Fix**: Check browser console for JavaScript errors

## Deliverables for Submission

1. **Azure Function URL**: `https://YOUR-APP.azurewebsites.net/api`
2. **Dashboard URL**: Your deployed dashboard link
3. **GitHub Repo**: Link to your repository
4. **Documentation PDF**: docs/Project_Phase2_Documentation.pdf

## Getting Help

If stuck, check:
1. Azure Portal → Function App → Logs
2. Browser Console (F12) for JavaScript errors
3. README.md for detailed instructions
4. Azure Function responses: add `?debug=true` to URLs

## Estimated Time
- Resource deployment: 10-15 minutes
- Dashboard deployment: 5-10 minutes
- Testing: 10 minutes
- **Total: 25-35 minutes**

Good luck! 🚀
