FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY requirements.txt requirements.txt
COPY app.py app.py
COPY mitigation.py mitigation.py
COPY feature_extraction.py feature_extraction.py
COPY train_model.py train_model.py
COPY simulate_traffic.py simulate_traffic.py

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python train_model.py

# Expose port
EXPOSE 5000

# Entry point
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "120", "app:app"]
