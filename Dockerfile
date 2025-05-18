FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Cloud Run's expected port
EXPOSE 8080

# Run the Streamlit app on Cloud Run's required port
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
