# Multi-stage build for stage0_search_api
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Copy dependency files
COPY Pipfile Pipfile.lock* ./

# Install pipenv and dependencies
RUN pip install pipenv && \
    pipenv install --system --deploy

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY source/ ./source/

# Set environment variables
ENV PYTHONPATH=/app
ENV SEARCH_API_PORT=8083

# Expose port
EXPOSE 8083

# Run the application
CMD ["python", "source/server.py"] 