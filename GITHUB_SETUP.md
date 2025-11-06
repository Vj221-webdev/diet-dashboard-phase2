# GitHub Repository Setup Guide

## Step-by-Step Instructions

### Option 1: Using GitHub Desktop (Easiest)

1. **Download GitHub Desktop**
   - Visit: https://desktop.github.com/
   - Install and sign in with your GitHub account

2. **Create New Repository**
   - Click "Create a New Repository on your hard drive"
   - Name: `diet-dashboard-phase2`
   - Local Path: Choose where you want the project
   - Click "Create Repository"

3. **Add Your Files**
   - Copy all project files into the repository folder
   - GitHub Desktop will automatically detect changes

4. **Commit Changes**
   - Write commit message: "Initial commit - Phase 2 implementation"
   - Click "Commit to main"

5. **Publish to GitHub**
   - Click "Publish repository"
   - Uncheck "Keep this code private" (for coursework)
   - Click "Publish repository"

---

### Option 2: Using Command Line

1. **Navigate to Project Directory**
   ```bash
   cd diet-dashboard-phase2
   ```

2. **Initialize Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Phase 2 implementation"
   ```

3. **Create GitHub Repository**
   - Go to https://github.com/new
   - Repository name: `diet-dashboard-phase2`
   - Description: "Cloud-based Nutritional Insights Dashboard - Phase 2"
   - Public repository
   - Don't initialize with README (we already have one)
   - Click "Create repository"

4. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/diet-dashboard-phase2.git
   git branch -M main
   git push -u origin main
   ```

---

### Option 3: Using VS Code

1. **Open Project in VS Code**
   ```bash
   code diet-dashboard-phase2
   ```

2. **Initialize Repository**
   - Click Source Control icon (left sidebar)
   - Click "Initialize Repository"
   - Stage all changes (+ icon)
   - Write commit message
   - Click ✓ to commit

3. **Publish to GitHub**
   - Click "Publish to GitHub" button
   - Choose repository name
   - Select "Public"
   - Click "Publish"

---

## Adding Your Dataset

The All_Diets.csv file is large (~2MB). You have two options:

### Option A: Include in Repository (Recommended)
```bash
git add All_Diets.csv
git commit -m "Add All_Diets dataset"
git push
```

### Option B: Use Git LFS (For Large Files)
```bash
# Install Git LFS
git lfs install

# Track CSV files
git lfs track "*.csv"
git add .gitattributes

# Add and commit
git add All_Diets.csv
git commit -m "Add dataset via Git LFS"
git push
```

---

## Repository Structure

Your GitHub repository should look like this:

```
diet-dashboard-phase2/
├── README.md                    ← Project overview
├── QUICKSTART.md               ← Quick start guide
├── TESTING.md                  ← Testing instructions
├── .gitignore                  ← Git ignore rules
├── All_Diets.csv              ← Dataset (optional)
├── azure-function/
│   ├── function_app.py        ← Azure Function code
│   ├── requirements.txt
│   ├── host.json
│   └── local.settings.json    ← (ignored by git)
├── dashboard/
│   ├── index.html             ← Dashboard UI
│   ├── styles.css
│   └── app.js
├── deployment/
│   ├── deploy.sh              ← Deployment script
│   └── deployment-info.txt    ← (ignored by git)
└── docs/
    └── Project_Phase2_Documentation.pdf
```

---

## Creating a Great README

Your README.md should include:

1. **Project Title and Description**
2. **Live Demo Links**
   - Azure Function URL
   - Dashboard URL
3. **Screenshots**
   - Dashboard with charts
   - Azure resources
4. **Technologies Used**
5. **Setup Instructions**
6. **Testing Instructions**
7. **Project Structure**
8. **Author Information**

Example:

````markdown
# Nutritional Insights Dashboard - Phase 2

Cloud-based data visualization dashboard analyzing 7,806 recipes across 5 diet types.

## 🚀 Live Demo

- **Dashboard**: [https://your-dashboard.azurestaticapps.net](https://your-dashboard.azurestaticapps.net)
- **API**: [https://your-function-app.azurewebsites.net/api](https://your-function-app.azurewebsites.net/api)

## 📊 Screenshots

![Dashboard](screenshots/dashboard.png)

## 🛠 Technologies

- **Backend**: Azure Functions (Python 3.9)
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Storage**: Azure Blob Storage
- **Deployment**: Azure Static Web Apps

## 📚 Documentation

See [README.md](README.md) for full documentation.

## 👨‍💻 Author

Vijay - SAIT Student
````

---

## Adding Screenshots

1. **Create screenshots folder**
   ```bash
   mkdir screenshots
   ```

2. **Capture and add screenshots**
   - Dashboard with all charts
   - Azure Portal resources
   - API responses

3. **Add to repository**
   ```bash
   git add screenshots/
   git commit -m "Add project screenshots"
   git push
   ```

---

## Updating README with Your URLs

After deployment, update README.md:

```markdown
## 🔗 Deployed Links

- **Azure Function API**: https://diet-function-app-123456.azurewebsites.net/api
- **Dashboard**: https://diet-dashboard-123456.azurestaticapps.net
- **GitHub Repository**: https://github.com/YOUR-USERNAME/diet-dashboard-phase2
```

---

## Creating Releases (Optional)

1. **Create a tag**
   ```bash
   git tag -a v1.0 -m "Phase 2 - Final Submission"
   git push origin v1.0
   ```

2. **Create GitHub Release**
   - Go to repository → Releases → Create new release
   - Tag: v1.0
   - Title: "Phase 2 - Cloud Dashboard"
   - Description: Project summary
   - Attach documentation PDF
   - Click "Publish release"

---

## GitHub Pages Deployment

If using GitHub Pages for dashboard:

1. **Enable GitHub Pages**
   - Repository Settings → Pages
   - Source: main branch
   - Folder: `/dashboard`
   - Click Save

2. **Update API URL**
   ```javascript
   // In dashboard/app.js
   let API_BASE_URL = 'https://your-function-app.azurewebsites.net/api';
   ```

3. **Access Dashboard**
   - URL: `https://YOUR-USERNAME.github.io/diet-dashboard-phase2/`

---

## Common Issues

**Issue**: Push rejected
```bash
# Solution: Pull first
git pull origin main --rebase
git push
```

**Issue**: File too large
```bash
# Solution: Use Git LFS
git lfs install
git lfs track "*.csv"
```

**Issue**: Permission denied
```bash
# Solution: Use HTTPS or setup SSH keys
# HTTPS:
git remote set-url origin https://github.com/USERNAME/REPO.git

# SSH:
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add key to GitHub: Settings → SSH Keys
```

---

## Best Practices

✅ **DO:**
- Write clear commit messages
- Commit frequently with logical changes
- Include comprehensive README
- Add screenshots and documentation
- Test everything before final push

❌ **DON'T:**
- Commit sensitive data (API keys, passwords)
- Commit large binary files without Git LFS
- Use generic commit messages ("updated files")
- Forget to update README with live URLs

---

## Submission Checklist

Before submitting your GitHub repository:

- [ ] All code is pushed to main branch
- [ ] README.md includes live demo URLs
- [ ] Screenshots are added and visible
- [ ] Documentation PDF is included
- [ ] .gitignore prevents sensitive files
- [ ] Repository is public (for grading)
- [ ] All links work and are accessible
- [ ] Code is well-organized and commented

---

## Getting Help

- **GitHub Docs**: https://docs.github.com
- **Git Basics**: https://git-scm.com/doc
- **Markdown Guide**: https://www.markdownguide.org

Good luck with your submission! 🎉
