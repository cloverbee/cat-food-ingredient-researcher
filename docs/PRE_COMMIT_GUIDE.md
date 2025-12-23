# Pre-commit Hooks Setup Guide

This project uses [pre-commit](https://pre-commit.com/) to automatically run code quality checks before each commit.

## 🎯 What Gets Checked

Pre-commit automatically runs these checks before every commit:

1. **Code Formatting**
   - ✨ **Black** - Formats Python code
   - 📦 **isort** - Organizes imports

2. **Code Quality**
   - 🔍 **Flake8** - Linting (with relaxed rules)
   - 🐛 **flake8-bugbear** - Finds likely bugs
   - 🔧 **flake8-comprehensions** - Better comprehensions
   - 🚀 **flake8-simplify** - Suggests simplifications

3. **File Checks**
   - ✂️ Trailing whitespace removal
   - 📄 End-of-file fixer
   - 🔀 Merge conflict detection
   - 🐍 Debug statement detection
   - 📦 Large file prevention

4. **Security**
   - 🔒 **detect-secrets** - Prevents committing API keys/passwords

## 🚀 Installation

### 1. Install Dependencies

```bash
# Install all dependencies including pre-commit
pip install -r requirements.txt
```

### 2. Install Pre-commit Hooks

```bash
# Install the git hooks
pre-commit install

# This creates .git/hooks/pre-commit
```

That's it! Pre-commit will now run automatically on `git commit`.

## 📝 Usage

### Automatic (Recommended)

Just commit normally. Pre-commit runs automatically:

```bash
git add .
git commit -m "Your commit message"
# Pre-commit hooks run automatically!
```

**What happens:**
- If all checks pass ✅ → Commit succeeds
- If auto-fixable issues exist 🔧 → Files are fixed, commit is aborted (stage fixes and commit again)
- If manual fixes needed ❌ → Commit is aborted, you fix issues, then commit again

### Manual Run

Run checks on all files without committing:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run

# Run specific hook
pre-commit run black --all-files
pre-commit run flake8 --all-files
```

### Skip Hooks (Not Recommended)

If you really need to skip hooks:

```bash
git commit -m "message" --no-verify
```

⚠️ **Warning:** Only skip if absolutely necessary!

## 🔧 Configuration

### Main Config: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
        args: ["--line-length", "120"]
```

### Hook-Specific Configs

- **Black**: `pyproject.toml`
- **Flake8**: `.flake8`
- **isort**: `.isort.cfg`
- **detect-secrets**: `.secrets.baseline`

## 🛠️ Common Workflows

### First Time Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install pre-commit hooks
pre-commit install

# 3. Run on all existing files (optional, will format everything)
pre-commit run --all-files

# 4. Commit the formatted files
git add .
git commit -m "chore: apply code formatting"
```

### Daily Development

```bash
# Make changes
vim src/api/main.py

# Stage changes
git add src/api/main.py

# Commit (hooks run automatically)
git commit -m "feat: add new endpoint"

# If hooks fail:
# - Review the output
# - Auto-fixed files are already modified
# - Stage the fixes and commit again
git add .
git commit -m "feat: add new endpoint"
```

### Update Hooks

```bash
# Update to latest versions
pre-commit autoupdate

# Then commit the updated config
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```

## 🔍 Hook Details

### Black (Code Formatter)

**What it does:**
- Formats code to consistent style
- Line length: 120 characters
- Automatic, no configuration needed

**Example output:**
```
black....................................................................Passed
```

### isort (Import Organizer)

**What it does:**
- Groups and sorts imports
- Sections: stdlib → third-party → first-party → local
- Black-compatible

**Example output:**
```
isort....................................................................Passed
```

### Flake8 (Linter)

**What it does:**
- Checks for errors and style issues
- Relaxed rules (max line: 120, complexity: 15)
- Won't auto-fix (manual changes needed)

**Example output:**
```
flake8...................................................................Passed
```

**If it fails:**
```
flake8...................................................................Failed
- hook id: flake8
- exit code: 1

src/api/main.py:10:1: F401 'sys' imported but unused
```

### detect-secrets (Security)

**What it does:**
- Scans for API keys, passwords, tokens
- Prevents accidental secret commits
- Uses `.secrets.baseline` for known false positives

**If it fails:**
```
detect-secrets...........................................................Failed
Potential secret found in src/config.py
```

**To update baseline:**
```bash
detect-secrets scan > .secrets.baseline
```

## ⚡ Performance

Pre-commit is fast because it:
- Only checks staged files (not all files)
- Runs hooks in parallel
- Caches results

Typical run time: **2-5 seconds**

## 🚫 Excluding Files

### Temporarily exclude a file:

```bash
# Add to commit without hooks
git commit --no-verify
```

### Permanently exclude files/directories:

Edit `.pre-commit-config.yaml`:

```yaml
exclude: |
  (?x)^(
      your_file\.py|
      your_directory/.*
  )$
```

Or per-hook:

```yaml
- repo: https://github.com/psf/black
  hooks:
    - id: black
      exclude: ^migrations/
```

## 🐛 Troubleshooting

### Hooks not running?

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Check installation
pre-commit --version
```

### Hook fails with error?

```bash
# Clean pre-commit cache
pre-commit clean

# Run again
pre-commit run --all-files
```

### Want to skip a hook temporarily?

Set environment variable:

```bash
SKIP=flake8 git commit -m "message"
```

### Python version mismatch?

Edit `.pre-commit-config.yaml`:

```yaml
default_language_version:
  python: python3.11  # Change to your version
```

## 📚 Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [detect-secrets](https://github.com/Yelp/detect-secrets)

## ✅ Benefits

- ✨ Consistent code style across team
- 🐛 Catch errors before they reach CI
- 🚀 Faster code reviews (no style debates)
- 🔒 Prevent security issues (leaked secrets)
- ⚡ Fast feedback loop (2-5 seconds)
- 🎯 Focus on logic, not formatting

## 🆘 Getting Help

If hooks are blocking you:

1. **Read the error message** - it usually tells you what's wrong
2. **Run manually** - `pre-commit run --all-files` to see all issues
3. **Skip if urgent** - `git commit --no-verify` (but fix later!)
4. **Ask the team** - Someone might have seen the issue before

---

**Last Updated:** December 8, 2025
