import datetime
import base64
import hashlib
from typing import Dict, Any
import sys
import traceback
from io import StringIO
import re # <-- Import the regular expression library

def _unescape_literal(s: str) -> str:
    """
    Replace every '\' with '\\' so that escape sequences survive.
    """
    return s.replace('\\', '\\\\')
#    return s.encode('utf-8').decode('unicode_escape')

def clean_input_string(input_str: str) -> str:
    """
    Strips quoting sequence from input strings 
    to ensure they are valid for use.
    """
    if not isinstance(input_str, str):
        return "" # Handle non-string input safely
    
    # Use regex to find and remove the problematic sequences:
    # <|\"|>
    cleaned = re.sub(r'<\|\"\|>', '', input_str).strip()
    return cleaned


def execute_python_code(code: str) -> Dict[str, Any]:
    """
    Executes the supplied Python code in a sandbox.

    Args:
        code: Python source to be executed.

    Returns:
    dict
        {
            "stdout": <text printed to stdout>,
            "stderr": <text printed to stderr>,
            "exception": <traceback string if an exception occurred, else None>
        }
    """
    code = clean_input_string(code)

    # ------------------------------------------------------------------ #
    # Un‑escape the incoming code (handles \\n, \\t, \\\\, etc.).
    # ------------------------------------------------------------------ #
    code = _unescape_literal(code)

    # ---- 1. Prepare isolated globals/locals ---------------------------------
    # An empty dict gives the executed code no pre‑existing names.
    # You can add a whitelist here, e.g. {"range": range, "len": len}
    safe_globals: Dict[str, Any] = {}
    safe_locals: Dict[str, Any] = {}

#    safe_globals = {
#        "__builtins__": {
#            "open": open,      # keep only open; omit os, subprocess, etc.
#            "print": print,
#        }
#    }

    # ---- 2. Capture output --------------------------------------------------
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = out_buf = StringIO()
    sys.stderr = err_buf = StringIO()

    exc_info = None

    try:
        # exec() runs the code string.  It raises any exception that occurs.
        exec(code, safe_globals, safe_locals)
    except Exception:
        # Store a nicely formatted traceback for the caller.
        exc_info = traceback.format_exc()
    finally:
        # ---- 3. Restore original streams ------------------------------------
        sys.stdout = old_out
        sys.stderr = old_err

        print(f"Code: \n{code}")
        print(f"\nStdout:\n{out_buf.getvalue()}")
        print(f"\nStderr:\n{err_buf.getvalue()}")
        print(f"\nException:\n{exc_info}")

    # ---- 4. Build the result dictionary ------------------------------------
    result = {
        "stdout": out_buf.getvalue(),
        "stderr": err_buf.getvalue(),
        "exception": exc_info,
    }
    return result

def get_current_location() -> str:
    """Returns the current location."""
    return "London"

def get_current_weather(location, unit) -> str:
    """
    Get the current weather in a given location
    Args:
        location: The city and state, e.g. San Francisco, CA.
        unit: "Celsius" or "Fahrenheit".

    """
    location = clean_input_string(location)
    unit = clean_input_string(unit)
    if "London" in location:
        return f"Weather in {location}: {22}° {unit}"
    elif "New York" in location:
        return f"Weather in {location}: {24}° {unit}"
    elif "North Pole" in location:
        return f"Weather in {location}: {-42}° {unit}"
    else:
        return f"Weather in {location}: unknown"

