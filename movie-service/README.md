# 🎬 CineBrain Movie Service

The **Movie Service** is the first microservice in CineBrain, a movie recommendation and Retrieval-Augmented Generation (RAG) platform.

It provides a REST API for storing and retrieving movie information from MovieLens dataset. The Movie Service is responsible only for movie data.

---

```

### Responsibilities

| File                   | Responsibility                               |
| ---------------------- | -------------------------------------------- |
| `main.py`              | Creates the FastAPI application              |
| `database.py`          | PostgreSQL connection and SQLAlchemy session |
| `models.py`            | SQLAlchemy database models                   |
| `routes/movies.py`     | Movie API endpoints                          |
| `requirements.txt`     | Python dependencies                          |

```

---

# 1. Create the Python Environment

From the CineBrain project directory:

```bash
cd CineBrain/movie-service
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

# 2. Install Dependencies

Install dependancies:

```bash
pip install -r requirements.txt
```

---

# 3. PostgreSQL Setup

The Movie Service uses PostgreSQL as its persistent database.

## Create the database

Open PostgreSQL:

```bash
sudo -u postgres psql
```

Create a database:

```sql
CREATE DATABASE movies;
```

Create a dedicated user:

```sql
CREATE USER movie_user WITH PASSWORD 'your_password';
```

Grant access:

```sql
GRANT ALL PRIVILEGES ON DATABASE movies TO movie_user;
```

Exit:

```sql
\q
```

---

# 4. Test the PostgreSQL Connection

Connect using:

```bash
psql -h localhost -U movie_user -d movies -W
```

You will be prompted for the password.

If the connection succeeds, PostgreSQL is ready.

---

# 5. Database Configuration

Create `.env` file with the field:

DATABASE_URL = postgresql://movie_user:password@localhost:5432/movies

with the PostgreSQL username and password you created.

---

# 6. Load the database

From the movie-service directory:

```bash
python3 -m app.load_data
```

Uvicorn should be unning on http://127.0.0.1:8001

---

# 5. Run the service

From the movie-service directory:

```bash
uvicorn app.main:app --reload --port 8001
```

Uvicorn should be unning on http://127.0.0.1:8001

---

