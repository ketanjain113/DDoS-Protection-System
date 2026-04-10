import sys
import os
import csv
import time
import threading
import joblib
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

# Import mitigation and feature extraction modules
import mitigation
from mitigation import block_ip, rate_limit, is_blocked, auto_recover, get_mitigation_stats
from feature_extraction import get_live_features, FEATURE_COLUMNS

# Flask app initialization
app = Flask(__name__)

# Configuration
MODEL_PATH = 'ddos_model.pkl'
TRAFFIC_LOG = 'traffic_log.csv'
PORT = 5000

# In-memory request log: dict keyed by IP, storing list of request dicts
request_log = {}
request_log_lock = threading.Lock()

# Global model
ddos_model = None
bootstrap_done = False
bootstrap_lock = threading.Lock()


def load_model():
    global ddos_model
    
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model file not found: {MODEL_PATH}")
        print("[ERROR] Please run train_model.py first to generate the model.")
        return False
    
    try:
        ddos_model = joblib.load(MODEL_PATH)
        print(f"[STARTUP] Model loaded successfully from {MODEL_PATH}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return False


def init_traffic_log():
    if not os.path.exists(TRAFFIC_LOG):
        with open(TRAFFIC_LOG, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'ip', 'endpoint', 'method', 'status_code', 'payload_size', 'label'])
        print(f"[STARTUP] Traffic log initialized: {TRAFFIC_LOG}")


def log_request(ip, endpoint, method, status_code, payload_size, label=0):
    try:
        with open(TRAFFIC_LOG, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                ip,
                endpoint,
                method,
                status_code,
                payload_size,
                label
            ])
    except Exception as e:
        print(f"[ERROR] Failed to log request: {e}")


def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs, take the first one
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr


def prune_request_log(ip, max_age_seconds=60):
    if ip not in request_log:
        return
    
    cutoff_time = datetime.now() - timedelta(seconds=max_age_seconds)
    request_log[ip] = [r for r in request_log[ip] if r['timestamp'] > cutoff_time]
    
    # Remove IP from dict if no requests left
    if len(request_log[ip]) == 0:
        del request_log[ip]


def update_request_log(ip, endpoint, method, payload_size, status_code):
    with request_log_lock:
        if ip not in request_log:
            request_log[ip] = []
        
        request_log[ip].append({
            'timestamp': datetime.now(),
            'endpoint': endpoint,
            'method': method,
            'payload_size': payload_size,
            'status_code': status_code
        })
        
        # Prune old entries
        prune_request_log(ip, max_age_seconds=60)


def detect_ip_activity(ip):
    if is_blocked(ip):
        return 'attack'

    try:
        with request_log_lock:
            features = get_live_features(ip, request_log)
    except Exception:
        features = [0] * len(FEATURE_COLUMNS)

    if ddos_model is None:
        return 'normal'

    try:
        feature_df = pd.DataFrame([features], columns=FEATURE_COLUMNS)
        prediction = ddos_model.predict(feature_df)[0]
    except Exception:
        return 'normal'

    if prediction == 2:
        return 'attack'
    if prediction == 1:
        return 'suspicious'
    return 'normal'


@app.before_request
def ddos_detection_middleware():
    if request.path == '/health' or request.path.startswith('/static/'):
        return None
    
    client_ip = get_client_ip()
    
    if is_blocked(client_ip):
        print(f"[BLOCK] Request from blocked IP {client_ip} rejected")
        return jsonify({'error': 'IP is blocked due to suspicious activity'}), 403
    
    # Extract request features
    try:
        with request_log_lock:
            features = get_live_features(client_ip, request_log)
    except Exception as e:
        print(f"[ERROR] Failed to extract features: {e}")
        features = [0] * len(FEATURE_COLUMNS)
    
    # Predict using model
    try:
        if ddos_model is not None:
            feature_df = pd.DataFrame([features], columns=FEATURE_COLUMNS)
            prediction = ddos_model.predict(feature_df)[0]
            
            # Handle predictions
            if prediction == 2:  # Attack detected
                print(f"[DETECT] ATTACK detected from {client_ip}")
                block_ip(client_ip)
                return jsonify({'error': 'Your IP has been blocked due to malicious activity'}), 403
            
            elif prediction == 1:  # Suspicious activity
                print(f"[DETECT] SUSPICIOUS activity from {client_ip}")
                rate_limit(client_ip)
    
    except Exception as e:
        print(f"[ERROR] Model prediction failed: {e}")
    
    # Update in-memory request log (will be done in after_request for status code)
    return None


