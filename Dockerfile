# QWED Action v3.0 Docker Image
# Includes all verification engines and security scanners
# Vulnerability Fix: Upgrade to bookworm and pin digest for immutability
# python:3.12-slim-bookworm @ 2024-02-11
FROM python:3.12-slim-bookworm@sha256:4a8e0824201e50fc44ee8d208a2b3e44f33e00448907e524066fca5a96eb5567

# Prevent python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage cache
COPY requirements.txt /app/requirements.txt

# Install dependencies with hash verification
# Vulnerability Fix: Pin versions with hashes to prevent supply chain attacks
RUN pip install --no-cache-dir --require-hashes -r /app/requirements.txt

# Copy the entire QWED SDK (local version with guards)
COPY qwed_sdk /app/qwed_sdk/

# Copy the entrypoint script
COPY action_entrypoint.py /action_entrypoint.py
RUN chmod +x /action_entrypoint.py

# Set Python path to use local SDK
ENV PYTHONPATH=/app

WORKDIR /github/workspace

ENTRYPOINT ["python", "/action_entrypoint.py"]
