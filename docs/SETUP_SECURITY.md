# 🔒 Security Setup Guide

## Quick Start for Development

### 1. Set Up Environment Variables

```bash
# Copy the development template
cp .env.development .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Minimum required changes in `.env`:**
```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 2. Generate a Secure Secret Key (Recommended)

```bash
# Option 1: Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Option 2: Using OpenSSL
openssl rand -hex 32
```

Copy the output and update `SECRET_KEY` in your `.env` file.

### 3. Start the Application

```bash
# Start database and vector store
docker-compose up -d

# Run migrations
alembic upgrade head

# Start the backend
uvicorn src.api.main:app --reload

# In another terminal, start the frontend
cd frontend
npm install
npm run dev
```

---

## 🚨 Important Security Notes

### What Changed?

We've removed all hard-coded secrets from the codebase. The application **will now fail to start** if required environment variables are not set. This is intentional - it's better to fail fast than run with insecure defaults.

### Required Environment Variables

| Variable | Required For | Where to Get |
|----------|--------------|--------------|
| `GEMINI_API_KEY` | AI features | https://makersuite.google.com/app/apikey |
| `SECRET_KEY` | Authentication | Generate with `openssl rand -hex 32` |
| `POSTGRES_PASSWORD` | Database | Use a strong password |

### Files You Need to Know About

- `.env.example` - Template with all available variables (committed to git)
- `.env.development` - Development defaults (committed to git)
- `.env` - Your personal config **NEVER commit this!** (gitignored)

---

## 🔐 Production Deployment

For production, follow these steps:

1. **Create production environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Set strong, unique values for:**
   - `POSTGRES_PASSWORD` - Database password (use a password manager)
   - `SECRET_KEY` - JWT signing key (generate with `openssl rand -hex 32`)
   - `GEMINI_API_KEY` - Your production API key
   - `ENVIRONMENT=production`

3. **Use a secrets manager:**
   - AWS: AWS Secrets Manager
   - Google Cloud: Secret Manager
   - Azure: Key Vault
   - Self-hosted: HashiCorp Vault

4. **Never commit .env files to version control!**

---

## ✅ Verification Checklist

After setup, verify your configuration:

- [ ] `.env` file exists and contains your API keys
- [ ] `.env` is listed when you run `git status` (it should NOT appear)
- [ ] Application starts without errors
- [ ] No secrets in `src/core/config.py` (check with `grep -i "sk-\|AIza" src/`)

---

## 🆘 Troubleshooting

### "Field required" error on startup

This means a required environment variable is missing. Check that your `.env` file contains:
- `GEMINI_API_KEY`
- `SECRET_KEY`
- `POSTGRES_PASSWORD`

### "Config loads successfully" test fails

1. Make sure you have a `.env` file (copy from `.env.development`)
2. Check that all required variables are set
3. Verify the file is in the project root directory

### Docker container fails to start

Check that your `.env` file has the database credentials:
```bash
POSTGRES_PASSWORD=your_password_here
```

---

## 📚 More Information

For detailed security information, see [SECURITY.md](./SECURITY.md)

For general project setup, see [README.md](./README.md)
