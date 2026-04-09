# ─────────────────────────────────────────────────────────────────
# Stage 1: Builder
#   Install Python deps into a clean layer so the final image
#   doesn't carry pip / build tools.
# ─────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /install

# Copy only the requirements so Docker can cache this layer
COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --prefix=/install/deps --no-cache-dir -r requirements.txt


# ─────────────────────────────────────────────────────────────────
# Stage 2: Runtime
# ─────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install/deps /usr/local

# Copy application source
COPY . .

# Ensure the model file can be written by the app user
RUN chown -R appuser:appgroup /app

USER appuser

# ─── Environment variables ────────────────────────────────────────
ENV FLASK_APP=app.py \
    FLASK_ENV=production \
    PORT=8000 \
    # Prevents Python from writing .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    # Prevents Python from buffering stdout/stderr
    PYTHONUNBUFFERED=1

EXPOSE 8000

# ─── Health check ─────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" \
  || exit 1

# ─── Run via Gunicorn (production WSGI server) ─────────────────────
# Workers = (2 × CPU cores) + 1  →  using 3 as a sensible default
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]
