# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir mysql-connector-python

# Copy service files
COPY server/database_manager.py .
COPY server/auth_service.py .
COPY server/course_service.py .
COPY server/transaction_service.py .
COPY server/api_gateway.py .

# Default command (will be overridden in docker-compose)
CMD ["python", "api_gateway.py"]
