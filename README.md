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

## 📄 License

Educational demonstration only.

## 👨‍💻 Author

**Ketan Jain** — [GitHub](https://github.com/ketanjain113)

---

**Built with 🛡️ for cloud security**

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
