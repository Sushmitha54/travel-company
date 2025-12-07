# Use Python 3.11
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy project files
COPY . .

# Install system dependencies (optional)
RUN apt-get update && apt-get install -y build-essential

# Upgrade pip and install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 10000

# Start gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:create_app"]
