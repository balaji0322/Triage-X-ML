# 🚀 GitHub Setup Guide

Step-by-step instructions to push this project to GitHub.

---

## 📋 Prerequisites

1. **Git installed**: Check with `git --version`
2. **GitHub account**: Sign up at https://github.com
3. **GitHub CLI (optional)**: Install from https://cli.github.com/

---

## 🔧 Method 1: Using GitHub CLI (Recommended)

### Step 1: Install GitHub CLI

**Windows**:
```bash
winget install --id GitHub.cli
```

**Mac**:
```bash
brew install gh
```

**Linux**:
```bash
sudo apt install gh  # Debian/Ubuntu
```

### Step 2: Authenticate

```bash
gh auth login
```

Follow the prompts to authenticate with your GitHub account.

### Step 3: Create Repository and Push

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Triage-X ML system with FastAPI and React"

# Create GitHub repository and push
gh repo create triage-x --public --source=. --remote=origin --push
```

**Done!** Your repository is now on GitHub.

---

## 🔧 Method 2: Using GitHub Web Interface

### Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `triage-x`
3. Description: `AI-powered patient triage system with XGBoost, FastAPI, and React`
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

### Step 2: Initialize Local Repository

```bash
# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Triage-X ML system with FastAPI and React"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/triage-x.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 📝 Recommended Commit Message

```
Initial commit: Triage-X ML system with FastAPI and React

Features:
- XGBoost classifier with 98% accuracy
- FastAPI backend with 4 endpoints (predict, feature_importance, explain, ping)
- React frontend with toast notifications
- SHAP explanations for model interpretability
- Environment-aware logging (dev/prod/test)
- Docker support with docker-compose
- Comprehensive documentation

Tech Stack:
- Backend: Python 3.10+, FastAPI, XGBoost, SHAP, Loguru
- Frontend: React 18, Axios, React-Toastify
- ML: XGBoost, Scikit-learn, Pandas, NumPy
- Deployment: Docker, Docker Compose
```

---

## 🏷️ Adding Topics/Tags

After creating the repository, add these topics for better discoverability:

1. Go to your repository on GitHub
2. Click the gear icon next to "About"
3. Add topics:
   - `machine-learning`
   - `healthcare`
   - `triage`
   - `xgboost`
   - `fastapi`
   - `react`
   - `python`
   - `javascript`
   - `docker`
   - `shap`
   - `explainable-ai`
   - `medical-ai`

---

## 📊 Repository Settings (Optional)

### Enable GitHub Pages (for documentation)

1. Go to **Settings** → **Pages**
2. Source: Deploy from a branch
3. Branch: `main` → `/docs` (if you have docs folder)
4. Click **Save**

### Add Repository Description

1. Go to repository main page
2. Click gear icon next to "About"
3. Description: `AI-powered patient triage system with XGBoost, FastAPI, and React`
4. Website: (your deployment URL if available)
5. Check: ✅ Releases, ✅ Packages

### Protect Main Branch

1. Go to **Settings** → **Branches**
2. Add rule for `main` branch
3. Enable:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging

---

## 🔄 Future Updates

### Making Changes

```bash
# Make your changes to files

# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add feature: SHAP visualization component"

# Push to GitHub
git push origin main
```

### Creating a New Branch

```bash
# Create and switch to new branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push branch to GitHub
git push origin feature/new-feature

# Create pull request on GitHub
```

---

## 📦 Creating Releases

### Using GitHub CLI

```bash
# Create a release
gh release create v1.0.0 --title "v1.0.0 - Initial Release" --notes "First stable release"
```

### Using GitHub Web Interface

1. Go to **Releases** → **Create a new release**
2. Tag version: `v1.0.0`
3. Release title: `v1.0.0 - Initial Release`
4. Description: Add release notes
5. Click **Publish release**

---

## 🔍 Verify Repository

After pushing, verify:

- ✅ All files are present
- ✅ README.md displays correctly
- ✅ .gitignore is working (no `node_modules/`, `__pycache__/`, etc.)
- ✅ LICENSE file is present
- ✅ Documentation files are readable

---

## 🐛 Troubleshooting

### Large Files Error

If you get an error about large files:

```bash
# Check file sizes
find . -type f -size +50M

# Remove large files from git
git rm --cached path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Commit and push
git commit -m "Remove large files"
git push origin main
```

### Authentication Issues

```bash
# Use personal access token instead of password
# Generate token at: https://github.com/settings/tokens

# Or use SSH
git remote set-url origin git@github.com:YOUR_USERNAME/triage-x.git
```

### Undo Last Commit (before push)

```bash
git reset --soft HEAD~1
```

---

## 📚 Additional Resources

- **GitHub Docs**: https://docs.github.com/
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf
- **GitHub CLI Manual**: https://cli.github.com/manual/

---

## ✅ Quick Checklist

Before pushing to GitHub:

- [ ] Remove sensitive data (API keys, passwords, etc.)
- [ ] Update README.md with your information
- [ ] Add LICENSE file
- [ ] Create .gitignore file
- [ ] Test that the application works
- [ ] Run backend tests (`python backend/test_backend_complete.py`)
- [ ] Check for large files (>50MB)
- [ ] Update contact information in README
- [ ] Add meaningful commit messages

---

**Ready to share your project with the world!** 🎉

For questions or issues, refer to [GitHub Support](https://support.github.com/).
