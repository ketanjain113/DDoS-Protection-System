# 🛡️ AI-Based DDoS Protection System

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Latest-green?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Educational-red)](#license)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)](#)

A **machine learning-powered DDoS attack detection and mitigation system** for cloud-hosted web applications. Detects anomalous traffic patterns in real-time using a trained Random Forest classifier with **sub-second latency** and automatic IP blocking.

> **Use Case**: Protect web APIs and web applications from volumetric DDoS attacks, slow-rate DDoS, and credential stuffing attempts.

---

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)  
- [Architecture](#-architecture)
- [Setup & Installation](#-setup--installation)
- [API Endpoints](#-api-endpoints)
- [Configuration](#-configuration)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [Future Enhancements](#-future-enhancements)
- [License](#license)

---

## ✨ Features

- ⚡ **Real-time Detection** - Sub-second latency with 7 behavioral features
- 🤖 **ML-Powered** - Random Forest classifier trained on simulated traffic
- 🚫 **Automatic Mitigation** - IP blocking, rate limiting, and auto-recovery
- 📊 **Live Monitoring** - REST API for protection statistics and metrics
- 🔒 **Thread-Safe** - Concurrent request handling with proper locking
- 🐳 **Docker Ready** - Pre-configured Dockerfile for containerization
- 📈 **Expected Accuracy** - 95%+ detection rate on test data

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip or conda

### 1. Clone & Install

```bash
git clone https://github.com/ketanjain113/DDoS-Protection-System.git
cd DDoS-Protection-System
pip install -r requirements.txt
```

### 2. Generate Training Data & Train Model

```bash
# Terminal 1: Start the Flask server
python app.py

# Terminal 2: Simulate traffic (500 normal + 1000 attack + 200 suspicious requests)
python simulate_traffic.py

# Terminal 3: Train the model
python train_model.py
```

### 3. Run Detection System

```bash
python app.py
```

Visit:
- 🏠 **Dashboard**: http://localhost:5000/
- 📊 **Stats**: http://localhost:5000/stats
- 🏥 **Health**: http://localhost:5000/health

---

## 🏗️ Architecture

### Project Components

| Component | Purpose | Highlights |
|-----------|---------|-----------|
| **app.py** | Flask web server | Real-time DDoS detection middleware |
| **feature_extraction.py** | Feature computation | 7 behavioral features + cyclical time encoding |
| **train_model.py** | Model training & evaluation | Random Forest & SVM comparison |
| **mitigation.py** | IP blocking & rate limiting | 5-min auto-recovery, thread-safe |
| **simulate_traffic.py** | Traffic simulation | Generates realistic attack patterns |
| **requirements.txt** | Dependencies | All Python packages listed |
| **Dockerfile** | Container config | Production-ready deployment |

### Request Processing Flow

```
Incoming Request
      ↓
[Extract Features] (1ms)
      ↓
[Load Model] [Predict] (5ms)
      ↓
[Save to Log] [Update Stats]
      ↓
├─ Normal (0)     → Allow
├─ Suspicious (1) → Rate Limit
└─ Attack (2)     → Block IP (5min cooldown)
```

### Feature Engineering

The system computes **7 features per 10-second window per IP**:

| Feature | Description | Example |
|---------|-------------|---------|
| `request_rate` | Requests in last 10 seconds | 500+ = suspicious |
| `ip_frequency` | Unique requests from IP in 60s | 10000+ = attack |
| `unique_endpoints` | Different endpoints hit | 1 (attack) vs 50 (normal) |
| `error_rate` | Fraction of 4xx/5xx responses | 0 (normal) vs 0.9 (attack) |
| `avg_payload_size` | Mean request body size | Bytes |
| `inter_arrival_time` | Mean time between requests | Milliseconds |
| `session_duration` | Time span of requests | Seconds |
| `time_of_day_sin/cos` | Cyclical hour encoding | [-1, 1] range |

---

## 🔧 Setup & Installation

### Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Requirements:**
- Flask (REST API)
- scikit-learn (ML models)
- pandas (Data processing)
- numpy (Numerical computing)

### Generate Training Data

The system requires training data before deployment:

```bash
# Terminal 1
python app.py

# Terminal 2 (sends 1700 total requests)
python simulate_traffic.py
```

**Traffic Distribution:**
- 500 normal requests from random IPs
- 1000 attack requests from 3 attacker IPs
- 200 suspicious requests from 2 IPs
- Logged to `traffic_log.csv`

### Train the Detection Model

```bash
python train_model.py
```

**Output:**
- `ddos_model.pkl` - Trained Random Forest model
- `confusion_matrix.png` - Performance visualization
- Console output - Classification report, feature importance

### Launch Protection System

```bash
python app.py
```

The server will:
1. Load the trained model from `ddos_model.pkl`
2. Start Flask on `http://localhost:5000`
3. Initialize auto-recovery background thread
4. Begin detecting and blocking attacks

---

## 🔌 API Endpoints

### System Management

| Method | Endpoint | Purpose | Example |
|--------|----------|---------|---------|
| GET | `/` | Welcome & endpoint list | Root page |
| GET | `/health` | Health check (bypasses DDoS detection) | Monitoring |
| GET | `/stats` | Real-time protection metrics | `curl localhost:5000/stats` |

### Application Routes

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/login` | Login endpoint |
| GET | `/api/data` | Data retrieval |
| POST | `/api/submit` | Data submission |

### Example Stats Response

```json
{
  "total_requests": 1500,
  "blocked_ips": 3,
  "rate_limited_ips": 2,
  "recent_detections": [
    {"ip": "192.168.1.100", "label": 2, "timestamp": "2026-04-09T10:30:00"},
    {"ip": "192.168.1.101", "label": 1, "timestamp": "2026-04-09T10:29:55"}
  ]
}
```

---

## ⚙️ Configuration

Customize system behavior by editing these files:

| Setting | File | Default | Purpose |
|---------|------|---------|---------|
| **Block Duration** | `mitigation.py` | 300s (5 min) | How long to block suspicious IPs |
| **Rate Limit Threshold** | `mitigation.py` | 50 requests | Trigger for rate limiting |
| **Feature Window** | `feature_extraction.py` | 10s | Aggregation period for features |
| **Request Log Window** | `feature_extraction.py` | 60s | In-memory log retention |
| **ML Model** | `train_model.py` | RandomForest | Change to SVM if desired |
| **Server Port** | `app.py` | 5000 | Flask listen port |

### Example: Switch to SVM

Edit `train_model.py` line ~100:

```python
# Change from Random Forest to SVM
best_model = svm_model  # was: rf_model
```

---

## 📈 Performance

**Typical Laptop Benchmarks:**

| Metric | Value |
|--------|-------|
| Model Load Time | < 100ms |
| Feature Extraction | < 1ms per request |
| Prediction Latency | < 5ms |
| Throughput | 1000+ requests/sec |
| Memory Footprint | ~50MB |

**Model Accuracy:**
- Precision: 95%+ (few false positives)
- Recall: 95%+ (catches most attacks)
- F1-Score: 95%+

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t ddos-protection:latest .
```

### Run Container

```bash
docker run -p 5000:5000 -v $(pwd)/data:/app/data ddos-protection:latest
```

> ⚠️ **Note**: The trained model `ddos_model.pkl` must exist before running. Generate it first with `python train_model.py`.

---

## 📊 Data Format

### traffic_log.csv

CSV file created during traffic simulation with columns:

| Column | Type | Example |
|--------|------|---------|
| `timestamp` | ISO datetime | 2026-04-09T10:30:45Z |
| `ip` | IP address | 192.168.1.100 |
| `endpoint` | Request path | /api/data |
| `method` | HTTP method | GET, POST |
| `status_code` | HTTP status | 200, 403, 404 |
| `payload_size` | Bytes | 512 |
| `label` | Class (0/1/2) | 0=normal, 1=suspicious, 2=attack |

---

## 🔒 Thread Safety

All shared state is protected with locks:

- `request_log_lock` - Protects in-memory request log
- `mitigation.lock` - Protects blocked_ips and rate_limited_ips dictionaries

**Auto-Pruning**: Entries older than 60 seconds are automatically removed to prevent memory leaks.

---

## 🐛 Troubleshooting

### Model file not found
```
ERROR: ddos_model.pkl not found
```
**Solution**: Run `python train_model.py` to generate the model first.

### Server won't start
```
Address already in use: ('127.0.0.1', 5000)
```
**Solution**: Change port in `app.py` or kill process using port 5000:
```bash
lsof -ti:5000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :5000   # Windows (then taskkill)
```

### Low model accuracy
- Ensure `simulate_traffic.py` completed fully
- Verify `traffic_log.csv` contains all 3 traffic classes
- Adjust `n_estimators` in RandomForestClassifier (higher = better)

### Memory issues
- Request log auto-prunes entries > 60 seconds
- Monitor with `curl localhost:5000/stats`
- Consider persistent storage for large-scale deployments

---

## 🚀 Future Enhancements

- [ ] **Distributed Detection** - Multi-server model ensembles
- [ ] **Adaptive Learning** - Online model updates with new patterns
- [ ] **Geographic Analysis** - GeoIP-based blocking
- [ ] **SIEM Integration** - Send logs to Splunk/ELK
- [ ] **Advanced Evasion** - Detect sophisticated attack variations
- [ ] **Honeypot Integration** - Detect reconnaissance phases
- [ ] **API Rate Limiting** - Per-user quotas
- [ ] **Fallback DNS/Anycast** - DDoS resilience

---

## 📝 Advanced Usage

### Custom Feature Engineering

Extend `feature_extraction.py` with:
```python
# Example: Add user-agent analysis
def extract_user_agent_features(user_agent):
    # Detect bot patterns, crawlers, etc.
    pass
```

### Integration with External Systems

Hook `/stats` endpoint to:
- 📊 Grafana/Datadog dashboards
- 🔔 PagerDuty/Slack alerts  
- 🎯 Jira/Azure DevOps incidents

### Using SVM Instead

```python
# In train_model.py
best_model = svm_model  # Line ~100
joblib.dump(best_model, 'ddos_model.pkl')
```

---

## 📂 Project Structure

```
ddos-protection/
├── app.py                    # Flask server (478 lines)
├── simulate_traffic.py       # Traffic simulator (271 lines)
├── feature_extraction.py     # Feature computation (245 lines)
├── train_model.py            # Model training (135 lines)
├── mitigation.py             # Mitigation logic (115 lines)
├── config.py                 # Configuration constants
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container image
├── postman_collection.json   # API testing
├── traffic_log.csv           # Generated traffic data
├── ddos_model.pkl            # Generated model (binary)
└── README.md                 # This file

Generated during runtime:
├── confusion_matrix.png      # Training visualization
└── *.pkl                     # Model checkpoints
```

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📄 License

This is a **demonstration system for educational purposes** only. Use at your own risk in production environments.

---

## 👨‍💻 Author

**Ketan Jain**  
[GitHub](https://github.com/ketanjain113) | [Email](mailto:your-email@example.com)

---

## 📚 References

- [scikit-learn RandomForest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [DDoS Types & Mitigation](https://owasp.org/www-community/attacks/DDoS)

---

**Built with 🛡️ for cloud security**

*Real-time DDoS detection using machine learning — protecting web applications from malicious traffic.*

1. **app.py** - Flask web server with real-time DDoS detection middleware
2. **feature_extraction.py** - Computes ML features from traffic data
3. **train_model.py** - Trains and evaluates the detection model
4. **mitigation.py** - IP blocking and rate limiting logic
5. **simulate_traffic.py** - Generates training data via traffic simulation
6. **requirements.txt** - Python dependency specifications
7. **Dockerfile** - Container configuration for deployment

## Features

### Real-time Detection
- **7 behavioral features** extracted from request patterns
- **Cyclical time encoding** for time-of-day patterns
- **Sub-second latency** for inference
- **Thread-safe** in-memory request log with auto-pruning

### Attack Classification
- **Normal (0)**: Legitimate user traffic
- **Suspicious (1)**: Rate limiting applied
- **Attack (2)**: IP blocked immediately

### Mitigation Strategies
1. **IP Blocking** - 404-style response, 5-minute auto-recovery
2. **Rate Limiting** - Sleep penalty for suspicious traffic
3. **Auto-Recovery** - Background thread unblocks IPs after cooldown
4. **Statistics API** - Monitor protection metrics in real-time

## Setup Instructions

### Prerequisites
- Python 3.11+
- pip or conda package manager

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Training Data

The system first needs to simulate traffic to train the model:

```bash
# Start Flask server (keep running in one terminal)
python app.py

# In another terminal, run the traffic simulation
python simulate_traffic.py
```

This will:
1. Send 500 normal requests from random IPs
2. Send 1000 attack requests from each of 3 attacker IPs
3. Send 200 suspicious requests from 2 IPs
4. Log all traffic to `traffic_log.csv`

### 3. Train the Model

After simulation completes:

```bash
python train_model.py
```

This will:
1. Load features from `traffic_log.csv`
2. Train Random Forest and SVM models
3. Evaluate on test data (80/20 split)
4. Save best model as `ddos_model.pkl`
5. Generate `confusion_matrix.png`

### 4. Run the Protection System

```bash
python app.py
```

The system will:
- Load the trained model
- Start the Flask server on `http://localhost:5000`
- Begin detecting and blocking attacks
- Start auto-recovery thread

### 5. Test the System

```bash
python simulate_traffic.py
```

Monitor `/stats` endpoint to see real-time protection metrics:

```bash
curl http://localhost:5000/stats
```

## API Endpoints

### System Endpoints
- **GET /** - Welcome message with endpoint list
- **GET /health** - Health check (skips DDoS detection)
- **GET /stats** - Protection statistics and recent detections

### Application Endpoints
- **GET /login** - Login endpoint
- **GET /api/data** - Data retrieval endpoint
- **POST /api/submit** - Data submission endpoint

## Feature Extraction

### Training Features (per 10-second window per IP)

| Feature | Description | Unit |
|---------|-------------|------|
| request_rate | Requests in last 10 seconds | count |
| ip_frequency | Unique requests from IP in 60s | count |
| unique_endpoints | Different endpoints hit | count |
| error_rate | Fraction of 4xx/5xx responses | fraction |
| avg_payload_size | Mean request body size | bytes |
| inter_arrival_time | Mean time between requests | seconds |
| session_duration | Time span of requests | seconds |
| time_of_day_sin | Hour of day (sine encoding) | [-1, 1] |
| time_of_day_cos | Hour of day (cosine encoding) | [-1, 1] |

### Real-time Features

Same features computed on-the-fly from in-memory request log (last 60 seconds).

## Model Performance

After training on simulated data, you'll see:
- Classification report with precision, recall, F1-score
- Feature importance rankings
- Confusion matrix visualization
- Model accuracy on test set (typically 95%+)

## Data Logging

### traffic_log.csv
Columns:
- **timestamp** - ISO format timestamp
- **ip** - Client IP (respects X-Forwarded-For header)
- **endpoint** - Request path
- **method** - HTTP method (GET/POST)
- **status_code** - Response status code
- **payload_size** - Request body size in bytes
- **label** - Traffic class (0=normal, 1=suspicious, 2=attack)

## Thread Safety

All shared state uses locks:
- `request_log_lock` - Protects in-memory request log
- `mitigation.lock` - Protects blocked_ips and rate_limited_ips dicts

Auto-pruning in `prune_request_log()` prevents memory leaks from the request log.

## Docker Deployment

### Build Image

```bash
docker build -t ddos-protection:latest .
```

### Run Container

```bash
docker run -p 5000:5000 -v $(pwd)/data:/app/data ddos-protection:latest
```

Note: Model file `ddos_model.pkl` must be generated before running.

## Configuration

Key parameters can be adjusted in the source files:

| Setting | File | Default | Purpose |
|---------|------|---------|---------|
| Block cooldown | mitigation.py | 300s (5 min) | Duration before IP auto-unblock |
| Rate limit threshold | mitigation.py | 50 requests | Requests before rate limiting kicks in |
| Request log window | feature_extraction.py | 60s | Window for computing features |
| Feature window | feature_extraction.py | 10s | Time window for aggregation |
| Model type | train_model.py | RandomForest | ML classifier (can change to SVM) |
| Flask port | app.py | 5000 | Server listen port |

## Troubleshooting

### "Model file not found"
Run `train_model.py` first to generate `ddos_model.pkl`

### Server won't start
- Check if port 5000 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Low accuracy in training
- Ensure `simulate_traffic.py` completes fully
- Check `traffic_log.csv` has all three traffic types
- Increase n_estimators in RandomForestClassifier

### Memory issues
- Request log auto-prunes entries > 60 seconds old
- Check system memory if handling millions of requests
- Consider implementing persistent storage

## Performance Metrics

Typical performance on a laptop:
- **Model load time**: < 100ms
- **Feature extraction**: < 1ms per request
- **Prediction latency**: < 5ms
- **Throughput**: 1000+ requests/second
- **Memory footprint**: ~50MB (model + buffers)

## Advanced Usage

### Using SVM Instead of Random Forest

Edit `train_model.py` and change the save logic:

```python
best_model = svm_model  # Instead of rf_model
```

### Custom Feature Engineering

Extend `feature_extraction.py` with additional features:
- Geo-IP blocking
- User-agent analysis
- Request pattern fingerprinting
- Behavioral ML (isolation forest)

### Integration with External Systems

Hook the `/stats` endpoint to:
- Monitoring dashboards (Grafana, Datadog)
- Alerting systems (PagerDuty, Slack)
- Incident management (Jira, Azure DevOps)

## Files Summary

```
ddos-protection/
├── app.py                    # Main Flask server (478 lines)
├── simulate_traffic.py       # Traffic simulator (271 lines)
├── feature_extraction.py     # Feature computation (245 lines)
├── train_model.py            # Model training (135 lines)
├── mitigation.py             # Mitigation logic (115 lines)
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container configuration
└── README.md                 # This file

Generated during runtime:
├── traffic_log.csv           # Traffic data log
├── ddos_model.pkl            # Trained model (binary)
└── confusion_matrix.png      # Training visualization
```

## License

This is a demonstration system for educational purposes.

## Future Enhancements

1. **Distributed Detection** - Multi-server model ensembles
2. **Adaptive Learning** - Online model updates with new attack patterns
3. **Geographic Analysis** - GeoIP blocking and regional thresholds
4. **SIEM Integration** - Send logs to Splunk, ELK, etc.
5. **Advanced Evasion** - Detect sophisticated attack variations
6. **API Rate Limiting** - Per-user API quotas
7. **DDoS Resilience** - Fallback DNS, anycast routing
8. **Honeypot Integration** - Detect reconnaissance phases

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review error logs in console output
3. Inspect `traffic_log.csv` for data quality
4. Check Flask debug output for request details

---

**Built with 🛡️ for cloud security**

System designed to detect DDoS attacks using machine learning in real-time, with automatic mitigation to protect web applications.
