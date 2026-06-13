FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including cron and nano
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    cron \
    postgresql-client \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Setup crontab
COPY crontab /etc/cron.d/skay-backup
RUN chmod 0644 /etc/cron.d/skay-backup
RUN crontab /etc/cron.d/skay-backup

# Create log file for cron
RUN touch /var/log/cron.log

# Create non-root user (but keep cron as root)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Start cron and uvicorn
CMD ["sh", "-c", "cron && uvicorn main:app --host 0.0.0.0 --port 8000"]