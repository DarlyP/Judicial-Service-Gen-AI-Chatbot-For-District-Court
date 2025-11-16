FROM python:3.14-slim

# Update package index and install base system tools
RUN apt-get update && apt-get install -y curl git ca-certificates && rm -rf /var/lib/apt/lists/*

# Install Ollama using the official installation script
RUN curl -fsSL https://ollama.com/install.sh | sh

# Configure important environment variables
# PYTHONUNBUFFERED: disable output buffering for immediate logs
# HOME: define the application home directory
# OLLAMA_HOST: host and port where the Ollama server listens
# OLLAMA_MODELS: directory path for storing Ollama models
ENV PYTHONUNBUFFERED=1 \
    HOME=/app \
    OLLAMA_HOST=127.0.0.1:11434 \
    OLLAMA_MODELS=/app/.ollama

# Set the working directory for the application
WORKDIR /app

# Copy dependency file and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application source code into the container
COPY . .

# Create the models directory and ensure it is writable
RUN mkdir -p /app/.ollama && chmod -R 777 /app/.ollama

# Ensure the entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Define the default command for starting the container
CMD ["/app/entrypoint.sh"]
