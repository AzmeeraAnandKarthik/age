# Use a prebuilt image with dlib and Python 3.7
FROM facehub/python-dlib:py37-cpu

# Set working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Install Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose default port
EXPOSE 8000

# Start the Flask app using gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]
