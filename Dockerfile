FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Download Chinook DB at build time
RUN python setup_db.py

# Railway injects $PORT dynamically; HuggingFace Spaces uses 7860
EXPOSE 7860

# Use shell form so $PORT is expanded at runtime
# Falls back to 7860 if PORT is not set (HuggingFace Spaces)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
