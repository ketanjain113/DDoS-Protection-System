import pandas as pd
import numpy as np
from datetime import datetime
import math

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


def extract_features(log_path='traffic_log.csv'):
    df = pd.read_csv(log_path)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Set timestamp as index for resampling
    df.set_index('timestamp', inplace=True)
    
    # Group by IP and 10-second windows
    features_list = []
    
    for ip in df['ip'].unique():
        ip_data = df[df['ip'] == ip]
        
        # Resample to 10-second windows
        windows = ip_data.resample('10s')
        
        for window_start, window_df in windows:
            if len(window_df) == 0:
                continue
            
            # Calculate features for this window
            request_rate = len(window_df)  # requests per 10 seconds
            
            # ip_frequency: count per 60 seconds (approximate with all data for now)
            ip_frequency = len(ip_data)
            
            # unique_endpoints: number of unique endpoints hits in this window
            unique_endpoints = window_df['endpoint'].nunique()
            
            # error_rate: fraction of requests with status >= 400
            error_count = (window_df['status_code'] >= 400).sum()
            error_rate = error_count / len(window_df) if len(window_df) > 0 else 0
            
            # avg_payload_size: mean payload size
            avg_payload_size = window_df['payload_size'].mean()
            
            # inter_arrival_time: mean time between requests
            if len(window_df) > 1:
                times = window_df.index
                inter_arrival_times = (times[1:] - times[:-1]).total_seconds()
                inter_arrival_time = inter_arrival_times.mean()
            else:
                inter_arrival_time = 0
            
            # session_duration: time span of requests in window
            session_duration = (window_df.index.max() - window_df.index.min()).total_seconds()
            
            # time_of_day_sin and cos: cyclical encoding of hour
            hour = window_start.hour
            time_of_day_sin = math.sin(2 * math.pi * hour / 24)
            time_of_day_cos = math.cos(2 * math.pi * hour / 24)
            
            # Get majority label for this window
            label = window_df['label'].mode()[0] if len(window_df) > 0 else 0
            
            features_list.append({
                'request_rate': request_rate,
                'ip_frequency': ip_frequency,
                'unique_endpoints': unique_endpoints,
                'error_rate': error_rate,
                'avg_payload_size': avg_payload_size,
                'inter_arrival_time': inter_arrival_time,
                'session_duration': session_duration,
                'time_of_day_sin': time_of_day_sin,
                'time_of_day_cos': time_of_day_cos,
                'label': label,
                'ip': ip
            })
    
    # Create DataFrame
    features_df = pd.DataFrame(features_list)
    
    # Drop rows with NaN
    features_df = features_df.dropna()
    
    return features_df


def get_live_features(ip, request_log):
    if ip not in request_log or len(request_log[ip]) == 0:
        # Return default features for unknown IP
        return [0] * len(FEATURE_COLUMNS)
    
    requests = request_log[ip]
    
    if len(requests) == 0:
        return [0] * len(FEATURE_COLUMNS)
    
    # Convert to list of timestamps and statuses
    timestamps = [r['timestamp'] for r in requests]
    statuses = [r['status_code'] for r in requests]
    payloads = [r['payload_size'] for r in requests]
    endpoints = [r['endpoint'] for r in requests]
    
    # request_rate: requests in last 10 seconds
    now = datetime.now()
    recent_requests = [t for t in timestamps if (now - t).total_seconds() <= 10]
    request_rate = len(recent_requests)
    
    # ip_frequency: requests in last 60 seconds
    freq_requests = [t for t in timestamps if (now - t).total_seconds() <= 60]
    ip_frequency = len(freq_requests)
    
    # unique_endpoints: unique endpoints in last 60 seconds
    freq_endpoints = [r['endpoint'] for r in requests 
                      if (now - r['timestamp']).total_seconds() <= 60]
    unique_endpoints = len(set(freq_endpoints))
    
    # error_rate: fraction with status >= 400 in last 60 seconds
    freq_statuses = [r['status_code'] for r in requests 
                     if (now - r['timestamp']).total_seconds() <= 60]
    error_count = sum(1 for s in freq_statuses if s >= 400)
    error_rate = error_count / len(freq_statuses) if len(freq_statuses) > 0 else 0
    
    # avg_payload_size: mean of recent payloads
    freq_payloads = [r['payload_size'] for r in requests 
                     if (now - r['timestamp']).total_seconds() <= 60]
    avg_payload_size = np.mean(freq_payloads) if len(freq_payloads) > 0 else 0
    
    # inter_arrival_time: mean time between requests
    if len(timestamps) > 1:
        inter_arrival_times = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                               for i in range(len(timestamps)-1)]
        inter_arrival_time = np.mean(inter_arrival_times)
    else:
        inter_arrival_time = 0
    
    # session_duration: time span from first to last request
    if len(timestamps) > 1:
        session_duration = (max(timestamps) - min(timestamps)).total_seconds()
    else:
        session_duration = 0
    
    # time_of_day_sin and cos
    hour = now.hour
    time_of_day_sin = math.sin(2 * math.pi * hour / 24)
    time_of_day_cos = math.cos(2 * math.pi * hour / 24)
    
    return [
        request_rate,
        ip_frequency,
        unique_endpoints,
        error_rate,
        avg_payload_size,
        inter_arrival_time,
        session_duration,
        time_of_day_sin,
        time_of_day_cos
    ]
