# 🎬 CineBrain

CineBrain is a multi-service movie recommendation system that combines movie metadata, semantic embeddings, collaborative filtering, content-based recommendations, and hybrid ranking.

The project is split into independent FastAPI services. Each service runs in its own Docker image, while Docker Compose provides the shared network, ports, environment variables, and service dependencies.

---

## Project architecture

```text
Movie Service (8000)
    │
    ├── Reads movie data from PostgreSQL
    └── Provides movie lookup and title search

Recommendation Service (8002)
    ├── Calls Movie Service for movie details
    ├── Uses MovieLens ratings for collaborative filtering
    └── Reads movie embeddings from Qdrant for content-based filtering

Embedding Service (8001)
    ├── Reads movie metadata from PostgreSQL
    ├── Generates embeddings with Sentence Transformer
    └── Stores vectors in Qdrant

Ranker Service (8003)
    ├── Calls Recommendation Service for collaborative results
    ├── Calls Recommendation Service for content-based results
    └── Combines and ranks the results with a hybrid score

Qdrant (6333)
    └── Stores the movie embedding collection

PostgreSQL (host:5432)
    └── Stores movie metadata; MovieLens ratings are read from CSV
```

### Service responsibilities

| Service | Port | Responsibility |
| --- | ---: | --- |
| Movie Service | 8000 | Stores and retrieves movie metadata |
| Embedding Service | 8001 | Generates and stores semantic movie embeddings |
| Recommendation Service | 8002 | Produces collaborative and content-based recommendations |
| Ranks Service | 8003 | Combines both recommendation sources into a hybrid ranking |
| Qdrant | 6333 | Stores movie vector embeddings |

---

## How the services connect

### Movie Service and PostgreSQL

The Movie Service reads its configuration from environment variables and connects to PostgreSQL using `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`.

In Docker Compose, the PostgreSQL connection uses the host gateway through `host.docker.internal`:

```text
movie-service -> host.docker.internal:5432/movies
```

The Movie Service exposes:

- `GET /movies/{movie_id}`
- `GET /search?query=...`

### Embedding Service and PostgreSQL

The Embedding Service reads movie records from PostgreSQL using `DATABASE_URL`. It builds text from each movie's title and genres, generates a 384-dimensional embedding, and stores the vector with its title and genres in Qdrant.

The embedding service connects to Qdrant using:

```text
embedding-service -> qdrant:6333
```

It exposes:

- `POST /embed`
- `GET /search?query=...`

### Recommendation Service

The Recommendation Service uses two recommendation sources:

1. **Collaborative filtering:** reads the `ratings.csv` dataset and trains an SVD model. It calls the Movie Service for movie details.
2. **Content-based filtering:** retrieves movie embeddings from Qdrant and searches for similar movies.

It connects to the other services using these internal URLs:

```text
recommendation-service -> movie-service:8000
recommendation-service -> qdrant:6333
```

The service exposes:

- `GET /recommendations/user/{user_id}`
- `GET /recommendations/movie/{movie_id}`

### Ranks Service

The Ranks Service calls the Recommendation Service twice:

1. It requests collaborative recommendations for a user.
2. It uses the first five collaborative results as seeds and requests content-based recommendations for those movies.

It then normalizes the scores and combines them using the current weights:

```text
Collaborative weight: 0.7
Content weight:      0.3
```

The final ranking is returned by:

```text
GET /recommendations/user/{user_id}?top_k=10
```

The Ranks Service connects to the Recommendation Service through:

```text
ranker-service -> recommendation-service:8002
```

---

## Docker Compose setup

The project includes a [docker-compose.yml](docker-compose.yml) file that defines the following services:

- `qdrant`
- `embedding-service`
- `movie-service`
- `recommendation-service`
- `ranker-service`

Each service has its own Dockerfile and is built from its service folder.

### Build the images

Run the following command from the project root:

```bash
docker compose build
```

This builds the Python images for all four application services.

### Start Qdrant first

Qdrant is required before the embedding data can be loaded:

```bash
docker compose up -d qdrant
```

The Qdrant container exposes:

- Port `6333` for the Qdrant API
- Port `6334` for the Qdrant dashboard

The Qdrant volume is persistent under the `qdrant_data` Docker volume.

### Prepare PostgreSQL

PostgreSQL is not created by this Compose file. Before starting the application services or loading embeddings, install/start PostgreSQL on the host and create the `movies` database and `movie_user` role. The role needs permission to create and read the movie tables. For a local PostgreSQL installation, open a superuser session:

