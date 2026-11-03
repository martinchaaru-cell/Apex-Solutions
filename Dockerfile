# Apex Solutions website and portal. Baseline H5: pinned slim image, non-root user, no secrets baked in.
FROM python:3.12.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY *.py ./
COPY docker-entrypoint.sh ./
COPY templates ./templates
COPY static ./static
COPY seed_documents ./seed_documents

# instance/ holds uploaded documents; it is mounted as a volume in docker-compose.yml
# The entrypoint starts as root only to fix ownership of a mounted disk, then drops to the apex user.
RUN useradd --create-home --uid 10001 apex && mkdir -p /app/instance/documents \
    && chown -R apex:apex /app/instance /app/seed_documents && chmod 700 /app/instance/documents \
    && chmod +x /app/docker-entrypoint.sh

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import os,urllib.request;urllib.request.urlopen('http://127.0.0.1:%s/robots.txt'%os.environ.get('PORT','8000'),timeout=4)"
CMD ["/app/docker-entrypoint.sh"]