def calculate_hash(text_to_hash: str) -> Dict[str, str]:
    """
    Calculates the SHA-1 hash of a given text string.

    Args:
        text_to_hash: The input string whose hash is to be calculated.

    Returns:
        A dictionary containing the 'result' key with the hexadecimal hash string.
    """
    text_to_hash = clean_input_string(text_to_hash)
    
    # 1. Encode the input string to bytes using UTF-8 (Equivalent to TextEncoder().encode(message))
    input_bytes = text_to_hash.encode('utf-8')
    
    # 2. Initialize the SHA-1 hash algorithm
    hasher = hashlib.sha1()
    
    # 3. Update the hash object with the bytes (Equivalent to crypto.subtle.digest)
    hasher.update(input_bytes)
    
    # 4. Get the hexadecimal representation of the digest (Equivalent to conversion/mapping)
    hash_hex = hasher.hexdigest()
    
    # Return the result in a dictionary format, mimicking the JSON output structure
    return {"result": hash_hex}


def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def add_numbers(a: float, b: float) -> float:
    """Adds two numbers.

    Args:
        a: The first number.
        b: The second number.
    """
    return a + b

import requests
from bs4 import BeautifulSoup
from typing import Callable, Any


def query_wikipedia(topic: str, lang: str) -> str:
    """
    Query summary from Wikipedia for a given topic.

    Args:
        topic (str): Extract ONLY the primary entity, person, or event 
            (e.g., "Albert Einstein", "2026 Oscars"). 
            Search for the broad subject so the tool can return the main article. 
            For time-sensitive facts, query the specific iteration. 
            The "topic" must be in the same language as the "lang".
        lang (str): The two-letter language code for the Wikipedia article.

    Returns:
        str: A formatted text summary, including an INFOBOX, that is concise.
    """
    
    # 🎯 CRITICAL FIX: Clean the input parameters immediately upon arrival
    clean_topic = clean_input_string(topic)
    clean_lang = clean_input_string(lang)
    
    if not clean_lang or not clean_topic:
        return "Error: Invalid or empty topic or language code provided after cleaning."

    base_url = f"https://{clean_lang}.wikipedia.org/w/api.php"

    from curl_cffi import requests  # re‑exports a Session compatible with `requests`
# -------------------------------------------------
# Create a session (optional but recommended)
# -------------------------------------------------
    session = requests.Session()
    
    try:
        # Use the cleaned variables for URL construction
        print(f"--- Starting search for {clean_topic} in language {clean_lang} ---")
        
        # Step 1: Fuzzy search
        search_params = {
            'action': 'query',
            'format': 'json',
            'generator': 'search',
            'gsrsearch': clean_topic,  # <-- Using cleaned topic
            'gsrlimit': '1',
            'prop': 'extracts',
            'explaintext': '1',
 #           'explaintext': '0', # For the entire article
            'exintro': '1',
            'origin': '*'
        }

        # Actually wants browser
        search_res = session.get(base_url, params=search_params)
#        search_res = requests.get(base_url, params=search_params)
        search_res.raise_for_status()
        search_data = search_res.json()

        pages = search_data.get('query', {}).get('pages')
        if not pages:
            return f"Error: No Wikipedia articles found matching '{topic}' in language '{lang}'."
        
        first_page_key = list(pages.keys())[0]
        page = pages[first_page_key]
        title = page.get('title')
        extract = page.get('extract') or ""



        # Step 2: Fetch the HTML of Section 0 (the top of the page) to grab the infobox
        infobox_text = ""
        try:
            parse_params = {
                'action': 'parse',
                'page': title,
                'section': '0',
                'prop': 'text',
                'format': 'json',
                'origin': '*'
            }

            parse_res = session.get(base_url, params=parse_params, impersonate="firefox")
#            parse_res = requests.get(base_url, params=parse_params)
            parse_res.raise_for_status()
            parse_data = parse_res.json()
            
            # The raw HTML is usually under 'parse' -> 'text' -> '*'
            html = parse_data.get('parse', {}).get('text', {}).get('*')

            if html:
                # Use BeautifulSoup to parse the HTML content
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find the infobox table (matching your original selector)
                infobox = soup.find('table', class_='infobox')
                
                if infobox:

                    tbody = infobox

