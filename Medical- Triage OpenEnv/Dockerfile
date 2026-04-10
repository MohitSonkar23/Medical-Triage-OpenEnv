FROM python:3.11-slim

WORKDIR /code

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# OpenEnv port
EXPOSE 8080

# Run inference.py
CMD ["python", "inference.py"]
