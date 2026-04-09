"""
Configuration file for DDoS Protection System.
Centralized settings for easy customization.
"""

# ============================================================================
# SERVER CONFIGURATION
# ============================================================================
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
FLASK_DEBUG = False
FLASK_THREADED = True

# ============================================================================
# MODEL CONFIGURATION  
# ============================================================================
MODEL_PATH = 'ddos_model.pkl'
MODEL_TYPE = 'RandomForest'  # or 'SVM'

# RandomForest parameters
RF_N_ESTIMATORS = 100
RF_RANDOM_STATE = 42
RF_CRITERION = 'gini'

# SVM parameters
SVM_KERNEL = 'rbf'
SVM_GAMMA = 'scale'
SVM_RANDOM_STATE = 42

# Train/Test split
TEST_SPLIT_RATIO = 0.2
STRATIFY_LABELS = True

# ============================================================================
# FEATURE EXTRACTION CONFIGURATION
# ============================================================================
REQUEST_LOG_WINDOW = 60  # seconds - keep track of last 60 seconds
FEATURE_WINDOW = 10     # seconds - compute features per 10-second window
FEATURE_COLUMNS = [
    'request_rate',
    'ip_frequency',
    'unique_endpoints',
    'error_rate',
    'avg_payload_size',
    'inter_arrival_time',
    'session_duration',
    'time_of_day_sin',
    'time_of_day_cos'
]

# ============================================================================
# MITIGATION CONFIGURATION
# ============================================================================
# IP Blocking
BLOCK_COOLDOWN_SECONDS = 300  # 5 minutes - how long to block an IP
ENABLE_AUTO_RECOVERY = True    # Auto-unblock IPs after cooldown

# Rate Limiting
RATE_LIMIT_THRESHOLD = 50      # Request count threshold before rate limiting
RATE_LIMIT_SLEEP = 0.5         # Seconds to sleep when rate limit exceeded
AUTO_RECOVERY_INTERVAL = 60    # Seconds between auto-recovery checks

# ============================================================================
# TRAFFIC LOGGING
# ============================================================================
TRAFFIC_LOG_PATH = 'traffic_log.csv'
LOG_COLUMNS = [
    'timestamp',
    'ip',
    'endpoint',
    'method',
    'status_code',
    'payload_size',
    'label'
]

# Label definitions
LABEL_NORMAL = 0
LABEL_SUSPICIOUS = 1
LABEL_ATTACK = 2

# ============================================================================
# DETECTION THRESHOLDS
# ============================================================================
# Prediction mappings
PREDICTION_MAPPING = {
    0: 'NORMAL',
    1: 'SUSPICIOUS',
    2: 'ATTACK'
}

# Actions based on prediction
PREDICTION_ACTIONS = {
    0: 'allow',          # Normal: allow request
    1: 'rate_limit',     # Suspicious: rate limit
    2: 'block'           # Attack: block IP
}

# ============================================================================
# TRAFFIC SIMULATION CONFIGURATION
# ============================================================================
# IP pool for simulation
FAKE_IP_POOL_SIZE = 50

# Normal traffic
NORMAL_REQUESTS = 500
NORMAL_REQUEST_DELAY_MIN = 0.5  # seconds
NORMAL_REQUEST_DELAY_MAX = 2.0  # seconds
NORMAL_PAYLOAD_MIN = 100        # bytes
NORMAL_PAYLOAD_MAX = 1000       # bytes

# Attack traffic
ATTACK_REQUESTS = 1000
ATTACK_REQUEST_DELAY = 0.01     # seconds - high frequency
ATTACK_PAYLOAD = 5000           # bytes - large payload
ATTACK_IPS = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

# Suspicious traffic
SUSPICIOUS_REQUESTS = 200
SUSPICIOUS_REQUEST_DELAY = 0.1  # seconds
SUSPICIOUS_PAYLOAD_MIN = 500    # bytes
SUSPICIOUS_PAYLOAD_MAX = 2000   # bytes
SUSPICIOUS_IPS = ["172.16.0.1", "172.16.0.2"]

# ============================================================================
# ENDPOINTS CONFIGURATION
# ============================================================================
PROTECTED_ENDPOINTS = [
    '/',
    '/login',
    '/api/data',
    '/api/submit'
]

SKIP_MIDDLEWARE_ENDPOINTS = [
    '/health',
    '/static/'
]

# ============================================================================
# LOGGING AND MONITORING
# ============================================================================
ENABLE_CONSOLE_LOGGING = True
ENABLE_FILE_LOGGING = True
LOG_FORMAT = '[%(levelname)s] %(message)s'
LOG_FILE = 'ddos_protection.log'

# Statistics
STATS_RECENT_DETECTIONS_COUNT = 10  # How many recent detections to track
STATS_UPDATE_INTERVAL = 60          # Seconds between stats updates

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================
# Thread settings
USE_THREADING = True
THREAD_POOL_SIZE = 10

# Request log
MAX_REQUEST_LOG_SIZE = 10000  # Max requests to keep in memory per IP
AUTO_PRUNE_INTERVAL = 60      # Seconds between pruning operations

# Model
BATCH_PREDICTION = False      # Batch predictions vs single
CACHE_FEATURES = False        # Cache computed features

# ============================================================================
# SECURITY
# ============================================================================
# Header validation
TRUSTED_HEADERS = ['X-Forwarded-For', 'X-Real-IP']
VALIDATE_HEADERS = True

# Request validation
MAX_PAYLOAD_SIZE = 10000  # bytes - reject larger payloads
MIN_PAYLOAD_SIZE = 0      # bytes

# ============================================================================
# DOCKER & DEPLOYMENT
# ============================================================================
DOCKER_PORT = 5000
DOCKER_IMAGE_NAME = 'ddos-protection'
DOCKER_IMAGE_TAG = 'latest'

# Environment detection
RUNNING_IN_DOCKER = False  # Set automatically based on environment

# ============================================================================
# DEVELOPMENT & DEBUGGING
# ============================================================================
DEBUG_MODE = False
VERBOSE_LOGGING = False
PRINT_FEATURE_VECTORS = False
SAVE_PREDICTIONS = False  # Save all predictions for analysis

# ============================================================================
# Helper function to get all config
# ============================================================================
def get_config():
    """Get all configuration as dictionary."""
    return {
        'server': {
            'host': FLASK_HOST,
            'port': FLASK_PORT,
            'debug': FLASK_DEBUG
        },
        'model': {
            'path': MODEL_PATH,
            'type': MODEL_TYPE
        },
        'mitigation': {
            'block_cooldown': BLOCK_COOLDOWN_SECONDS,
            'rate_limit_threshold': RATE_LIMIT_THRESHOLD
        },
        'features': {
            'window': FEATURE_WINDOW,
            'columns': len(FEATURE_COLUMNS)
        },
        'logging': {
            'path': TRAFFIC_LOG_PATH,
            'columns': len(LOG_COLUMNS)
        }
    }

if __name__ == '__main__':
    import json
    print(json.dumps(get_config(), indent=2))
