# AI HRMS

Production-oriented **Agentic AI HRMS** built with Python, FastAPI, LangGraph, and RAG.

Employees, managers, and HR admins interact through role-specialized agents that share core HR workflows (leave, attendance, policies, tickets, and more).

```
AI HRMS
   │
   ├── Employee Agent
   ├── Manager Agent
   └── HR Agent
           │
           └── Shared HR Workflows → Postgres + Tools + RAG
```

## Stack

| Layer | Technology |
|--------|------------|
| API | FastAPI + Uvicorn |
| Agents | LangGraph + LangChain |
| Database | PostgreSQL |
| Config | `python-dotenv` |

## Project structure

```
HRMS/
├── app/
│   ├── main.py          # FastAPI entrypoint
│   └── db.py            # SQLAlchemy engine & session
├── db/
│   ├── schema.sql       # Production-shaped HRMS schema
│   └── seed.sql         # Dummy org data (8 employees)
├── .env.example
├── .gitignore
└── requirements.txt
```

## Prerequisites

- Python 3.11+ (3.12/3.14 also fine)
- PostgreSQL running locally
- `psql` / `createdb` available on PATH

## Setup

### 1. Clone and create a virtualenv

```bash
cd HRMS
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If you need DB drivers and are starting fresh:

```bash
pip install fastapi uvicorn[standard] sqlalchemy "psycopg[binary]" python-dotenv langgraph langchain
pip freeze > requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your local Postgres credentials:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/hrms
```

### 3. Create database and load schema + seed

```bash
createdb hrms
# or: psql -U postgres -c "CREATE DATABASE hrms;"

psql -d hrms -f db/schema.sql
psql -d hrms -f db/seed.sql
```

Verify:

```bash
psql -d hrms -c "SELECT employee_code, first_name, last_name FROM employees;"
```

You should see 8 NovaTech employees.

To reset and reseed:

```bash
dropdb hrms && createdb hrms
psql -d hrms -f db/schema.sql
psql -d hrms -f db/seed.sql
```

## Run the API

From the project root with the venv active:

```bash
uvicorn app.main:app --reload
```

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | App info |
| http://127.0.0.1:8000/health/db | DB connectivity (`employees: 8`) |
| http://127.0.0.1:8000/docs | Swagger UI |

## Seed personas (for agent testing later)

| Role | Email | Notes |
|------|--------|--------|
| Employee | `neha.verma@novatech.example` | Reports to Rohan |
| Manager | `rohan.mehta@novatech.example` | Eng manager |
| HR Admin | `priya.nair@novatech.example` | HRBP + admin |

## Roadmap (high level)

1. **Done:** Postgres schema, seed data, FastAPI + DB health check  
2. **Next:** SQLAlchemy models, REST APIs for employees / leave  
3. **Then:** LangGraph agents (Employee / Manager / HR) with tools  
4. **Later:** RAG over policies, human-in-the-loop approvals, observability  

## License

Private / unpublished — update when you choose a license.
