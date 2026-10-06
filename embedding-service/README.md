# 🎬 CineBrain Embedding Service

The **Embedding Service** is the second microservice in CineBrain, a movie recommendation and Retrieval-Augmented Generation (RAG) platform.

It provides a REST API for generating movie embeddings and searching semantically in a vector database (Qdrant). The service uses movie metadata stored in PostgreSQL and creates vectors for semantic similarity searches.

---

## Responsibilities

| File | Responsibility |
| --- | --- |
| `main.py` | Creates the FastAPI application and registers the routes |
| `database.py` | PostgreSQL connection and SQLAlchemy session |
| `embedder.py` | Creates embeddings with a Sentence Transformer model |
| `qdrant_client.py` | Connects to the local Qdrant server |
| `create_collection.py` | Creates the Qdrant `movies` collection |
| `load_embeddings.py` | Loads movie data and uploads embeddings to Qdrant |
| `routes/embeddings.py` | Embedding and semantic-search endpoints |
| `requirements.txt` | Python dependencies |

---

# 1. Create the Python Environment

From the CineBrain project directory:

```bash
cd CineBrain/embedding-service
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

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 3. Configure PostgreSQL and Qdrant

The Embedding Service reads movie records from PostgreSQL and searches vectors in Qdrant.

Create `.env` file with the field:

DATABASE_URL = postgresql://movie_user:password@localhost:5432/movies

with the PostgreSQL username and password you created.

Make sure the database and user exist before loading embeddings. The database setup is described in the Movie Service documentation.

Start Qdrant locally:

```bash
docker run --rm -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

The Qdrant client connects to `localhost:6333` through `app/qdrant_client.py`.

---

# 4. Create the Qdrant Collection

From the embedding-service directory:

```bash
python3 -m app.create_collection
```

This creates the `movies` collection with 384-dimensional cosine vectors.

> The script recreates the collection, so running it again will replace the existing collection data.

---

# 5. Load the Movie Embeddings

The movie data must first be loaded into PostgreSQL by the Movie Service.

Then run:

```bash
python3 -m app.load_embeddings
```

The script:

1. Reads movies from PostgreSQL.
2. Builds text from each movie title and genres.
3. Generates an embedding with `all-MiniLM-L6-v2`.
4. Uploads the embedding and metadata to Qdrant in batches of 500 points.

---

# 6. Run the Embedding Service

From the embedding-service directory:

```bash
uvicorn app.main:app --reload --port 8001
```

The service should be available at:

```text
http://127.0.0.1:8001
```

---

# 7. API Endpoints

## Embed text

```bash
curl -X POST http://127.0.0.1:8001/embed \
  -H "Content-Type: application/json" \
  -d '{"text":"A science fiction movie about space travel"}'
```

The request body must contain a `text` field. The response contains the generated embedding vector.

## Search semantically

```bash
curl "http://127.0.0.1:8001/search?query=space%20travel"
```

The `query` parameter is embedded and searched against the Qdrant `movies` collection. The response contains the five closest matching movie vectors and their payloads.

---

# 8. Service Flow

```text
Movie Service
    │
    ├── Stores movie title and genre data in PostgreSQL
    │
    ▼
Embedding Service
    ├── Reads movie metadata from PostgreSQL
    ├── Generates embeddings
    └── Uploads vectors to Qdrant

Embedding Service API
    ├── POST /embed
    └── GET /search?query=...
```

---

