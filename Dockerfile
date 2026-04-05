FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create reports directory
RUN mkdir -p reports

# Non-root user for security
RUN useradd -m -u 1001 cyberguard && chown -R cyberguard:cyberguard /app
USER cyberguard

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
