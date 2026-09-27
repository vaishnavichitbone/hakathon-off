# OpporTune

**Discover the right opportunity. Know why it fits. Act before the deadline.**

OpporTune is a personalized opportunity discovery platform for students. It goes beyond simple listings by intelligently matching students with internships, hackathons, and courses based on their unique profiles (skills, interests, education). 

Built for the **FIT-FEST 2026 HACKATHON**.

## Key Features

1. **Explainable Match Score:** Not just a random percentage. We tell you exactly which skills and interests matched, and what you're missing.
2. **Opportunity Priority Engine:** Automatically categorizes opportunities into High/Medium priority based on match score and approaching deadlines.
3. **Application Kanban Tracker:** Move opportunities from "Saved" -> "Applied" -> "Selected" on a visual board.
4. **My Roadmap:** Sorts your best matches into "Apply Now", "Prepare & Apply", and "Learn First" (when you're missing required skills).
5. **Modern Dashboard:** Track your application statistics and urgent deadlines at a glance.

## System Architecture & Tech Stack

**Frontend:**
- HTML5, CSS3 (Custom Glassmorphism UI)
- Vanilla JavaScript
- FontAwesome Icons

**Backend:**
- Python 3.11
- FastAPI
- SQLAlchemy ORM
- JWT Authentication

**Database:**
- PostgreSQL (via Docker)
- *Fallback for local quick dev without Docker: SQLite*

**Deployment:**
- Docker & Docker Compose
- Google Cloud Run

## Local Setup

### Prerequisites
- Python 3.11+
- (Optional but recommended) Docker Desktop

### 1. Backend Setup

```bash
# Create and activate virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Or on Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the database (creates demo user, admin, and demo opportunities)
python seed_data.py

# Run the backend server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

Since it's pure HTML/JS, you can simply use a tool like Live Server in VS Code, or Python's built-in HTTP server:

```bash
python -m http.server 8080
```
Then navigate to `http://localhost:8080/frontend/index.html`

### 3. Docker (Alternative Setup)

To run everything (PostgreSQL + FastAPI backend) via Docker:

```bash
docker-compose up --build -d
```
The API will be available at `http://localhost:8000`.

## Google Cloud Run Deployment

1. Build and push the Docker image to Google Container Registry (GCR) or Artifact Registry:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/opportune
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy opportune \
  --image gcr.io/YOUR_PROJECT_ID/opportune \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=your_cloud_sql_postgres_url,SECRET_KEY=your_production_secret"
```

## Demo Credentials

If you ran `seed_data.py`, use the following accounts:

**Student:**
Email: `student@opportune.com`
Password: `student123`

**Admin:**
Email: `admin@opportune.com`
Password: `admin123`

## Future Scope
- AI-based resume parsing to automatically fill student profiles.
- Notification engine (email/SMS) for upcoming deadlines.
- Institutional login integration (OAuth).
