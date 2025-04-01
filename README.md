# T2SQL - Natural Language to SQL Converter

A SaaS application that converts natural language questions into SQL queries by leveraging database metadata and use-case knowledge.

## Features

- Connect to any database via API
- Upload database metadata and use-case documentation
- Natural language to SQL query conversion
- Support for multiple SQL dialects (MySQL, Oracle, etc.)
- Secure authentication system
- Modern, responsive UI

## Tech Stack

- Backend: Python with FastAPI
- Frontend: React with TypeScript
- Database: PostgreSQL
- Authentication: JWT
- SQL Generation: LangChain + LLM

## Project Structure

```
t2sql/
├── backend/           # FastAPI backend
├── frontend/         # React frontend
├── docs/            # Documentation
└── docker/          # Docker configuration
```

## Setup Instructions

1. Clone the repository
2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env` in both backend and frontend directories
   - Update the variables as needed

5. Start the development servers:
   - Backend: `uvicorn main:app --reload`
   - Frontend: `npm run dev`

## License

MIT 