from abc import ABC, abstractmethod

class BaseExfiltrator(ABC):
    """Base class for data exfiltration methods"""

    @abstractmethod
    def get_exfil_url(self):
        """Return the URL or endpoint for exfiltration"""
        pass

    @abstractmethod
    def process_data(self, data):
        """Process the exfiltrated data"""
        pass
