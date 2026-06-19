# Render Deployment Configuration

## Runtime

Python 3

---

## Branch

main

---

## Build Command

pip install -r requirements.txt

---

## Start Command

gunicorn run:app

---

## Environment Variables

### DATABASE_URL

Key:
DATABASE_URL

Value:
postgresql://postgres.xxxxx:your_password@aws-1-ap-south-1.pooler.supabase.com:5432/postgres?sslmode=require

---

### SECRET_KEY

Key:
SECRET_KEY

Value:
9fA3xP@7Rk!2DqM8#ZbLw4^sC0N%YVJH

---

### FLASK_ENV

Key:
FLASK_ENV

Value:
production

---

### PORT (Optional)

Key:
PORT

Value:
10000

---

## Deployment Flow

1. Push code to GitHub main branch.
2. Create Supabase project.
3. Copy Supabase DATABASE_URL.
4. Create Render Web Service.
5. Connect GitHub repository.
6. Select main branch.
7. Configure Build Command.
8. Configure Start Command.
9. Add Environment Variables.
10. Deploy Service.
11. Monitor Render Logs.
12. Verify Health Endpoint.
13. Test Registration Flow.
14. Test Login Flow.
15. Test Profile Page.
16. Test Logout Flow.

---

## Local Migration To Supabase

pip install psycopg2-binary

pip freeze > requirements.txt

PowerShell:

$env:DATABASE_URL="YOUR_SUPABASE_DATABASE_URL"

flask db upgrade

Remove-Item Env:DATABASE_URL

---

## Health Check

URL:

https://your-render-service.onrender.com/health

Expected Response:

{
"status": "UP",
"service": "login-system"
}

---

## Required Variables

DATABASE_URL
SECRET_KEY

---

## Optional Variables

FLASK_ENV
PORT

---

## Final Checklist

Factory Pattern ✅

Blueprints ✅

SQLAlchemy ✅

Flask-Migrate ✅

SQLite Local Development ✅

Supabase Ready ✅

Render Ready ✅

Health Endpoint ✅

Register/Login Flow Tested ✅

Production Deployment Ready ✅