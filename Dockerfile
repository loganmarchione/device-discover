FROM python:3.14-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src/app.py .
COPY src/templates/ templates/

# Expose the port the app runs on
EXPOSE 3001

# Run the application
CMD ["python", "app.py"]
