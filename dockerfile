# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy all application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory
RUN mkdir -p generated_pdfs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--reload"]