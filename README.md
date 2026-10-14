# Secure API Gateway with Rate Limiting

A backend API Gateway built with Python and FastAPI that provides API-key
authentication, Redis-backed Token Bucket rate limiting, request logging,
and backend API forwarding.

## Features

- API-key authentication using `X-API-Key`
- Token Bucket rate limiting using Redis
- Configurable request limits
- 401 response for missing API key
- 403 response for invalid API key
- 429 response when rate limit is exceeded
- `X-RateLimit-Remaining` response header
- `Retry-After` response header
- Request logging with IP, method, path, status and response time
- Backend API forwarding using HTTPX
- Health-check endpoint
- Swagger API documentation
- Docker support for Redis
- Environment-based configuration

## Architecture

Client
  |
  v
API Key Authentication
  |
  v
Request Logging
  |
  v
Rate Limiting
  |
  v
API Gateway
  |
  v
Backend API
  |
  v
Response

## Tech Stack

- Python
- FastAPI
- Redis
- HTTPX
- Docker
- Uvicorn
- Pydantic Settings

## Project Structure

app/
- api/routes/
  - ping.py
  - gateway.py
- core/
  - auth.py
  - config.py
  - logging.py
  - request_logging.py
- limiter/
  - middleware.py
  - redis_client.py
  - token_bucket.py
- main.py

## Environment Setup

Create `.env` from `.env.example`.

Example:

APP_NAME=Secure API Gateway
LOG_LEVEL=INFO
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
RATE_LIMIT_TOKENS=10
RATE_LIMIT_WINDOW_SECONDS=60
API_KEY=your-secret-api-key
BACKEND_URL=https://jsonplaceholder.typicode.com

Never commit the real `.env` file.

## Run Locally

Start Redis:

    docker compose up -d redis

Create/activate a Python virtual environment and install dependencies:

    pip install -r requirements.txt

Start the gateway:

    uvicorn app.main:app --reload

Health check:

    http://127.0.0.1:8000/health

Swagger documentation:

    http://127.0.0.1:8000/docs

## API Authentication

Protected requests must include:

    X-API-Key: your-secret-api-key

Missing API key:

    401 Unauthorized

Invalid API key:

    403 Forbidden

## Rate Limiting

The gateway uses a Redis-backed Token Bucket implementation.

Default configuration:

    10 requests / 60 seconds

When the request limit is exceeded:

    429 Too Many Requests

## Gateway Example

Request:

    GET /gateway/posts/1

The gateway authenticates the request, applies rate limiting, logs the
request, forwards it to the configured backend API and returns the response.

## Future Improvements

- Web dashboard
- Per-user/API-key rate limits
- Redis transactions or Lua scripting for atomic rate-limit updates
- JWT authentication
- Monitoring and analytics
- Multiple backend services
- Automated CI/CD