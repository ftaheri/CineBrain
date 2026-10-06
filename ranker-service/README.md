# 🎬 CineBrain Ranks Service

The **Ranker Service** is the final recommendation layer in CineBrain, a movie recommendation and Retrieval-Augmented Generation (RAG) platform.

It combines two recommendation sources:

- **Collaborative recommendations** from the Recommendation Service.
- **Content-based recommendations** from the Recommendation Service using Qdrant movie embeddings.

The service normalizes both result sets, combines their scores, and returns a ranked list of movies for a user.

---

## Responsibilities

| File | Responsibility |
| --- | --- |
| `main.py` | Creates the FastAPI application and registers the routes |
| `client.py` | Calls the Recommendation Service over HTTP |
| `hybrid.py` | Normalizes, combines, deduplicates, and ranks recommendations |
| `routes/recommendation.py` | Exposes the hybrid recommendation endpoint |
| `requirements.txt` | Python dependencies |

---

# 1. Create the Python Environment

From the CineBrain project directory:

```bash
cd CineBrain/ranker-service
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

# 3. Start the Required Services

The Ranks Service depends on the Recommendation Service, which must be running on port `8002`.

Start the Recommendation Service first:

```bash
cd recommendation-service
uvicorn app.main:app --reload --port 8002
```

The Recommendation Service must have its collaborative model trained and its Qdrant data available before hybrid recommendations can be generated.

---

# 4. Run the Ranks Service

From the ranker-service directory:

```bash
uvicorn app.main:app --reload --port 8003
```

The service should be available at:

```text
http://127.0.0.1:8003
```

---

# 5. API Endpoints

## Service health

```bash
curl http://127.0.0.1:8003/
```

The response is:

```json
{
  "service": "hybrid-recommendation-service",
  "status": "running"
}
```

## Get hybrid recommendations for a user

```bash
curl "http://127.0.0.1:8003/recommendations/user/1?top_k=10"
```

The response contains the selected user ID and a ranked list of movies:

```json
{
  "user_id": 1,
  "recommendations": [
    {
      "movie_id": 2,
      "title": "Movie Title",
      "hybrid_score": 0.85,
      "collaborative_score": 0.7,
      "content_score": 0.3
    }
  ]
}
```

The `top_k` query parameter controls the number of results and defaults to `10`.

---

# 6. Recommendation Flow

```text
Ranks Service
    │
    ├── Requests collaborative recommendations from port 8002
    │
    ├── Uses the top collaborative movies as content seeds
    │
    ├── Requests content-based recommendations from port 8002
    │
    ├── Normalizes both score sets
    │
    ├── Combines duplicate movies
    │
    └── Returns the top-ranked movies
```

The current hybrid configuration is:

```text
Collaborative weight: 0.7
Content weight:      0.3
```

The weights must sum to `1.0`. The default configuration is defined in `app/routes/recommendation.py`.

---

# 7. How the Hybrid Ranking Works

The Ranks Service performs the following steps:

1. Requests up to 20 collaborative recommendations for the user.
2. Uses the first five collaborative results as seeds.
3. Requests up to 20 content-based recommendations for each seed movie.
4. Removes duplicate movie IDs while retaining the highest content score.
5. Normalizes collaborative and content scores to the range `[0, 1]`.
6. Combines recommendations into one dictionary keyed by movie ID.
7. Calculates the hybrid score:

$$
\text{hybrid score} =
\text{collaborative weight}\times\text{collaborative score} +
\text{content weight}\times\text{content score}
$$

8. Sorts the combined results by hybrid score in descending order.
9. Returns the requested top-K results.

