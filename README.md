# 🛡️ AI-Based DDoS Protection System

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Educational-red)](#license)

ML-powered DDoS detection system with real-time attack classification and automatic IP blocking. Uses Random Forest to detect anomalous traffic patterns in **< 5ms** latency.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1: Start server
python app.py

# Terminal 2: Generate training data
python simulate_traffic.py

# Terminal 3: Train model
python train_model.py

# Run protection system
python app.py
```

Visit: http://localhost:5000/stats for metrics

## ✨ Features

- ⚡ Real-time detection (< 5ms latency)
- 🤖 Random Forest classifier (95%+ accuracy)
- 🚫 Automatic IP blocking & rate limiting
- 📊 REST API for monitoring
- 🔒 Thread-safe concurrent handling
- 🐳 Docker ready

## 📁 Components

| File | Purpose |
|------|---------|
| `app.py` | Flask server with DDoS detection middleware |
| `feature_extraction.py` | Computes 7 ML features per request |
| `train_model.py` | Trains Random Forest on traffic data |
| `mitigation.py` | IP blocking & rate limiting logic |
| `simulate_traffic.py` | Generates training data |

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Welcome page |
| GET | `/health` | Health check |
| GET | `/stats` | Protection metrics |
| GET | `/login` | Login endpoint |
| GET/POST | `/api/*` | Application routes |

## ⚙️ Configuration

| Setting | File | Default |
|---------|------|---------|
| Block Duration | `mitigation.py` | 300s (5 min) |
| Rate Limit | `mitigation.py` | 50 requests |
| Feature Window | `feature_extraction.py` | 10s |
| Server Port | `app.py` | 5000 |

## 🐳 Docker

```bash
docker build -t ddos-protection .
docker run -p 5000:5000 ddos-protection
```

## 🐛 Troubleshooting

**Model not found**: Run `python train_model.py` first

**Port in use**: Change port in `app.py` or kill process:
```bash
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows
```

**Low accuracy**: Ensure `simulate_traffic.py` completes and check `traffic_log.csv` has all 3 classes

## 📊 Performance

| Metric | Value |
|--------|-------|
| Latency | < 5ms |
| Throughput | 1000+ req/s |
| Memory | ~50MB |
| Accuracy | 95%+ |


## 👨‍💻 Author

**Ketan Jain** — [GitHub](https://github.com/ketanjain113)
