import json
import sys

def get_current_weather(location: str) -> str:
    return "Hot"

def square_the_number(input_num: float) -> float:
    return input_num ** 2

import requests
from bs4 import BeautifulSoup
from typing import Callable, Any
import re

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
#    clean_topic = clean_input_string(topic)
#    clean_lang = clean_input_string(lang)
    
#    if not clean_lang or not clean_topic:
#        return "Error: Invalid or empty topic or language code provided after cleaning."

#    base_url = f"https://{clean_lang}.wikipedia.org/w/api.php"
    base_url = f"https://{lang}.wikipedia.org/w/api.php"

    from curl_cffi import requests  # re‑exports a Session compatible with `requests`
# -------------------------------------------------
# Create a session (optional but recommended)
# -------------------------------------------------
    session = requests.Session()
    
    try:
        # Use the cleaned variables for URL construction
#        print(f"--- Starting search for {clean_topic} in language {clean_lang} ---")
        print(f"--- Starting search for {topic} in language {lang} ---")
        
        # Step 1: Fuzzy search
        search_params = {
            'action': 'query',
            'format': 'json',
            'generator': 'search',
#            'gsrsearch': clean_topic,  # <-- Using cleaned topic
            'gsrsearch': topic,  # <-- Using topic
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

                    print("DEBUG INFOBOX HTML:")
                    print(infobox.prettify())  # Pretty-prints the HTML

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

from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="EMPTY"
)

messages=[
#        {
#            "role": "system",
#            "content": [
#                {
#                    "type": "text",
#                    "text": "<|think|>"
#                }
#            ]
#        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": sys.argv[1],
#                    "text": "Find the square of 1024 using the tool.",
                }
            ]
        },
    ]
tools=[{
        "type":"function",
        "function":{
            "name":"get_current_weather",
            "description":"Get the current weather in a given location",
            "parameters":{
                "type":"object",
                "properties":{
                    "location":{
                        "type":"string",
                        "description":"The city and country/state, e.g. `San Francisco, CA`, or `Paris, France`"
                    }
                },
                "required":["location"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name": "square_the_number",
            "description": "output the square of the number.",
            "parameters": {
                "type": "object",
                "required": ["input_num"],
                "properties": {
                    'input_num': {
                        'type': 'number', 
                        'description': 'input_num is a number that will be squared'
                        }
                },
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name": "query_wikipedia",
            "description": "Query summary from Wikipedia for a given topic.",
            "parameters": {
                "type": "object",
                "required": ["topic", "lang"],
                "properties": {
                    'topic': {
                        'type': 'string',
                        'description': 'Extract ONLY the primary entity, person, or event. The "topic" must be in the same language as the "lang".'
                        },
                    'lang': {
                        'type': 'string',
                        'description': 'The two-letter language code for the Wikipedia article.'
                        }
                },
            }
        }
    },
    ]

tool_map = {
    "square_the_number": square_the_number,
  "get_current_weather": get_current_weather,
      "query_wikipedia": query_wikipedia
}

tool_buffers = {}
thinking_open = False

try:
  while True:

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        stream=True
    )

    thinking_open = False
    tool_buffers = {}

    assistant_message = {
        "role": "assistant",
        "content": "",
        "tool_calls": []
    }

    finish_reason = None

    # ==========================================
    # STREAM LOOP
    # ==========================================

    for chunk in stream:

        choice = chunk.choices[0]
        delta = choice.delta

        reasoning = getattr(delta, "reasoning_content", None)
        content = getattr(delta, "content", None)
        tool_calls = getattr(delta, "tool_calls", None)

        if choice.finish_reason:
            finish_reason = choice.finish_reason

        # --------------------------------------
        # reasoning
        # --------------------------------------
        if reasoning:

            if not thinking_open:
                print("[thinking: ", end="", flush=True)
                thinking_open = True

            print(reasoning, end="", flush=True)

        # --------------------------------------
        # assistant text
        # --------------------------------------
        if content:

            if thinking_open:
                print("]\n", flush=True)
                thinking_open = False

            assistant_message["content"] += content

            print(content, end="", flush=True)

        # --------------------------------------
        # tool calls
        # --------------------------------------
        if tool_calls:

            if thinking_open:
                print("]\nCalling tool?", flush=True)
                thinking_open = False

            for tc in tool_calls:

                index = tc.index

                if index not in tool_buffers:
                    tool_buffers[index] = {
                        "id": "",
                        "name": "",
                        "arguments": ""
                    }

                if tc.id:
                    tool_buffers[index]["id"] = tc.id

                fn = tc.function

                if fn.name:
                    tool_buffers[index]["name"] = fn.name

                if fn.arguments:
                    tool_buffers[index]["arguments"] += fn.arguments

    # ==========================================
    # CLOSE THINKING BLOCK
    # ==========================================
    if thinking_open:
        print("]")

    # ==========================================
    # NORMAL COMPLETION
    # ==========================================
    if finish_reason == "stop":

        messages.append({
            "role": "assistant",
            "content": assistant_message["content"]
        })

      # print("\n\n[done]")
        break

    # ==========================================
    # TOOL EXECUTION
    # ==========================================
    elif finish_reason == "tool_calls":
      # print("=== TOOL CALLS ===")
        for i, tool in tool_buffers.items():
            print(f"\nTool #{i}")
            print("Name:", tool["name"])
            print("Arguments:")
            print(tool["arguments"])



        # 1. build assistant tool-call message
        assistant_tool_calls = []

        for i, tool in tool_buffers.items():
            assistant_tool_calls.append({
                "id": tool["id"],
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "arguments": tool["arguments"]
                }
            })

        # 2. append ASSISTANT tool-call message FIRST
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": assistant_tool_calls
        })

        # 3. execute tools + append tool results
        for i, tool in tool_buffers.items():

            fn_name = tool["name"]
            fn_args = json.loads(tool["arguments"])

            result = tool_map[fn_name](**fn_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool["id"],
                "content": json.dumps(result)
            })
        print("\n[tool completed]\n")

#    elif finish_reason == "stop":
#        print("\n\n[done]")

except KeyboardInterrupt:
    # User pressed Ctrl‑C – stop streaming without a traceback
    print("\n[interrupted]")
finally:
    # Ensure the cursor ends on a new line even if no interrupt occurs
    print()
