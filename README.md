# Currency Monitoring Test Task

A simple Django web app that:
- periodically fetches exchange rates (relative to UAH) from the Monobank API;
- stores exchange-rate history in PostgreSQL;
- provides a REST API for managing tracked currencies;
- includes a management command to export current rates to CSV;
- includes OpenAPI/Swagger documentation.

## Stack

- Python 3.12+
- Django 5+
- Django Rest Framework
- Celery + Celery Beat
- PostgreSQL
- Redis (broker/result backend for Celery)
- drf-spectacular (OpenAPI / Swagger)

## Quick Start (Local)

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Create `.env` from the example file:

```bash
copy .env.example .env
```

3. Start PostgreSQL and Redis (locally or with Docker).

4. Run migrations:

```bash
cd src
python manage.py migrate
```

5. Run the initial rate sync:

```bash
python manage.py sync_currency_rates
```

6. Start Django:

```bash
python manage.py runserver
```

7. Start Celery worker and beat (in separate terminals):

```bash
cd src
celery -A config worker -l info
celery -A config beat -l info
```

## Run with Docker Compose

```bash
docker compose up --build
```

After startup:
- API: `http://localhost:8000/api/`
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## API Endpoints

### 1) Get tracked currencies with current rate
- `GET /api/currencies/tracked/`

### 2) Get currencies available for tracking
- `GET /api/currencies/available/`

### 3) Add a currency to tracking
- `POST /api/currencies/tracked/add/`
- Example body:

```json
{
  "code": 840
}
```

### 4) Get currency rate history for a time period
- `GET /api/currencies/{code}/history/?start=2026-01-01T00:00:00Z&end=2026-01-02T00:00:00Z`

### 5) Enable / disable monitoring
- `PATCH /api/currencies/tracked/{id}/monitoring/`
- Example body:

```json
{
  "is_enabled": false
}
```

## Management commands

### Sync rates

```bash
python manage.py sync_currency_rates
```

### Export current rates to CSV

```bash
python manage.py export_currency_rates --output currency_rates.csv
```

## Periodic Update

- Celery Beat runs `currencies.tasks.sync_currency_rates` every 10 minutes.
- Data source: `https://api.monobank.ua/bank/currency`.

## Project Structure

```text
.
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── src
    ├── config
    ├── currencies
    └── manage.py
```
