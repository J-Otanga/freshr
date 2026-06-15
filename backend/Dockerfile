# Use the official Python 3.12 image as a base
FROM python:3.12-slim

# Tell Python not to write .pyc files and to print logs directly to the terminal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your actual application code into the container
COPY . .

# Expose port 8000 for the frontend to connect to
EXPOSE 8000

# The command to start your FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]