```bash
sudo -u postgres psql
```

Then create the role and database (replace the example password with your own):

```sql
CREATE ROLE movie_user WITH LOGIN PASSWORD 'change_this_password';
CREATE DATABASE movies OWNER movie_user;
```

Exit `psql` with `\q`. If the role or database already exists, update the existing role password and database ownership instead of creating duplicates:

```sql
ALTER ROLE movie_user WITH LOGIN PASSWORD 'change_this_password';
ALTER DATABASE movies OWNER TO movie_user;
```

The Movie Service and Embedding Service must use matching PostgreSQL credentials. Update the `movie-service` environment values in `docker-compose.yml`:

```yaml
POSTGRES_HOST: host.docker.internal
POSTGRES_PORT: 5432
POSTGRES_DB: movies
POSTGRES_USER: movie_user
POSTGRES_PASSWORD: change_this_password
```

Also update the `embedding-service` `DATABASE_URL` in the same Compose file with that username, password, host, port, and database:

```yaml
DATABASE_URL: postgresql://movie_user:change_this_password@host.docker.internal:5432/movies
```

Keep `host.docker.internal` when PostgreSQL is running on the same host as Docker. If it runs elsewhere, use a hostname or address reachable from the containers and make sure PostgreSQL permits connections from Docker. The database must contain the movie records before the embedding loader can run. The loader command below does not create or populate PostgreSQL tables.

To create the `movies` table, start the Movie Service after PostgreSQL is ready; its startup creates the SQLAlchemy tables. Then import the CSV data. The Docker image does not include the host-side `data` folder, so mount it for this one-time import:

```bash
sudo docker compose up -d movie-service
sudo docker compose run --rm -v "$PWD/movie-service/data:/app/data:ro" movie-service python -m app.load_data
```

Run the commands from the repository root. The import uses the PostgreSQL settings configured for `movie-service` in Compose.

### One-time embedding setup

The embedding data must be loaded once after PostgreSQL has been configured and populated with movie records, and after Qdrant is available.

Run the embedding container's loader from the repository root:

```bash
sudo docker compose run --rm embedding-service python -m app.load_embeddings
```

This command performs the following operations:

1. Creates the `movies` Qdrant collection if it does not already exist.
2. Connects to PostgreSQL using `DATABASE_URL`.
3. Reads all movies from the `movies` table.
4. Builds text using the movie title and genres.
5. Generates a Sentence Transformer embedding for each movie.
6. Uploads the embeddings, titles, and genres to Qdrant in batches of 500 points.

The loader is implemented in [embedding-service/app/load_embeddings.py](embedding-service/app/load_embeddings.py). It uses the same Qdrant client and collection configuration as the embedding service.

> The one-time loader is required only when the collection is empty, missing, or the movie embeddings need to be refreshed. It should not be run for every service startup.

### Start all services

After the embeddings have been loaded, start the application services:

```bash
sudo docker compose up -d
```

The services will then be available at:

| Service | URL |
| --- | --- |
| Movie Service | http://localhost:8000 |
| Embedding Service | http://localhost:8001 |
| Recommendation Service | http://localhost:8002 |
| Ranks Service | http://localhost:8003 |

---

## One-time setup order

The recommended order is:

1. Start PostgreSQL, create the `movie_user` role and `movies` database, and update both PostgreSQL connection settings in `docker-compose.yml` as described above.
2. Build the Docker images:

   ```bash
   docker compose build
   ```

3. Start Qdrant and Movie Service. Movie Service startup creates the database table:

   ```bash
    sudo docker compose up -d qdrant movie-service
   ```

4. Load the movie CSV into PostgreSQL:

    ```bash
    sudo docker compose run --rm -v "$PWD/movie-service/data:/app/data:ro" movie-service python -m app.load_data
    ```

5. Load the movie embeddings once:

   ```bash
   sudo docker compose run --rm embedding-service python -m app.load_embeddings
   ```

6. Start all services:

   ```bash
   sudo docker compose up -d
   ```

The embedding loader uses `host.docker.internal` to reach PostgreSQL, while Qdrant is reached through the Compose network service name `qdrant`.

---

## Current project status

- Movie metadata and lookup are available through the Movie Service.
- Embeddings are generated and stored in Qdrant.
- Collaborative filtering and content-based recommendation endpoints are available in the Recommendation Service.
- The Ranks Service combines both recommendation sources.
- The root README documents the Docker workflow and the one-time embedding load step.
