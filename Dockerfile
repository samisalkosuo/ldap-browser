# Multi-stage build for LDAP Browser

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend with frontend
FROM python:3.11-slim

# Install system dependencies for python-ldap
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libldap2-dev \
    libsasl2-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1001 -s /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy backend requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy built frontend
COPY --from=frontend-builder /app/frontend/build ./static

# Create directory for temporary files
RUN mkdir -p /tmp && chmod 777 /tmp

# Switch to non-root user
USER appuser

# Environment variables for LDAP connection defaults
# These can be overridden at runtime
ENV LDAP_PROTOCOL=ldap \
    LDAP_HOST= \
    LDAP_PORT=389 \
    LDAP_BIND_DN= \
    LDAP_USERNAME= \
    LDAP_PASSWORD= \
    LDAP_BASE_DN= \
    LDAP_TIMEOUT_SECONDS=10

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "main.py"]

# Made with Bob
