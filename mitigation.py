import time
import threading
from datetime import datetime

# Global dictionaries to track blocked and rate-limited IPs
blocked_ips = {}  # ip -> block_timestamp
rate_limited_ips = {}  # ip -> request_count
lock = threading.Lock()  # Lock for thread-safe access
total_mitigations = 0  # Counter for total mitigation actions
detection_log = []  # Store last detections for /stats endpoint


def block_ip(ip):
    global total_mitigations
    with lock:
        blocked_ips[ip] = time.time()
        total_mitigations += 1
        print(f"[MITIGATION] IP {ip} has been BLOCKED at {datetime.now().isoformat()}")
        detection_log.append({
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'action': 'BLOCKED'
        })
        # Keep only last 10 detections
        if len(detection_log) > 10:
            detection_log.pop(0)


def rate_limit(ip):
    global total_mitigations
    with lock:
        if ip not in rate_limited_ips:
            rate_limited_ips[ip] = 0
        rate_limited_ips[ip] += 1
        
        if rate_limited_ips[ip] > 50:
            detection_log.append({
                'timestamp': datetime.now().isoformat(),
                'ip': ip,
                'action': 'RATE_LIMITED'
            })
            # Keep only last 10 detections
            if len(detection_log) > 10:
                detection_log.pop(0)
            total_mitigations += 1
            print(f"[MITIGATION] IP {ip} is RATE LIMITED (count: {rate_limited_ips[ip]})")
            time.sleep(0.5)


def is_blocked(ip):
    with lock:
        return ip in blocked_ips


def auto_recover():
    with lock:
        current_time = time.time()
        to_remove = []
        
        for ip, block_time in blocked_ips.items():
            if current_time - block_time > 300:  # 5 minutes = 300 seconds
                to_remove.append(ip)
        
        for ip in to_remove:
            del blocked_ips[ip]
            print(f"[RECOVERY] IP {ip} has been UNBLOCKED after 5-minute cooldown")
        
        # Reset rate limiting counters
        rate_limited_ips.clear()


def get_mitigation_stats():
    with lock:
        return {
            'blocked_ips_count': len(blocked_ips),
            'rate_limited_ips_count': len(rate_limited_ips),
            'total_mitigations': total_mitigations,
            'detection_log': detection_log.copy()
        }
