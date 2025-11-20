# Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.6.1

WORKDIR /app

# system deps for building some Python packages (kept minimal)
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential git curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# copy only requirements first to leverage build cache
COPY requirements.txt /app/requirements.txt

RUN python -m pip install --upgrade pip \
 && pip install -r /app/requirements.txt \
 && pip cache purge

# copy project
COPY . /app

# create a non-root user (recommended)
RUN useradd --create-home --shell /bin/bash appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 7860

# run uvicorn to expose the A2A-wrapped agent on 0.0.0.0:7860
CMD ["uvicorn", "agent:generate_song_a2a", "--host", "0.0.0.0", "--port", "7860", "--reload"]
