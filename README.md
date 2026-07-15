# MediSense AI — Healthcare Diagnosis & Hospital Management (Phase 1)

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your real MySQL password:
   ```
   cp .env.example .env
   ```

4. Make sure MySQL is running and the database exists:
   ```sql
   CREATE DATABASE healthcare_db;
   ```

5. Run the app:
   ```
   uvicorn app.main:app --reload
   ```

6. Visit:
   - http://127.0.0.1:8000 — landing page
   - http://127.0.0.1:8000/docs — interactive API docs (auto-generated!)
   - http://127.0.0.1:8000/db-check — confirms MySQL connection
