# Python 3.11 sebagai base image
FROM python:3.11-slim

# # Set working directory
# WORKDIR /app

# Copy file requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode sumber ke dalam container
COPY . .

# Expose port untuk FastAPI
EXPOSE 8000

# Perintah untuk menjalankan aplikasi menggunakan uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
