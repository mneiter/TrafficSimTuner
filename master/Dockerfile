# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (optional, if needed)
RUN apt-get update && apt-get install -y gcc

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY ./app ./app
COPY ./templates ./templates

# Make shared available everywhere
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Set the default working directory to /app
WORKDIR /app

# Expose port (optional, for documentation)
EXPOSE 8000

# Run the server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
