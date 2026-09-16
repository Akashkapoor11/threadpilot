# Deployment

## One-command local stack

```bash
docker compose up --build
```

The browser app is available at `http://localhost:8080`; FastAPI docs are available at `/docs`. PostgreSQL is persisted in the `pgdata` volume.

## Render public deployment

The repository includes `render.yaml`, which provisions a Docker web service and a managed PostgreSQL database. Render supports `fromDatabase` references for injecting the database connection string into a service, and its current Blueprint spec supports Docker web services and Postgres resources.

1. Push the repository to GitHub.
2. In Render, create a new Blueprint from the repository.
3. Review the generated `threadpilot-as01` service and `threadpilot-db` database.
4. The API normalizes Render's `postgresql://...` URL to the installed `psycopg` driver.
5. Deploy. The health check is `/api/health`.
6. Copy the public service URL into the hackathon submission and use the same URL for the demo video.

For the optional LLM path, add `LLM_API_KEY`, `LLM_BASE_URL` and `LLM_MODEL` in Render's environment settings. Never commit the API key.

### Free-tier note
Render currently offers free web services and free Postgres for testing/preview use, but its free Postgres databases expire after 30 days and free services have resource limitations. For a hackathon demo this can be useful; use a paid database/service for longer-lived production availability.
