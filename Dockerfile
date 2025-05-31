FROM python:3.11-slim

WORKDIR /app

# Install OS-level dependencies
RUN apt-get update && apt-get install -y \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . .

# Set environment variables from .env (in production, this is passed separately)
# For local development, install python-dotenv to read this
RUN pip install python-dotenv

EXPOSE 8080

# Run Streamlit app
# CMD streamlit run app.py --server.port=8080 --server.enableCORS=false
CMD streamlit run app.py --server.port=8080 --server.address=0.0.0.0 --server.enableCORS=false --server.headless=true

