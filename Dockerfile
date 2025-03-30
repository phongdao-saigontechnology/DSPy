FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy requirements first to leverage Docker cache
COPY pyproject.toml uv.lock ./

RUN uv add git+https://github.com/hendrycks/math.git
RUN uv sync --frozen

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8765

ENV PYTHONPATH="/app:$PYTHONPATH"

# Command to run the application
CMD ["uv", "run", "app.py"]
