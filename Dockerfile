# Use Python 3.7.4 as base
FROM python:3.7.4-slim

# Avoid buffering
ENV PYTHONUNBUFFERED=1

# Install system dependencies for dlib and opencv
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy app code
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port used by gunicorn
EXPOSE 8000

# Run the app with gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
