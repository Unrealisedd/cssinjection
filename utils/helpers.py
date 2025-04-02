import logging
import base64
import re
import urllib.parse

logger = logging.getLogger('exfilx')

def encode_for_url(data):
    """Encode data to be safely included in a URL"""
    return urllib.parse.quote(data)

def decode_from_url(data):
    """Decode URL-encoded data"""
    return urllib.parse.unquote(data)

def encode_to_base64(data):
    """Encode data to base64"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return base64.b64encode(data).decode('utf-8')

def decode_from_base64(data):
    """Decode base64 data"""
    return base64.b64decode(data).decode('utf-8')

def encode_to_hex(data):
    """Encode data to hexadecimal"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    return data.hex()

def decode_from_hex(data):
    """Decode hexadecimal data"""
    return bytes.fromhex(data).decode('utf-8')

def chunk_data(data, chunk_size=63):
    """
    Split data into chunks for DNS exfiltration
    DNS labels are limited to 63 characters
    """
    return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]

def detect_sensitive_data(text):
    """
    Detect potentially sensitive data patterns in text
    Returns a dictionary of detected data types and values
    """
    patterns = {
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'phone': r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
        'ip_address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
    }

    results = {}

    for data_type, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            results[data_type] = matches

    return results

def sanitize_output(data):
    """Sanitize data for display (e.g., mask sensitive information)"""
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            if key in ['password', 'credit_card', 'ssn']:
                if isinstance(value, list):
                    sanitized[key] = ['*' * len(str(v)) for v in value]
                else:
                    sanitized[key] = '*' * len(str(value))
            else:
                sanitized[key] = value
        return sanitized
    return data
