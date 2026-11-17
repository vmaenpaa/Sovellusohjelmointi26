# Ollama setup for Insights

Ollama must be installed on the host, and the model must be downloaded before Insights will work.

The tested model is **`mimo-v2.6`**. The model name in this guide matches
`OLLAMA_MODEL=mimo-v2.6` in the root `.env.example`.

## 1. Install and pull Ollama

Install Ollama for your operating system from the
[official Ollama download page](https://ollama.com/download).

Confirm Ollama and pull the tested model:

```bash
ollama --version
ollama pull mimo-v2.6
ollama list
```

You may replace `mimo-v2.6` with another installed model, but also update
`OLLAMA_MODEL` in the root `.env`. Keep the `.env` and `.env.example` model names
consistent when sharing setup changes.

## 2. Set environment variables

Copy the root environment template if `.env` does not exist:

```bash
cp .env.example .env
```

Set these variables in the root `.env` (OLLAMA_BASE_URL and OLLAMA_MODEL already set in .env.example):

```env
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=mimo-v2.6
OLLAMA_TIMEOUT=30
```

- `AI_PROVIDER=ollama` selects the local Ollama provider.
- `OLLAMA_BASE_URL` is the URL of Ollama as seen by the API process.
   - With the API running directly on the host:
   `OLLAMA_BASE_URL=http://localhost:11434`
   - With the API running in Docker Compose:
   `OLLAMA_BASE_URL=http://host.docker.internal:11434`

- `OLLAMA_MODEL` is the exact model name returned by `ollama list`.
- `OLLAMA_TIMEOUT` is the number of seconds the API waits for Ollama.

### Host vs Docker networking

After changing `.env`, restart the API container or local API process:

```bash
docker compose up --build
# or, for a locally started API:
# cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 3. Success demo

1. Confirm Ollama is running and the model is installed:

   ```bash
   ollama list
   curl http://localhost:11434/api/tags
   ```

2. Start the database, API, and frontend using Docker Compose.
3. Open `http://localhost:5173`, register or log in, and add training session data.
4. Open `/insights` through the app navigation or directly at
   `http://localhost:5173/insights`.
5. Select **This week** or **This month**, optionally enter a focus, and click
   **Generate insights**.
6. Confirm the result contains separate `summary`, `strengths`,
   `recommendations`, and `caveats` sections.

You can also call `POST /ai/insights` in `http://localhost:8000/docs` after
authorizing as a logged-in user.

## 4. “AI down” demo

1. Stop Ollama, for example by stopping the Ollama application or service.
2. Open `/insights`, choose a period, and generate an insight.
3. Confirm the Insights page shows a clear friendly error. The API should return
   HTTP 503 for an Ollama connection or timeout failure.
4. Confirm the rest of the app still works: open Sessions, Calendar, Plans, or
   Progress. Insights are optional and should not make the rest of the app fail.

Start Ollama again and retry Insights to return to the success demo.

## Common failures

| Problem | Check |
| --- | --- |
| Model not found or missing | Run `ollama pull mimo-v2.6`, then `ollama list`. `OLLAMA_MODEL` must exactly match the model name. |
| Connection refused to Ollama | Confirm Ollama is running and verify the base URL for your API process. |
| Wrong base URL | Host API: use `http://localhost:11434`. Docker API: use `http://host.docker.internal:11434`. |
| Timeout too low | Increase `OLLAMA_TIMEOUT`, for example to `60` or higher on slower machines. Restart the API after editing `.env`. |
| Ollama has not finished loading | Wait for `ollama pull` and the first model run to finish, then retry. |
| 503 from `/ai/insights` | Ollama is stopped/unreachable, the model is unavailable, or the request exceeded `OLLAMA_TIMEOUT`. |
