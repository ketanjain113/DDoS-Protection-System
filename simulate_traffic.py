"""
Traffic simulation for DDoS detection model training and testing.
Generates normal, attack, and suspicious traffic patterns.
"""
import requests
import time
import random
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('--url', type=str, default='http://localhost:5000',
                    help='Base URL of the Flask server')
parser.add_argument('--mode', type=str, default='all', choices=['all', 'normal', 'attack', 'suspicious'],
                    help='Which simulation to run')
parser.add_argument('--normal-requests', type=int, default=500,
                    help='Number of normal requests to send')
parser.add_argument('--attack-requests', type=int, default=1000,
                    help='Number of requests per attack IP')
parser.add_argument('--suspicious-requests', type=int, default=200,
                    help='Number of suspicious requests per suspicious IP')
parser.add_argument('--attack-ips', type=int, default=3,
                    help='Number of attacker IPs to use in full simulation')
parser.add_argument('--suspicious-ips', type=int, default=2,
                    help='Number of suspicious IPs to use in full simulation')
args = parser.parse_args()
BASE_URL = args.url

# Random pool of fake IP addresses
FAKE_IPS = [f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}" 
            for _ in range(50)]

ENDPOINTS = [
    ('GET', '/'),
    ('GET', '/login'),
    ('GET', '/api/data'),
    ('POST', '/api/submit'),
    ('GET', '/health')
]

TRAFFIC_LOG = 'traffic_log.csv'


def log_traffic(ip, endpoint, method, status_code, payload_size, label):
    timestamp = datetime.now().isoformat()
    with open(TRAFFIC_LOG, 'a') as f:
        f.write(f"{timestamp},{ip},{endpoint},{method},{status_code},{payload_size},{label}\n")


def make_request(method, url, ip, endpoint, payload_size, timeout=5):
    try:
        headers = {'X-Forwarded-For': ip}
        data = 'X' * payload_size  # Simple payload

        request_kwargs = {
            'url': url,
            'headers': headers,
            'timeout': timeout,
        }
        if method.upper() == 'POST':
            request_kwargs['data'] = data

        response = requests.request(method.upper(), **request_kwargs)
        return response.status_code, payload_size
    except Exception as e:
        print(f"[ERROR] Request to {endpoint} from {ip} failed: {e}")
        return None, None


def simulate_normal(n=500):
    """
    Simulate normal traffic from many different IPs.
    
    Args:
        n (int): Number of requests to simulate
    """
    print(f"\n[SIMULATION] Starting NORMAL traffic simulation ({n} requests)...")
    
    for i in range(n):
        # Random IP from pool
        ip = random.choice(FAKE_IPS)
        
        # Random endpoint
        method, endpoint = random.choice(ENDPOINTS)
        
        # Build URL
        url = f"{BASE_URL}{endpoint}" if endpoint != '/' else BASE_URL
        
        # Random delay and payload
        delay = random.uniform(0.5, 2.0)
        payload_size = random.randint(100, 1000)
        
        # Make request
        status_code, ps = make_request(method, url, ip, endpoint, payload_size)
        
        if status_code:
            log_traffic(ip, endpoint, method, status_code, ps, label=0)
        
        if i % 50 == 0:
            print(f"  Sent {i+1}/{n} requests")
        
        time.sleep(delay)
    
    print(f"[SIMULATION] NORMAL traffic simulation complete!")


def simulate_attack(attacker_ip, n=1000):
    """
    Simulate DDoS attack from a single IP.
    High-frequency requests with large payloads.
    
    Args:
        attacker_ip (str): IP address launching the attack
        n (int): Number of attack requests
    """
    print(f"\n[SIMULATION] Starting ATTACK from {attacker_ip} ({n} requests)...")
    
    method = 'GET'
    endpoint = '/api/data'
    url = f"{BASE_URL}{endpoint}"
    payload_size = 5000  # Large payload
    
    for i in range(n):
        # Very short delay between requests (high frequency)
        delay = 0.01
        
        # Make request
        status_code, ps = make_request(method, url, attacker_ip, endpoint, payload_size)
        
        if status_code:
            log_traffic(attacker_ip, endpoint, method, status_code, ps, label=2)  # label=2 for attack
        
        if i % 200 == 0:
            print(f"  Sent {i+1}/{n} attack requests from {attacker_ip}")
        
        time.sleep(delay)
    
    print(f"[SIMULATION] ATTACK simulation complete!")


def simulate_suspicious(ip, n=200):
    """
    Simulate suspicious traffic pattern.
    Medium request rate with multiple endpoints.
    
    Args:
        ip (str): IP address with suspicious activity
        n (int): Number of suspicious requests
    """
    print(f"\n[SIMULATION] Starting SUSPICIOUS traffic from {ip} ({n} requests)...")
    
    for i in range(n):
        # Random endpoint (multiple different ones)
        method, endpoint = random.choice(ENDPOINTS)
        
        # Build URL
        url = f"{BASE_URL}{endpoint}" if endpoint != '/' else BASE_URL
        
        # Medium delay and moderate payload
        delay = 0.1
        payload_size = random.randint(500, 2000)
        
        # Make request
        status_code, ps = make_request(method, url, ip, endpoint, payload_size)
        
        if status_code:
            log_traffic(ip, endpoint, method, status_code, ps, label=1)  # label=1 for suspicious
        
        if i % 50 == 0:
            print(f"  Sent {i+1}/{n} suspicious requests")
        
        time.sleep(delay)
    
    print(f"[SIMULATION] SUSPICIOUS traffic simulation complete!")


def initialize_traffic_log():
    """Initialize traffic log CSV with headers."""
    with open(TRAFFIC_LOG, 'w') as f:
        f.write("timestamp,ip,endpoint,method,status_code,payload_size,label\n")
    print(f"[INIT] Traffic log initialized: {TRAFFIC_LOG}")


def run_simulation():
    """
    Run complete traffic simulation.
    1. Normal traffic
    2. DDoS attacks from configured attacker IPs
    3. Suspicious traffic from configured suspicious IPs
    """
    print("=" * 60)
    print("DDoS TRAFFIC SIMULATION STARTED")
    print("=" * 60)
    
    # Initialize traffic log
    initialize_traffic_log()
    
    # Wait a moment for server to be ready
    print("\n[WAIT] Waiting 3 seconds for server to be ready...")
    time.sleep(3)
    
    # Simulate traffic in sequence
    try:
        attack_ips = [f"10.0.0.{i+1}" for i in range(args.attack_ips)]
        suspicious_ips = [f"172.16.0.{i+1}" for i in range(args.suspicious_ips)]

        if args.mode in ('all', 'normal'):
            simulate_normal(n=args.normal_requests)

        if args.mode in ('all', 'attack'):
            for attack_ip in attack_ips:
                simulate_attack(attack_ip, n=args.attack_requests)
                time.sleep(2)  # Pause between attacks

        if args.mode in ('all', 'suspicious'):
            for susp_ip in suspicious_ips:
                simulate_suspicious(susp_ip, n=args.suspicious_requests)
                time.sleep(1)
        
        print("\n" + "=" * 60)
        print("DDoS TRAFFIC SIMULATION COMPLETE")
        print("=" * 60)
        print(f"Check {TRAFFIC_LOG} for the generated traffic data.")
        
    except Exception as e:
        print(f"\n[ERROR] Simulation failed: {e}")
        print(f"Make sure Flask server is running on {BASE_URL}")


if __name__ == '__main__':
    run_simulation()
