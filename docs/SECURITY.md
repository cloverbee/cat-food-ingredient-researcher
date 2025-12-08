# Security Configuration Guide

## 🔒 Security Improvements Implemented

This document describes the security improvements made to the Cat Food Ingredient Researcher project.

### ✅ What Was Fixed

#### 1. **Removed Hard-Coded Secrets**
**CRITICAL ISSUES FOUND AND FIXED:**
- ❌ Hard-coded OpenAI API key in `src/core/config.py` (REMOVED)
- ❌ Hard-coded Gemini API key in `src/core/config.py` (REMOVED)
- ❌ Weak default passwords and secret keys with fallback values (REMOVED)
- ❌ Database credentials hard-coded in `docker-compose.yml` (REMOVED)

#### 2. **Improved Pydantic Settings Implementation**
- ✅ Now using `pydantic-settings` v2.x with proper configuration
- ✅ Using `Field()` with `...` (Ellipsis) to mark required environment variables
- ✅ Using `@computed_field` for derived values (DATABASE_URL)
- ✅ Removed manual `os.getenv()` calls in favor of Pydantic's built-in env loading
- ✅ No longer manually calling `load_dotenv()` (Pydantic handles this)
- ✅ Added `SettingsConfigDict` for better configuration management

#### 3. **Environment Variable Management**
- ✅ Created `.env.example` - Template file with all required variables
- ✅ Created `.env.development` - Safe defaults for local development
- ✅ Updated `.gitignore` to exclude all `.env*` files except `.env.example`
- ✅ Updated `docker-compose.yml` to use environment variables

---

## 🚀 Setup Instructions

### For Development

1. **Copy the development environment file:**
   ```bash
   cp .env.development .env
   ```

2. **Add your API keys:**
   Edit `.env` and add your actual API keys:
   ```bash
   GEMINI_API_KEY=your_actual_gemini_key_here
   # OPENAI_API_KEY=your_openai_key_here  # Optional
   ```

3. **Generate a secure SECRET_KEY (recommended even for dev):**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   # Or use openssl:
   openssl rand -hex 32
   ```
   Update the `SECRET_KEY` in your `.env` file.

4. **Start the services:**
   ```bash
   docker-compose up -d
   ```

### For Production

1. **Create your production .env file:**
   ```bash
   cp .env.example .env
   ```

2. **Set ALL required environment variables:**
   - `POSTGRES_PASSWORD` - Use a strong, unique password
   - `SECRET_KEY` - Generate with `openssl rand -hex 32`
   - `GEMINI_API_KEY` - Your production Gemini API key
   - Review and update all other values as needed

3. **NEVER commit the .env file to git!**
   The `.gitignore` file already excludes it, but double-check.

---

## 🔐 Required Environment Variables

### Critical (Must Set for Production)

| Variable | Description | How to Generate |
|----------|-------------|-----------------|
| `POSTGRES_PASSWORD` | Database password | Use a password manager or `openssl rand -base64 32` |
| `SECRET_KEY` | JWT signing key | `openssl rand -hex 32` or `python -c "import secrets; print(secrets.token_hex(32))"` |
| `GEMINI_API_KEY` | Google Gemini API key | Get from https://makersuite.google.com/app/apikey |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (if using OpenAI) | None |
| `ENVIRONMENT` | Runtime environment | `development` |
| `POSTGRES_SERVER` | Database host | `localhost` |
| `POSTGRES_USER` | Database username | `postgres` |
| `POSTGRES_DB` | Database name | `cat_food_research` |
| `POSTGRES_PORT` | Database port | `5433` |
| `QDRANT_HOST` | Vector DB host | `localhost` |
| `QDRANT_PORT` | Vector DB port | `6333` |

---

## 🛡️ Security Best Practices

### ✅ DO:
- ✅ Use strong, unique passwords for production databases
- ✅ Rotate API keys regularly
- ✅ Use different secrets for different environments
- ✅ Store production secrets in a secure secret manager (AWS Secrets Manager, Azure Key Vault, etc.)
- ✅ Limit API key permissions to only what's needed
- ✅ Monitor API key usage for unusual activity
- ✅ Use environment-specific `.env` files (never commit them)

### ❌ DON'T:
- ❌ NEVER commit `.env` files to version control
- ❌ NEVER share API keys in chat, email, or documentation
- ❌ NEVER use development secrets in production
- ❌ NEVER hard-code secrets in source code
- ❌ NEVER use default/example passwords in production

---

## 🔍 Verification

To verify your configuration is secure:

1. **Check for hard-coded secrets:**
   ```bash
   # This should return no results:
   grep -r "sk-proj-\|AIza" src/
   ```

2. **Verify .env is gitignored:**
   ```bash
   git check-ignore .env
   # Should output: .env
   ```

3. **Test configuration loading:**
   ```bash
   python -c "from src.core.config import settings; print('Config loaded successfully')"
   ```

---

## 🚨 What To Do If Secrets Were Exposed

If you accidentally committed secrets to git:

1. **Immediately rotate the exposed credentials:**
   - Revoke the API key from the provider's dashboard
   - Generate a new key
   - Update your `.env` file

2. **Remove from git history (if needed):**
   ```bash
   # Use git-filter-repo or BFG Repo-Cleaner
   # Contact your security team for guidance
   ```

3. **Force push the cleaned history (coordinate with team):**
   ```bash
   git push --force
   ```

4. **Notify your team and security officer**

---

## 📋 Migration Notes

### Changes Made to Code

1. **`src/core/config.py`**
   - Removed all hard-coded API keys and secrets
   - Migrated from manual `os.getenv()` to Pydantic Settings v2
   - Made sensitive fields required (will fail on startup if not set)
   - Added field descriptions and validation

2. **`docker-compose.yml`**
   - Changed hard-coded values to use environment variables
   - Added default fallbacks for non-sensitive values
   - Made `POSTGRES_PASSWORD` required (will error if not set)

3. **`.gitignore`**
   - Enhanced to exclude all environment files and sensitive data
   - Added comprehensive Python, Node.js, and IDE patterns

### Breaking Changes

⚠️ **The application will now FAIL to start if required environment variables are not set.**

This is intentional and by design - it's better to fail fast than run with insecure defaults.

Required variables:
- `POSTGRES_PASSWORD`
- `SECRET_KEY`
- `GEMINI_API_KEY`

---

## 📚 Additional Resources

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_CheatSheet.html)
- [12 Factor App - Config](https://12factor.net/config)
- [Google Cloud Secret Manager](https://cloud.google.com/secret-manager)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)

---

## 📞 Questions?

If you have questions about the security configuration, please contact the development team or security officer.

**Last Updated:** December 8, 2025

