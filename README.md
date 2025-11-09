# Clinical Nutrition Platform

A full‑stack application for managing clinical nutrition workflows.
It provides role‑based access for doctors and patients, subscription and affiliate systems, and a nutrition planning engine.

## Project Structure

- backend/ — Django REST API (auth, subscriptions, affiliates, nutrition)
- frontend/ — React (TypeScript) app with Tailwind CSS

## Tech Stack

- Backend: Python 3, Django, Django REST Framework, PostgreSQL, Stripe, Celery/Redis
- Frontend: React 18, TypeScript, Vite/CRA (per current config), Tailwind CSS
- Infra/Dev: Node.js, npm, Git

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL 13+
- Redis (for background tasks/Celery if you plan to run them)
- Stripe account (test keys)

## Quick Start

Clone the repository:

```bash
git clone https://github.com/Mohsen-rm/Clinical-Nutrition-Platform.git
cd Clinical-Nutrition-Platform
```

Create environment files based on the examples below.

---

## Backend (Django)

Location: `backend/`

### 1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment

Create a `.env` file inside `backend/` with values similar to:

```env
SECRET_KEY=django-insecure-development-key-change-in-production-12345
DEBUG=True
DB_NAME=clinical_nutrition_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
STRIPE_SECRET_KEY=sk_test_your_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
FRONTEND_URL=http://localhost:3000
REDIS_URL=redis://localhost:6379/0
```

### 4) Apply migrations and create a superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5) Run the server

```bash
python manage.py runserver 8000
```

API base URL: `http://localhost:8000/api/`

Optional: start Celery workers if you use scheduled/background tasks.

```bash
celery -A clinical_platform worker -l info
```

---

## Frontend (React)

Location: `frontend/`

### 1) Install dependencies

```bash
npm install
```

### 2) Configure environment

Create `frontend/.env` with:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key
REACT_APP_FRONTEND_URL=http://localhost:3000
```

### 3) Start the dev server

```bash
npm start
```

The app will run at `http://localhost:3000`.

---

## Test Accounts (example)

- Doctor: `doctor@example.com` / `doctor123`
- You can create more accounts via the backend admin or registration flow.

---

## Useful Scripts

Backend (from `backend/`):

- `python manage.py runserver` — start API
- `python manage.py test` — run tests
- `python create_sample_data.py` — load sample data (if present)

Frontend (from `frontend/`):

- `npm start` — dev server
- `npm run build` — production build
- `npm test` — run tests

---

## Troubleshooting

- Ensure PostgreSQL and Redis are running locally, and credentials match `.env`.
- Stripe keys must be valid test keys for local development.
- If CORS errors appear, confirm `FRONTEND_URL` in backend `.env`.

---

## License

This project is provided as-is for demonstration and development purposes.
