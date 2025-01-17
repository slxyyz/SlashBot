# Dockerfile
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install dependencies (use virtualenv to reduce image size)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    pip install --upgrade pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Set the command to run your bot
CMD ["python", "bot.py"]