@app.after_request
def log_and_update(response):
    # Skip for health check
    if request.path == '/health':
        return response
    
    client_ip = get_client_ip()
    endpoint = request.path
    method = request.method
    status_code = response.status_code
    
    # Get payload size from request
    payload_size = len(request.get_data()) if request.get_data() else 0
    
    # Update in-memory request log
    update_request_log(client_ip, endpoint, method, payload_size, status_code)
    
    # Log to CSV (default label=0 for normal, will be updated during training)
    log_request(client_ip, endpoint, method, status_code, payload_size, label=0)
    
    return response


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Welcome to DDoS Protection System',
        'endpoints': {
            '/': 'Home',
            '/login': 'Login endpoint',
            '/api/data': 'Data API',
            '/api/submit': 'Submit data',
            '/health': 'Health check',
            '/stats': 'Protection statistics'
        }
    }), 200


@app.route('/login', methods=['GET'])
def login():
    return jsonify({
        'message': 'Login page',
        'status': 'ok'
    }), 200


@app.route('/api/data', methods=['GET'])
def api_data():
    """Data API endpoint."""
    return jsonify({
        'data': [1, 2, 3, 4, 5],
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/submit', methods=['POST'])
def api_submit():
    data = request.get_json() or {}
    return jsonify({
        'message': 'Data received',
        'id': 12345,
        'received_at': datetime.now().isoformat()
    }), 201


@app.route('/health', methods=['GET'])
def health():
    model_loaded = os.path.exists('ddos_model.pkl')
    return jsonify({"status": "ok", "model_loaded": model_loaded}), 200


@app.route('/stats', methods=['GET'])
def stats():
    stats_data = get_mitigation_stats()
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'blocked_ips': stats_data['blocked_ips_count'],
        'rate_limited_ips': stats_data['rate_limited_ips_count'],
        'total_mitigations': stats_data['total_mitigations'],
        'recent_detections': stats_data['detection_log'][-10:] 
    }), 200


@app.route('/simulate/attack', methods=['POST'])
def simulate_attack_endpoint():
    data = request.get_json() or {}
    target_ip = data.get('target_ip', '192.168.1.100')
    num_requests = data.get('requests', 100)
    min_requests_for_block = int(data.get('min_requests_for_block', 30))
    min_blocked_requests_for_ip_block = int(data.get('min_blocked_requests_for_ip_block', 5))
    with request_log_lock:
        prune_request_log(target_ip, max_age_seconds=60)
        baseline_count = len(request_log.get(target_ip, []))

    results = {
        "allowed": 0,
        "blocked": 0,
        "target_ip": target_ip,
        "min_requests_for_block": min_requests_for_block,
        "min_blocked_requests_for_ip_block": min_blocked_requests_for_ip_block
    }
    blocked_detections = 0

    for _ in range(num_requests):
        if mitigation.is_blocked(target_ip):
            results["blocked"] += 1
            time.sleep(0.01)
            continue

        update_request_log(target_ip, '/api/data', 'GET', 5000, 200)

        with request_log_lock:
            current_burst_size = len(request_log.get(target_ip, [])) - baseline_count
            if current_burst_size < 0:
                current_burst_size = 0

        detection_result = detect_ip_activity(target_ip)
        if detection_result == 'attack' and current_burst_size >= min_requests_for_block:
            blocked_detections += 1
            results["blocked"] += 1

            if blocked_detections >= min_blocked_requests_for_ip_block:
                mitigation.block_ip(target_ip)
        else:
            results["allowed"] += 1
        time.sleep(0.01)
    return jsonify(results)


@app.route('/simulate/normal', methods=['POST'])
def simulate_normal_endpoint():
    import random
    data = request.get_json() or {}
    num_requests = data.get('requests', 50)
    ip_pool = [f"10.0.{i}.{j}" for i in range(5) for j in range(5)]
    results = {"allowed": 0, "blocked": 0}
    for _ in range(num_requests):
        ip = random.choice(ip_pool)
        update_request_log(ip, '/', 'GET', random.randint(100, 1000), 200)
        detection_result = detect_ip_activity(ip)
        if detection_result == 'attack':
            mitigation.block_ip(ip)
            results["blocked"] += 1
        else:
            results["allowed"] += 1
        time.sleep(0.05)
    return jsonify(results)


def auto_recover_loop():
    while True:
        time.sleep(60)
        mitigation.auto_recover()

def start_auto_recovery_thread():
    recovery_thread = threading.Thread(target=auto_recover_loop, daemon=True)
    recovery_thread.start()
    print("[STARTUP] Auto-recovery background thread started (60s interval)")


def bootstrap_app():
    global bootstrap_done
    with bootstrap_lock:
        if bootstrap_done:
            return
        init_traffic_log()
        if not load_model():
            print("[WARNING] System will run without ML detection.")
            print("[WARNING] Requests will be logged but not filtered.")
        start_auto_recovery_thread()
        bootstrap_done = True


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response


def main():
    print("=" * 70)
    print("DDoS PROTECTION SYSTEM - STARTING UP")
    print("=" * 70)
    
    bootstrap_app()
    
    print(f"\n[STARTUP] Starting Flask server on http://0.0.0.0:{PORT}")
    print("[STARTUP] Press CTRL+C to stop\n")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=PORT, debug=False, use_reloader=False)

bootstrap_app()


if __name__ == '__main__':
    main()
