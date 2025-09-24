FROM python:3.10-slim

# Install system dependencies for rasterio, GDAL, etc.
RUN apt-get update && \
    apt-get install -y gdal-bin libgdal-dev && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . .

# Default command
CMD ["python", "-m", "pipeline.main"]