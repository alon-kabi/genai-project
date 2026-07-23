# Recruiting Chatbot PoC

A proof-of-concept recruiting assistant for a **Python Developer** role. Candidates chat in SMS-style turns; a main agent routes to specialized advisors for job questions (RAG) and interview scheduling (SQL Server).

Built with **Python**, **LangChain**, **OpenAI**, **Streamlit**, **ChromaDB**, and **Microsoft SQL Server**.

## Features

- **Multi-agent orchestration** — `MainAgent` handles dialogue; fixed routing phrases delegate to `InfoAdvisor` or `ScheduleAdvisor`.
- **Job information (RAG)** — Embeds a job-description PDF at startup and answers role questions via ChromaDB + OpenAI embeddings.
- **Interview scheduling** — LangChain tools backed by SQL Server:
  - `get_schedule` — list available slots by position and date
  - `interview_booking` — book a slot (requires candidate name and phone)
  - `update_interview` — reschedule an existing booking
  - `cancel_interview` — soft-cancel and release the slot
- **Dual SQL backends** — `pyodbc` (recommended on Windows) or `pymssql`, selectable via environment variable.
- **Session logging** — Each turn is recorded to `logs/sessions/` as JSON for debugging and review.
- **Two interfaces** — Streamlit web UI (`app.py`) or terminal CLI (`python -m src.main`).

## Architecture

```
User message
    │
    ▼
MainAgent (gpt-4o-mini, in-memory history)
    │
    ├─ "Let me find that information for you." → InfoAdvisor (RAG tool)
    │
    └─ "I will check available slots for you." → ScheduleAdvisor (SQL tools)
```

Prompts live in `prompts/` and control routing, clarification, scheduling rules, and job-info behavior.

## Prerequisites

- Python 3.10+ (3.11 recommended)
- OpenAI API key
- SQL Server with the `Tech` database (see [Database setup](#database-setup))
- For `pyodbc`: [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server) (or set `MSSQL_DRIVER`)

## Getting started

### 1. Clone and install

```bash
cd genai-project
python -m venv .venv

# Windows
.\.venv\Scripts\activate
pip install -r requirements.txt

# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...

# SQL Server (database defaults to Tech)
MSSQL_BACKEND=pyodbc
MSSQL_SERVER=localhost
MSSQL_DATABASE=Tech
MSSQL_USER=your_user
MSSQL_PASSWORD=your_password
MSSQL_DRIVER=ODBC Driver 17 for SQL Server
```

Use `MSSQL_BACKEND=pymssql` only if TCP connectivity to SQL Server is enabled and `pyodbc` is unavailable.

### 3. Job description PDF

Place the job description at:

```text
data/docs/Python Developer Job Description.pdf
```

The PDF is loaded into an in-memory Chroma collection on each run (nothing persists after exit).

### 4. Database setup

Run the seed script against your SQL Server instance to create the `Tech` database, `Schedule` table, sample slots, and `InterviewBooking` table:

```text
sql/seed_schedule.sql
```

## Usage

Always run commands from the **project root** (`genai-project`).

### Streamlit UI

```bash
streamlit run app.py
```

### Terminal CLI

```bash
python -m src.main
```

CLI commands:

- `exit` — quit
- `dump` — write the current session log to `logs/sessions/` and exit

On errors, session dumps (including traceback) are written automatically.

## Project structure

```text
genai-project/
├── app.py                      # Streamlit entry point
├── prompts/                    # System prompts (main, schedule, info, …)
├── data/
│   └── docs/                   # Job description PDF for RAG
├── sql/
│   └── seed_schedule.sql       # DB schema and sample schedule data
├── logs/
│   └── sessions/               # Session JSON dumps (gitignored)
├── src/
│   ├── main.py                 # CLI entry point
│   └── shared/
│       ├── conversation_manager.py
│       ├── main_agent.py       # Orchestrator
│       ├── info_advisor.py     # RAG job-info agent
│       ├── schedule_advisor.py # Scheduling tools + agent
│       ├── mssql_backend.py    # pyodbc / pymssql abstraction
│       ├── session_logger.py
│       ├── exit_advisor.py
│       └── rag/
│           └── chroma_client.py
├── requirements.txt
└── README.md
```

## Scheduling tools (summary)

| Tool | Purpose |
|------|---------|
| `get_schedule` | Available slots by position; optional `day` for a specific date |
| `interview_booking` | Book slot; requires `CandidateName`, `CandidatePhone`, `Interview_type` (Zoom or Office) |
| `update_interview` | Reschedule to a new date/time/type |
| `cancel_interview` | Mark booking cancelled and free the slot |

Position matching uses `LIKE` patterns so partial names (e.g. "Python") match stored values.

The schedule advisor resolves relative dates (e.g. "next Friday") using today's date injected into its prompt.

## Technologies

- [LangChain](https://python.langchain.com/) — agents, tools, chat history
- [OpenAI](https://platform.openai.com/) — `gpt-4o-mini` for chat; `text-embedding-3-small` for RAG
- [Streamlit](https://streamlit.io/) — web chat UI
- [ChromaDB](https://www.trychroma.com/) — ephemeral vector store
- [pandas](https://pandas.pydata.org/) — SQL result handling
- [pyodbc](https://github.com/mkleehammer/pyodbc) / [pymssql](https://pymssql.readthedocs.io/) — SQL Server access

## License

Internal proof-of-concept — no license specified.