#                    print("DEBUG INFOBOX HTML:")
#                    print(infobox.prettify())  # Pretty-prints the HTML

                    rows = infobox.find('tbody').find_all('tr', recursive=False)
                    for row in rows:
                        th = row.find('th', recursive=False)
                        td = row.find('td', recursive=False)

                        nested_table = td.find('table') if td else None

                        if nested_table:
                            # Recursively parse the nested table
                            nested_tbody = nested_table.find('tbody') or nested_table
                            nested_rows = nested_tbody.find_all('tr', recursive=False)

                            for nested_row in nested_rows:
                                nested_th = nested_row.find('th')
                                nested_td = nested_row.find('td')

                                if nested_th and nested_td:

                                    for hidden in nested_td.find_all('span', {'style': lambda x: x and 'display: none' in x}):
                                        hidden.decompose()
                                    for sup in nested_td.find_all('sup'):
                                        sup.decompose()

                                    key = nested_th.get_text(separator=' ', strip=True)
#                                    value = nested_td.get_text(separator=' ', strip=True)

                                    # Special handling for lists
                                    lis = nested_td.find_all('li')
                                    if lis:
                                        parts = []

                                        # Get direct text nodes before the list
                                        for content in nested_td.contents:
                                            if getattr(content, 'name', None) in ('ul', 'ol', 'div'):
                                                break

                                            if isinstance(content, str):
                                                text = content.strip()
                                                if text:
                                                    parts.append(text)

                                        parts.extend(
                                            li.get_text(" ", strip=True)
                                            for li in lis
                                        )

                                        value = " | ".join(parts)
                                    else:
                                        value = nested_td.get_text(" ", strip=True)


                                    infobox_text += f"{key}: {value}\n"

                        elif th and td:
                            for hidden in td.find_all('span', {'style': lambda x: x and 'display: none' in x}):
                                hidden.decompose()
                            for sup in td.find_all('sup'):
                                sup.decompose()

                            key = th.get_text(separator=' ', strip=True)
#                            value = td.get_text(separator=' ', strip=True)
                            if lis:
                                value = " | ".join(
                                    li.get_text(" ", strip=True)
                                    for li in lis
                                )
                            else:
                                value = td.get_text(" ", strip=True)

                            infobox_text += f"{key}: {value}\n"

        except requests.exceptions.RequestException as e:
            print(f"Warning: Failed to parse infobox (network error): {e}")
        except Exception as e:
            print(f"Warning: Failed to parse infobox (parsing error): {e}")

        # Step 3: Combine Infobox and Extract
        final_result = ""
        if infobox_text:
            final_result += f"---\nINFOBOX:\n{infobox_text}"
#            print(f"DEBUG STRING REPR: {repr(infobox_text)}\n\n")  # Shows \n as literal \n
            print(f"INFOBOX:\n{infobox_text}\n")

        if extract:
            final_result += f"---\nSUMMARY:\n{extract}"
            print(f"SUMMARY:\n{extract}\nEND")
        
        if not final_result.strip():
             return f"Found page '{title}' but no text or infobox was available."

        # Step 4: Apply language-based safety caps (Replicating your logic)
        max_chars = 10000
        if lang.lower() == 'zh':
            max_chars = 3000
        elif lang.lower() == 'fr':
            max_chars = 8600
        elif lang.lower() == 'es':
            max_chars = 9000
            
        if len(final_result) > max_chars:
            final_result = final_result[:max_chars] + "\n\n... [TRUNCATED TO SAVE CONTEXT]"
            
        return final_result

    except requests.exceptions.RequestException as e:
        return f"Critical API Error: Could not connect to Wikipedia. Details: {e}"
    except Exception as e:
        return f"An unexpected error occurred while running the Wikipedia tool: {e}"

system_instruction = "<|think|>"

# The list the LLM receives
tools = [execute_python_code, query_wikipedia]  # <--- Added your new tool here
# add_numbers, get_current_time, calculate_hash, get_current_weather, get_current_location,
